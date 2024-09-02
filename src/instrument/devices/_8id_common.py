"""
Classes used by various devices at 8-ID.

.. note:: No ophyd objects are created in this module.
"""

__all__ = """
    HV_Motors
    SydorTP4U
    Transfocator
""".split()


import logging

from ophyd import Component
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
    pv_h
        (str) : EPICS PV suffix for the horizontal motor PV.
    pv_v
        (str) : EPICS PV suffix for the vertical motor PV.

    Example::

        base = HV_Motors("IOC:DB:", name="base", pv_h="m9", pv_v="m10")
        # which creates:
        # base.h.pvname: IOC:DB:m9
        # base.v.pvname: IOC:DB:m10
    """

    h = FCpt(EpicsMotor, "{prefix}{_pv_h}", labels={"motors"})
    v = FCpt(EpicsMotor, "{prefix}{_pv_v}", labels={"motors"})

    def __init__(
        self,
        prefix: str,
        *args,
        pv_h: str = "",
        pv_v: str = "",
        **kwargs,
    ):
        self._pv_h = pv_h
        self._pv_v = pv_v
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


class Transfocator(MotorBundle):
    """
    Transfocator (compound refractive lens, CRL).

    Example::

        rl1 = Transfocator(
            "8iddSoft:TRANS:",
            name="rl1",
            pv_y="m1",
            pv_x="m2",
            pv_yaw="m3",
            pv_pitch="m4",
            pv_lens1="m5",
            pv_lens2="m6",
            pv_lens3="m7",
            pv_lens4="m8",
            pv_lens5="m9",
            pv_lens6="m10",
            pv_lens7="m11",
            pv_lens8="m12",
            pv_lens9="m13",
            pv_lens10="m14",
        )

    .. note:: POLAR instrument has some related functions (`transfocator.py`).
        https://github.com/APS-4ID-POLAR/polar_instrument/pull/7/files
    """

    # Motors that position the CRL assembly.
    # By some convention, the names x&y are used rather than h&v.
    x = FCpt(EpicsMotor, "{prefix}{_pv_x}", labels={"motors"})
    y = FCpt(EpicsMotor, "{prefix}{_pv_y}", labels={"motors"})
    pitch = FCpt(EpicsMotor, "{prefix}{_pv_pitch}", labels={"motors"})
    yaw = FCpt(EpicsMotor, "{prefix}{_pv_yaw}", labels={"motors"})

    # Motors that insert or remove each lens.
    # Note: Operated as two-position motors.  Consider refactoring as such.
    lens1 = FCpt(EpicsMotor, "{prefix}{_pv_lens1}", labels={"lens"})
    lens2 = FCpt(EpicsMotor, "{prefix}{_pv_lens2}", labels={"lens"})
    lens3 = FCpt(EpicsMotor, "{prefix}{_pv_lens3}", labels={"lens"})
    lens4 = FCpt(EpicsMotor, "{prefix}{_pv_lens4}", labels={"lens"})
    lens5 = FCpt(EpicsMotor, "{prefix}{_pv_lens5}", labels={"lens"})
    lens6 = FCpt(EpicsMotor, "{prefix}{_pv_lens6}", labels={"lens"})
    lens7 = FCpt(EpicsMotor, "{prefix}{_pv_lens7}", labels={"lens"})
    lens8 = FCpt(EpicsMotor, "{prefix}{_pv_lens8}", labels={"lens"})
    lens9 = FCpt(EpicsMotor, "{prefix}{_pv_lens9}", labels={"lens"})
    lens10 = FCpt(EpicsMotor, "{prefix}{_pv_lens10}", labels={"lens"})

    # TODO: Describe parameters of each lens.
    # TODO: Add method(s) to select & report focal parameters based on lens combination.

    def __init__(
        self,
        prefix: str,
        *args,
        pv_x: str = "",
        pv_y: str = "",
        pv_yaw: str = "",
        pv_pitch: str = "",
        pv_lens1: str = "",
        pv_lens2: str = "",
        pv_lens3: str = "",
        pv_lens4: str = "",
        pv_lens5: str = "",
        pv_lens6: str = "",
        pv_lens7: str = "",
        pv_lens8: str = "",
        pv_lens9: str = "",
        pv_lens10: str = "",
        **kwargs,
    ):
        self._pv_x = pv_x
        self._pv_y = pv_y
        self._pv_pitch = pv_pitch
        self._pv_yaw = pv_yaw
        self._pv_lens0 = pv_lens1
        self._pv_lens2 = pv_lens2
        self._pv_lens3 = pv_lens3
        self._pv_lens4 = pv_lens4
        self._pv_lens5 = pv_lens5
        self._pv_lens6 = pv_lens6
        self._pv_lens7 = pv_lens7
        self._pv_lens8 = pv_lens8
        self._pv_lens9 = pv_lens9
        self._pv_lens10 = pv_lens10
        super().__init__(prefix, *args, **kwargs)
