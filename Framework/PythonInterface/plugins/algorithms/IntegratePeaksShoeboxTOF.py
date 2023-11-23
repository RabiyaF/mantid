# Mantid Repository : https://github.com/mantidproject/mantid
#
# Copyright &copy; 2023 ISIS Rutherford Appleton Laboratory UKRI,
#     NScD Oak Ridge National Laboratory, European Spallation Source
#     & Institut Laue - Langevin
# SPDX - License - Identifier: GPL - 3.0 +
from mantid.api import (
    DataProcessorAlgorithm,
    AlgorithmFactory,
    MatrixWorkspaceProperty,
    IPeaksWorkspaceProperty,
    WorkspaceUnitValidator,
    FileProperty,
    FileAction,
)
from mantid.kernel import (
    Direction,
    FloatBoundedValidator,
    IntBoundedValidator,
    StringListValidator,
    EnabledWhenProperty,
    PropertyCriterion,
)
import numpy as np
from scipy.ndimage import uniform_filter
from scipy.signal import convolve
from IntegratePeaksSkew import InstrumentArrayConverter, get_fwhm_from_back_to_back_params
from FindSXPeaksConvolve import make_kernel, get_kernel_shape
from enum import Enum


class PEAK_STATUS(Enum):
    WEAK = "Weak peak"
    STRONG = "Strong peak"
    ON_EDGE = "Peak mask is on the detector edge"
    ON_EDGE_INTEGRATED = "Peak mask is on the detector edge"
    NO_PEAK = "No peak detected."


class WeakPeak:
    def __init__(self, ipk, ispec, tof, tof_fwhm, ipks_near):
        self.ipk = ipk
        self.ispec = ispec  # spectrum at center of kernel that corresponds to max I/sigma from convolution
        self.tof = tof  # TOF at center of kernel that corresponds to max I/sigma from convolution
        self.tof_fwhm = tof_fwhm
        self.ipks_near = ipks_near


class ShoeboxResult:
    """
    This class is used to hold data and integration parameters for single-crystal Bragg peaks
    """

    def __init__(self, ipk, pk, x, y, peak_shape, ipos, ipk_pos, intens_over_sig, status, strong_peak=None, ipk_strong=None):
        self.peak_shape = list(peak_shape)
        self.kernel_shape = list(get_kernel_shape(*self.peak_shape)[0])
        self.ipos = list(ipos) if ipos is not None else ipos
        self.ipos_pk = list(ipk_pos)
        self.labels = ["Row", "Col", "TOF"]
        self.ysum = []
        self.extents = []
        self.status = status
        # integrate y over each dim
        for idim in range(len(peak_shape)):
            self.ysum.append(y.sum(axis=idim))
            if idim < 2:
                self.extents.append([0, y.shape[idim]])
            else:
                self.extents.append([x[0], x[-1]])
        # extract peak properties
        intens_over_sig = np.round(intens_over_sig, 1)
        hkl = np.round(pk.getHKL(), 2)
        wl = np.round(pk.getWavelength(), 2)
        tth = np.round(np.degrees(pk.getScattering()), 1)
        d = np.round(pk.getDSpacing(), 2)
        self.title = (
            f"{ipk} ({','.join(str(hkl)[1:-1].split())})"
            f"\n$I/\\sigma$={intens_over_sig}\n"
            rf"$\lambda$={wl} $\AA$; "
            rf"$2\theta={tth}^\circ$; "
            rf"d={d} $\AA$"
            f"\n{status.value}"
        )
        if strong_peak is not None and ipk_strong is not None:
            self.title = f"{self.title} (shoebox taken from ipk={ipk_strong} {np.round(strong_peak.getHKL(), 2)})"

    def plot_integrated_peak(self, fig, axes, norm_func, rect_func):
        for iax, ax in enumerate(axes):
            extents = self.extents.copy()
            extents.pop(iax)
            im = ax.imshow(
                self.ysum[iax], aspect=self.ysum[iax].shape[1] / self.ysum[iax].shape[0]
            )  # , extent=np.flip(extents, axis=0).flatten())
            im.set_norm(norm_func())
            # plot shoebox
            if self.ipos is not None:
                self.plot_shoebox(iax, ax, rect_func)
            # plot peak position
            cen = self.ipos_pk.copy()
            cen.pop(iax)
            ax.plot(cen[1], cen[0], "xr")
            # set labels
            labels = self.labels.copy()
            labels.pop(iax)
            ax.set_xlabel(labels[1])
            ax.set_ylabel(labels[0])
        # set title
        fig.suptitle(self.title)

    def plot_shoebox(self, iax, ax, rect_func):
        cen = self.ipos.copy()
        cen.pop(iax)
        # plot peak region
        shape = self.peak_shape.copy()
        shape.pop(iax)
        self._plot_rect(ax, cen, shape, rect_func)
        # plot kernel (incl. bg shell)
        shape = self.kernel_shape.copy()
        shape.pop(iax)
        self._plot_rect(ax, cen, shape, rect_func, ls="--")

    def _plot_rect(self, ax, cen, shape, rect_func, ls="-"):
        bottom_left = [cen[1] - shape[1] // 2 - 0.5, cen[0] - shape[0] // 2 - 0.5]
        rect = rect_func(bottom_left, shape[1], shape[0], linewidth=1.5, edgecolor="r", facecolor="none", alpha=0.75, ls=ls)
        ax.add_patch(rect)


class IntegratePeaksShoeboxTOF(DataProcessorAlgorithm):
    def name(self):
        return "IntegratePeaksShoeboxTOF"

    def category(self):
        return "Diffraction\\Reduction"

    def seeAlso(self):
        return ["IntegratePeaksSkew", "FindSXPeaksConvolve"]

    def summary(self):
        return "Integrate single-crystal Bragg peaks in MatrixWorkspaces with x-unit of TOF using a shoebox."

    def PyInit(self):
        # Input
        self.declareProperty(
            MatrixWorkspaceProperty(
                name="InputWorkspace", defaultValue="", direction=Direction.Input, validator=WorkspaceUnitValidator("TOF")
            ),
            doc="A MatrixWorkspace to integrate (x-axis must be TOF).",
        )
        self.declareProperty(
            IPeaksWorkspaceProperty(name="PeaksWorkspace", defaultValue="", direction=Direction.Input),
            doc="A PeaksWorkspace containing the peaks to integrate.",
        )
        self.declareProperty(
            IPeaksWorkspaceProperty(name="OutputWorkspace", defaultValue="", direction=Direction.Output),
            doc="The output PeaksWorkspace will be a copy of the input PeaksWorkspace with the" " integrated intensities.",
        )
        # shoebox dimensions
        self.declareProperty(
            name="NRows",
            defaultValue=5,
            direction=Direction.Input,
            validator=IntBoundedValidator(lower=3),
            doc="Number of row components in the detector to use in the convolution kernel. "
            "For WISH row components correspond to pixels along a single tube.",
        )
        self.declareProperty(
            name="NCols",
            defaultValue=5,
            direction=Direction.Input,
            validator=IntBoundedValidator(lower=3),
            doc="Number of column components in the detector to use in the convolution kernel. "
            "For WISH column components correspond to tubes.",
        )
        self.declareProperty(
            name="NBins",
            defaultValue=11,
            direction=Direction.Input,
            validator=IntBoundedValidator(lower=3),
            doc="Number of TOF bins to use in the convolution kernel.",
        )
        self.declareProperty(
            name="GetNBinsFromBackToBackParams",
            defaultValue=False,
            direction=Direction.Input,
            doc="If true the number of TOF bins used in the convolution kernel will be calculated from the FWHM of the "
            "BackToBackExponential peak using parameters defined in the instrument parameters.xml file.",
        )
        self.declareProperty(
            name="NFWHM",
            defaultValue=4,
            direction=Direction.Input,
            validator=IntBoundedValidator(lower=1),
            doc="If GetNBinsFromBackToBackParams=True then the number of TOF bins will be NFWHM x FWHM of the "
            "BackToBackExponential at the peak detector and TOF.",
        )
        use_nBins = EnabledWhenProperty("GetNBinsFromBackToBackParams", PropertyCriterion.IsDefault)
        self.setPropertySettings("NBins", use_nBins)
        use_nfwhm = EnabledWhenProperty("GetNBinsFromBackToBackParams", PropertyCriterion.IsNotDefault)
        self.setPropertySettings("NFWHM", use_nfwhm)
        self.declareProperty(
            name="NShoeboxInWindow",
            defaultValue=3.0,
            direction=Direction.Input,
            validator=FloatBoundedValidator(lower=2.0),
            doc="Extent of window in TOF and detector row and column as a multiple of the shoebox length along each dimension.",
        )
        for prop in ["NRows", "NCols", "NBins", "GetNBinsFromBackToBackParams", "NFWHM", "NShoeboxInWindow"]:
            self.setPropertyGroup(prop, "Shoebox Dimensions")
        # shoebox optimisation
        self.declareProperty(
            name="OptimiseShoebox",
            defaultValue=True,
            direction=Direction.Input,
            doc="If OptimiseShoebox=True then shoebox size will be optimised to maximise Intensity/Sigma of the peak.",
        )
        self.declareProperty(
            name="WeakPeakStrategy",
            defaultValue="Fix",
            direction=Direction.Input,
            validator=StringListValidator(["Fix", "NearestStrongPeak"]),
            doc="If WeakPeakStrategy=Fix then fix the shoebox dimensions. If WeakPeakStrategy=NearestStrongPeak then"
            "the shoebox dimensions will be taken from the nearest strong peak (determined by StrongPeakThreshold)."
            "The TOF extent of the shoebox will be scaled by the FWHM of the BackToBackExponential peaks if"
            "GetNBinsFromBackToBackParams=True.",
        )
        self.declareProperty(
            name="WeakPeakThreshold",
            defaultValue=0.0,
            direction=Direction.Input,
            validator=FloatBoundedValidator(lower=0.0),
            doc="Intenisty/Sigma threshold below which a peak is considered weak.",
        )
        optimise_shoebox_enabled = EnabledWhenProperty("OptimiseShoebox", PropertyCriterion.IsDefault)
        self.setPropertySettings("WeakPeakStrategy", optimise_shoebox_enabled)
        self.setPropertySettings("WeakPeakThreshold", optimise_shoebox_enabled)
        for prop in ["OptimiseShoebox", "WeakPeakStrategy", "WeakPeakThreshold"]:
            self.setPropertyGroup(prop, "Shoebox Optimisation")
        # peak validation
        self.declareProperty(
            name="IntegrateIfOnEdge",
            defaultValue=False,
            direction=Direction.Input,
            doc="If IntegrateIfOnEdge=False then peaks with shoebox that includes detector IDs at the edge of the bank "
            " will not be integrated.",
        )
        self.declareProperty(
            name="NRowsEdge",
            defaultValue=1,
            direction=Direction.Input,
            validator=IntBoundedValidator(lower=1),
            doc="Shoeboxes containing detectors NRowsEdge from the detector edge are defined as on the edge.",
        )
        self.declareProperty(
            name="NColsEdge",
            defaultValue=1,
            direction=Direction.Input,
            validator=IntBoundedValidator(lower=1),
            doc="Shoeboxes containing detectors NColsEdge from the detector edge are defined as on the edge.",
        )
        edge_check_enabled = EnabledWhenProperty("IntegrateIfOnEdge", PropertyCriterion.IsDefault)
        self.setPropertySettings("NRowsEdge", edge_check_enabled)
        self.setPropertySettings("NColsEdge", edge_check_enabled)
        for prop in ["IntegrateIfOnEdge", "NRowsEdge", "NColsEdge"]:
            self.setPropertyGroup(prop, "Edge Checking")
        # Corrections
        self.declareProperty(
            name="LorentzCorrection",
            defaultValue=True,
            direction=Direction.Input,
            doc="Correct the integrated intensity by multiplying by the Lorentz factor "
            "sin(theta)^2 / lambda^4 - do not do this if the data have already been corrected.",
        )
        self.setPropertyGroup("LorentzCorrection", "Corrections")
        # plotting
        self.declareProperty(
            FileProperty("OutputFile", "", FileAction.OptionalSave, ".pdf"),
            "Optional file path in which to write diagnostic plots (note this will slow the " "execution of algorithm).",
        )
        self.setPropertyGroup("OutputFile", "Plotting")

    def validateInputs(self):
        issues = dict()
        # check shoebox dimensions
        for prop in ["NRows", "NCols", "NBins"]:
            if not self.getProperty(prop).value % 2:
                issues[prop] = f"{prop} must be an odd number."
        # check valid peak workspace
        ws = self.getProperty("InputWorkspace").value
        inst = ws.getInstrument()
        pk_ws = self.getProperty("PeaksWorkspace").value
        if inst.getName() != pk_ws.getInstrument().getName():
            issues["PeaksWorkspace"] = "PeaksWorkspace must have same instrument as the InputWorkspace."
        if pk_ws.getNumberPeaks() < 1:
            issues["PeaksWorkspace"] = "PeaksWorkspace must have at least 1 peak."
        # check that is getting dTOF from back-to-back params then they are present in instrument
        if self.getProperty("GetNBinsFromBackToBackParams").value:
            # check at least first peak in workspace has back to back params
            if not inst.getComponentByName(pk_ws.column("BankName")[0]).hasParameter("B"):
                issues[
                    "GetNBinsFromBackToBackParams"
                ] = "Workspace doesn't have back to back exponential coefficients defined in the parameters.xml file."
        return issues

    def PyExec(self):
        # get input
        ws = self.getProperty("InputWorkspace").value
        peaks = self.getProperty("PeaksWorkspace").value
        # shoebox dimensions
        get_nbins_from_b2bexp_params = self.getProperty("GetNBinsFromBackToBackParams").value
        nfwhm = self.getProperty("NFWHM").value
        nshoebox = self.getProperty("NShoeboxInWindow").value
        # shoebox optimisation
        do_optimise_shoebox = self.getProperty("OptimiseShoebox").value
        weak_peak_strategy = self.getProperty("WeakPeakStrategy").value
        weak_peak_threshold = self.getProperty("WeakPeakThreshold").value
        # validation
        integrate_on_edge = self.getProperty("IntegrateIfOnEdge").value
        nrows_edge = self.getProperty("NRowsEdge").value
        ncols_edge = self.getProperty("NColsEdge").value
        # corrections
        do_lorz_cor = self.getProperty("LorentzCorrection").value
        # saving file
        output_file = self.getProperty("OutputFile").value

        # create output table workspace
        peaks = self.exec_child_alg("CloneWorkspace", InputWorkspace=peaks, OutputWorkspace="out_peaks")

        array_converter = InstrumentArrayConverter(ws)
        weak_peaks_list = []
        ipks_strong = []
        results = np.full(peaks.getNumberPeaks(), None)
        for ipk, peak in enumerate(peaks):
            status = PEAK_STATUS.NO_PEAK
            intens, sigma = 0.0, 0.0

            detid = peak.getDetectorID()
            bank_name = peaks.column("BankName")[ipk]
            pk_tof = peak.getTOF()

            # check TOF is in limits of x-axis
            xdim = ws.getXDimension()
            if xdim.getMinimum() < pk_tof < xdim.getMaximum():
                # get shoebox kernel for initial integration
                nrows = self.getProperty("NRows").value  # get these inside loop as overwritten if shoebox optimised
                ncols = self.getProperty("NCols").value
                ispec = ws.getIndicesFromDetectorIDs([detid])[0]
                itof = ws.yIndexOfX(pk_tof, ispec)
                bin_width = np.diff(ws.readX(ispec)[itof : itof + 2])[0]  # used later to scale intensity
                if get_nbins_from_b2bexp_params:
                    fwhm = get_fwhm_from_back_to_back_params(peak, ws, detid)
                    nbins = max(3, int(nfwhm * fwhm / bin_width)) if fwhm is not None else self.getProperty("NBins").value
                    nbins = round_up_to_odd_number(nbins)
                else:
                    nbins = self.getProperty("NBins").value
                kernel = make_kernel(nrows, ncols, nbins)

                # get data array and crop
                peak_data = array_converter.get_peak_data(
                    peak, detid, bank_name, nshoebox * kernel.shape[0], nshoebox * kernel.shape[1], nrows_edge, ncols_edge
                )
                x, y, esq, ispecs = get_and_clip_data_arrays(ws, peak_data, pk_tof, ispec, kernel, nshoebox)

                # perform initial integration
                intens_over_sig = convolve_shoebox(y, esq, kernel)

                # identify best shoebox position near peak
                ix = np.argmin(abs(x - pk_tof))
                ipos = find_nearest_peak_in_data_window(intens_over_sig, ispecs, x, ws, peaks, ipk, peak_data.irow, peak_data.icol, ix)

                # perform final integration if required
                det_edges = peak_data.det_edges if not integrate_on_edge else None
                if ipos is not None:
                    # integrate at that position (without smoothing I/sigma)
                    intens, sigma, status = integrate_shoebox_at_pos(y, esq, kernel, ipos, weak_peak_threshold, det_edges)
                    if status == PEAK_STATUS.STRONG and do_optimise_shoebox:
                        ipos, (nrows, ncols, nbins) = optimise_shoebox(y, esq, (nrows, ncols, nbins), ipos)
                        kernel = make_kernel(nrows, ncols, nbins)
                        # re-integrate but this time check for overlap with edge
                        intens, sigma, status = integrate_shoebox_at_pos(y, esq, kernel, ipos, weak_peak_threshold, det_edges)

                if status == PEAK_STATUS.WEAK and do_optimise_shoebox and weak_peak_strategy == "NearestStrongPeak":
                    # look for possible strong peaks at any TOF in the window (won't know if strong until all pks integrated)
                    ipks_near, _ = find_ipks_in_window(ws, peaks, ispecs, ipk)
                    weak_peaks_list.append(WeakPeak(ipk, ispecs[ipos[0], ipos[1]], x[ipos[-1]], fwhm, ipks_near))
                else:
                    if status == PEAK_STATUS.STRONG:
                        ipks_strong.append(ipk)
                    if output_file:
                        # save result for plotting
                        i_over_sig = intens / sigma if sigma > 0 else 0.0
                        results[ipk] = ShoeboxResult(
                            ipk, peak, x, y, [nrows, ncols, nbins], ipos, [peak_data.irow, peak_data.icol, ix], i_over_sig, status
                        )
                # scale summed intensity by bin width to get integrated area
                intens = intens * bin_width
                sigma = sigma * bin_width
            set_peak_intensity(peak, intens, sigma, do_lorz_cor)

        if len(ipks_strong):
            # set function for calculating distance metric between peaks
            # if know back to back params then can scale TOF extent by ratio of FWHM
            # otherwise just look for peak closest in QLab
            calc_dist_func = calc_angle_between_peaks if get_nbins_from_b2bexp_params else calc_dQsq_between_peaks

            for weak_pk in weak_peaks_list:
                # get peak
                ipk = weak_pk.ipk
                peak = peaks.getPeak(ipk)
                bank_name = peaks.column("BankName")[ipk]
                pk_tof = peak.getTOF()
                # find nearest strong peak to get shoebox dimensions from
                ipks_near_strong = []
                for ipk_near in weak_pk.ipks_near:
                    if results[ipk_near].status == PEAK_STATUS.STRONG:
                        ipks_near_strong.append(ipk_near)
                if not ipks_near_strong:
                    # no peaks in detector window at any TOF, look in all table
                    ipks_near_strong = ipks_strong
                # loop over strong peaks and find nearest peak
                ipk_strong = None
                dist_min = np.inf
                for ipk_near in ipks_near_strong:
                    dist = calc_dist_func(peak, peaks.getPeak(ipk_near))
                    if dist < dist_min:
                        ipk_strong = ipk_near
                strong_pk = peaks.getPeak(ipk_strong)

                # get peak shape and make kernel
                nrows, ncols, nbins = results[ipk_strong].peak_shape
                if get_nbins_from_b2bexp_params:
                    # scale TOF extent by ratio of fwhm
                    strong_pk_fwhm = get_fwhm_from_back_to_back_params(strong_pk, ws, strong_pk.getDetectorID())
                    nbins = max(3, int(nbins * (weak_pk.tof_fwhm / strong_pk_fwhm)))
                    nbins = round_up_to_odd_number(nbins)
                kernel = make_kernel(nrows, ncols, nbins)
                # get data array in peak region (keep same window size, nshoebox, for plotting)
                peak_data = array_converter.get_peak_data(
                    peak, peak.getDetectorID(), bank_name, nshoebox * kernel.shape[0], nshoebox * kernel.shape[1], nrows_edge, ncols_edge
                )
                x, y, esq, ispecs = get_and_clip_data_arrays(ws, peak_data, pk_tof, ispec, kernel, nshoebox)
                # integrate at previously found ipos
                ipos = [*np.argwhere(ispecs == weak_pk.ispec)[0], np.argmin(abs(x - weak_pk.tof))]
                det_edges = peak_data.det_edges if not integrate_on_edge else None
                intens, sigma, status = integrate_shoebox_at_pos(y, esq, kernel, ipos, weak_peak_threshold, det_edges)
                # scale summed intensity by bin width to get integrated area
                intens = intens * bin_width
                sigma = sigma * bin_width
                set_peak_intensity(peak, intens, sigma, do_lorz_cor)
                if output_file:
                    # save result for plotting
                    i_over_sig = intens / sigma if sigma > 0 else 0.0
                    results[ipk] = ShoeboxResult(
                        ipk,
                        peak,
                        x,
                        y,
                        [nrows, ncols, nbins],
                        ipos,
                        [peak_data.irow, peak_data.icol, np.argmin(abs(x - pk_tof))],
                        i_over_sig,
                        status,
                        strong_peak=strong_pk,
                        ipk_strong=ipk_strong,
                    )
        elif weak_peak_strategy == "NearestStrongPeak":
            raise ValueError(
                f"No peaks found with I/sigma > WeakPeakThreshold ({weak_peak_threshold}) - can't "
                f"estimate shoebox dimension for weak peaks. Try reducing WeakPeakThreshold or set "
                f"WeakPeakStrategy to Fix"
            )

        # plot output
        plot_integration_reuslts(output_file, results)

        # assign output
        self.setProperty("OutputWorkspace", peaks)

    def exec_child_alg(self, alg_name, **kwargs):
        alg = self.createChildAlgorithm(alg_name, enableLogging=False)
        alg.initialize()
        for prop, value in kwargs.items():
            alg.setProperty(prop, value)
        alg.execute()
        if "OutputWorkspace" in alg.outputProperties():
            return alg.getProperty("OutputWorkspace").value
        else:
            return None


def round_up_to_odd_number(number):
    if not number % 2:
        number += 1
    return number


def plot_integration_reuslts(output_file, results):
    # import inside this function as not allowed to import at point algorithms are registered
    from matplotlib.pyplot import subplots, close
    from matplotlib.patches import Rectangle
    from matplotlib.colors import LogNorm
    from matplotlib.backends.backend_pdf import PdfPages

    try:
        with PdfPages(output_file) as pdf:
            for result in results:
                if result:
                    fig, axes = subplots(1, 3, figsize=(12, 5), subplot_kw={"projection": "mantid"})
                    fig.subplots_adjust(wspace=0.3)  # ensure plenty space between subplots (want to avoid slow tight_layout)
                    result.plot_integrated_peak(fig, axes, LogNorm, Rectangle)
                    pdf.savefig(fig)
                    close(fig)
    except OSError:
        raise RuntimeError(
            f"OutputFile ({output_file}) could not be opened - please check it is not open by "
            f"another programme and that the user has permission to write to that directory."
        )


def calc_angle_between_peaks(pk1, pk2):
    return abs(pk1.getQLabFrame().angle(pk2.getQLabFrame()))


def calc_dQsq_between_peaks(pk1, pk2):
    return (pk1.getQLabFrame() - pk2.getQLabFrame()).norm2()


def get_and_clip_data_arrays(ws, peak_data, pk_tof, ispec, kernel, nshoebox):
    x, y, esq, ispecs = peak_data.get_data_arrays()  # 3d arrays [rows x cols x tof]
    x = x[peak_data.irow, peak_data.icol, :]  # take x at peak centre, should be same for all detectors
    # crop data array to TOF region of peak using shoebox dimension
    itof = ws.yIndexOfX(pk_tof, ispec)  # need index in y now (note x values are points even if were edges)
    tof_slice = slice(
        int(np.clip(itof - nshoebox * kernel.shape[-1] // 2, a_min=0, a_max=len(x))),
        int(np.clip(itof + nshoebox * kernel.shape[-1] // 2, a_min=0, a_max=len(x))),
    )
    x = x[tof_slice]
    y = y[:, :, tof_slice]
    esq = esq[:, :, tof_slice]
    return x, y, esq, ispecs


def convolve_shoebox(y, esq, kernel, mode="same", do_smooth=True):
    yconv = convolve(y, kernel, mode=mode)
    econv = np.sqrt(convolve(esq, kernel**2, mode=mode))
    with np.errstate(divide="ignore", invalid="ignore"):
        intens_over_sig = yconv / econv
    intens_over_sig[~np.isfinite(intens_over_sig)] = 0
    intens_over_sig = uniform_filter(intens_over_sig, size=len(y.shape))
    # zero edges where convolution is invalid
    if mode == "same":
        edge_mask = np.ones(intens_over_sig.shape, dtype=bool)
        center_slice = tuple(slice(nedge, -nedge) for nedge in (np.asarray(kernel.shape) - 1) // 2)
        edge_mask[center_slice] = False
        intens_over_sig[edge_mask] = 0
    return intens_over_sig


def find_nearest_peak_in_data_window(data, ispecs, x, ws, peaks, ipk, irow, icol, ix, threshold=2):
    ipks_near, ispecs_peaks = find_ipks_in_window(ws, peaks, ispecs, ipk, tof_min=x.min(), tof_max=x.max())
    if len(ipks_near) > 0:
        tofs = peaks.column("TOF")
        # get position of nearby peaks in data array in fractional coords
        shape = np.array(data.shape)
        pos_near = [
            np.r_[np.argwhere(ispecs == ispecs_peaks[ii])[0], np.argmin(abs(x - tofs[ipk_near]))] / shape
            for ii, ipk_near in enumerate(ipks_near)
        ]
        # sort data in descending order and select strongest data point nearest to pk (in fractional coordinates)
        isort = list(zip(*np.unravel_index(np.argsort(-data, axis=None), data.shape)))
        pk_pos = np.array([irow, icol, ix]) / np.array(data.shape)
        imax_nearest = None
        for ibin in isort:
            if data[ibin] > threshold:
                # calc distance to predicted peak position
                bin_pos = np.array(ibin) / shape
                pk_dist_sq = np.sum((pk_pos - bin_pos) ** 2)
                for pos in pos_near:
                    if np.sum((pos - bin_pos) ** 2) > pk_dist_sq:
                        imax_nearest = ibin
                        break
                else:
                    continue  # executed if inner loop did not break (i.e. pixel closer to nearby peak than this peak)
                break  # execute if inner loop did break and else branch ignored (i.e. found bin closest to this peak)
        return imax_nearest  # could be None if no peak found
    else:
        # no nearby peaks - return position of maximum in data
        return np.unravel_index(np.argmax(data), data.shape)


def find_ipks_in_window(ws, peaks, ispecs, ipk, tof_min=None, tof_max=None):
    ispecs_peaks = ws.getIndicesFromDetectorIDs([int(p.getDetectorID()) for p in peaks])
    ipks_near = np.isin(ispecs_peaks, ispecs)
    if tof_min and tof_max:
        tofs = peaks.column("TOF")
        ipks_near = np.logical_and.reduce((tofs >= tof_min, tofs <= tof_max, ipks_near))
    ipks_near = np.flatnonzero(ipks_near)  # convert to index
    ipks_near = np.delete(ipks_near, np.where(ipks_near == ipk))  # remove the peak of interest
    return ipks_near, ispecs_peaks


def integrate_shoebox_at_pos(y, esq, kernel, ipos, weak_peak_threshold, det_edges=None):
    slices = tuple(
        [
            slice(
                np.clip(ii - kernel.shape[idim] // 2, a_min=0, a_max=y.shape[idim]),
                np.clip(ii + kernel.shape[idim] // 2 + 1, a_min=0, a_max=y.shape[idim]),
            )
            for idim, ii in enumerate(ipos)
        ]
    )

    status = PEAK_STATUS.NO_PEAK
    if det_edges is not None and det_edges[slices[:-1]].any():
        status = PEAK_STATUS.ON_EDGE
        intens, sigma = 0.0, 0.0
    else:
        if y[slices].size != kernel.size:
            # peak is partially on edge, but we continue to integrate with a partial kernel
            status = PEAK_STATUS.ON_EDGE_INTEGRATED  # don't want to optimise weak peak shoeboxes using edge peaks
            kernel_slices = []
            for idim in range(len(ipos)):
                # start/stop indices in kernel (by default all elements)
                istart, iend = 2 * [None]
                # get index in y where kernel starts
                iy_start = ipos[idim] - kernel.shape[idim] // 2
                if iy_start < 0:
                    istart = -iy_start  # chop of ii elements at the begninning of the kernel along this dimension
                elif iy_start > y.shape[idim] - kernel.shape[idim]:
                    iend = y.shape[idim] - iy_start  # include only up to number of elements remaining in y
                kernel_slices.append(slice(istart, iend))
            kernel = kernel[tuple(kernel_slices)]
            # re-normalise the shell to have integral = 0
            inegative = kernel > 0
            kernel[inegative] = -np.sum(kernel[~inegative]) / np.sum(inegative)
        intens = np.sum(y[slices] * kernel)
        sigma = np.sqrt(np.sum(esq[slices] * (kernel**2)))
        if status == PEAK_STATUS.NO_PEAK:
            status = PEAK_STATUS.STRONG if intens / sigma > weak_peak_threshold else PEAK_STATUS.WEAK
    return intens, sigma, status


def optimise_shoebox(y, esq, peak_shape, ipos, nfail_max=2):
    best_peak_shape = list(peak_shape)
    best_ipos = list(ipos)
    for idim in range(3)[::-1]:
        nfailed = 0
        max_intens_over_sig = -np.inf
        this_peak_shape = best_peak_shape.copy()
        this_peak_shape[idim] = min(1, round_up_to_odd_number(peak_shape[idim] // 2) - 2)
        while True:
            # make kernel
            this_peak_shape[idim] = this_peak_shape[idim] + 2
            kernel = make_kernel(*this_peak_shape)
            # get slice the size of kernel along all other dims centered on best ipos from other dims
            slices = [
                slice(np.clip(ii - kernel.shape[idim] // 2, 0, y.shape[idim]), np.clip(ii + kernel.shape[idim] // 2 + 1, 0, y.shape[idim]))
                for idim, ii in enumerate(best_ipos)
            ]
            # incl. elements along dim that give valid convolution in initial peak region
            slices[idim] = slice(
                np.clip(ipos[idim] - peak_shape[idim] // 2 - kernel.shape[idim] // 2, 0, y.shape[idim]),
                np.clip(ipos[idim] + peak_shape[idim] // 2 + kernel.shape[idim] // 2 + 1, 0, y.shape[idim]),
            )
            slices = tuple(slices)
            if y[slices].shape[idim] <= kernel.shape[idim]:
                # no valid convolution region
                break
            this_intens_over_sig = np.squeeze(convolve_shoebox(y[slices], esq[slices], kernel, mode="valid"))
            imax = np.argmax(this_intens_over_sig)
            if this_intens_over_sig[imax] > max_intens_over_sig:
                max_intens_over_sig = this_intens_over_sig[imax]
                best_ipos[idim] = imax + max(ipos[idim] - peak_shape[idim] // 2, kernel.shape[idim] // 2)
                best_peak_shape[idim] = this_peak_shape[idim]
                nfailed = 0
            else:
                nfailed += 1
                if not nfailed < nfail_max:
                    break
    return best_ipos, best_peak_shape


def set_peak_intensity(pk, intens, sigma, do_lorz_cor):
    if do_lorz_cor:
        L = (np.sin(pk.getScattering() / 2) ** 2) / (pk.getWavelength() ** 4)  # at updated peak pos
    else:
        L = 1
    # set peak object intensity
    pk.setIntensity(L * intens)
    pk.setSigmaIntensity(L * sigma)


# register algorithm with mantid
AlgorithmFactory.subscribe(IntegratePeaksShoeboxTOF)
