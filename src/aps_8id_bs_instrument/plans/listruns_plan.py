from __future__ import annotations

import logging

from bluesky import plan_stubs as bps

logger = logging.getLogger(__name__)
logger.info(__file__)


def listruns(num=5):
    from apstools.utils import listruns

    print(listruns(num=num))
    yield from bps.null()
