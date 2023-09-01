"""
Write each run to a NeXus/HDF5 file.

IMPORTANT
See the note about waiting for the nxwriter to finish AFTER EACH ACQUISITION!
https://bcda-aps.github.io/apstools/dev/api/_filewriters.html#apstools.callbacks.nexus_writer.NXWriter
"""

__all__ = ["nxwriter"]

import h5py
from apstools.callbacks import NXWriterAPS

from .._iconfig import iconfig
# from ..framework.initialize import RE


class MyNXWriter(NXWriterAPS):
    """
    Modify the default behavior of NXWriter for XPCS.
    """

    def get_sample_title(self):
        """
        Get the title from the metadata or modify the default.

        default title: S{scan_id}-{plan_name}-{short_uid}
        """
        try:
            title = f'S{self.scan_id:05d}-{self.metadata["title"]}'
        except KeyError:
            # title = super().get_sample_title()  # the default title
            title = f"S{self.scan_id:05d}-{self.plan_name}-{self.uid[:7]}"
        return title
    
    def write_stream_external(self, parent, d, subgroup, stream_name, k, v):
        """
        Modify the default behavior of NXWriter.  Don't copy the image.

        Create an external file link to the image file data.
        Do not delay by waiting for the image file to close, then copying
        the image data to the one NeXus file.
        """
        # TODO: Do not bother with ExternalLink (for now, at least)
        # TODO: record the name(s) of the external file resources.
        resource_id = self.get_unique_resource(d)
        fname = self.getResourceFile(resource_id)

        h5addr = "/entry/data/data"  # NeXus default data address.
        # TODO: Which file path to use when making the external link?
        ds = h5py.ExternalLink(str(fname), h5addr)  # TODO: check the path
        subgroup["value"] = ds
        # FIXME: attrs don't work here, refactor
        # ds.attrs["image_file"] = str(fname)
        # ds.attrs["image_address"] = h5addr
        # ds.attrs["bluesky_resource_id"] = resource_id
        # ds.attrs["shape"] = v.get("shape", "")
        # ds.attrs["target"] = ds.name

    def get_unique_resource(self, datum_id_list):
        # count number of unique resources (expect only 1)
        resource_id_list = []
        for datum_id in datum_id_list:
            resource_id = self.externals[datum_id]["resource"]
            if resource_id not in resource_id_list:
                resource_id_list.append(resource_id)
        if len(resource_id_list) != 1:
            # fmt: off
            raise ValueError(
                f"{len(resource_id_list)}"
                f" unique resource UIDs: {resource_id_list}"
            )
            # fmt: on
        return resource_id_list[0]

    # TODO: include the metadata like we did previously
    #   old_code/spec_support/APS_DM_8idi.py starting at line ~310
    #   Use a separate stream named "ad_metadata"
    #   OR, use labels=("ad_metadata",) as each device is defined
    #      and write a separate stream (stream: label_start_ad_metadata)
    #      do like we do for motors .


nxwriter = MyNXWriter()  # create the callback instance
#RE.subscribe(nxwriter.receiver)  # subscribe to the RunEngine

warn_missing = iconfig.get("NEXUS_WARN_MISSING_CONTENT", False)
nxwriter.warn_on_missing_content = warn_missing
nxwriter.file_extension = iconfig.get("NEXUS_FILE_EXTENSION", "hdf")

# NeXus files are written into current working directory.  Here are the controls:
# nxwriter.file_path = pathlib.Path("XPCS may want to override!!!")
# nxwriter.file_name = pathlib.Path("XPCS may want to override!!!")
# https://github.com/BCDA-APS/apstools/blob/main/apstools/callbacks/nexus_writer.py#L297
