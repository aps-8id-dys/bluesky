"""
configure the Bluesky framework
"""


def warn_if_not_aps_controls_subnet():
    """APS-U controls are on private subnets.  Check and advise as applicable."""

    import socket
    import warnings

    xray_subnet = ".xray.aps.anl.gov"
    controls_subnet = "10.54."

    host_name = socket.gethostname()
    if host_name.endswith(xray_subnet):
        host_ip_addr = socket.gethostbyname(host_name)
        if not host_ip_addr.startswith(controls_subnet):
            warnings.warn(
                f"Your APS workstation ({host_name}) has IP {host_ip_addr!r}."
                "  If you experience EPICS connection timeouts,"
                " consider switching to a workstation on the controls subnet"
                f" which has an IP starting with {controls_subnet!r}"
            )


warn_if_not_aps_controls_subnet()

# fmt: off

from aps_8id_bs_instrument.framework.check_bluesky import *
from aps_8id_bs_instrument.framework.check_python import *
from aps_8id_bs_instrument.framework.dm_setup import *
from aps_8id_bs_instrument.framework.initialize import *
from aps_8id_bs_instrument.framework.metadata import *
