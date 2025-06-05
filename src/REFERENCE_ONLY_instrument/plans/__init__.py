"""
Custom Plan Definitions & Instatiations
"""

from .qnw_plans import find_qnw_index, te, temp_ramp, te_env, temp_ramp_env
# from .qnw_vac_plans import set_qnw_vac

from .select_sample_env import select_sample_env
from .sample_info_unpack import select_sample, sort_qnw, gen_folder_prefix
from .select_detector import select_detector

from .util_8idi import get_machine_name, temp2str

from .nexus_acq_eiger_int import setup_eiger_int_series
from .nexus_acq_eiger_int import eiger_acq_int_series

from .nexus_acq_eiger_ext import setup_eiger_ext_trig
from .nexus_acq_eiger_ext import eiger_acq_ext_trig
from .nexus_acq_eiger_ext import setup_softglue_ext_trig
from .nexus_acq_eiger_ext import softglue_start_pulses
from .nexus_acq_eiger_ext import softglue_stop_pulses

# from .nexus_acq_rigaku_zdt import setup_rigaku_ZDT_series
# from .nexus_acq_rigaku_zdt import rigaku_acq_ZDT_series

from .nexus_acq_rigaku_zdt_robust_test import setup_rigaku_ZDT_series
from .nexus_acq_rigaku_zdt_robust_test import rigaku_acq_ZDT_series

from .nexus_acq_rigaku_zdt_fly import setup_rigaku_ZDT_fly
from .nexus_acq_rigaku_zdt_fly import rigaku_acq_ZDT_fly

# from .eiger_movie_mode import setup_eiger_tv_mode

from .shutter_logic import pre_align
from .shutter_logic import post_align
from .shutter_logic import showbeam
from .shutter_logic import blockbeam
from .shutter_logic import shutteron
from .shutter_logic import shutteroff

from .scan_8idi import x_lup
from .scan_8idi import y_lup
from .scan_8idi import rheo_x_lup, rheo_y_lup, rheo_set_x_lup
from .scan_8idi import att

from .rheometer_wait import wait_for_mcr
from .move_sample import mesh_grid_move

from .spec_8IDE_eiger4M import submit_Nexus_DM

from .dm_util import dm_setup, dm_run_job
