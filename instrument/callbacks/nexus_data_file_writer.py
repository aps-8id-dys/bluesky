"""
Write each run to a NeXus/HDF5 file.

IMPORTANT
See the note about waiting for the nxwriter to finish AFTER EACH ACQUISITION!
https://bcda-aps.github.io/apstools/dev/api/_filewriters.html#apstools.callbacks.nexus_writer.NXWriter
"""

__all__ = ["nxwriter"]

from apstools.callbacks import NXWriterAPS

from .._iconfig import iconfig
from ..framework.initialize import RE


class MyNXWriter(NXWriterAPS):
    def get_sample_title(self):
        """
        Get the title from the metadata or modify the default.

        default title: S{scan_id}-{plan_name}-{short_uid}
        """
        try:
            title = self.metadata["title"]
        except KeyError:
            # title = super().get_sample_title()  # the default title
            title = f"S{self.scan_id:05d}-{self.plan_name}-{self.uid[:7]}"
        return title
    
    # FIXME: do not copy the image data to this file
    # TODO: include the metadata like we did previously
    #   old_code/spec_support/APS_DM_8idi.py starting at line ~310
    #   Use a separate stream named "ad_metadata"
    #   OR, use labels=("ad_metadata",) as each device is defined
    #      and write a separate stream (stream: label_start_ad_metadata)
    #      do like we do for motors .


nxwriter = MyNXWriter()  # create the callback instance
RE.subscribe(nxwriter.receiver)  # subscribe to the RunEngine

warn_missing = iconfig.get("NEXUS_WARN_MISSING_CONTENT", False)
nxwriter.warn_on_missing_content = warn_missing
nxwriter.file_extension = iconfig.get("NEXUS_FILE_EXTENSION", "hdf")

# NeXus files are written into current working directory.  Here are the controls:
# nxwriter.file_path = pathlib.Path("XPCS may want to override!!!")
# nxwriter.file_name = pathlib.Path("XPCS may want to override!!!")
# https://github.com/BCDA-APS/apstools/blob/main/apstools/callbacks/nexus_writer.py#L297
