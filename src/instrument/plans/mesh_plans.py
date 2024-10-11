"""
XPCS plans for scanning over a mesh.

.. automodule::
    ~mesh_list_grid_scan
    ~xpcs_mesh
"""

import logging

import apstools.plans
import numpy as np
from bluesky import plan_stubs as bps
from toolz import partition

logger = logging.getLogger(__name__)
logger.info(__file__)

from ..initialize_bs_tools import oregistry  # noqa: E402


def mesh_list_grid_scan(
    detectors,
    *args,
    number_of_collection_points,
    snake_axes=False,
    per_step=None,
    md=None,
):
    """
    Scan over a multi-dimensional mesh.

    Collect a total of $n$ points; each motor is on an independent trajectory.

    Here, the motors are specified as motor **names** (to match the queueserver
    interface). With the names, the ophyd registry is searched for the actual
    motor object.

    Calls: ``apstools.plans.xpcs_mesh.mesh_list_grid_scan()``.  See that plan
    for a detailed description of its arguments.
    """
    # Translate the motor names into motor objects.
    axes_parameters = []
    for motor_name, pos_list in partition(2, args):
        if isinstance(motor_name, str):
            motor_object = oregistry.find(motor_name)
        else:
            # Assume caller provided actual motor object.
            motor_object = motor_name
        axes_parameters += [motor_object, pos_list]

    # Use same-named plan from apstools.
    uid = yield from apstools.plans.mesh_list_grid_scan(
        detectors,
        *axes_parameters,
        number_of_collection_points,
        snake_axes=snake_axes,
        per_step=per_step,
        md=md,
    )
    return uid


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
    start, end, and number of points (s, e, n). These define a mesh of size (n1 x
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
        # fmt: off
        yield from bps.mv(
            area_det.cam.acquire_time, acquire_time,
            area_det.cam.acquire_period, acquire_period,
            area_det.cam.num_images, nframes,
        )
        # fmt: on
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
        md=md,
    )
