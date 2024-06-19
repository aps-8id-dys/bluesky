"""
lineup2: Lineup a positioner.  Works with queueserver.

.. caution:: This is an early draft and is subject to change!

Replaces ``lineup()`` and ``lup()`` plans which could not be used with the
queueserver.
"""

__all__ = [
    "lineup2",  # "smart" choice (peak must be a *peak*) to center after scan
    "signal_stats",
]

import logging
import math

from bluesky import plan_stubs as bps
from bluesky import plans as bp
from bluesky import preprocessors as bpp

logger = logging.getLogger(__name__)

logger.info(__file__)

from ..callbacks import SignalStatsCallback

factor_fwhm = 2 * math.sqrt(2 * math.log(2))  # FWHM = factor_fwhm * sigma
signal_stats = SignalStatsCallback()
signal_stats.stop_report = False


def lineup2(detectors, mover, rel_start, rel_end, points, nscans=2, feature="centroid"):
    """
    Lineup and center a given mover, relative to current position.

    This plan can be used in the queueserver.  It does not require the 
    bluesky BestEffortCallback.  Instead, it uses *PySumReg*  [#pysumreg]_
    to compute statistics for each signal in a 1-D scan.

    New in release 1.6.18

    .. caution:: This is an early draft and is subject to change!

    .. index:: Bluesky Plan; lineup2; lineup

    PARAMETERS

    detectors [*Readable*]:
        Detector object or list of detector objects (each is a Device or
        Signal). If a list, the first Signal will be used for alignment.
    mover *Movable*:
        Mover object, such as motor or other positioner.
    rel_start *float*:
        Starting point for the scan, relative to the current mover position.
    rel_end *float*:
        Ending point for the scan, relative to the current mover position.
    points *int*:
        Number of points in the scan.
    nscans *int*:
        Number of scans.  (default: 2)  Scanning will stop if any scan cannot
        find a peak.
    feature *str*:
        Use this statistical measure (default: centroid) to set the mover
        position after a peak has been found.  Must be one of these values:

        ==========  ====================
        feature     description
        ==========  ====================
        centroid    center of mass
        x_at_max_y  x location of y maximum
        x_at_min_y  x location of y minimum
        ==========  ====================

        Statistical analysis provided by *PySumReg*.  [#pysumreg]_

        .. [#pysumreg] https://prjemian.github.io/pysumreg/latest/
    """

    signal_stats.stop_report = False  # Turn this automation off.

    # Allow for feature to be defined using a name from PeakStats.
    xref_PeakStats = {
        "com": "centroid",
        "cen": "x_at_max_y",
        "max": "x_at_max_y",
        "min": "x_at_min_y",
    }
    # translate from PeakStats feature to SignalStats
    feature = xref_PeakStats.get(feature, feature)

    def get_x_by_feature():
        """Return the X value of the specified ``feature``."""
        stats = principal_signal_stats()
        if strong_peak(stats) and not too_wide(stats):
            return getattr(stats, feature)

    def principal_signal_stats() -> str:
        """Return the name of the first detector Signal."""
        return signal_stats._stats[signal_stats._y_names[0]]

    def strong_peak(stats) -> bool:
        """Determine if the peak is strong."""
        try:
            value = (stats.max_y - stats.min_y) / stats.sigma
            return value > 2.5
        except ZeroDivisionError:  # not enough samples
            value = abs(stats.max_y / stats.min_y)
            return value > 4

    def too_wide(stats):
        """Does the measured peak width fill the full range of X?"""
        try:
            x_range = stats.max_x - stats.min_x
            fwhm = stats.sigma * factor_fwhm
            return fwhm > 0.9 * x_range
        except ZeroDivisionError:  # not enough samples
            return True

    @bpp.subs_decorator(signal_stats.receiver)
    def _inner():
        """Run the scan, collecting statistics at each step."""
        # TODO: save signal stats into separate stream
        yield from bp.rel_scan(detectors, mover, rel_start, rel_end, points)

    while nscans > 0:  # allow for repeated scans
        yield from _inner()  # Run the scan.
        nscans -= 1

        target = get_x_by_feature()
        if target is None:
            nscans = 0  # Nothing found, no point scanning again.
        else:
            yield from bps.mv(mover, target)  # Move to the feature position.
            logger.info("Moved %s to %s: %f", mover.name, feature, mover.position)

            if nscans > 0:
                # move the end points for the next scan
                rel_end = principal_signal_stats().sigma * factor_fwhm
                rel_start = -rel_end
