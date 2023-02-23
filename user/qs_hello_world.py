#!/usr/bin/env python
"""
Run the hello_world() plan with the Bluesky Queueserver.

This code is simpler than bsqs_client.py but it only runs top-to-bottom, adding
sleep(10) & hello_world() to the queue.  It starts the queue if it is idle. Runs
on both agate (LAN) & lapis (localhost).

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

RM.item_add(BPlan("sleep", 10))
RM.item_add(BPlan("hello_world"))

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
