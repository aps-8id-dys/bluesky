from bluesky import plan_stubs as bps
import logging

logger = logging.getLogger(__name__)
logger.info(__file__)


def listruns(num=5):
    from apstools.utils import listruns
    print(listruns(num=num))
    yield from bps.null()
