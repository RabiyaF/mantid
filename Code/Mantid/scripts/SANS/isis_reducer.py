"""
    ISIS-specific implementation of the SANS Reducer. 
    
    WARNING: I'm still playing around with the ISIS reduction to try to 
    understand what's happening and how best to fit it in the Reducer design. 
     
"""
from reduction.instruments.sans.sans_reducer import SANSReducer
import reduction.instruments.sans.sans_reduction_steps as sans_reduction_steps
import isis_reduction_steps
from mantidsimple import *
import os
import copy

import sys

################################################################################
# Avoid a bug with deepcopy in python 2.6, details and workaround here:
# http://bugs.python.org/issue1515
if sys.version_info[0] == 2 and sys.version_info[1] == 6:
    import types
    def _deepcopy_method(x, memo):
        return type(x)(x.im_func, copy.deepcopy(x.im_self, memo), x.im_class)
    copy._deepcopy_dispatch[types.MethodType] = _deepcopy_method
################################################################################

## Version number
__version__ = '0.0'

class ISISReducer(SANSReducer):
    """
        ISIS Reducer
        TODO: need documentation for all the data member
        TODO: need to see whether all those data members really belong here
    """    
    #the rebin parameters used by Q1D
    Q_REBIN = None
    QXY2 = None
    DQY = None

    # Component positions
    PHIMIN=-90.0
    PHIMAX=90.0
    PHIMIRROR=True
    
    ## Path for user settings files
    _user_file_path = '.'

    def _to_steps(self):
        """
            Defines the steps that are run and their order
        """
        self._prepare_raw = []
#        self._reduction_steps.append(self.data_loader)
#        self._reduction_steps.append(self.user_settings)
#        self._prepare_raw.append(self.place_det_sam)
        self._prepare_raw.append(self.geometry)
        #---- creates a new workspace leaving the raw data behind 
        self._fork_ws = [self.out_name]

        self._proc_TOF = [self.flood_file]
        self._proc_TOF.append(self.crop_detector)
        self._proc_TOF.append(self.mask)
        self._proc_TOF.append(self.to_wavelen)

        self._proc_wav = [self.norm_mon]
        self._proc_wav.append(self.transmission_calculator)
        self._proc_wav.append(self._corr_and_scale)
        self._proc_wav.append(self._geo_corr)

        self._can = [self.background_subtracter]
        
        self._tidy = [self._zero_error_flags]
        self._tidy.append(self._rem_zeros)
        
        #steps used by the centre finder
        self._no_Q = self._proc_TOF + self._proc_wav
        #steps used to process a can workspace
        self._conv_Q = self._no_Q + [self.to_Q]

        #list of steps to completely reduce a workspace
        self._reduction_steps = self._prepare_raw + self._fork_ws + self._conv_Q + self._can+ self._tidy

    def _init_steps(self):
        """
            Initialises the steps that are not initialised by (ISIS)CommandInterface.
        """
        
        self.data_loader =     None
        self.user_settings =   None
        self.place_det_sam =   isis_reduction_steps.MoveComponents()
        self.geometry =        sans_reduction_steps.GetSampleGeom()
        self.out_name =       isis_reduction_steps.GetOutputName()
        self.flood_file =      isis_reduction_steps.CorrectToFileISIS(
            '', 'SpectrumNumber','Divide', self.out_name.name_holder)
        self.crop_detector =   isis_reduction_steps.CropDetBank(
            self.out_name.name_holder)
        self.samp_trans_load = None
        self.can_trans_load =  None
        self.mask =self._mask= isis_reduction_steps.Mask_ISIS()
        self.to_wavelen =      isis_reduction_steps.UnitsConvert('Wavelength')
        self.norm_mon =        isis_reduction_steps.NormalizeToMonitor()
        self.transmission_calculator =\
                               isis_reduction_steps.TransmissionCalc(loader=None)
        self._corr_and_scale = isis_reduction_steps.ISISCorrections()
        self.to_Q =            isis_reduction_steps.ConvertToQ(
	                                         container=self._temporys)
        self.background_subtracter = None
        self._geo_corr =       sans_reduction_steps.SampleGeomCor(self.geometry)
        self._zero_error_flags=isis_reduction_steps.ReplaceErrors()
        self._rem_zeros =      sans_reduction_steps.StripEndZeros()

        self.set_Q_output_type(self.to_Q.output_type)
	
    def __init__(self):
        SANSReducer.__init__(self)
        self.output_wksp = None
        self.sample_wksp = None
        self.full_trans_wav = False
        self._monitor_set = False
	#workspaces that this reducer uses and will delete at the end
        self._temporys = {'Q1D errors' : None}
	#the output workspaces created by a data analysis
	self._outputs = {}
	#all workspaces created by this reducer
	self._workspace = [self._temporys, self._outputs] 

        self._init_steps()
	
    def _reduce(self):
        """
            Execute the list of all reduction steps
        """
        # defines the order the steps are run in, any steps not in that list wont be run  
        self._to_steps()

        # Check that an instrument was specified
        if self.instrument is None:
            raise RuntimeError, "Reducer: trying to run a reduction without an instrument specified"

        self.output_wksp = self.sample_wksp
        #Correct(sample_setup, wav_start, wav_end, use_def_trans, finding_centre)
        self._run(self._reduction_steps)

        #any clean up, possibly removing workspaces 
        self.post_process()
        self.clean = False
        
        return self.output_wksp
    
    def run_no_Q(self, output_name):
        self.name_outwksp(output_name)
        self._to_steps()
 
        self._run(self._no_Q)
        self.clean = False
        
    def _run(self, steps):
        for item in steps:
            if item:
                item.execute(self, self.output_wksp)

    
    def reduce_can(self, to_reduce, new_wksp=None, run_Q=True):
        """
            Apply the sample corrections to a can workspace. This reducer is deep copied
            and the output workspace name, transmission and monitor workspaces are changed.
            Then the reduction is applied to the given workspace 
            @param to_reduce: the workspace that will be corrected
            @param new_wksp: the name of the workspace that will store the result (default the name of the input workspace)
        """
        if not new_wksp:
            new_wksp = to_reduce

        # Can correction
        new_reducer = copy.deepcopy(self)

        #set the workspace that we've been setting up as the one to be processed 
        new_reducer.sample_wksp = to_reduce
        new_reducer.output_wksp = new_wksp

        #give the name of the new workspace to the first algorithm that was run
        new_reducer.flood_file.out_container[0] = new_wksp
        #the line below is required if the step above is optional
        new_reducer.crop_detector.out_container[0] = new_wksp
        
        if new_reducer.transmission_calculator:
            new_reducer.transmission_calculator.set_loader(new_reducer.can_trans_load)
            new_reducer.transmission_calculator.calculated_samp = \
                new_reducer.transmission_calculator.calculated_can

        norm_step_ind = new_reducer.step_num(new_reducer.norm_mon)
        new_reducer._reduction_steps[norm_step_ind] = \
            isis_reduction_steps.NormalizeToMonitor(raw_ws=to_reduce)
           
        if run_Q:
            new_reducer.run_conv_Q()
        else:
            new_reducer.run_no_Q('dummy')

    def name_outwksp(self, new_name):
        #give the name of the new workspace to the first algorithm that was run
        self.flood_file.out_container = [new_name]
        #the line below is required if the step above is optional
        self.crop_detector.out_container = [new_name]

    def run_from_raw(self):
        """
            Assumes the reducer is copied from a running one
            Executes all the steps after moving the components
        """
        self._run_steps(
                       start_ind=self.step_num(self._fork_ws[0]),
                       stop_ind=len(self._reduction_steps))

        #any clean up, possibly removing workspaces 
        self.post_process()
        self.clean = False
        
        return self.output_wksp

    def run_conv_Q(self, reducer=None):
        """
            Assumes the reducer is copied from a running one
            Executes all the commands required to correct a can workspace
        """
        if not reducer:
            reducer = self
            
        steps = reducer._conv_Q
        #the reducer is completely setup, run it
        reducer._run_steps(
                          start_ind=reducer.step_num(steps[0]),
                          stop_ind=reducer.step_num(steps[len(steps)-1]))
    
    def _run_steps(self, start_ind = None, stop_ind = None):
        """
            Assumes the reducer is copied from a running one
            Run part of the chain, starting at the first specified step
            and ending at the last. If start or finish are set to None
            they will default to the first and last steps in the chain
            respectively. No pre- or post-processing is done. Assumes
            there are no duplicated steps
            @param start_ind the index number of the first step to run
            @param end_ind the index of the last step that will be run
        """

        if start_ind is None:
            start_ind = 0

        if stop_ind is None:
            stop_ind = len(self._reduction_steps)

        self.output_wksp = self.sample_wksp
        for item in self._reduction_steps[start_ind:stop_ind+1]:
            if not item is None:
                item.execute(self, self.output_wksp)

        self.clean = False
        return self.output_wksp

    def keep_un_normalised(self, keep):
        """
	        Use this function to keep the un-normalised workspace from the
	        normalise to monitor step and use it for the Q1D error estimate.
	        Call this function with keep = False to disable this
	        @param keep: set tot True to keep the workspace, False to delete it
        """
        if keep:
            self._temporys['Q1D errors'] = 'to_delete_prenormed'
        else:
            if self._temporys['Q1D errors']:
               if mtd.workspaceExists(self._temporys['Q1D errors']):
                   DeleteWorkspace(self._temporys['Q1D errors'])
                   self._temporys['Q1D errors'] = None
	    
	self.norm_mon.save_original = self._temporys['Q1D errors']

    def set_Q_output_type(self, out_type):
       self.keep_un_normalised(self.to_Q.output_type == '1D')
       self.to_Q.set_output_type(out_type)

    def post_process(self):
        # Store the mask file within the final workspace so that it is saved to the CanSAS file
        if self.user_settings is None:
            user_file = 'None'
        else:
            user_file = self.user_settings.filename
        AddSampleLog(self.output_wksp, "UserFile", user_file)
	
	for role in self._temporys.keys():
	    try:
	        DeleteWorkspace(self._temporys[role])
	    except:
	        #if cleaning up isn't possible there is probably nothing we can do
		pass

    def set_user_path(self, path):
        """
            Set the path for user files
            @param path: user file path
        """
        if os.path.isdir(path):
            self._user_file_path = path
        else:
            raise RuntimeError, "ISISReducer.set_user_path: provided path is not a directory (%s)" % path

    def get_user_path(self):
        return self._user_file_path
    
    user_file_path = property(get_user_path, set_user_path, None, None)

    def set_background(self, can_run=None, reload = True, period = -1):
        """
            Sets the can data to be subtracted from sample data files
            @param data_file: Name of the can run file
        """
        if can_run is None:
            self.background_subtracter = None
        else:
            self.background_subtracter = isis_reduction_steps.CanSubtraction(can_run, reload=reload, period=period)

    def set_trans_fit(self, lambda_min=None, lambda_max=None, fit_method="Log"):
        self.transmission_calculator.set_trans_fit(lambda_min, lambda_max, fit_method, override=True)
        
    def set_trans_sample(self, sample, direct, reload=True, period_t = -1, period_d = -1):
        if not issubclass(self.samp_trans_load.__class__, sans_reduction_steps.BaseTransmission):
            self.samp_trans_load = isis_reduction_steps.LoadTransmissions(reload=reload)
        self.samp_trans_load.set_trans(sample, period_t)
        self.samp_trans_load.set_direc(direct, period_d)
        self.transmission_calculator.set_loader(self.samp_trans_load)

    def set_trans_can(self, can, direct, reload = True, period_t = -1, period_d = -1):
        if not issubclass(self.can_trans_load.__class__, sans_reduction_steps.BaseTransmission):
            self.can_trans_load = isis_reduction_steps.LoadTransmissions(is_can=True, reload=reload)
        self.can_trans_load.set_trans(can, period_t)
        self.can_trans_load.set_direc(direct, period_d)

    def set_monitor_spectrum(self, specNum, interp=False, override=True):
        if override:
            self._monitor_set=True
        
        self.instrument.set_interpolating_norm(interp)
        
        if not self._monitor_set or override:
            self.instrument.set_incident_mon(specNum)
                        
    def set_trans_spectrum(self, specNum, interp=False, override=True):
        self.instrument.incid_mon_4_trans_calc = int(specNum)

        self.transmission_calculator.interpolate = interp

    def step_num(self, step):
        """
            Returns the index number of a step in the
            list of steps that have _so_ _far_ been
            added to the chain
        """
        return self._reduction_steps.index(step)

    def get_instrument(self):
        """
            Convenience function used by the inst property to make
            calls shorter
        """
        return self.instrument
 
    #quicker to write than .instrument 
    inst = property(get_instrument, None, None, None)
 
    def Q_string(self):
        return '    Q range: ' + self.Q_REBIN +'\n    QXY range: ' + self.QXY2+'-'+self.DQXY

    def ViewCurrentMask(self):
        self._mask.view(self.instrument)

    def reference(self):
        return self

    CENT_FIND_RMIN = None
    CENT_FIND_RMAX = None
