"""
APS BDP demo: 2024-02
"""

# from apstools.plans.xpcs_mesh import mesh_list_grid_scan

import logging

import numpy as np
from bluesky import plan_stubs as bps

from ..initialize_bs_tools import oregistry
from .xpcs_mesh_plans import mesh_list_grid_scan

logger = logging.getLogger(__name__)
logger.info(__file__)


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
    """
    Measure XPCS in repeated passes through a 2-D mesh.

    Mesh is defined by two positioner axes m1 & m2. Each axis has parameters for
    start, end, and number of steps (s, e, n). These define a mesh of size (n1 x
    n2).  The mesh is converted to a list of m1 & m2 positions to be measured in
    sequence.

    The actual number of data collections, number_of_collection_points, is not
    required to be equal to the number of mesh points.  The list of mesh
    coordinates wll be repeated as necessary to collect the required number of
    collection points.

    The sequence of mesh points will consider 'snake_axes', which reverses the
    sequence of 'm2' points on each increment of 'm1'.

    At each collection, the area detector will acquire 'nframes' with
    acquisition parameters 'acquire_time' & 'acquire_period'.
    """
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
