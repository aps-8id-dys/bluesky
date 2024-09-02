"""
Classes used by various devices at 8-ID.

.. note:: No ophyd objects are created in this module.
"""

__all__ = """
    HV_Motors
    SydorTP4U
""".split()


import logging

from ophyd import EpicsMotor
from ophyd import EpicsSignalRO
from ophyd import FormattedComponent as FCpt
from ophyd import MotorBundle
from ophyd import QuadEM
from ophyd.areadetector.plugins import ImagePlugin_V34
from ophyd.areadetector.plugins import StatsPlugin_V34
from ophyd.quadem import QuadEMPort

logger = logging.getLogger(__name__)
logger.info(__file__)


class HV_Motors(MotorBundle):
    """
    Horizontal/Vertical Motor Stage with h & v translations.

    Parameters

    prefix
        (str) : EPICS PV prefix common to both motors.
        Includes trailing delimiter, such as ':', as needed.
        (Same convention as used with GUI screens, IOC startup scripts,
        and other EPICS configuration.)
    h_pv
        (str) : EPICS PV suffix for the horizontal motor PV.
    v_pv
        (str) : EPICS PV suffix for the vertical motor PV.

    Example::

        base = HV_Motors("IOC:DB:", name="base", h_pv="m9", v_pv="m10")
        # which creates:
        # base.h.pvname: IOC:DB:m9
        # base.v.pvname: IOC:DB:m10
    """

    h = FCpt(EpicsMotor, "{prefix}{_h_pv}", labels={"motors"})
    v = FCpt(EpicsMotor, "{prefix}{_v_pv}", labels={"motors"})

    def __init__(
        self,
        prefix: str,
        *args,
        h_pv: str = "",
        v_pv: str = "",
        **kwargs,
    ):
        self._h_pv = h_pv
        self._v_pv = v_pv
        super().__init__(prefix, *args, **kwargs)


class SydorTP4U(QuadEM):
    """
    Sydor TP4U quad electrometer.
    
    Example::

        xbpm2 = SydorTP4U("8idiSoft:T4U_BPM:", name="xbpm2")
    """

    conf = Component(QuadEMPort, port_name="T4U_BPM")

    # latest versions of the AD plugins
    current1 = Component(StatsPlugin_V34, "Current1:")
    current2 = Component(StatsPlugin_V34, "Current2:")
    current3 = Component(StatsPlugin_V34, "Current3:")
    current4 = Component(StatsPlugin_V34, "Current4:")
    image = Component(ImagePlugin_V34, "image1:")
    sum_all = Component(StatsPlugin_V34, "SumAll:")

    # better as text than numbers
    firmware = Component(EpicsSignalRO, "Firmware", string=True, kind="config")
    model = Component(EpicsSignalRO, "Model", string=True, kind="config")
