"""
Unit test for Vesuvio pre-fitting steps

Assumes that mantid can be imported and the data paths
are configured to find the Vesuvio data
"""
import unittest

from mantid.api import AlgorithmManager
from VesuvioTesting import create_test_ws
import vesuvio.commands as vesuvio

class VesuvioPreFitTest(unittest.TestCase):

    _test_ws = None

    def setUp(self):
        if self._test_ws is not None:
            return
        # Cache a TOF workspace
        self.__class__._test_ws = create_test_ws()

    # -------------- Success cases ------------------

    def test_smooth_uses_requested_number_of_points(self):
        alg = self._create_algorithm(InputWorkspace=self._test_ws,
                                     Smoothing="Neighbour", SmoothingOptions="NPoints=3",
                                     BadDataError=-1)
        alg.execute()
        output_ws = alg.getProperty("OutputWorkspace").value

        self.assertEqual(2, output_ws.getNumberHistograms())
        self.assertAlmostEqual(50.0, output_ws.readX(0)[0])
        self.assertAlmostEqual(562.0, output_ws.readX(0)[-1])

        self.assertAlmostEqual(0.09337135, output_ws.readY(0)[0])
        self.assertAlmostEqual(0.00060365, output_ws.readY(0)[-1])
        self.assertAlmostEqual(0.084563, output_ws.readY(1)[0])
        self.assertAlmostEqual(-0.00403775, output_ws.readY(1)[-1])

    def test_mask_only_masks_over_threshold(self):
        err_start = self._test_ws.readE(1)[-1]
        self._test_ws.dataE(1)[-1] = 1.5e6

        alg = self._create_algorithm(InputWorkspace=self._test_ws,
                                     Smoothing="None", BadDataError=1.0e6)
        alg.execute()
        self._test_ws.dataE(1)[-1] = err_start
        output_ws = alg.getProperty("OutputWorkspace").value

        self.assertEqual(2, output_ws.getNumberHistograms())
        self.assertAlmostEqual(50.0, output_ws.readX(0)[0])
        self.assertAlmostEqual(562.0, output_ws.readX(0)[-1])

        self.assertAlmostEqual(0.0279822, output_ws.readY(0)[0])
        self.assertAlmostEqual(0.0063585, output_ws.readY(0)[-1])
        self.assertAlmostEqual(0.0155041, output_ws.readY(1)[0])
        # Masked
        self.assertAlmostEqual(0.0, output_ws.readY(1)[-1])

    # -------------- Failure cases ------------------

    def test_invalid_smooth_opt_raises_error_on_validate(self):
        alg = self._create_algorithm(InputWorkspace=self._test_ws,
                                     Smoothing="Neighbour", SmoothingOptions="npts=3")
        self.assertRaises(RuntimeError, alg.execute)

    # -------------- Helpers --------------------

    def _create_algorithm(self, **kwargs):
        alg = AlgorithmManager.createUnmanaged("VesuvioPreFit")
        alg.initialize()
        alg.setChild(True)
        alg.setProperty("OutputWorkspace", "__unused")
        for key, value in kwargs.iteritems():
            alg.setProperty(key, value)
        return alg
        
    '''def _create_test_ws(self):
        ###### Simulates LoadVesuvio with spectrum number 135-136 #################
        tof_ws = CreateSimulationWorkspace(Instrument='Vesuvio',BinParams=[49,2,563],UnitX='TOF')
        tof_ws = CropWorkspace(tof_ws,StartWorkspaceIndex=134,EndWorkspaceIndex=135) # index one less than spectrum number
        tof_ws = ConvertToPointData(tof_ws)
        SetInstrumentParameter(tof_ws, ParameterName='t0',ParameterType='Number',Value='0.5')
        SetInstrumentParameter(tof_ws, ParameterName='sigma_l1', ParameterType='Number', Value='0.021')
        SetInstrumentParameter(tof_ws, ParameterName='sigma_l2', ParameterType='Number', Value='0.023')
        SetInstrumentParameter(tof_ws, ParameterName='sigma_tof', ParameterType='Number', Value='0.3')
        SetInstrumentParameter(tof_ws, ParameterName='sigma_theta', ParameterType='Number', Value='0.028')
        SetInstrumentParameter(tof_ws, ParameterName='hwhm_lorentz', ParameterType='Number', Value='24.0')
        SetInstrumentParameter(tof_ws, ParameterName='sigma_gauss', ParameterType='Number', Value='73.0')
        # Algorithm allows separate parameters for the foils
        SetInstrumentParameter(tof_ws, ComponentName='foil-pos0', ParameterName='hwhm_lorentz',
                               ParameterType='Number', Value='144.0')
        SetInstrumentParameter(tof_ws, ComponentName='foil-pos0', ParameterName='sigma_gauss',
                               ParameterType='Number', Value='20.0')
        SetInstrumentParameter(tof_ws, ComponentName='foil-pos1', ParameterName='hwhm_lorentz',
                               ParameterType='Number', Value='144.0')
        SetInstrumentParameter(tof_ws, ComponentName='foil-pos1', ParameterName='sigma_gauss',
                               ParameterType='Number', Value='20.0')

        arr_y_0 = np.asarray([0.0279822, 0.1587605, 0.0534081, 0.055589, 0.0154309, -0.0137594, -0.0051854, 0.0023374, 0.131721, 0.0039364, 0.1935434, 0.0193096, -0.0062345, 0.0023902, -0.0040375, 0.0043059, 0.1577286, 0.0083578, 0.0648338, 0.0696508, -0.0013759, 0.0033154, -0.0008886, 8.67e-05, 0.0072103, 0.0015019, 0.0259273, 0.0183395, 0.0072991, -0.0024434, 0.0057123, 0.0157501, 0.2030135, 0.3095373, 0.0234369, 0.0125052, 0.0071439, 0.0135502, 0.0175092, 0.0119797, 0.0363222, 0.0194647, 0.0244774, 0.0265381, 0.0189537, 0.0359726, 0.023707, 0.0391928, 0.0459597, 0.0392336, 0.0417778, 0.036422, 0.0568132, 0.0424851, 0.0432542, 0.0605573, 0.0496959, 0.086144, 0.2629902, 0.4663805, 0.1050775, 0.062194, 0.0530962, 0.0435767, 0.0469903, 0.0392462, 0.0307214, 0.0267018, 0.0221355, 0.0334414, 0.0352838, 0.021433, 0.0210262, 0.0356013, 0.032687, 0.0265155, 0.0271023, 0.0201944, 0.0074697, 0.0123702, 0.0073939, 0.002461, 0.0202981, 0.0226783, 0.0055991, 0.0252422, 0.0239618, 0.0101082, 0.0141603, -0.0003597, 0.0125734, 0.0037756, 0.0025411, 0.0084439, 0.0127981, 0.014032, -0.0009435, 0.0013394, 0.0173213, 0.0057206, -0.0012773, -0.0021051, -0.0025929, 0.0089874, 0.00098, 0.0078117, 0.0112268, 0.005673, -0.0056119, 0.0092864, 0.0074909, 0.0024653, 0.012757, 0.0022201, 0.0105046, -0.0006327, -0.0021474, 0.0156625, 0.0107478, 0.0173584, 0.0018866, 0.0131581, 0.0155948, 0.0251798, 0.0215185, 0.0133919, 0.0413915, 0.0423395, 0.0330503, 0.0457673, 0.0663854, 0.0697569, 0.0915387, 0.1078947, 0.1139649, 0.2391652, 0.3495295, 0.4186069, 0.4659951, 0.4397788, 0.4607338, 0.4232483, 0.323764, 0.2026262, 0.1889135, 0.0954193, 0.0924742, 0.1009313, 0.0522692, 0.0556634, 0.0417043, 0.0348195, 0.0520627, 0.0557692, 0.0633281, 0.0814483, 0.1032962, 0.1364041, 0.1340803, 0.1434188, 0.152608, 0.1277786, 0.0986823, 0.0789467, 0.0481237, 0.0216125, 0.0072505, 0.026356, 0.0158784, 0.005582, 0.0198579, 0.008183, -0.0040249, -0.0022096, 0.0007557, -0.0089817, -0.0050716, 0.0113601, 0.0044671, 0.0093089, -0.0052041, -0.0091243, -0.0009747, 0.0038765, 0.0084152, -0.0020985, 0.0024573, -0.0080375, -0.0010825, -0.0024205, 0.0084446, 0.0002166, 0.0005044, 0.0044596, 0.0021728, 0.0001159, -0.0054755, -0.0056922, 0.0065526, -0.0036411, -0.0138637, 0.0099348, -0.0048227, -0.0029783, -0.0002207, -0.0125268, -0.0009914, 0.0088224, -0.0009368, 0.0055571, 0.0003298, 0.0009209, -0.0008864, 0.0058332, 0.0052585, -0.0019276, -0.0001564, -0.005547, 0.0039876, -0.0051404, -0.0021916, -0.0035655, -0.0018638, 0.0076461, -0.0154677, -0.0062851, -0.0071069, 0.0076426, -0.0036411, 0.0019039, -0.0020335, -0.0062465, -0.0115891, -0.003828, -0.0006906, 0.002403, -0.0012887, 0.0061918, -0.0079949, -0.0080552, 0.0027878, -0.0013177, -0.0021298, -0.0053362, 0.0083187, 0.0059659, -0.0048295, 0.0116407, -0.0048947, 0.0032214, -0.0017089, 0.0018194, -0.0005464, 0.0108776, 0.0041985, -0.0051512, 0.0063585])
        arr_y_1 = np.asarray([0.0155041, 0.1536219, 0.0705738, 0.0379744, -0.0057821, -0.0070227, -0.0102393, 0.0066189, 0.1688158, 0.0197819, 0.1805022, 0.0586206, 0.0049459, 0.0026698, -0.0096383, -0.0107852, 0.1691328, 0.0025864, 0.0487438, 0.05435, 0.0145951, 0.0020499, -0.0044584, -0.0053, -0.0030876, 0.0028747, 0.0267385, 0.0189885, 0.0059005, -0.0013181, 0.0028342, 0.0130067, 0.1728085, 0.2307516, 0.0278331, 0.0088497, 0.0067179, 0.0080358, 0.0030305, 0.0046967, 0.0096459, 0.0047008, 0.0084455, 0.0120191, 0.0270126, 0.0182201, 0.0163271, 0.0191555, 0.023674, 0.0235553, 0.0255388, 0.0318359, 0.0324973, 0.0471974, 0.0322757, 0.0376968, 0.0561852, 0.054098, 0.2902402, 0.4723219, 0.1265552, 0.0613737, 0.0608245, 0.0510366, 0.0562233, 0.0589178, 0.0472395, 0.0248228, 0.0298321, 0.0521667, 0.050088, 0.0486207, 0.0417202, 0.0361827, 0.0307559, 0.0290634, 0.0443114, 0.032456, 0.0544284, 0.0362842, 0.0349844, 0.033014, 0.0214423, 0.0276229, 0.028285, 0.0313363, 0.02097, 0.0267219, 0.0258398, 0.010141, 0.0106303, 0.0039375, 0.015176, 0.0034047, 0.0059373, -0.004565, 0.0104247, -0.0008644, 0.0147386, 0.0124944, 0.0123692, 0.0024143, 0.0037337, 0.022632, 0.0099649, 0.0195163, 0.0047546, 0.0074703, -0.0060777, 0.0016553, 0.0069532, 0.0054889, -0.0005565, 0.0112504, 0.0040078, 0.0074051, 0.0063331, 0.0102157, 0.0047149, 0.0127409, 0.0089766, 0.0235059, 0.00578, 0.0143666, 0.0426174, 0.0173149, 0.0398941, 0.035563, 0.0175214, 0.0582518, 0.0636831, 0.04697, 0.068431, 0.1184043, 0.1461161, 0.162931, 0.3157118, 0.4525623, 0.4967857, 0.523506, 0.4821948, 0.3780588, 0.2820117, 0.207971, 0.1729326, 0.1142599, 0.0876062, 0.0766886, 0.0525184, 0.0380988, 0.0277054, 0.0357547, 0.0505474, 0.0848206, 0.0703005, 0.0717423, 0.1077341, 0.1199088, 0.1628344, 0.1448108, 0.1300938, 0.1409894, 0.1013017, 0.0803294, 0.0406706, 0.0344452, 0.0026992, 0.0173314, -0.0126389, 0.0120812, -0.0051448, -0.0021643, -0.003559, 0.0138709, 0.0101377, 0.0098284, 0.0082292, 0.0137698, -0.0055618, 0.007306, -0.0056595, -0.0078945, -0.0051356, -0.0072695, 0.01265, 0.0080837, -0.005344, -0.0036535, -0.0006843, 0.0050228, -0.0080933, -0.0043142, -0.0044235, 0.0112926, 0.0010335, -0.0113243, 0.0014798, 0.0005514, 0.0013085, -0.0028369, -0.0065483, -0.0001666, -0.0056202, -0.0045502, 0.0086047, -0.0072272, -0.0053373, -0.0014784, 0.0032562, 0.0008801, 0.0026446, 0.0031951, 0.0047381, 0.0085383, 0.0001579, 0.0023464, -3.99e-05, -0.0122899, -0.0036615, -0.0031306, -0.0066083, -0.0083091, -0.0035266, 0.0042567, 0.0028019, -0.0051763, 0.0021928, -0.0097969, 0.0021567, 0.0085299, 0.0064114, 0.0033908, -0.0043158, 0.0069325, 0.0008151, 0.0042793, 0.0013347, 0.0013185, 0.0038647, -0.0020497, 0.0123985, -0.0057112, 0.002795, -0.0045571, -0.0048399, -0.0019391, -0.0034512, -0.0106117, 0.008804, -0.0092454, -0.0025024, 0.0031131, -0.0067306, 0.0009606, -0.0045944, -0.000978, -0.0070975])
        arr_e_0 = np.asarray([0.0117934, 0.0232831, 0.0168164, 0.016756, 0.0112667, 0.0100075, 0.0099231, 0.0121869, 0.021429, 0.0105043, 0.025484, 0.0134925, 0.0096227, 0.0091661, 0.0091281, 0.0116373, 0.0234749, 0.0097467, 0.0149447, 0.0161787, 0.0083018, 0.0078142, 0.0077371, 0.0077135, 0.007965, 0.0080072, 0.0083331, 0.0081693, 0.0080592, 0.0081219, 0.0082476, 0.008897, 0.0250279, 0.0260982, 0.0097062, 0.0079405, 0.0075758, 0.0074112, 0.0073532, 0.0073761, 0.0074566, 0.0076131, 0.0076406, 0.0074831, 0.0074437, 0.0074479, 0.0074209, 0.0074945, 0.0074309, 0.007556, 0.0076618, 0.0079848, 0.0082724, 0.0084415, 0.0084575, 0.0085785, 0.0091171, 0.0113204, 0.0266042, 0.0351075, 0.0150392, 0.0099525, 0.0084158, 0.0078287, 0.0076499, 0.0075415, 0.0074585, 0.0073683, 0.0072875, 0.0072455, 0.0072661, 0.0072289, 0.0072093, 0.007192, 0.0071952, 0.0071795, 0.0071541, 0.007182, 0.0071747, 0.0071445, 0.0071336, 0.0071546, 0.0071329, 0.0071197, 0.007111, 0.0071184, 0.0070917, 0.0071031, 0.0071153, 0.0071178, 0.0070956, 0.0071312, 0.0071409, 0.0071443, 0.0071458, 0.0071629, 0.0071689, 0.0072234, 0.007265, 0.0072728, 0.0072859, 0.0073305, 0.0073767, 0.0074788, 0.0076235, 0.007508, 0.0074702, 0.0075216, 0.0075446, 0.0075961, 0.0076602, 0.0077166, 0.0078025, 0.0079166, 0.0079982, 0.0081365, 0.0082818, 0.0084539, 0.0086485, 0.0088334, 0.0091078, 0.0093325, 0.0096282, 0.0099459, 0.010298, 0.0107183, 0.0111722, 0.0116923, 0.0123477, 0.0131453, 0.0141059, 0.0153067, 0.0168664, 0.0188378, 0.0215785, 0.0252547, 0.0297239, 0.0341553, 0.0363284, 0.036487, 0.0359624, 0.0340507, 0.0302363, 0.0260919, 0.0226238, 0.0199234, 0.0178687, 0.0162593, 0.0149562, 0.0139467, 0.0131031, 0.0124185, 0.0119215, 0.0114997, 0.0111242, 0.0108195, 0.0105417, 0.0103237, 0.0101095, 0.0099069, 0.0096583, 0.0094356, 0.0092308, 0.0090096, 0.0088297, 0.0086338, 0.0084891, 0.0083431, 0.0082116, 0.0081362, 0.008016, 0.0079332, 0.0078449, 0.0077658, 0.0076912, 0.0076462, 0.007587, 0.0075248, 0.0074751, 0.0074872, 0.0073898, 0.0073925, 0.0073482, 0.0073209, 0.007292, 0.0072602, 0.0072301, 0.0072017, 0.007183, 0.0071619, 0.007144, 0.0071174, 0.007112, 0.00708, 0.0070853, 0.0070637, 0.0070514, 0.0070139, 0.0069797, 0.0070052, 0.0069708, 0.0069296, 0.006924, 0.0069337, 0.0069133, 0.0069052, 0.0068889, 0.0068652, 0.0068289, 0.0068375, 0.0068342, 0.0068225, 0.0068038, 0.0067748, 0.0068026, 0.0067666, 0.0067659, 0.0067589, 0.0067484, 0.0067405, 0.0067178, 0.006715, 0.0066678, 0.0066726, 0.0066721, 0.0066528, 0.006642, 0.0066683, 0.0066481, 0.0066452, 0.0066207, 0.0066431, 0.0066053, 0.0066193, 0.0066244, 0.0066009, 0.0066162, 0.0065871, 0.0065945, 0.0066129, 0.0065851, 0.0065817, 0.0065496, 0.0065723, 0.0065763, 0.0065389, 0.0065244, 0.0065359, 0.0065508, 0.0065261, 0.006513, 0.0064937, 0.0064965, 0.0065011, 0.0064914, 0.0064738, 0.005104])
        arr_e_1 = np.asarray([0.0119812, 0.0235948, 0.0170881, 0.0169412, 0.0113467, 0.0100467, 0.0099591, 0.0122446, 0.021694, 0.0106207, 0.0258788, 0.0137264, 0.0098265, 0.0093254, 0.0092983, 0.0117886, 0.0238711, 0.0099137, 0.0151285, 0.0164322, 0.0084087, 0.0078611, 0.0077933, 0.0077606, 0.0080533, 0.0080753, 0.0083849, 0.0082235, 0.0080834, 0.0081785, 0.00828, 0.0089247, 0.0254183, 0.0266835, 0.0098427, 0.0079567, 0.0076163, 0.0074207, 0.0073728, 0.0073525, 0.0074369, 0.0076019, 0.0076312, 0.0074738, 0.0074779, 0.0074474, 0.00744, 0.0074944, 0.0074468, 0.0075523, 0.0076914, 0.0079919, 0.0083741, 0.0084816, 0.0085195, 0.0086432, 0.0091691, 0.0114414, 0.0271048, 0.0359963, 0.0153496, 0.0100647, 0.008485, 0.0079395, 0.0077323, 0.007629, 0.007561, 0.0074265, 0.0073354, 0.007391, 0.0073725, 0.0073246, 0.0073014, 0.007301, 0.0072968, 0.0072843, 0.0072793, 0.0072583, 0.0072565, 0.0072145, 0.0072381, 0.0072325, 0.0072183, 0.0072041, 0.0071931, 0.0072088, 0.0071794, 0.0072075, 0.0071874, 0.0071725, 0.0071942, 0.0071737, 0.0071835, 0.0072119, 0.0071954, 0.0072173, 0.0072499, 0.0072646, 0.0072882, 0.0073204, 0.0073508, 0.0073825, 0.007442, 0.0075377, 0.0076689, 0.0075563, 0.0075362, 0.0075632, 0.0075928, 0.0076414, 0.0077114, 0.0077809, 0.0078769, 0.0079524, 0.0080765, 0.0082101, 0.0083588, 0.0084939, 0.0087091, 0.008918, 0.0091502, 0.0094322, 0.0097226, 0.0100435, 0.010415, 0.0108302, 0.011312, 0.0118621, 0.0124791, 0.0132884, 0.0142738, 0.0155095, 0.0170857, 0.0191345, 0.0219161, 0.0256854, 0.0303414, 0.0348718, 0.037129, 0.0373102, 0.0367249, 0.0346941, 0.0307096, 0.0264297, 0.022881, 0.0200893, 0.0179581, 0.0163181, 0.0150394, 0.014018, 0.0132097, 0.0125433, 0.0120173, 0.0115888, 0.0112336, 0.0109438, 0.0106731, 0.0104799, 0.0102466, 0.0100184, 0.0098015, 0.0095945, 0.0093333, 0.0091293, 0.0089336, 0.0087198, 0.0085649, 0.0084356, 0.0082874, 0.0082099, 0.0080872, 0.0079842, 0.0079151, 0.0078377, 0.0077902, 0.007707, 0.007662, 0.0076153, 0.0075523, 0.0075291, 0.0074836, 0.0074488, 0.007429, 0.0073991, 0.0073745, 0.0073075, 0.0072881, 0.0072854, 0.0072833, 0.0072148, 0.0072024, 0.0072041, 0.0071856, 0.0071668, 0.0071128, 0.0071183, 0.0071181, 0.0070825, 0.0070735, 0.0070799, 0.00703, 0.0070211, 0.007016, 0.0069915, 0.0069892, 0.0069808, 0.0069451, 0.0069381, 0.0069487, 0.0069271, 0.0068951, 0.0068936, 0.0068922, 0.0068515, 0.0068546, 0.0068424, 0.0068702, 0.0068161, 0.0068288, 0.0068064, 0.0068164, 0.0067947, 0.0067576, 0.0067458, 0.0067581, 0.0067441, 0.0067195, 0.006722, 0.0067399, 0.0067166, 0.006718, 0.0067062, 0.0067045, 0.0066759, 0.0066714, 0.0066959, 0.0066707, 0.0066597, 0.0066539, 0.0066722, 0.0066292, 0.00664, 0.0066266, 0.0066505, 0.0066249, 0.0066093, 0.0066099, 0.0066379, 0.0065929, 0.0065849, 0.0065925, 0.0065547, 0.0065503, 0.0065823, 0.0065533, 0.006557, 0.005196])

        tof_ws.setY(0, arr_y_0)
        tof_ws.setY(1, arr_y_1)
        tof_ws.setE(0, arr_e_0)
        tof_ws.setE(1, arr_e_1)
        return tof_ws'''

if __name__ == "__main__":
    unittest.main()

