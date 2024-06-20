"""
APS BDP demo: 2024-02
"""

# from apstools.plans.xpcs_mesh import mesh_list_grid_scan

import logging

from user.xpcs_mesh import mesh_list_grid_scan

logger = logging.getLogger(__name__)
logger.info(__file__)

import numpy as np
from bluesky import plan_stubs as bps

from aps_8id_bs_instrument.framework import oregistry


def xpcs_mesh(
    area_det_name="eiger4M",
    detectors=None,
    m1="sample.x",
    s1=0,
    e1=1,
    n1=3,
    m2="sample.y",
    s2=0,
    e2=2,
    n2=5,
    number_of_collection_points=20,
    snake_axes=False,
    acquire_time=0.001,
    acquire_period=0.001,
    nframes=1_000,
    # header_index="A001",
    md=None,
):
    # TODO: called for alignment or XPCS data collection
    # Area detector is configured different for each of these.

    if detectors is None:
        detectors = []
    m1_positions = np.linspace(s1, e1, n1).tolist()
    m2_positions = np.linspace(s2, e2, n2).tolist()

    area_det = oregistry.find(area_det_name)
    if area_det in detectors:
        yield from bps.mv(
            area_det.cam.acquire_time,
            acquire_time,
            area_det.cam.acquire_period,
            acquire_period,
            area_det.cam.num_images,
            nframes,
        )
        # TODO: add user control of detector trigger_mode
        # Includes configuration of soft glue as needed.
        # Probably will need more user keywords for this.

    yield from mesh_list_grid_scan(
        [area_det] + detectors,
        m1,
        m1_positions,
        m2,
        m2_positions,
        number_of_collection_points=number_of_collection_points,
        snake_axes=snake_axes,
        md=None,
    )
