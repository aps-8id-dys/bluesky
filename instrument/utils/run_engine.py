"""Run Engine Specific file"""

import logging

import databroker
from bluesky import RunEngine as BlueskyRunEngine
from bluesky import suspenders
from bluesky.utils import PersistentDict
from bluesky.utils import ProgressBarManager
from ophydregistry import ComponentNotFound
from ophydregistry import Registry

from .iconfig_loader import iconfig

log = logging.getLogger(__name__)


def run_engine(
    cat=None,
    bec=None,
    preprocessors=None,
    md_path=None,
) -> BlueskyRunEngine:
    """Factory function that creates a Bluesky RunEngine."""

    RE = BlueskyRunEngine()
    # Add the best-effort callback
    if bec is not None:
        RE.subscribe(bec)

    # Install suspenders
    try:
        # TODO: PEP8 naming convention.
        #   Lower-case 'aps' has been the common name.
        aps = Registry().find("APS")
    except ComponentNotFound:
        log.warning("APS device not found, suspenders not installed.")
    else:
        # Suspend when shutter permit is disabled
        RE.install_suspender(
            suspenders.SuspendWhenChanged(
                signal=aps.shutter_permit,
                expected_value="PERMIT",
                allow_resume=True,
                sleep=3,
                tripped_message="Shutter permit revoked.",
            )
        )
    # Install databroker connection
    if cat is None:
        cat = databroker.temp().v2
    RE.subscribe(cat.v1.insert)

    # Add preprocessors
    if preprocessors is not None:
        RE.preprocessors.append(preprocessors)

    # Save/restore RE.md dictionary
    if md_path is not None:
        RE.preprocessors.append(preprocessors)
        RE.md = PersistentDict(md_path)

    if iconfig.get("USE_PROGRESS_BAR", False):
        # Add a progress bar.
        pbar_manager = ProgressBarManager()
        RE.waiting_hook = pbar_manager

    return RE
