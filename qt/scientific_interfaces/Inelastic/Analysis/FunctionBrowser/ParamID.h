// Mantid Repository : https://github.com/mantidproject/mantid
//
// Copyright &copy; 2024 ISIS Rutherford Appleton Laboratory UKRI,
//   NScD Oak Ridge National Laboratory, European Spallation Source,
//   Institut Laue - Langevin & CSNS, Institute of High Energy Physics, CAS
// SPDX - License - Identifier: GPL - 3.0 +
#pragma once

#include <functional>
#include <map>
#include <string>

namespace MantidQt {
namespace CustomInterfaces {
namespace IDA {

enum class ParamID {
  NONE,
  LOR1_AMPLITUDE,
  LOR1_PEAKCENTRE,
  LOR1_FWHM,
  LOR2_AMPLITUDE_1,
  LOR2_PEAKCENTRE_1,
  LOR2_FWHM_1,
  LOR2_AMPLITUDE_2,
  LOR2_PEAKCENTRE_2,
  LOR2_FWHM_2,
  TW_HEIGHT,
  TW_DIFFCOEFF,
  TW_TAU,
  TW_CENTRE,
  FD_HEIGHT,
  FD_DIFFCOEFF,
  FD_CENTRE,
  CE_HEIGHT,
  CE_TAU,
  CE_L,
  CE_CENTRE,
  HR_HEIGHT,
  HR_TAU,
  HR_L,
  HR_CENTRE,
  DELTA_HEIGHT,
  DELTA_CENTER,
  TEMPERATURE,
  SE_HEIGHT,
  SE_TAU,
  SE_BETA,
  SE_CENTRE,
  EDP_HEIGHT,
  EDP_CENTRE,
  EDP_RADIUS,
  IDP_INTENSITY,
  IDP_RADIUS,
  IDP_DIFFUSION,
  IDP_SHIFT,
  DP_INTENSITY,
  DP_RADIUS,
  DP_DIFFUSION,
  DP_SHIFT,
  DRDC_INTENSITY,
  DRDC_RADIUS,
  DRDC_DECAY,
  DRDC_SHIFT,
  IDRDC_INTENSITY,
  IDRDC_RADIUS,
  IDRDC_DECAY,
  IDRDC_SHIFT,
  EDRDC_HEIGHT,
  EDRDC_CENTRE,
  EDRDC_RADIUS,
  IRD_HEIGHT,
  IRD_RADIUS,
  IRD_TAU,
  IRD_CENTRE,
  EIRD_HEIGHT,
  EIRD_RADIUS,
  IIRD_HEIGHT,
  IIRD_RADIUS,
  IIRD_TAU,
  IIRD_CENTRE,
  FLAT_BG_A0,
  LINEAR_BG_A0,
  LINEAR_BG_A1,
};

static std::map<ParamID, std::string> g_paramName{
    {ParamID::LOR1_AMPLITUDE, "Amplitude"},
    {ParamID::LOR1_PEAKCENTRE, "PeakCentre"},
    {ParamID::LOR1_FWHM, "FWHM"},
    {ParamID::LOR2_AMPLITUDE_1, "Amplitude"},
    {ParamID::LOR2_PEAKCENTRE_1, "PeakCentre"},
    {ParamID::LOR2_FWHM_1, "FWHM"},
    {ParamID::LOR2_AMPLITUDE_2, "Amplitude"},
    {ParamID::LOR2_PEAKCENTRE_2, "PeakCentre"},
    {ParamID::LOR2_FWHM_2, "FWHM"},
    {ParamID::TW_HEIGHT, "Height"},
    {ParamID::TW_DIFFCOEFF, "DiffCoeff"},
    {ParamID::TW_TAU, "Tau"},
    {ParamID::TW_CENTRE, "Centre"},
    {ParamID::FD_HEIGHT, "Height"},
    {ParamID::FD_DIFFCOEFF, "DiffCoeff"},
    {ParamID::FD_CENTRE, "Centre"},
    {ParamID::CE_HEIGHT, "Height"},
    {ParamID::CE_TAU, "Tau"},
    {ParamID::CE_L, "L"},
    {ParamID::CE_CENTRE, "Centre"},
    {ParamID::HR_HEIGHT, "Height"},
    {ParamID::HR_TAU, "Tau"},
    {ParamID::HR_L, "L"},
    {ParamID::HR_CENTRE, "Centre"},
    {ParamID::DELTA_HEIGHT, "Height"},
    {ParamID::DELTA_CENTER, "Centre"},
    {ParamID::TEMPERATURE, "Temperature"},
    {ParamID::SE_HEIGHT, "Height"},
    {ParamID::SE_TAU, "Tau"},
    {ParamID::SE_BETA, "Beta"},
    {ParamID::SE_CENTRE, "Centre"},
    {ParamID::DP_INTENSITY, "f1.Intensity"},
    {ParamID::DP_RADIUS, "f1.Radius"},
    {ParamID::DP_DIFFUSION, "f1.Diffusion"},
    {ParamID::DP_SHIFT, "f1.Shift"},
    {ParamID::EDP_HEIGHT, "Height"},
    {ParamID::EDP_CENTRE, "Centre"},
    {ParamID::EDP_RADIUS, "Radius"},
    {ParamID::IDP_INTENSITY, "Intensity"},
    {ParamID::IDP_RADIUS, "Radius"},
    {ParamID::IDP_DIFFUSION, "Diffusion"},
    {ParamID::IDP_SHIFT, "Shift"},
    {ParamID::DRDC_INTENSITY, "f1.Intensity"},
    {ParamID::DRDC_RADIUS, "f1.Radius"},
    {ParamID::DRDC_DECAY, "f1.Decay"},
    {ParamID::DRDC_SHIFT, "f1.Shift"},
    {ParamID::IDRDC_INTENSITY, "Intensity"},
    {ParamID::IDRDC_RADIUS, "Radius"},
    {ParamID::IDRDC_DECAY, "Decay"},
    {ParamID::IDRDC_SHIFT, "Shift"},
    {ParamID::EDRDC_HEIGHT, "Height"},
    {ParamID::EDRDC_CENTRE, "Centre"},
    {ParamID::EDRDC_RADIUS, "Radius"},
    {ParamID::IRD_HEIGHT, "f1.Height"},
    {ParamID::IRD_RADIUS, "f1.Radius"},
    {ParamID::IRD_TAU, "f1.Tau"},
    {ParamID::IRD_CENTRE, "f1.Centre"},
    {ParamID::EIRD_HEIGHT, "Height"},
    {ParamID::EIRD_RADIUS, "Radius"},
    {ParamID::IIRD_HEIGHT, "Height"},
    {ParamID::IIRD_RADIUS, "Radius"},
    {ParamID::IIRD_TAU, "Tau"},
    {ParamID::IIRD_CENTRE, "Centre"},
    {ParamID::FLAT_BG_A0, "A0"},
    {ParamID::LINEAR_BG_A0, "A0"},
    {ParamID::LINEAR_BG_A1, "A1"},
};

inline ParamID &operator++(ParamID &id) {
  id = ParamID(static_cast<std::underlying_type<ParamID>::type>(id) + 1);
  return id;
}

inline void applyToParamIDRange(ParamID from, ParamID to, const std::function<void(ParamID)> &fun) {
  if (from == ParamID::NONE || to == ParamID::NONE)
    return;
  for (auto i = from; i <= to; ++i)
    fun(i);
}

} // namespace IDA
} // namespace CustomInterfaces
} // namespace MantidQt