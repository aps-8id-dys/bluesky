"""
Write the metadata file for processing a bluesky run with a DM workflow.

All metadata content comes from the bluesky run's metadata dictionary. The
bluesky session is responsible to provide all expected metadata keys.
"""

import logging
import pathlib

import databroker
import h5py
import yaml

from .conversions import ts2iso
from .iconfig_loader import iconfig

CATALOG = iconfig["DATABROKER_CATALOG"]
XPCS_LAYOUT_VERSION = "APS-8IDI-202310"

logger = logging.getLogger(__name__)


def write_xpcs_metadata_file(run_uid, md_file, catalog=None, overwrite=False):
    """
    Write the XPCS metadata file given the bluesky run uid.

    Parameters

    run_uid (str): The uid of the run's start.  This can be the full string
        or the first few characters which identify the run uniquely.
    md_file (str): Name of the file to be written.
    catalog (str): Name of the databroker catalog with the 'run_uid'.
        Defaults to the instrument's catalog from the 'iconfig.yml' file.
    overwrite (bool): Raise 'FileExistsError' if 'md_file' exists and
        'overwrite=False' (the default).

    Example::

        write_xpcs_metadata_file("abcd123", "path/to/metadata/file.hdf")
    """
    h5file = pathlib.Path(md_file)
    if h5file.exists() and not overwrite:
        raise FileExistsError(md_file)

    # These will raise exceptions if they fail to exist or connect.
    cat = databroker.catalog[catalog or CATALOG]
    run = cat[run_uid]

    if "stop" not in run.metadata:
        raise KeyError(f"Bluesky {run_uid=!r} has no 'stop' document.")
    if run.metadata["stop"]["exit_status"] not in ("success"):
        raise ValueError(
            f"Bluesky {run_uid=!r} was not successful."
            f"  Reason: {run.metadata['stop'].get('reason', 'not provided')}"
        )

    logger.info("Writing metadata file: %r", h5file.resolve())
    with h5py.File(h5file, "w") as h5root:
        h5root.attrs["xpcs_layout_version"] = XPCS_LAYOUT_VERSION
        h5root.attrs["h5py_version"] = h5py.__version__

        # create NeXus group structure
        nxentry = h5root.create_group("entry")
        nxentry.attrs["NX_class"] = "NXentry"
        nxentry.create_dataset("xpcs_layout_version", data=XPCS_LAYOUT_VERSION)

        # NXdata group is not required at this time by NeXus.

        nxinstrument = nxentry.create_group("instrument")
        nxinstrument.attrs["NX_class"] = "NXinstrument"

        bluesky_group = nxinstrument.create_group("bluesky")
        bluesky_group.attrs["NX_class"] = "NXnote"

        run_md_group = bluesky_group.create_group("metadata")
        run_md_group.attrs["NX_class"] = "NXnote"

        # TODO: write data from bluesky stream(s).

        # Write all the run metadata.
        units = {
            # Add known units to certain metadata keys.
            "X_energy": "keV",
            "incident_beam_size_nm_xy": "nm",
        }
        for k, v in run.metadata["start"].items():
            if isinstance(v, (dict, tuple, list)):
                # Save complicated metadata structures as YAML text
                v = yaml.dump(v)
                ds = run_md_group.create_dataset(k, data=v)
                ds.attrs["text_format"] = "yaml"
            else:
                ds = run_md_group.create_dataset(k, data=v)

            ds.attrs["target"] = ds.name
            if k in units:
                ds.attrs["units"] = units[k]

        # A few legacy patchups.
        patches = {
            "bcx": "beam_center_x",
            "bcy": "beam_center_y",
            "t0": "acquire_time",
            "t1": "acquire_period",
        }
        for old, new in patches.items():
            if old in run_md_group and new not in run_md_group:
                run_md_group[new] = run_md_group[old]

        # While these things are nice to know, they are not required.
        try:
            nxentry.create_dataset("program_name", data="bluesky")

            # Create HDF5 links (from bluesky data)
            nxentry["entry_identifier"] = run_md_group["uid"]
            nxentry["entry_identifier_uuid"] = run_md_group["uid"]
            nxentry["scan_number"] = run_md_group["uid"]
            bluesky_group["uid"] = run_md_group["uid"]

            nxentry["scan_id"] = run_md_group["scan_id"]

            if "title" in run_md_group:
                nxentry["title"] = run_md_group["title"]

            nxentry["start_time"] = ts2iso(run.metadata["start"]["time"])
            if "time" in run.metadata.get("stop", {}):
                # no "stop" document in failed runs
                nxentry["end_time"] = ts2iso(run.metadata["stop"]["time"])
                ds = nxentry.create_dataset(
                    "duration",
                    data=run.metadata["stop"]["time"] - run.metadata["start"]["time"],
                )
                ds.attrs["units"] = "s"

            if "plan_name" in run_md_group:
                nxentry["plan_name"] = run_md_group["plan_name"]
                bluesky_group["plan_name"] = run_md_group["plan_name"]
        except Exception as reason:
            logger.warning("Problem when finalizing %r: %r", md_file, str(reason))
