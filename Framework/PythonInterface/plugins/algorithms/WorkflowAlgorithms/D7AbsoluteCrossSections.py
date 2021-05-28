# Mantid Repository : https://github.com/mantidproject/mantid
#
# Copyright &copy; 2018 ISIS Rutherford Appleton Laboratory UKRI,
#   NScD Oak Ridge National Laboratory, European Spallation Source,
#   Institut Laue - Langevin & CSNS, Institute of High Energy Physics, CAS
# SPDX - License - Identifier: GPL - 3.0 +

from mantid.api import AlgorithmFactory, NumericAxis, PropertyMode, Progress, PythonAlgorithm, \
    WorkspaceGroupProperty, WorkspaceGroup
from mantid.kernel import Direction, EnabledWhenProperty, FloatBoundedValidator, \
    PropertyCriterion, PropertyManagerProperty, StringListValidator

from mantid.simpleapi import *

from scipy.constants import physical_constants
import numpy as np
import math


class D7AbsoluteCrossSections(PythonAlgorithm):

    _sampleAndEnvironmentProperties = None

    @staticmethod
    def _max_value_per_detector(ws, one_per_detector=True):
        if isinstance(mtd[ws], WorkspaceGroup):
            max_values = np.zeros(shape=(mtd[ws][0].getNumberHistograms(),
                                         mtd[ws].getNumberOfEntries()))
            err_values = np.zeros(shape=(mtd[ws][0].getNumberHistograms(),
                                         mtd[ws].getNumberOfEntries()))
            for entry_no, entry in enumerate(mtd[ws]):
                max_values[:, entry_no] = entry.extractY().T
                err_values[:, entry_no] = entry.extractE().T
        else:
            max_values = mtd[ws].extractY().T
            err_values = mtd[ws].extractE().T
        max_values = max_values.flatten()
        err_values = err_values.flatten()
        if one_per_detector:
            indices = np.argmax(max_values, axis=1)
            values = np.zeros(shape=len(indices))
            errors = np.zeros(shape=len(indices))
            for index_no, index in enumerate(indices):
                values[index_no] = max_values[index]
                errors[index_no] = err_values[index]
        else:
            index = np.argmax(max_values)
            values = max_values[index]
            errors = err_values[index]
        return values, errors

    @staticmethod
    def _set_as_distribution(ws):
        for entry in mtd[ws]:
            entry.setDistribution(True)
        return ws

    def category(self):
        return 'ILL\\Diffraction'

    def summary(self):
        return 'Separates magnetic, nuclear coherent, and incoherent components for diffraction and spectroscopy data,' \
               'and corrects the sample data for detector efficiency and normalises it to the chosen standard.'

    def seeAlso(self):
        return ['D7YIGPositionCalibration', 'PolDiffILLReduction']

    def name(self):
        return 'D7AbsoluteCrossSections'

    def validateInputs(self):
        issues = dict()

        normalisation_method = self.getPropertyValue('NormalisationMethod')

        if normalisation_method == 'Vanadium' and self.getProperty('VanadiumInputWorkspace').isDefault:
            issues['VanadiumInputWorkspace'] = 'Vanadium input workspace is mandatory for when detector efficiency calibration' \
                                                    ' is "Vanadium".'

        if normalisation_method in ['Incoherent', 'Paramagnetic']:
            if self.getProperty('CrossSectionSeparationMethod').isDefault:
                issues['NormalisationMethod'] = 'Chosen sample normalisation requires input from the cross-section separation.'
                issues['CrossSectionSeparationMethod'] = 'Chosen sample normalisation requires input from the cross-section separation.'

            if normalisation_method == 'Paramagnetic' and self.getPropertyValue('CrossSectionSeparationMethod') == 'Uniaxial':
                issues['NormalisationMethod'] = 'Paramagnetic normalisation is not compatible with uniaxial measurement.'
                issues['CrossSectionSeparationMethod'] = 'Paramagnetic normalisation is not compatible with uniaxial measurement.'

        if normalisation_method != 'None' or self.getPropertyValue('CrossSectionSeparationMethod') == '10p':
            sampleAndEnvironmentProperties = self.getProperty('SampleAndEnvironmentProperties').value
            if len(sampleAndEnvironmentProperties) == 0:
                issues['SampleAndEnvironmentProperties'] = 'Sample parameters need to be defined.'
            else:
                required_keys = []
                if normalisation_method == 'Incoherent':
                    required_keys = ['FormulaUnits', 'SampleMass', 'FormulaUnitMass']
                elif normalisation_method == 'Incoherent' and self.getProperty('AbsoluteUnitsNormalisation').value:
                    required_keys.append('IncoherentCrossSection')
                elif normalisation_method == 'Paramagnetic':
                    required_keys.append('SampleSpin')

                if self.getPropertyValue('CrossSectionSeparationMethod') == '10p':
                    required_keys.append('ThetaOffset')

                for key in required_keys:
                    if key not in sampleAndEnvironmentProperties:
                        issues['SampleAndEnvironmentProperties'] = '{} needs to be defined.'.format(key)

        return issues

    def PyInit(self):

        self.declareProperty(WorkspaceGroupProperty('InputWorkspace', '',
                                                    direction=Direction.Input),
                             doc='The input workspace with spin-flip and non-spin-flip data.')

        self.declareProperty(WorkspaceGroupProperty('RotatedXYZWorkspace', '',
                                                    direction=Direction.Input,
                                                    optional=PropertyMode.Optional),
                             doc='The workspace used in 10p method when data is taken as two XYZ'
                                 +' measurements rotated by 45 degress.')

        self.declareProperty(WorkspaceGroupProperty('OutputWorkspace', '',
                                                    direction=Direction.Output,
                                                    optional=PropertyMode.Optional),
                             doc='The output workspace.')

        self.declareProperty(name="CrossSectionSeparationMethod",
                             defaultValue="None",
                             validator=StringListValidator(["None", "Uniaxial", "XYZ", "10p"]),
                             direction=Direction.Input,
                             doc="What type of cross-section separation to perform.")

        self.declareProperty(name="OutputUnits",
                             defaultValue="TwoTheta",
                             validator=StringListValidator(["TwoTheta", "Q", "Qxy"]),
                             direction=Direction.Input,
                             doc="The choice to display the output either as a function of detector twoTheta,"
                                 +" or the momentum exchange.")

        self.declareProperty(name="NormalisationMethod",
                             defaultValue="None",
                             validator=StringListValidator(["None", "Vanadium", "Incoherent",  "Paramagnetic"]),
                             direction=Direction.Input,
                             doc="Method to correct detector efficiency and normalise data.")

        self.declareProperty(name="OutputTreatment",
                             defaultValue="Individual",
                             validator=StringListValidator(["Individual", "Merge"]),
                             direction=Direction.Input,
                             doc="Which treatment of the provided scan should be used to create output.")

        self.declareProperty(name="MeasurementTechnique",
                             defaultValue="Powder",
                             validator=StringListValidator(["Powder", "SingleCrystal"]),
                             direction=Direction.Input,
                             doc="What type of measurement technique has been used to collect the data.")

        self.declareProperty(PropertyManagerProperty('SampleAndEnvironmentProperties', dict()),
                             doc="Dictionary for the information about sample and its environment.")

        self.declareProperty(name="ScatteringAngleBinSize",
                             defaultValue=0.5,
                             validator=FloatBoundedValidator(lower=0),
                             direction=Direction.Input,
                             doc="Scattering angle bin size in degrees used for expressing scan data on a single TwoTheta axis.")

        self.setPropertySettings("ScatteringAngleBinSize", EnabledWhenProperty('OutputTreatment', PropertyCriterion.IsEqualTo, 'Merge'))

        self.declareProperty(WorkspaceGroupProperty('VanadiumInputWorkspace', '',
                                                    direction=Direction.Input,
                                                    optional=PropertyMode.Optional),
                             doc='The name of the vanadium workspace.')

        self.setPropertySettings('VanadiumInputWorkspace', EnabledWhenProperty('NormalisationMethod',
                                                                               PropertyCriterion.IsEqualTo, 'Vanadium'))

        self.declareProperty('AbsoluteUnitsNormalisation', True,
                             doc='Whether or not express the output in absolute units.')

        self.declareProperty("IsotropicMagnetism", True,
                             doc="Whether the paramagnetism is isotropic (Steward, Ehlers) or anisotropic (Schweika).")

        self.declareProperty('ClearCache', True,
                             doc='Whether or not to delete intermediate workspaces.')

    def _data_structure_helper(self, ws):
        user_method = self.getPropertyValue('CrossSectionSeparationMethod')
        measurements = set()
        for name in mtd[ws].getNames():
            last_underscore = name.rfind("_")
            measurements.add(name[last_underscore+1:])
        nMeasurements = len(measurements)
        error_msg = "The provided data cannot support {} measurement cross-section separation."
        if nMeasurements == 6 and user_method == '10p' and self.getProperty('RotatedXYZWorkspace').isDefault:
            raise RuntimeError(error_msg.format(user_method))
        elif nMeasurements == 2:
            if user_method == '10p':
                raise RuntimeError(error_msg.format(user_method))
            if user_method == 'XYZ':
                raise RuntimeError(error_msg.format(user_method))
        if nMeasurements not in [2, 6, 10]:
            raise RuntimeError("The analysis options are: Uniaxial, XYZ, and 10p. "
                               + "The provided input does not fit in any of these measurement types.")
        return nMeasurements

    def _read_experiment_properties(self, ws):
        """Reads the user-provided dictionary that contains sample geometry (type, dimensions) and experimental conditions,
         such as the beam size and calculates derived parameters."""
        self._sampleAndEnvironmentProperties = self.getProperty('SampleAndEnvironmentProperties').value
        if 'InitialEnergy' not in self._sampleAndEnvironmentProperties:
            h = physical_constants['Planck constant'][0]  # in m^2 kg^2 / s^2
            neutron_mass = physical_constants['neutron mass'][0]  # in0 kg
            wavelength = mtd[ws][0].getRun().getLogData('monochromator.wavelength').value * 1e-10  # in m
            joules_to_mev = 1e3 / physical_constants['electron volt'][0]
            self._sampleAndEnvironmentProperties['InitialEnergy'] = joules_to_mev * math.pow(h / wavelength, 2) / (2 * neutron_mass)

        if self.getPropertyValue('NormalisationMethod') != 'None' and 'NMoles' not in self._sampleAndEnvironmentProperties:
            sample_mass = self._sampleAndEnvironmentProperties['SampleMass'].value
            formula_units = self._sampleAndEnvironmentProperties['FormulaUnits'].value
            formula_unit_mass = self._sampleAndEnvironmentProperties['FormulaUnitMass'].value
            self._sampleAndEnvironmentProperties['NMoles'] = (sample_mass / formula_unit_mass) * formula_units

    def _create_angle_dists(self, ws):
        """
        Calculates sin^2 (alpha) and cos^2 (alpha) for all detectors, needed by Schweika's anisotropic cross-section
        separation.
        :param ws: Sample workspace.
        :return: Tuple with two workspaces containing sin^2 (alpha) and cos^2 (alpha)
        """
        ws_to_transpose = mtd[ws][0].name()
        angle_ws = mtd[ws][0].name() + "_tmp_angle"
        conv_to_theta = 0.5  # conversion to half of the scattering angle
        if self.getPropertyValue('MeasurementTechnique') != 'SingleCrystal':
            # for single crystal, the spectrum axis is already converted
            ConvertSpectrumAxis(InputWorkspace=mtd[ws][0],
                                OutputWorkspace=angle_ws,
                                Target='SignedTheta',
                                OrderAxis=False)
            ws_to_transpose = angle_ws
            conv_to_theta *= -1.0  # the sign needs to be flipped
        Transpose(InputWorkspace=ws_to_transpose, OutputWorkspace=angle_ws)
        theta = conv_to_theta * mtd[angle_ws].extractX()[0]
        alpha = (theta - self._sampleAndEnvironmentProperties['KiXAngle'].value) * np.pi / 180.0
        cos2_alpha_arr = np.power(np.cos(alpha), 2)
        sin2_alpha_arr = np.power(np.sin(alpha), 2)
        sin2_alpha_name = 'sin2_alpha'
        cos2_alpha_name = 'cos2_alpha'
        cos2_m_sin2_alpha_name = 'cos2_m_sin2_alpha'
        CreateWorkspace(OutputWorkspace=sin2_alpha_name, DataX=np.arange(1), DataY=sin2_alpha_arr, NSpec=len(alpha))
        CreateWorkspace(OutputWorkspace=cos2_alpha_name, DataX=np.arange(1), DataY=cos2_alpha_arr, NSpec=len(alpha))
        Minus(LHSWorkspace=cos2_alpha_name, RHSWorkspace=sin2_alpha_name, OutputWorkspace=cos2_m_sin2_alpha_name)
        if self.getProperty('ClearCache').value:
            DeleteWorkspaces(WorkspaceList=[angle_ws, sin2_alpha_name, cos2_alpha_name])
        return cos2_m_sin2_alpha_name

    def _cross_section_separation(self, ws, nMeasurements):
        """Separates coherent, incoherent, and magnetic components based on spin-flip and non-spin-flip intensities of the
        current sample. The method used is based on either the user's choice or the provided data structure."""
        DEG_2_RAD =  np.pi / 180.0
        user_method = self.getPropertyValue('CrossSectionSeparationMethod')
        isotropic_magnetism = self.getProperty('IsotropicMagnetism').value
        tmp_names = set()
        if user_method == "XYZ" and not isotropic_magnetism:
            cos2_m_sin2_alpha = self._create_angle_dists(ws)
            tmp_names.add(cos2_m_sin2_alpha)
        n_detectors = mtd[ws][0].getNumberHistograms()
        double_xyz_method = False
        if not self.getProperty('RotatedXYZWorkspace').isDefault:
            double_xyz_method = True
            second_xyz_ws = self.getPropertyValue('RotatedXYZWorkspace')
        separated_cs = []

        for entry_no in range(0, mtd[ws].getNumberOfEntries(), nMeasurements):
            sigma_z_sf = mtd[ws][entry_no]
            sigma_z_nsf = mtd[ws][entry_no+1]
            total_cs = mtd[ws][entry_no].name() + '_Total'
            nuclear_cs = mtd[ws][entry_no].name() + '_Coherent'
            incoherent_cs = mtd[ws][entry_no].name() + '_Incoherent'
            if nMeasurements == 2:
                data_total = sigma_z_nsf + sigma_z_sf
                RenameWorkspace(InputWorkspace=data_total, OutputWorkspace=total_cs)
                separated_cs.append(total_cs)
                data_nuclear = sigma_z_nsf - 0.5 * sigma_z_sf
                RenameWorkspace(InputWorkspace=data_nuclear, OutputWorkspace=nuclear_cs)
                separated_cs.append(nuclear_cs)
                data_incoherent = 1.5 * sigma_z_sf
                RenameWorkspace(InputWorkspace=data_incoherent, OutputWorkspace=incoherent_cs)
                separated_cs.append(incoherent_cs)
            elif nMeasurements == 6 or nMeasurements == 10:
                sigma_y_sf = mtd[ws][entry_no+2]
                sigma_y_nsf = mtd[ws][entry_no+3]
                sigma_x_sf = mtd[ws][entry_no+4]
                sigma_x_nsf = mtd[ws][entry_no+5]
                average_magnetic_cs = mtd[ws][entry_no].name() + '_AverageMagnetic'
                if isotropic_magnetism:
                    magnetic_name_1 = '_SFMagnetic'
                    magnetic_name_2 = '_NSFMagnetic'
                else:
                    magnetic_name_1 = '_PerpendicularMagnetic_Y'
                    magnetic_name_2 = '_PerpendicularMagnetic_Z'
                magnetic_1_cs = mtd[ws][entry_no].name() + magnetic_name_1
                magnetic_2_cs = mtd[ws][entry_no].name() + magnetic_name_2
                if nMeasurements == 6 and user_method == 'XYZ':
                    # Total cross-section:
                    data_total = (sigma_z_nsf + sigma_x_nsf + sigma_y_nsf + sigma_z_sf + sigma_x_sf + sigma_y_sf) / 3.0
                    RenameWorkspace(InputWorkspace=data_total, OutputWorkspace=total_cs)
                    separated_cs.append(total_cs)
                    if isotropic_magnetism: # Steward's isotropic cross-section separation
                        # Magnetic component
                        data_sf_magnetic = 2.0 * (-2.0 * sigma_z_sf + sigma_x_sf + sigma_y_sf)
                        data_nsf_magnetic = 2.0 * (2.0 * sigma_z_nsf - sigma_x_nsf - sigma_y_nsf)
                        RenameWorkspace(InputWorkspace=data_sf_magnetic, OutputWorkspace=magnetic_1_cs)
                        RenameWorkspace(InputWorkspace=data_nsf_magnetic, OutputWorkspace=magnetic_2_cs)
                        data_average_magnetic = WeightedMean(InputWorkspace1=magnetic_1_cs,
                                                             InputWorkspace2=magnetic_2_cs)
                        RenameWorkspace(InputWorkspace=data_average_magnetic, OutputWorkspace=average_magnetic_cs)
                        separated_cs.append(average_magnetic_cs)
                        # Nuclear coherent component
                        data_nuclear = (2.0*(sigma_x_nsf + sigma_y_nsf + sigma_z_nsf)
                                        - (sigma_x_sf + sigma_y_sf + sigma_z_sf)) / 6.0
                        # Incoherent component
                        data_incoherent = 0.5 * (sigma_x_sf + sigma_y_sf + sigma_z_sf) - data_average_magnetic
                    else: # anisotropic, Schweika's cross-section separation
                        # Nuclear coherent component
                        data_nuclear = 0.5 * (sigma_x_nsf + sigma_y_nsf - sigma_z_sf)
                        # Incoherent component
                        data_incoherent = 1.5 * ((sigma_x_nsf - sigma_y_nsf) / mtd[cos2_m_sin2_alpha] + sigma_z_sf)
                        # Magnetic components
                        data_perp_magnetic_y = sigma_z_sf - (2.0/3.0) * data_incoherent
                        data_perp_magnetic_z = sigma_z_nsf - data_incoherent / 3.0 - data_nuclear
                        RenameWorkspace(InputWorkspace=data_perp_magnetic_y, OutputWorkspace=magnetic_1_cs)
                        RenameWorkspace(InputWorkspace=data_perp_magnetic_z, OutputWorkspace=magnetic_2_cs)
                    RenameWorkspace(InputWorkspace=data_nuclear, OutputWorkspace=nuclear_cs)
                    separated_cs.append(nuclear_cs)
                    RenameWorkspace(InputWorkspace=data_incoherent, OutputWorkspace=incoherent_cs)
                    separated_cs.append(incoherent_cs)
                    separated_cs.append(magnetic_1_cs)
                    separated_cs.append(magnetic_2_cs)
                else:
                    if not double_xyz_method:
                        sigma_xmy_sf = mtd[ws][entry_no+6]
                        sigma_xmy_nsf = mtd[ws][entry_no+7]
                        sigma_xpy_sf = mtd[ws][entry_no+8]
                        sigma_xpy_nsf = mtd[ws][entry_no+9]
                    else:
                        # assumed is averaging of twice measured Z-axis:
                        sigma_z_sf = 0.5 * (sigma_z_sf + mtd[second_xyz_ws][entry_no])
                        sigma_z_nsf = 0.5 * (sigma_z_nsf + mtd[second_xyz_ws][entry_no+1])
                        sigma_xmy_sf = mtd[second_xyz_ws][entry_no+2]
                        sigma_xmy_nsf = mtd[second_xyz_ws][entry_no+3]
                        sigma_xpy_sf = mtd[second_xyz_ws][entry_no+4]
                        sigma_xpy_nsf = mtd[second_xyz_ws][entry_no+5]
                    # Magnetic component
                    theta_0 = DEG_2_RAD * self._sampleAndEnvironmentProperties['ThetaOffset'].value
                    theta_value = np.zeros(n_detectors)
                    for det_no in range(n_detectors):
                        theta_value[det_no] = mtd[ws][entry_no].detectorInfo().twoTheta(det_no)
                    alpha_value = theta_value - 0.5*np.pi - theta_0
                    cos_alpha_value = np.cos(alpha_value)
                    c0_value = cos_alpha_value**2
                    c4_value = (cos_alpha_value - np.pi / 4.0)**2

                    x_axis = mtd[ws][entry_no].readX(0)
                    c0_t2_m4 = CreateWorkspace(DataX=x_axis, DataY=2*c0_value-4, NSPec=n_detectors,
                                               ParentWorkspace=mtd[ws][entry_no])
                    tmp_names.add('c0_t2_m4')
                    c0_t2_p2 = CreateWorkspace(DataX=x_axis, DataY=2*c0_value+2, NSPec=n_detectors,
                                               ParentWorkspace=mtd[ws][entry_no])
                    tmp_names.add('c0_t2_p2')
                    mc0_t4_p2 = CreateWorkspace(DataX=x_axis, DataY=-4*c0_value+2, NSPec=n_detectors,
                                                ParentWorkspace=mtd[ws][entry_no])
                    tmp_names.add('mc0_t4_p2')
                    c4_t2_m4 = CreateWorkspace(DataX=x_axis, DataY=2*c4_value-4, NSPec=n_detectors,
                                               ParentWorkspace=mtd[ws][entry_no])
                    tmp_names.add('c4_t2_m4')
                    c4_t2_p2 = CreateWorkspace(DataX=x_axis, DataY=2*c4_value+2, NSPec=n_detectors,
                                               ParentWorkspace=mtd[ws][entry_no])
                    tmp_names.add('c4_t2_p2')
                    mc4_t4_p2 = CreateWorkspace(DataX=x_axis, DataY=-4*c4_value+2, NSPec=n_detectors,
                                                ParentWorkspace=mtd[ws][entry_no])
                    tmp_names.add('mc4_t4_p2')
                    cos_2alpha = CreateWorkspace(DataX=x_axis, DataY=np.cos(2*alpha_value), NSPec=n_detectors,
                                                 ParentWorkspace=mtd[ws][entry_no])
                    tmp_names.add('cos_2alpha')
                    sin_2alpha = CreateWorkspace(DataX=x_axis, DataY=np.cos(2*alpha_value), NSPec=n_detectors,
                                                 ParentWorkspace=mtd[ws][entry_no])
                    tmp_names.add('sin_2alpha')

                    magnetic_nsf_cos2alpha = c0_t2_m4 * sigma_x_nsf + c0_t2_p2 * sigma_y_nsf + mc0_t4_p2 * sigma_z_nsf
                    magnetic_sf_cos2alpha = (-1) * c0_t2_m4 * sigma_x_sf - c0_t2_p2 * sigma_y_sf - mc0_t4_p2 * sigma_z_sf
                    magnetic_nsf_sin2alpha = c4_t2_m4 * sigma_xpy_nsf + c4_t2_p2 * sigma_xmy_nsf + mc4_t4_p2 * sigma_z_nsf
                    magnetic_sf_sin2alpha = (-1) * c4_t2_m4 * sigma_xpy_sf - c4_t2_p2 * sigma_xmy_sf - mc4_t4_p2 * sigma_z_sf
                    tmp_names.add('magnetic_sf_cos2alpha')
                    tmp_names.add('magnetic_nsf_cos2alpha')
                    tmp_names.add('magnetic_sf_sin2alpha')
                    tmp_names.add('magnetic_nsf_sin2alpha')

                    data_nsf_magnetic = magnetic_nsf_cos2alpha * cos_2alpha \
                        + magnetic_nsf_sin2alpha * sin_2alpha
                    data_nsf_magnetic.getAxis(0).setUnit(mtd[ws][entry_no].getAxis(0).getUnit().unitID())
                    data_nsf_magnetic.getAxis(1).setUnit(mtd[ws][entry_no].getAxis(1).getUnit().unitID())

                    data_sf_magnetic = magnetic_sf_cos2alpha * cos_2alpha + magnetic_sf_sin2alpha * sin_2alpha
                    data_sf_magnetic.getAxis(0).setUnit(mtd[ws][entry_no].getAxis(0).getUnit().unitID())
                    data_sf_magnetic.getAxis(1).setUnit(mtd[ws][entry_no].getAxis(1).getUnit().unitID())

                    data_average_magnetic = WeightedMean(InputWorkspace1=data_sf_magnetic,
                                                         InputWorkspace2=data_nsf_magnetic)

                    # Nuclear coherent component
                    data_nuclear = (2.0 * (sigma_x_nsf + sigma_y_nsf + 2*sigma_z_nsf + sigma_xpy_nsf + sigma_xmy_nsf)
                                    - (sigma_x_sf + sigma_y_sf + 2*sigma_z_sf + sigma_xpy_sf + sigma_xmy_sf)) / 12.0
                    RenameWorkspace(InputWorkspace=data_nuclear, OutputWorkspace=nuclear_cs)
                    separated_cs.append(nuclear_cs)
                    # Incoherent component
                    data_incoherent_lhs = 0.25 * (sigma_x_sf + sigma_y_sf + 2*sigma_z_sf + sigma_xpy_sf + sigma_xmy_sf)
                    tmp_names.add('data_incoherent_lhs')
                    Minus(LHSWOrkspace=data_incoherent_lhs, RHSWorkspace=data_average_magnetic, OutputWorkspace=incoherent_cs)
                    separated_cs.append(incoherent_cs)
                    RenameWorkspace(InputWorkspace=data_average_magnetic, OutputWorkspace=average_magnetic_cs)
                    separated_cs.append(average_magnetic_cs)
                    RenameWorkspace(InputWorkspace=data_sf_magnetic, OutputWorkspace=magnetic_1_cs)
                    separated_cs.append(magnetic_1_cs)
                    RenameWorkspace(InputWorkspace=data_nsf_magnetic, OutputWorkspace=magnetic_2_cs)
                    separated_cs.append(magnetic_2_cs)

        if self.getProperty('ClearCache').value and tmp_names != set(): # clean only when non-empty
            DeleteWorkspaces(WorkspaceList=list(tmp_names))
        output_name = ws + '_separated_cs'
        GroupWorkspaces(InputWorkspaces=separated_cs, OutputWorkspace=output_name)
        return output_name

    def _detector_efficiency_correction(self, cross_section_ws):
        """Calculates detector efficiency using either vanadium data, incoherent,
        or paramagnetic scattering cross-sections."""

        calibrationType = self.getPropertyValue('NormalisationMethod')
        normaliseToAbsoluteUnits = self.getProperty('AbsoluteUnitsNormalisation').value
        det_efficiency_ws = cross_section_ws + '_det_efficiency'
        norm_ws = 'normalisation_ws'
        tmp_name = 'det_eff'
        tmp_names = []
        to_clean = []
        if calibrationType == 'Vanadium':
            if normaliseToAbsoluteUnits:
                normFactor = self._sampleAndEnvironmentProperties['NMoles'].value
                CreateSingleValuedWorkspace(DataValue=normFactor, OutputWorkspace=norm_ws)
            else:
                normalisationFactors, dataE = self._max_value_per_detector(mtd[cross_section_ws].name(),
                                                                           one_per_detector=False)
                unit_ws = 'unit'
                CreateSingleValuedWorkspace(DataValue=1.0, ErrorValue=0.0,
                                            OutputWorkspace=unit_ws)
                maximumFactors_ws = "maximum_vanadium_ws"
                CreateSingleValuedWorkspace(DataValue=normalisationFactors, ErrorValue=dataE,
                                            OutputWorkspace=maximumFactors_ws)
                Divide(LHSWorkspace=unit_ws, RHSWorkspace=maximumFactors_ws, OutputWorkspace=norm_ws)
                to_clean += [unit_ws, maximumFactors_ws]

            to_clean.append(norm_ws)
            Multiply(LHSWorkspace=cross_section_ws,
                     RHSWorkspace=norm_ws,
                     OutputWorkspace=det_efficiency_ws)
        elif calibrationType in  ['Paramagnetic', 'Incoherent']:
            if calibrationType == 'Paramagnetic':
                spin = self._sampleAndEnvironmentProperties['SampleSpin'].value
                for entry_no, entry in enumerate(mtd[cross_section_ws]):
                    ws_name = '{0}_{1}'.format(tmp_name, entry_no)
                    tmp_names.append(ws_name)
                    const = (2.0/3.0) * math.pow(physical_constants['neutron gyromag. ratio'][0]
                                                 * physical_constants['classical electron radius'][0], 2)
                    paramagneticComponent = mtd[cross_section_ws][3]
                    normalisation_name = 'normalisation_{}'.format(ws_name)
                    to_clean.append(normalisation_name)
                    CreateSingleValuedWorkspace(DataValue=const * spin * (spin+1), OutputWorkspace=normalisation_name)
                    Divide(LHSWorkspace=paramagneticComponent,
                           RHSWorkspace=normalisation_name,
                           OutputWorkspace=ws_name)
            else: # Incoherent
                for spectrum_no in range(mtd[cross_section_ws][2].getNumberHistograms()):
                    if normaliseToAbsoluteUnits:
                        normFactor = self._sampleAndEnvironmentProperties['IncoherentCrossSection'].value
                        CreateSingleValuedWorkspace(DataValue=normFactor, OutputWorkspace=norm_ws)
                    else:
                        normalisationFactors, dataE = self._max_value_per_detector(mtd[cross_section_ws].name(),
                                                                                   one_per_detector=False)
                        if isinstance(normalisationFactors, float):
                            CreateSingleValuedWorkspace(DataValue=normalisationFactors,
                                                        ErrorValue=dataE,
                                                        OutputWorkspace=norm_ws)
                        else:
                            CreateWorkspace(dataX=mtd[cross_section_ws][1].readX(0), dataY=normalisationFactors,
                                            dataE=dataE,
                                            NSpec=mtd[cross_section_ws][1].getNumberHistograms(),
                                            OutputWorkspace=norm_ws)
                    ws_name = '{0}_{1}'.format(tmp_name, spectrum_no)
                    tmp_names.append(ws_name)
                    Divide(LHSWorkspace=mtd[cross_section_ws][2],
                           RHSWorkspace=norm_ws,
                           OutputWorkspace=ws_name)
                    to_clean.append(norm_ws)

            GroupWorkspaces(InputWorkspaces=tmp_names, OutputWorkspace=det_efficiency_ws)

        if self.getProperty('ClearCache').value and len(to_clean) != 0:
            DeleteWorkspaces(to_clean)
        return det_efficiency_ws

    def _normalise_sample_data(self, sample_ws, det_efficiency_ws):
        """Normalises the sample data using the detector efficiency calibration workspace."""

        normalisation_method = self.getPropertyValue('NormalisationMethod')
        is_single_crystal = self.getPropertyValue('MeasurementTechnique') == 'SingleCrystal'
        if is_single_crystal and normalisation_method == 'Vanadium':
            # the length of the spectrum axis is twice the size of Vanadium, as data comes from two omega scans
            AppendSpectra(InputWorkspace1=det_efficiency_ws, InputWorkspace2=det_efficiency_ws,
                          OutputWorkspace=det_efficiency_ws)

        single_efficiency_per_POL = False
        if mtd[sample_ws].getNumberOfEntries() != mtd[det_efficiency_ws].getNumberOfEntries():
            single_efficiency_per_POL = True
        tmp_names = []
        for entry_no, entry in enumerate(mtd[sample_ws]):
            det_eff_entry_no = int(entry_no / 2)
            if normalisation_method == 'Vanadium':
                det_eff_entry_no = 0
            elif single_efficiency_per_POL:
                det_eff_entry_no = int(entry_no / 2)
                if entry_no % 2 != 0:
                    det_eff_entry_no -= 1

            ws_name = entry.name() + '_normalised'
            tmp_names.append(ws_name)
            Divide(LHSWorkspace=entry,
                   RHSWorkspace=mtd[det_efficiency_ws][det_eff_entry_no],
                   OutputWorkspace=ws_name)
        output_ws = self.getPropertyValue('OutputWorkspace')
        GroupWorkspaces(InputWorkspaces=tmp_names, Outputworkspace=output_ws)
        return output_ws

    def _q_rebin(self, ws):
        """
        Rebins the single crystal omega scan measurement output onto 2D Qx-Qy grid.
        :param ws: Output of the cross-section separation and/or normalisation.
        :return: WorkspaceGroup containing 2D distributions on a Qx-Qy grid.
        """
        fld = self._sampleAndEnvironmentProperties['fld'].value if 'fld' in self._sampleAndEnvironmentProperties else 1
        nQ = self._sampleAndEnvironmentProperties['nQ'].value if 'nQ' in self._sampleAndEnvironmentProperties else 80
        omega_shift = self._sampleAndEnvironmentProperties['OmegaShift'].value \
            if 'OmegaShift' in self._sampleAndEnvironmentProperties else 0
        wavelength = mtd[ws][0].getRun().getLogData('monochromator.wavelength').value
        ki = 2 * np.pi / wavelength
        dE = 0.0  # monochromatic data
        kf = np.sqrt(ki * ki - dE / 2.07194)
        twoTheta = -mtd[ws][0].getAxis(1).extractValues() * np.pi / 180.0  # detector positions in radians
        omega = mtd[ws][0].getAxis(0).extractValues() * np.pi / 180.0  # omega scan angle in radians
        ntheta = len(twoTheta)
        nomega = len(omega)
        # omega = -1.0 * np.matrix(np.flip(omega, 0)) - omega_shift * np.pi / 180.0
        omega = np.matrix(omega) + omega_shift * np.pi / 180.0
        Qmag = np.sqrt(ki * ki + kf * kf - 2 * ki * kf * np.cos(twoTheta))
        # beta is the angle between ki and Q
        beta = (twoTheta / np.abs(twoTheta)) * np.arccos((ki * ki - kf * kf + Qmag * Qmag) / (2 * ki * Qmag))
        alpha = -np.pi/2 + omega.T * np.ones(shape=(1, ntheta)) + np.ones(shape=(nomega, 1)) * beta
        Qx = np.multiply((np.ones(shape=(nomega, 1)) * Qmag), np.cos(alpha)).T
        Qy = np.multiply((np.ones(shape=(nomega, 1)) * Qmag), np.sin(alpha)).T
        Qmax = 1.1 * np.max(Qmag)
        dQ = Qmax / nQ
        output_names = []
        for entry in mtd[ws]:
            w_out = np.zeros(shape=((fld + 1) * nQ, (fld + 1) * nQ))
            e_out = np.zeros(shape=((fld + 1) * nQ, (fld + 1) * nQ))
            n_out = np.zeros(shape=((fld + 1) * nQ, (fld + 1) * nQ))
            w_in = entry.extractY()
            e_in = entry.extractE()
            for theta in range(ntheta):
                for omega in range(nomega):
                    if fld == 1:
                        ix = int(((Qx[theta, omega] + dQ / 2.) / dQ) + nQ)
                        iy = int(((Qy[theta, omega] + dQ / 2.) / dQ) + nQ)
                        if Qx[theta, omega] > 0.99 * Qmax or Qy[theta, omega] > 0.99 * Qmax:
                            continue
                    else:
                        ix = int(abs((Qx[theta, omega]) + dQ / 2.) / dQ)
                        iy = int(abs((Qy[theta, omega]) + dQ / 2.) / dQ)
                    w_out[ix, iy] += w_in[theta, omega]
                    e_out[ix, iy] += e_in[theta, omega]**2
                    n_out[ix, iy] += 1.
            w_out /= n_out
            e_out = np.sqrt(e_out / n_out)
            w_out_name = entry.name() + '_qxqy'
            output_names.append(w_out_name)
            data_x = [(val-(fld*nQ)) * dQ for val in range((fld+1)*nQ)]
            # data_x = [(val-(fld*nQ)) * dQ * 6.759 * np.cos(17.26*np.pi/180.0)/(2*np.pi) for val in range((fld+1)*nQ)]
            y_axis = NumericAxis.create(int((fld+1)*nQ))
            for q_index in range(int((fld+1)*nQ)):
                y_axis.setValue(q_index, (q_index-(fld*nQ))*dQ)
                # y_axis.setValue(q_index, (q_index-(fld*nQ))*dQ*10.412/(2*np.pi))
            CreateWorkspace(DataX=data_x, DataY=w_out, DataE=e_out, NSpec=int((fld+1)*nQ),
                            OutputWorkspace=w_out_name)
            mtd[w_out_name].replaceAxis(1, y_axis)
            mtd[w_out_name].getAxis(0).setUnit('Label').setLabel('Qx', r'\AA^{-1}')
            mtd[w_out_name].getAxis(1).setUnit('Label').setLabel('Qy', r'\AA^{-1}')
            ReplaceSpecialValues(InputWorkspace=w_out_name, OutputWorkspace=w_out_name, NaNValue=0,
                                 NaNError=0, InfinityValue=0, InfinityError=0)
        DeleteWorkspace(Workspace=ws)
        GroupWorkspaces(InputWorkspaces=output_names, OutputWorkspace=ws)
        return ws

    def _set_units(self, ws, nMeasurements):
        output_unit = self.getPropertyValue('OutputUnits')
        unit_symbol = 'barn / sr / formula unit'
        unit = r'd$\sigma$/d$\Omega$'
        self._set_as_distribution(ws)
        if output_unit == 'TwoTheta':
            if mtd[ws].getNumberOfEntries()/nMeasurements > 1 and self.getPropertyValue('OutputTreatment') == 'Merge':
                self._merge_polarisations(ws)
                ConvertAxisByFormula(InputWorkspace=ws, OutputWorkspace=ws, Axis='X', Formula='-x')
            else:
                ConvertSpectrumAxis(InputWorkspace=ws, OutputWorkspace=ws, Target='SignedTheta', OrderAxis=False)
                ConvertAxisByFormula(InputWorkspace=ws, OutputWorkspace=ws, Axis='Y', Formula='-y')
                Transpose(InputWorkspace=ws, OutputWorkspace=ws)
        elif output_unit == 'Q':
            if mtd[ws].getNumberOfEntries()/nMeasurements > 1 and self.getPropertyValue('OutputTreatment') == 'Merge':
                self._merge_polarisations(ws)
                wavelength = mtd[ws][0].getRun().getLogData('monochromator.wavelength').value # in Angstrom
                # flips axis sign and converts detector 2theta to momentum exchange
                formula = '4*pi*sin(-0.5*pi*x/180.0)/{}'.format(wavelength)
                ConvertAxisByFormula(InputWorkspace=ws, OutputWorkspace=ws, Axis='X', Formula=formula)
                # manually set the correct x-axis unit
                for entry in mtd[ws]:
                    entry.getAxis(0).setUnit('MomentumTransfer')
            else:
                ConvertSpectrumAxis(InputWorkspace=ws, OutputWorkspace=ws, Target='ElasticQ',
                                    EFixed=self._sampleAndEnvironmentProperties['InitialEnergy'].value,
                                    OrderAxis=False)
                Transpose(InputWorkspace=ws, OutputWorkspace=ws)
        elif output_unit == 'Qxy':
            ws = self._q_rebin(ws)

        if self.getPropertyValue('NormalisationMethod') in ['Incoherent', 'Paramagnetic']:
            unit = 'Normalized intensity'
            unit_symbol = ''
        if isinstance(mtd[ws], WorkspaceGroup):
            for entry in mtd[ws]:
                entry.setYUnitLabel("{} ({})".format(unit, unit_symbol))
        else:
            mtd[ws].setYUnitLabel("{} ({})".format(unit, unit_symbol))
        return ws

    def _merge_polarisations(self, ws):
        pol_directions = set()
        numors = set()
        for name in mtd[ws].getNames():
            last_underscore = name.rfind("_")
            if name[last_underscore+1:] == 'normalised':
                short_name = name[:last_underscore]
                second_last = short_name.rfind("_")
                numors.add(short_name[:second_last])
                pol_directions.add(short_name[second_last + 1:]+name[last_underscore:])
            else:
                numors.add(name[:last_underscore])
                pol_directions.add(name[last_underscore + 1:])
        if len(numors) > 1:
            names_list = []
            for direction in sorted(list(pol_directions)):
                name = '{0}_{1}'.format(ws, direction)
                list_pol = []
                for numor in numors:
                    list_pol.append('{0}_{1}'.format(numor, direction))
                self._call_sum_data(input_name=','.join(list_pol), output_name=name)
                names_list.append(name)
            DeleteWorkspaces(WorkspaceList=ws)
            GroupWorkspaces(InputWorkspaces=names_list, OutputWorkspace=ws)
        return ws

    def _call_sum_data(self, input_name, output_name=''):
        if output_name == '':
            output_name = input_name
        SumOverlappingTubes(InputWorkspaces=input_name, OutputWorkspace=output_name,
                            OutputType='1D', ScatteringAngleBinning=self.getProperty('ScatteringAngleBinSize').value,
                            Normalise=True, HeightAxis='-0.1,0.1')
        return output_name

    def _get_number_reports(self):
        nreports = 4
        if self.getPropertyValue('CrossSectionSeparationMethod') != 'None':
            nreports += 1
        return nreports

    def PyExec(self):
        progress = Progress(self, start=0.0, end=1.0, nreports=self._get_number_reports())
        input_ws = self.getPropertyValue('InputWorkspace')
        output_ws = self.getPropertyValue('OutputWorkspace')
        progress.report('Loading experiment properties')
        self._read_experiment_properties(input_ws)
        nMeasurements = self._data_structure_helper(input_ws)
        to_clean = []
        normalisation_method = self.getPropertyValue('NormalisationMethod')
        if self.getPropertyValue('CrossSectionSeparationMethod') == 'None':
            if normalisation_method == 'Vanadium':
                det_efficiency_input = self.getPropertyValue('VanadiumInputWorkspace')
                progress.report('Calculating detector efficiency correction')
                det_efficiency_ws = self._detector_efficiency_correction(det_efficiency_input)
                progress.report('Normalising sample data')
                output_ws = self._normalise_sample_data(input_ws, det_efficiency_ws)
                to_clean.append(det_efficiency_ws)
            else:
                CloneWorkspace(InputWorkspace=input_ws, OutputWorkspace=output_ws)
        else:
            progress.report('Separating cross-sections')
            component_ws = self._cross_section_separation(input_ws, nMeasurements)
            self._set_as_distribution(component_ws)
            if normalisation_method != 'None':
                if normalisation_method == 'Vanadium':
                    det_efficiency_input = self.getPropertyValue('VanadiumInputWorkspace')
                else:
                    det_efficiency_input = component_ws
                progress.report('Calculating detector efficiency correction')
                det_efficiency_ws = self._detector_efficiency_correction(det_efficiency_input)
                progress.report('Normalising sample data')
                output_ws = self._normalise_sample_data(component_ws, det_efficiency_ws)
                to_clean += [component_ws, det_efficiency_ws]
            else:
                RenameWorkspace(InputWorkspace=component_ws, OutputWorkspace=output_ws)
        progress.report('Setting units')
        output_ws = self._set_units(output_ws, nMeasurements)
        self._set_as_distribution(output_ws)
        self.setProperty('OutputWorkspace', mtd[output_ws])
        if self.getProperty('ClearCache').value and len(to_clean) != 0:
            DeleteWorkspaces(WorkspaceList=to_clean)


AlgorithmFactory.subscribe(D7AbsoluteCrossSections)
