"""
this file makes the .py files here importable
"""

# flake8: noqa

from .. import iconfig

if iconfig.get("WRITE_NEXUS_DATA_FILES", False):
    from .nexus_data_file_writer import nxwriter

if iconfig.get("WRITE_SPEC_DATA_FILES", False):
    from .spec_data_file_writer import specwriter

from .scan_signal_statistics import SignalStatsCallback

del iconfig
