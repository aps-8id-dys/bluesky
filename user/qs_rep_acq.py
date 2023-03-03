#!/usr/bin/env python
"""
Run the repeated_acquire() plan with the Bluesky Queueserver.

see: https://blueskyproject.io/bluesky-queueserver-api/usage.html
"""

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

# def repeated_acquire(
#     acq_rep=3,
#     file_name="Test",
#     acquire_time=0.001,
#     acquire_period=0.001,
#     n_images=10_000,
#     file_path="/home/8ididata/2023-1/bluesky202301",
#     use_hdf=False,
#     md={},
# ):

frame_rate = 200
duration = 10
n_images = duration * frame_rate
title = (
    "BDP streaming demo with Bluesky Queueserver,"
    f" {frame_rate} fps for ~{duration} s."
)

RM.item_add(BPlan("sleep", 3))
for i in range(3):
    RM.item_add(
        BPlan(
            "repeated_acquire",
            acq_rep=1,
            file_name="BDPQS",
            # acquire_time=1.0 / frame_rate,
            # acquire_period=1.0 / frame_rate + 0.000_5,
            # n_images=n_images,
            # file_path="/home/8ididata/2023-1/bluesky202301",
            use_hdf=False,
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
