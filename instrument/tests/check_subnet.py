"""Test to see if you're on APS Subnet"""

import socket
import warnings


def warn_if_not_aps_controls_subnet():
    """APS-U controls are on private subnets.  Check and advise as applicable."""

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
                f" which has an IP starting with {controls_subnet!r}",
                stacklevel=2,
            )
