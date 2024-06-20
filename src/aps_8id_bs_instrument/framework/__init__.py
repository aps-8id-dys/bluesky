"""
configure the Bluesky framework
"""

from aps_8id_bs_instrument.framework.check_subnet import warn_if_not_aps_controls_subnet
from aps_8id_bs_instrument.framework.check_version import (
    check_databroker_version,
    check_ophyd_version,
    check_python_version,
)

check_python_version()
check_ophyd_version()
check_databroker_version()
warn_if_not_aps_controls_subnet()
