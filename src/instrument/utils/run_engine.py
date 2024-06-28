"""Run Engine Specific file"""

import logging

import databroker
from bluesky import RunEngine as BlueskyRunEngine
from bluesky import suspenders
from bluesky.callbacks.best_effort import BestEffortCallback
from bluesky.utils import PersistentDict
from bluesky.utils import ProgressBarManager
from ophydregistry import Registry

from .config_utils import iconfig
from .exceptions import ComponentNotFound

log = logging.getLogger(__name__)

catalog = None  # TODO: Is the global symbol in this module used?


# def save_data(name, doc):  # Not needed with changes below.
#     """save data for databroker"""
#     global catalog
#     if catalog is None:
#         catalog = databroker.catalog["8idi_xpcs"]
#     # Save the document
#     catalog.v1.insert(name, doc)


def run_engine(
	cat=None,
	bec=None,
	preprocessors=None,
	md_path=None,
) -> BlueskyRunEngine:
    """Factory function that creates a Bluesky RunEngine."""
    global catalog  # TODO: Is the global symbol in this module used?

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
	catalog = cat  # TODO: Is the global symbol in this module used?
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


# -----------------------------------------------------------------------------
# :author:    Mark Wolfman
# :email:     wolfman@anl.gov
# :copyright: Copyright © 2023, UChicago Argonne, LLC
#
# Distributed under the terms of the 3-Clause BSD License
#
# The full license is in the file LICENSE, distributed with this software.
#
# DISCLAIMER
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
# -----------------------------------------------------------------------------
