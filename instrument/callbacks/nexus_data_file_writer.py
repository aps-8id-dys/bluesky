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

        The design is to have all HDF5 files (metadata, image, analysis) in the
        same directory.  This makes it easy to create external file links.

        BUT, some detectors do not create an HDF5 file. We'll have to re-visit
        external links when we get such a detector.

        Do not delay by waiting for the image file to close, then copying the
        image data to the one NeXus file.

        Advice is to ALWAYS use a RELATIVE file path with ExternalLink.  When
        the master:external file pair are moved, the new location can construct
        the expected relative path using softlinks (or Windows aliases).
        """
        resource_id = self.get_unique_resource(d)
        fname = self.getResourceFile(resource_id)

        # Link to image file in the same directory.
        h5addr = "/entry/data/data"  # NeXus default data address.
        subgroup["value"] = h5py.ExternalLink(fname.name, h5addr)

        ds = subgroup.create_dataset("image_file_name", data=fname.name)
        ds.attrs["bluesky_resource_id"] = resource_id
        ds.attrs["shape"] = v.get("shape", "")
        ds.attrs["target"] = ds.name

    def get_ioc_file_path(self):
        import pathlib
        from instrument.devices.ad_lambda2M import LAMBDA2M_FILES_ROOT

        # NOTE: The default is specific for the Lambda2M detector!
        # Actual IOC file path is not present in the resource or datum docs.
        # Get from run's metadata or pick default.

        dir = self.metadata.get("ADIOC_FILE_DIR", LAMBDA2M_FILES_ROOT)
        return pathlib.Path(dir)

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
# RE.subscribe(nxwriter.receiver)  # subscribe to the RunEngine

warn_missing = iconfig.get("NEXUS_WARN_MISSING_CONTENT", False)
nxwriter.warn_on_missing_content = warn_missing
nxwriter.file_extension = iconfig.get("NEXUS_FILE_EXTENSION", "hdf")

# NeXus files are written into current working directory.  Here are the controls:
# nxwriter.file_path = pathlib.Path("XPCS may want to override!!!")
# nxwriter.file_name = pathlib.Path("XPCS may want to override!!!")
# https://github.com/BCDA-APS/apstools/blob/main/apstools/callbacks/nexus_writer.py#L297
