#ifndef MANTID_ALGORITHMS_WEIGHTINGSTRATEGY_H_
#define MANTID_ALGORITHMS_WEIGHTINGSTRATEGY_H_

#include "MantidKernel/System.h"


namespace Mantid
{
namespace Algorithms
{

  /** WeightingStrategy : 
  
    Abstract weighting strategy, which can be applied to calculate individual 
    weights for each pixel based upon disance from epicenter. Generated for use with SmoothNeighbours.
    
    @date 2011-11-30

    Copyright &copy; 2011 ISIS Rutherford Appleton Laboratory & NScD Oak Ridge National Laboratory

    This file is part of Mantid.

    Mantid is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 3 of the License, or
    (at your option) any later version.

    Mantid is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.

    File change history is stored at: <https://svn.mantidproject.org/mantid/trunk/Code/Mantid>
    Code Documentation is available at: <http://doxygen.mantidproject.org>
  */
    class DLLExport WeightingStrategy
    {
    public:
      /// Constructor
      WeightingStrategy(const double cutOff);
      /// Constructor
      WeightingStrategy();
      /// Destructor
      virtual ~WeightingStrategy();
      /**
      Calculate the weight at distance from epicenter.
      @param distance : absolute distance from epicenter
      @return calculated weight
      */
      virtual double weightAt(const double& distance) = 0;

      /**
      Calculate the weight at distance from epicenter.
      @param adjX : The number of Y (vertical) adjacent pixels to average together
      @param ix : current index x
      @param adjY : The number of X (vertical) adjacent pixels to average together
      @param iy : current index y
      */
      virtual double weightAt(const double& adjX,const double& ix, const double& adjY, const double& iy) = 0;
    protected:
      /// Cutoff member.
      double m_cutOff;
    };

    /*
    Flat (no weighting) strategy. Concrete WeightingStrategy
    */
    class DLLExport FlatWeighting : public WeightingStrategy
    {
    public:
      FlatWeighting();
      virtual ~FlatWeighting();
      virtual double weightAt(const double&,const double&, const double&, const double&);
      double weightAt(const double&);
    };

    /*
    Linear weighting strategy.
    */
    class DLLExport LinearWeighting : public WeightingStrategy
    {
    public: 
      LinearWeighting(const double cutOff);
      virtual ~LinearWeighting();
      double weightAt(const double& distance);
      virtual double weightAt(const double& adjX,const double& ix, const double& adjY, const double& iy);
    };

    /*
    Parabolic weighting strategy.
    */
    class DLLExport ParabolicWeighting : public WeightingStrategy
    {
    public: 
      ParabolicWeighting();
      virtual ~ParabolicWeighting();
      double weightAt(const double&);
      virtual double weightAt(const double& adjX,const double& ix, const double& adjY, const double& iy);
    };

    /*
    Null weighting strategy.
    */
    class DLLExport NullWeighting : public WeightingStrategy
    {
    public:
      NullWeighting();
      virtual ~NullWeighting();
      double weightAt(const double&);
      virtual double weightAt(const double&,const double&, const double&, const double&);
    };

    /*
    Gaussian Strategy
    */
    class DLLExport GaussianWeighting1D : public WeightingStrategy
    {
    public:
      GaussianWeighting1D(double cutOff, double sigma);
      GaussianWeighting1D(double sigma);
      virtual ~GaussianWeighting1D();
      virtual double weightAt(const double &);
      virtual double weightAt(const double&,const double&, const double&, const double&);
    private:
      void init(const double sigma);
      double calculateGaussian(const double normalisedDistanceSq);
      double m_coeff;
      double m_twiceSigmaSquared;
    };




} // namespace Algorithms
} // namespace Mantid

#endif  /* MANTID_ALGORITHMS_WEIGHTINGSTRATEGY_H_ */