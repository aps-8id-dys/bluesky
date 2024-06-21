"""
this file makes the .py files here importable
"""

from aps_8id_bs_instrument import iconfig

if iconfig.get("WRITE_NEXUS_DATA_FILES", False):
    from aps_8id_bs_instrument.callbacks.nexus_data_file_writer import *

if iconfig.get("WRITE_SPEC_DATA_FILES", False):
    from aps_8id_bs_instrument.callbacks.spec_data_file_writer import *

del iconfig

from aps_8id_bs_instrument.callbacks.scan_signal_statistics import *
