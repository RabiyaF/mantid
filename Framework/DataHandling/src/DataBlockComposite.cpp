#include "MantidDataHandling/DataBlockComposite.h"
#include "MantidDataHandling/DataBlockGenerator.h"
#include <algorithm>
#include <cassert>

namespace {

  const int64_t invalidIntervalValue = std::numeric_limits<int64_t>::min();

/**
 * Gets all removal intervals which have an overlap with the original interval.
 * This can be either
 * 1. partial overlap: check if start or stop of remove interval
 * is contained in original interval.
 * 2. remove interval is contained in original interval: same check as above
 * 3. remove interval contains original interval: check start value of original
 * in range
 */
std::vector<std::pair<int64_t, int64_t>>
getRemovalIntervalsRelevantForTheCurrentOriginalInterval(
    const std::pair<int64_t, int64_t> &original,
    const std::vector<std::pair<int64_t, int64_t>> &removeIntervals) {

  auto hasOverlap = [](const std::pair<int64_t, int64_t> &original,
                       const std::pair<int64_t, int64_t> &toRemove) {
    return ((original.first <= toRemove.first) &&
            (toRemove.first <= original.second)) ||
           ((original.first <= toRemove.second) &&
            (toRemove.second <= original.second)) ||
           ((toRemove.first <= original.first) &&
            (original.first <= toRemove.second));
  };

  std::vector<std::pair<int64_t, int64_t>> overlaps;
  for (auto &removeInterval : removeIntervals) {
    if (hasOverlap(original, removeInterval)) {
      overlaps.push_back(removeInterval);
    }
  }
  return overlaps;
}

/**
* Handles the scenario:
*   original :        |------....
*   toRemove:     |------|
*   result:
         cut             |---....
         return: NONE
*/
void handleLeftHandSideOverlap(std::pair<int64_t, int64_t> &original,
                               const std::pair<int64_t, int64_t> &toRemove) {
  original.first = toRemove.second + 1;
}

/**
* Handles the scenario:
*   original :  ...------|
*   toRemove:        |------|
*   result:
        cut     we are at the end, set interval to invalid
     return     ...-|
*/
std::pair<int64_t, int64_t>
handleRightHandSideOverlap(std::pair<int64_t, int64_t> &original,
                           const std::pair<int64_t, int64_t> &toRemove) {
   auto newInterval = std::make_pair(original.first, toRemove.first - 1);
   original.first = invalidIntervalValue;
   original.second = invalidIntervalValue;
   return newInterval;
}

/**
* Handles the scenario:
*   original :  ...------------....
*   toRemove:        |------|
*   result:
       cut                  |---...
    return      ...--|
*/
std::pair<int64_t, int64_t>
handleFullyContained(std::pair<int64_t, int64_t> &original,
                     const std::pair<int64_t, int64_t> &toRemove) {
  // It is important to first creat the new pair and then perform the cut
  auto newPair = std::make_pair(original.first, toRemove.first - 1);
  original.first = toRemove.second + 1;
  return newPair;
}

std::vector<std::pair<int64_t, int64_t>> getSlicedIntervals(
    std::pair<int64_t, int64_t> original,
    const std::vector<std::pair<int64_t, int64_t>> &removeIntervals) {
  // If there is nothing to remove return the original
  if (removeIntervals.empty()) {
    return std::vector<std::pair<int64_t, int64_t>>{original};
  }

  // There are several overlap scenarios.
  // 1. Full overlap
  //    original :    |-------|      and |------|
  //    toRemove: ...------------... and |------|
  // 2. Left hand side overlap
  //    original :     |------...  and |-----....
  //    toRemove:   |------|       and |---|
  // 3. Right hand side overlap
  //    original :  ...-------|    and ...-----|
  //    toRemove:          |-----| and     |---|
  // 4. Fully contained
  //    original :  ...-------...
  //    toRemove:       |---|

  auto isFullOverlap = [](const std::pair<int64_t, int64_t> &original,
                          const std::pair<int64_t, int64_t> &toRemove) {
    return (toRemove.first <= original.first) &&
           (original.first <= toRemove.second) &&
           (toRemove.first <= original.second) &&
           (original.second <= toRemove.second);
  };

  auto isLeftHandSideOverlap = [](const std::pair<int64_t, int64_t> &original,
                                  const std::pair<int64_t, int64_t> &toRemove) {
    return (toRemove.first <= original.first) &&
           (original.first <= toRemove.second) &&
           (toRemove.second < original.second);
  };

  auto isRightHandSideOverlap =
      [](const std::pair<int64_t, int64_t> &original,
         const std::pair<int64_t, int64_t> &toRemove) {
        return (original.first < toRemove.first) &&
               (toRemove.first <= original.second) &&
               (original.second <= toRemove.second);
      };

  auto isFullyContained = [](const std::pair<int64_t, int64_t> &original,
                             const std::pair<int64_t, int64_t> &toRemove) {
    return (original.first < toRemove.first) &&
           (toRemove.first < original.second) &&
           (original.first < toRemove.second) &&
           (toRemove.second < original.second);
  };

  // Use that removeIntervals has oredred, non-overlapping intervals
  // Subtract all the removeIntervals
  std::vector<std::pair<int64_t, int64_t>> newIntervals;
  for (auto &removeInterval : removeIntervals) {

    if (isFullOverlap(original, removeInterval)) {
      // In this case we should remove everything. At this point newIntervals
      // should still be empty, since the remove intervals should not be
      // overlapping
      assert(newIntervals.empty() && "DataBlockComposite: The newIntervals container should be empty");
      // Set the remainder of the original to invalid, such that we don't pick it up at the very end
      original.first = invalidIntervalValue;
      original.second = invalidIntervalValue;
      break;
    } else if (isRightHandSideOverlap(original, removeInterval)) {
      auto newInterval = handleRightHandSideOverlap(original, removeInterval);
      newIntervals.push_back(newInterval);
    } else if (isLeftHandSideOverlap(original, removeInterval)) {
      handleLeftHandSideOverlap(original, removeInterval);
    } else if (isFullyContained(original, removeInterval)) {
      auto newInterval = handleFullyContained(original, removeInterval);
      newIntervals.push_back(newInterval);
    } else {
      throw std::runtime_error(
          "DataBlockComposite: The intervals don't seem to overlap.");
    }
  }

  // There might be some remainder in the original interval, e.g if there wasn't a full overlap removal
  // or no righ-hand-side overlap of a removal interval
  if ((original.first != invalidIntervalValue) &&
    (original.second != invalidIntervalValue)) {
    newIntervals.push_back(original);
  }

  return newIntervals;
}
}

namespace Mantid {
namespace DataHandling {

int64_t DataBlockComposite::getMinSpectrumID() const {
  int64_t min = std::numeric_limits<int64_t>::max();
  for (const auto &child : m_dataBlocks) {
    auto temp = child.getMinSpectrumID();
    if (temp < min) {
      min = temp;
    }
  }
  return min;
}

void DataBlockComposite::setMinSpectrumID(int64_t) {
  // DO NOTHING
}

int64_t DataBlockComposite::getMaxSpectrumID() const {
  int64_t max = std::numeric_limits<int64_t>::min();
  for (const auto &child : m_dataBlocks) {
    auto temp = child.getMaxSpectrumID();
    if (temp > max) {
      max = temp;
    }
  }
  return max;
}

void DataBlockComposite::setMaxSpectrumID(int64_t) {
  // DO NOTHING
}

std::unique_ptr<DataBlockGenerator> DataBlockComposite::getGenerator() const {
  std::vector<std::pair<int64_t, int64_t>> intervals;
  for (const auto &dataBlock : m_dataBlocks) {
    intervals.push_back(std::make_pair(dataBlock.getMinSpectrumID(),
                                       dataBlock.getMaxSpectrumID()));
  }
  return Mantid::Kernel::make_unique<DataBlockGenerator>(intervals);
}

void DataBlockComposite::addDataBlock(DataBlock dataBlock) {
  // Set the number of periods, number of spectra and number of channel
  m_numberOfPeriods = dataBlock.getNumberOfPeriods();
  m_numberOfChannels = dataBlock.getNumberOfChannels();
  m_numberOfSpectra = dataBlock.getNumberOfSpectra();

  // Insert the data block
  m_dataBlocks.push_back(dataBlock);
}

size_t DataBlockComposite::getNumberOfSpectra() const {
  size_t total = 0;
  for (const auto &element : m_dataBlocks) {
    total += element.getNumberOfSpectra();
  }
  return total;
}

DataBlockComposite DataBlockComposite::
operator+(const DataBlockComposite &other) {
  DataBlockComposite output;
  output.m_dataBlocks.insert(std::end(output.m_dataBlocks),
                             std::begin(m_dataBlocks), std::end(m_dataBlocks));
  output.m_dataBlocks.insert(std::end(output.m_dataBlocks),
                             std::begin(other.m_dataBlocks),
                             std::end(other.m_dataBlocks));
  return output;
}

std::vector<DataBlock> DataBlockComposite::getIntervals() {
  // Sort the intervals. We sort them by minimum value
  auto comparison = [](const DataBlock &el1, const DataBlock &el2) {
    return el1.getMinSpectrumID() < el2.getMinSpectrumID();
  };
  std::sort(m_dataBlocks.begin(), m_dataBlocks.end(), comparison);
  return m_dataBlocks;
}

/**
 * Removes the input data blocks from the current list of data blocks.
 * @param toRemove: data block composite to remove
 *
 * original: |-----|  |-------|     |----|
 * toRemove:     |------|       |--|
 * result:   |---|      |------|    |----|
 */
void DataBlockComposite::removeSpectra(DataBlockComposite &toRemove) {
  // Get intervals for current data blocks
  std::vector<std::pair<int64_t, int64_t>> originalIntervals;
  for (auto &dataBlock : m_dataBlocks) {
    originalIntervals.emplace_back(std::make_pair(
        dataBlock.getMinSpectrumID(), dataBlock.getMaxSpectrumID()));
  }

  // Get intervals for the data blocks which should be removed
  auto removeBlocks = toRemove.getIntervals();
  std::vector<std::pair<int64_t, int64_t>> toRemoveIntervals;
  for (auto &dataBlock : removeBlocks) {
    toRemoveIntervals.emplace_back(std::make_pair(
        dataBlock.getMinSpectrumID(), dataBlock.getMaxSpectrumID()));
  }

  // Now create the new intervals which don't include the removeInterval values
  std::vector<std::pair<int64_t, int64_t>> newIntervals;
  for (auto &originalInterval : originalIntervals) {
    // Find all relevant remove intervals. In principal this could
    // be made more efficient.
    auto currentRemovalIntervals =
        getRemovalIntervalsRelevantForTheCurrentOriginalInterval(
            originalInterval, toRemoveIntervals);
    auto slicedIntervals =
        getSlicedIntervals(originalInterval, currentRemovalIntervals);
    newIntervals.insert(std::end(newIntervals), std::begin(slicedIntervals),
                        std::end(slicedIntervals));
  }

  // Create a new set of data blocks
  auto numberOfPeriods = m_dataBlocks[0].getNumberOfPeriods();
  auto numberOfChannels = m_dataBlocks[0].getNumberOfChannels();
  auto numberOfSpectra = m_dataBlocks[0].getNumberOfSpectra();

  m_dataBlocks.clear();
  for (auto &newInterval : newIntervals) {
    DataBlock dataBlock(numberOfPeriods,
                        newInterval.second - newInterval.first + 1,
                        numberOfChannels);
    dataBlock.setMinSpectrumID(newInterval.first);
    dataBlock.setMaxSpectrumID(newInterval.second);
    m_dataBlocks.push_back(dataBlock);
  }
}
}
}
