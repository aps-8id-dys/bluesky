#!/usr/bin/env python
"""
Run the bdp_acquire() plan with the Bluesky Queueserver.

Activate conda environment::

    bash
    become_bluesky

Add job(s) to the QS and start the queue::

    ./user/qs_bdp_acquire.py  # add jobs to the QS and start the queue

QS GUI::

    queue-monitor \
        --zmq-control-addr tcp://lapis.xray.aps.anl.gov:60615 \
        --zmq-info-addr tcp://lapis.xray.aps.anl.gov:60625 &

Watch QS output on (bash) command line::

    qserver-console-monitor \
        --zmq-info-addr tcp://lapis.xray.aps.anl.gov:60625

Acquisition plan API::

    def bdp_acquire(
        acq_rep=3,
        file_name="Test",
        acquire_time=0.005,
        acquire_period=0.005,
        n_images=2_000,
        file_path="/home/8ididata/2023-1/bluesky202301",
        method="stream",  # "stream" (PVA) or "file" (HDF5)
        md={},
    ):

see: https://blueskyproject.io/bluesky-queueserver-api/usage.html
"""

from __future__ import annotations

import yaml
from bluesky_queueserver_api import BPlan
from bluesky_queueserver_api.zmq import REManagerAPI

ZMQ_CONTROL_ADDR = "tcp://lapis.xray.aps.anl.gov:60615"
ZMQ_INFO_ADDR = "tcp://lapis.xray.aps.anl.gov:60625"

RM = REManagerAPI(
    zmq_control_addr=ZMQ_CONTROL_ADDR,
    zmq_info_addr=ZMQ_INFO_ADDR,
)

# status = RM.status()
# print(yaml.dump(status, indent=2))

frame_rate = 200  # Top speed seems to be 1_000 fps, stay below this
duration = 10  # seconds
# now, the computed terms
n_images = int(duration * frame_rate)
acquire_time = 1.0 / frame_rate
title = (
    "BDP streaming demo with Bluesky Queueserver,"
    f" {frame_rate} fps for ~{duration} s."
)

RM.item_add(BPlan("sleep", 3))
for i in range(3):
    RM.item_add(
        BPlan(
            "bdp_acquire",
            acq_rep=1,
            file_name="BDPQS",
            acquire_time=acquire_time,
            # acquire_period is ignored by this cam
            acquire_period=acquire_time,
            n_images=n_images,
            file_path="/home/8ididata/2023-1/bluesky202301",
            # method="file",  # default: "stream"
            md={"title": title},
        )
    )
    RM.item_add(BPlan("sleep", 3))

if not RM.status()["worker_environment_exists"]:
    RM.environment_open()
    RM.wait_for_idle()

if RM.status()["re_state"] == "idle":
    RM.queue_start()
# RM.wait_for_idle()  # optional

status = RM.status()
print(yaml.dump(status, indent=2))

# RM.environment_close()  # optional
# RM.wait_for_idle()

RM.close()
