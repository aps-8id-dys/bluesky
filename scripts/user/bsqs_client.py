#!/usr/bin/env python

# FIXME:

raise RuntimeError("Not ready for use.")

"""
Bluesky QS client program to initiate data acquisition.

- Next, we need to build the Python client software that Miaoqi (or whoever)
  will run to initiate the data acquisition process.  Previous BDP demo will be
  a good template for this.
- We will also build the user-facing bluesky plan that the beam line wants.  The
  one we used today is a good prototype.
- Then, we create (modify the existing code, actually) the code to initiate a DM
  workflow from that same Python client.
- We may need to create a PVA to communicate workflow configuration previously
  communicated in an HDF5 file.
"""

# https://blueskyproject.io/bluesky-queueserver-api/usage.html

import datetime
import pathlib
import sys

import h5py
import ophyd
import yaml
from bluesky_queueserver_api import BPlan
from bluesky_queueserver_api.comm_base import RequestFailedError
from bluesky_queueserver_api.zmq import REManagerAPI

RM = REManagerAPI()


def ready():
    """
    Is the queueserver ready (and idle)?
    """
    status = qs_status()
    return (
        (status["manager_state"] == "idle")
        and (status["re_state"] == "idle")
        and (status["worker_environment_state"] == "idle")
        and (status["worker_environment_exists"])
        and (status["msg"].startswith("RE Manager"))  # RE Manager v0.0.14
    )


def qs_status():
    try:
        status = RM.status(reload=True)
    except (
        # bluesky_queueserver_api.comm_base.RequestTimeoutError,
        # bluesky_queueserver.manager.comms.CommTimeoutError,
        TimeoutError,
        Exception,
    ) as exinfo:
        # (status["manager_state"] == "idle")
        # and (status["re_state"] == "idle")
        # and (status["worker_environment_state"] == "idle")
        # and (status["worker_environment_exists"])
        # and (status["msg"].startswith("RE Manager"))  # RE Manager v0.0.14
        status = dict(
            manager_state="timeout",
            re_state="unknown",
            worker_environment_state="unknown",
            worker_environment_exists=False,
            msg=str(exinfo),
        )
    return status


def reopen_environment():
    try:
        RM.environment_close()
        RM.wait_for_idle()
    except RequestFailedError:
        pass
    RM.environment_open()
    RM.wait_for_idle()


def repeated_acquire(x, y, hfile=None):
    """
    Repeated acquire.
    """
    RM.item_add(BPlan("repeated_acquire", x=float(x), y=float(y)))
    RM.queue_start()
    RM.wait_for_idle()


def get_user_parameters():
    import argparse

    parser = argparse.ArgumentParser(
        prog=pathlib.Path(__file__).name,
        description=__doc__.strip().splitlines()[0],
    )

    subcommand = parser.add_subparsers(title="subcommand", description="subcommand(s)")

    sc = subcommand.add_parser("repeated_acquire", description="Repeated acquire")
    # file_name="Test",
    # acquire_time=0.001,
    # acquire_period=0.001,
    # n_images=10_000,
    # file_path="/home/8ididata/2023-1/bluesky202301",
    sc.add_argument("file_name", help="file name")
    sc.add_argument("acquire_time", help="acquire time, s")
    sc.add_argument("acquire_period", help="acquire period, s")
    sc.add_argument("n_images", help="number of images to acquire")
    sc.add_argument("file_path", help="file path")
    sc.set_defaults(phase="repeated_acquire")

    sc = subcommand.add_parser(
        "qreopen",
        description="(re)open the queueserver (bluesky RunEngine) environment.",
    )
    sc.set_defaults(phase="qreopen")

    sc = subcommand.add_parser(
        "status",
        description="queueserver status",
    )
    sc.set_defaults(phase="status")

    return parser.parse_args()


def command_line():
    opts = get_user_parameters()
    if not hasattr(opts, "phase"):
        print("Error: MUST provide a subcommand.")
        sys.exit(1)
    print(f"{opts = }")

    if opts.phase == "qreopen":
        reopen_environment()
    elif ready():
        # https://git.aps.anl.gov/bcda/beamline-data-pipelines-data-management-workflows/-/blob/main/example-03/control_game.py#L284
        if opts.phase == "repeated_acquire":
            print(f"TODO: {opts.phase=}")
        if opts.phase == "status":
            status = qs_status()
            print(f"{type(status)=} {status=}")
        else:
            print(f"TODO: {opts.phase=}")
    else:
        status = qs_status() or "not available"
        print(yaml.dump(status, indent=2))
        print(f"Queueserver {status=}.")


if __name__ == "__main__":
    command_line()
