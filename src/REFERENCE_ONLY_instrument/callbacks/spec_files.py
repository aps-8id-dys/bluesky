"""
Write SPEC data files.
"""

try:
    # upgrade comes with apstools 1.6.20
    from apstools.callbacks import SpecWriterCallback2 as callback
except ImportError:
    from apstools.callbacks import SpecWriterCallback as callback

specwriter = callback()
specwriter.write_new_scan_header = False  # issue #1032
