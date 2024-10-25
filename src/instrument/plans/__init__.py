"""
Custom Plan Definitions & Instatiations
"""

# flake8: noqa

# sanity check plans
from .demo_hello_world import hello_world
from .demo_sim_1d import demo_sim_1d

# beamline specific plans
from .bdp_demo import mc_test
from .bdp_demo import xpcs_bdp_demo_plan
from .bdp_demo import xpcs_reset_index
from .bdp_demo import xpcs_setup_user
# from .independent import kickoff_dm_workflow
# from .independent import setup_detector
from .independent_test import kickoff_dm_workflow, setup_det_ext_trig, setup_det_ext_trig, setup_softglue_ext_trig
from .independent import simple_acquire
from .mesh_plans import xpcs_mesh

# from .select_sample_env import select_sample_env
from .select_sample import select_sample, open_shutter, close_shutter
from .qnw_plans import set_qnw
