"""
Hello, World! demo for bluesky testing.

EXAMPLE::

    RE(hello_world())
"""

__all__ = """
    hello_world
""".split()

import logging

from bluesky import plans as bp
from ophyd import Component
from ophyd import Device
from ophyd import Signal

logger = logging.getLogger(__name__)
logger.info(__file__)


class HelloDevice(Device):
    """Simple ophyd device."""

    number = Component(Signal, value=0, kind="hinted")
    text = Component(Signal, value="", kind="normal")


hello_device = HelloDevice(name="hello")
hello_device.stage_sigs["number"] = 1
hello_device.stage_sigs["text"] = "Hello, World!"
hello_device.number.name = hello_device.name


def hello_world():
    """Simple plan for testing purposes."""
    yield from bp.count([hello_device], md=dict(title="test QS"))
