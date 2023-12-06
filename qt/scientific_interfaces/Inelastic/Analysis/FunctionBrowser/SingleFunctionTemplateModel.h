// Mantid Repository : https://github.com/mantidproject/mantid
//
// Copyright &copy; 2019 ISIS Rutherford Appleton Laboratory UKRI,
//   NScD Oak Ridge National Laboratory, European Spallation Source,
//   Institut Laue - Langevin & CSNS, Institute of High Energy Physics, CAS
// SPDX - License - Identifier: GPL - 3.0 +
#pragma once

#include "Analysis/ParameterEstimation.h"
#include "DllConfig.h"
#include "MantidAPI/IFunction_fwd.h"
#include "MantidAPI/ITableWorkspace_fwd.h"
#include "MantidQtWidgets/Common/FunctionModel.h"
#include "MantidQtWidgets/Common/IndexTypes.h"

#include <QMap>
#include <boost/optional.hpp>
#include <string>

namespace MantidQt {
namespace CustomInterfaces {
namespace IDA {

class IDAFunctionParameterEstimation;

using namespace Mantid::API;
using namespace MantidWidgets;

class MANTIDQT_INELASTIC_DLL SingleFunctionTemplateModel : public FunctionModel {
public:
  SingleFunctionTemplateModel();
  SingleFunctionTemplateModel(std::unique_ptr<IDAFunctionParameterEstimation> parameterEstimation);
  void setFunction(IFunction_sptr fun) override;
  void updateAvailableFunctions(const std::map<std::string, std::string> &functionInitialisationStrings);

  void setFitType(const QString &name);
  QString getFitType();
  void removeFitType();
  QStringList getFunctionList();
  int getEnumIndex();
  void setGlobal(const QString &name, bool isGlobal);

  EstimationDataSelector getEstimationDataSelector() const;
  void updateParameterEstimationData(DataForParameterEstimationCollection &&data);

  void estimateFunctionParameters();

private:
  QString m_fitType;
  DataForParameterEstimationCollection m_estimationData;
  QMap<QString, IFunction_sptr> m_fitTypeToFunctionStore;
  QMap<QString, QStringList> m_globalParameterStore;
  QStringList m_fitTypeList;
  boost::optional<QString> findFitTypeForFunctionName(const QString &name) const;
  // Parameter estimation
  std::unique_ptr<IDAFunctionParameterEstimation> m_parameterEstimation;
};

} // namespace IDA
} // namespace CustomInterfaces
} // namespace MantidQt