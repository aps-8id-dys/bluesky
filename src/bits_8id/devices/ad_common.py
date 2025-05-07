"""
EPICS area_detector common support
"""

__all__ = """
    BasicCam_V34
    CamBase_V34
    FileBase_V34
    SimDetectorCam_V34
    XpcsAD_EpicsFileNameHDF5Plugin
    XpcsAD_factory
    XpcsAD_ImagePlugin
    XpcsAD_OverlayPlugin
    XpcsAD_PluginMixin
    XpcsAD_PvaPlugin
    XpcsAD_ROIPlugin
    XpcsAD_StatsPlugin
    XpcsAD_TransformPlugin
""".split()

import logging
import time
from pathlib import PurePath

from apstools.devices import AD_EpicsFileNameHDF5Plugin
from apstools.devices import AD_plugin_primed
from apstools.devices import AD_prime_plugin2
from apstools.devices import CamMixin_V34
from ophyd import ADComponent
from ophyd import EpicsSignal
from ophyd import EpicsSignalRO
from ophyd import EpicsSignalWithRBV
from ophyd.areadetector import CamBase
from ophyd.areadetector import DetectorBase
from ophyd.areadetector import EigerDetectorCam
from ophyd.areadetector import SimDetectorCam
from ophyd.areadetector import SingleTrigger
from ophyd.areadetector.plugins import CodecPlugin_V34
from ophyd.areadetector.plugins import FileBase
from ophyd.areadetector.plugins import ImagePlugin_V34
from ophyd.areadetector.plugins import OverlayPlugin_V34
from ophyd.areadetector.plugins import PluginBase_V34
from ophyd.areadetector.plugins import ProcessPlugin_V34
from ophyd.areadetector.plugins import PvaPlugin_V34
from ophyd.areadetector.plugins import ROIPlugin_V34
from ophyd.areadetector.plugins import StatsPlugin_V34
from ophyd.areadetector.plugins import TransformPlugin_V34
from ophyd.ophydobj import Kind
from ophyd.status import Status

from ..utils.iconfig_loader import iconfig

logger = logging.getLogger(__name__)
logger.info(__file__)


BLUESKY_FILES_ROOT = PurePath(iconfig["AREA_DETECTOR"]["BLUESKY_FILES_ROOT"])
IMAGE_DIR = iconfig["AREA_DETECTOR"].get("IMAGE_DIR", "%Y/%m/%d/")


class CamBase_V34(CamBase):
    """
    Updates to CamBase since v22.

    PVs removed from AD now.
    """

    pool_max_buffers = None


class FileBase_V34(FileBase):
    """
    Updates to FileBase since v22.

    PVs removed from AD now.
    """

    file_number_sync = None
    file_number_write = None


class EigerDetectorCam_V34(CamMixin_V34, EigerDetectorCam):
    """Revise EigerDetectorCam for ADCore revisions."""

    initialize = ADComponent(EpicsSignal, "Initialize", kind="config")

    # These components not found on Eiger 4M at 8-ID-I
    file_number_sync = None
    file_number_write = None
    fw_clear = None
    link_0 = None
    link_1 = None
    link_2 = None
    link_3 = None
    dcu_buff_free = None
    offset = None


class BasicCam_V34(CamMixin_V34, CamBase_V34):
    """Basic camera support, such as the HHL Mirrors in 8-ID-A."""

    offset = None


class Lambda2MCam(CamBase_V34):
    """
    Support for the Lambda 2M cam controls.

    https://x-spectrum.de/products/lambda/
    """

    _html_docs = ["Lambda2MCam.html"]

    firmware_version = ADComponent(EpicsSignalRO, "FirmwareVersion_RBV", kind="omitted")
    operating_mode = ADComponent(EpicsSignalWithRBV, "OperatingMode", kind="config")
    serial_number = ADComponent(EpicsSignalRO, "SerialNumber_RBV", kind="omitted")
    temperature = ADComponent(EpicsSignalWithRBV, "Temperature", kind="config")
    wait_for_plugins = ADComponent(
        EpicsSignal, "WaitForPlugins", string=True, kind="config"
    )

    energy_threshold = ADComponent(EpicsSignalWithRBV, "EnergyThreshold", kind="config")
    dual_mode = ADComponent(EpicsSignalWithRBV, "DualMode", string=True, kind="config")
    dual_threshold = ADComponent(EpicsSignalWithRBV, "DualThreshold", kind="config")

    EXT_TRIGGER = 0


class Rigaku3MCam(CamBase_V34):
    """Support for the RigakuSi3M camera controls."""

    _html_docs = ["Rigaku3MCam.html"]
    wait_for_plugins = ADComponent(
        EpicsSignal, "WaitForPlugins", string=True, kind="config"
    )

    # sparse_enable = ADComponent(EpicsSignal, "SparseEnable", string=True)
    fast_file_name = ADComponent(EpicsSignalWithRBV, "FileName", string=True)
    fast_file_path = ADComponent(EpicsSignalWithRBV, "FilePath", string=True)
    image_mode = ADComponent(EpicsSignalWithRBV, "ImageMode", string=True)
    output_resolution = ADComponent(EpicsSignalWithRBV, "OutputResolution", string=True)
    dual_threshold = ADComponent(EpicsSignal, "DualThreshold")
    upper_threshold = ADComponent(EpicsSignalWithRBV, "UpperThreshold")
    lower_threshold = ADComponent(EpicsSignalWithRBV, "LowerThreshold")

    output_control = ADComponent(EpicsSignalWithRBV, "OutputControl", string=True)
    trigger_edge = ADComponent(EpicsSignalWithRBV, "TriggerEdge", string=True)
    # trigger_mode replaces same (SignalWithRBV) in CamBase
    trigger_mode = ADComponent(EpicsSignalWithRBV, "TriggerMode", string=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # kind attribute must be set after Components are initialized
        attrs = """
            dual_threshold
            fast_file_name
            fast_file_path
            image_mode
            lower_threshold
            output_control
            output_resolution
            trigger_edge
            trigger_mode
            upper_threshold
        """.split()
        for attr in attrs:
            getattr(self, attr).kind = "config"


class SimDetectorCam_V34(CamMixin_V34, SimDetectorCam):
    """Revise SimDetectorCam for ADCore revisions."""


class XpcsAD_PluginMixin(PluginBase_V34):
    """Remove property attribute found in AD IOCs now."""

    _asyn_pipeline_configuration_names = None


class XpcsAD_EpicsFileNameHDF5Plugin(XpcsAD_PluginMixin, AD_EpicsFileNameHDF5Plugin):
    """Remove property attribute not found in AD IOCs now."""

    @property
    def _plugin_enabled(self):
        return self.stage_sigs.get("enable") in (1, "Enable")

    def generate_datum(self, *args, **kwargs):
        if self._plugin_enabled:
            super().generate_datum(*args, **kwargs)

    def read(self):
        if self._plugin_enabled:
            readings = super().read()
        else:
            readings = {}
        return readings

    def stage(self):
        if self._plugin_enabled:
            staged_objects = super().stage()
        else:
            staged_objects = []
        return staged_objects

    def trigger(self):
        if self._plugin_enabled:
            trigger_status = super().trigger()
        else:
            trigger_status = Status(self)
            trigger_status.set_finished()
        return trigger_status


class XpcsAD_ImagePlugin(XpcsAD_PluginMixin, ImagePlugin_V34):
    """Remove property attribute found in AD IOCs now."""


class XpcsAD_OverlayPlugin(XpcsAD_PluginMixin, OverlayPlugin_V34):
    """Remove property attribute found in AD IOCs now."""


class XpcsAD_ProcessPlugin(XpcsAD_PluginMixin, ProcessPlugin_V34):
    """Remove property attribute found in AD IOCs now."""


class XpcsAD_PvaPlugin(XpcsAD_PluginMixin, PvaPlugin_V34):
    """Remove property attribute found in AD IOCs now."""


class XpcsAD_ROIPlugin(XpcsAD_PluginMixin, ROIPlugin_V34):
    """Remove property attribute found in AD IOCs now."""


class XpcsAD_StatsPlugin(XpcsAD_PluginMixin, StatsPlugin_V34):
    """Remove property attribute found in AD IOCs now."""


class XpcsAD_TransformPlugin(XpcsAD_PluginMixin, TransformPlugin_V34):
    """Remove property attribute found in AD IOCs now."""


def XpcsAreaDetectorFactory(det_key, **kwargs):
    """Simpler than XpcsAD_factory().  Use detector key from iconfig."""
    ad_conf = iconfig["AREA_DETECTOR"][det_key]
    IOC_FILES_ROOT = PurePath(ad_conf["IOC_FILES_ROOT"])

    WRITE_PATH_TEMPLATE = f"{IOC_FILES_ROOT / IMAGE_DIR}/"
    READ_PATH_TEMPLATE = f"{BLUESKY_FILES_ROOT / IMAGE_DIR}/"

    cam_class = {
        "ADSIM_4M": SimDetectorCam_V34,
        "ADSIM_16M": SimDetectorCam_V34,
        "FLAG1": BasicCam_V34,
        "FLAG2": BasicCam_V34,
        "FLAG3": BasicCam_V34,
        "FLAG4": BasicCam_V34,
    }[det_key]

    return XpcsAD_factory(
        ad_conf["PV_PREFIX"],
        ad_conf["NAME"],
        cam_class,
        WRITE_PATH_TEMPLATE,
        READ_PATH_TEMPLATE,
        labels=("area_detector",),
        **kwargs,
    )


def XpcsAD_factory(
    prefix,
    name,
    cam_class,
    write_path,
    read_path,
    labels=("area_detector",),
    use_image=True,
    use_overlay=True,
    use_process=True,
    use_pva=True,
    use_roi=True,
    use_stats=True,
    use_transform=True,
    **kwargs,
):
    """
    Create XPCS area detector with standard configuration.

    Returns a detector object or ``None`` if the detector does not connect.

    PARAMETERS

    prefix *str* :
        EPICS IOC prefix for the area detector.
    name *str* :
        Name of the Python detector object to be created.
    cam_class *object* :
        Custom subclass of CamBase_V34 for this detector.
    write_path *str* :
        Directory root for image files *as seen by the IOC.*
        MUST end with a "/".
    read_path *str* :
        Directory root for image files *as seen by the bluesky databroker.*
        MUST end with a "/".
    labels *object* :
        List or tuple of text labels for this detector.  Used by ``%wa``.
    kwargs :
        Anything else the caller wants to add, as ``keyword=value`` pairs.
    """

    class AreaDetector(SingleTrigger, DetectorBase):
        cam = ADComponent(cam_class, "cam1:")
        # In the AD IOC, cam --> codec & image
        codec1 = ADComponent(CodecPlugin_V34, "Codec1:")  # needed by PVA and HDF
        if use_image:
            image = ADComponent(XpcsAD_ImagePlugin, "image1:")

        # In the AD IOC, codec1 --> hdf1 & pva
        hdf1 = ADComponent(
            XpcsAD_EpicsFileNameHDF5Plugin,
            "HDF1:",
            write_path_template=f"{PurePath(write_path)}/",
            read_path_template=f"{PurePath(read_path)}/",
            kind="normal",
        )
        if use_pva:
            pva = ADComponent(XpcsAD_PvaPlugin, "Pva1:")

        # If AD IOC sends codec1 to roi (& roi1?)
        if use_process:
            proc1 = ADComponent(XpcsAD_ProcessPlugin, "Proc1:")
        if use_overlay:
            over1 = ADComponent(XpcsAD_OverlayPlugin, "Over1:")
        if use_roi:
            roi1 = ADComponent(XpcsAD_ROIPlugin, "ROI1:")
        if use_stats:
            stats1 = ADComponent(XpcsAD_StatsPlugin, "Stats1:")
        if use_transform:
            trans1 = ADComponent(XpcsAD_TransformPlugin, "Trans1:")

    # tricky: Make it look as if we defined a custom class for this detector.
    # Use the cam class name.
    title = cam_class.__name__.rstrip("_V34").rstrip("Cam")
    AreaDetector.__name__ = f"XpcsAD_{title}"
    AreaDetector.__qualname__ = AreaDetector.__name__

    # ADSimDetector does not subclass from CamBase_V34
    # TODO: Find different way to validate.
    # if not issubclass(cam_class, CamBase_V34):
    #     raise TypeError(f"{cam_class} must be a subclass of  {CamBase_V34.__name__}")

    t0 = time.time()
    try:
        connection_timeout = iconfig.get("PV_CONNECTION_TIMEOUT", 15)
        det = AreaDetector(prefix, name=name, labels=labels, **kwargs)
        det.wait_for_connection(timeout=connection_timeout)
    except (KeyError, NameError, TimeoutError) as exinfo:
        # fmt: off
        logger.warning(
            "Error connecting with PV='%s in %.2fs, %s",
            prefix, time.time() - t0, str(exinfo),
        )
        logger.warning("Setting '%s' to 'None'.", name)
        det = None
        # fmt: on

    else:
        # just in case these things are not defined in the class source code
        det.cam.stage_sigs["wait_for_plugins"] = "Yes"
        for nm in det.component_names:
            obj = getattr(det, nm)
            if "blocking_callbacks" in dir(obj):  # is it a plugin?
                obj.stage_sigs["blocking_callbacks"] = "No"

        plugin = det.hdf1  # for convenience below
        plugin.kind = Kind.config | Kind.normal  # Ensure plugin's read is called.
        plugin.stage_sigs.move_to_end("capture", last=True)

        if iconfig.get("ALLOW_AREA_DETECTOR_WARMUP", False):
            if det.connected:
                if not AD_plugin_primed(plugin):
                    AD_prime_plugin2(plugin)

    return det
