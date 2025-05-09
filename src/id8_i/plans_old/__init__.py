"""
Custom Plan Definitions & Instatiations
"""

from ..plans.move_sample import mesh_grid_move
from ..plans.nexus_acq_eiger_ext import eiger_acq_ext_trig
from ..plans.nexus_acq_eiger_ext import setup_eiger_ext_trig
from ..plans.nexus_acq_eiger_ext import setup_softglue_ext_trig
from ..plans.nexus_acq_eiger_ext import softglue_start_pulses
from ..plans.nexus_acq_eiger_ext import softglue_stop_pulses
from ..plans.nexus_acq_eiger_int import eiger_acq_int_series
from ..plans.nexus_acq_eiger_int import setup_eiger_int_series
from ..plans.nexus_acq_rigaku_zdt import rigaku_acq_ZDT_series
from ..plans.nexus_acq_rigaku_zdt import setup_rigaku_ZDT_series
from ..plans.nexus_acq_rigaku_zdt_fly import rigaku_acq_ZDT_fly
from ..plans.nexus_acq_rigaku_zdt_fly import setup_rigaku_ZDT_fly
from ..plans.qnw_plans import find_qnw_index
from ..plans.qnw_plans import te
from ..plans.qnw_plans import te_env
from ..plans.qnw_plans import temp_ramp
from ..plans.qnw_plans import temp_ramp_env
from ..plans.rheometer_wait import wait_for_mcr
from ..plans.sample_info_unpack import gen_folder_prefix
from ..plans.sample_info_unpack import select_sample
from ..plans.sample_info_unpack import sort_qnw
from ..plans.select_detector import select_detector

# from .qnw_vac_plans import set_qnw_vac
from ..plans.select_sample_env import select_sample_env
from ..plans.shutter_logic import blockbeam
from ..plans.shutter_logic import post_align

# from .eiger_movie_mode import setup_eiger_tv_mode
from ..plans.shutter_logic import pre_align
from ..plans.shutter_logic import showbeam
from ..plans.shutter_logic import shutteroff
from ..plans.shutter_logic import shutteron
from ..plans.spec_8IDE_eiger4M import submit_Nexus_DM
from .dm_util import dm_run_job
from .dm_util import dm_setup
from .scan_8idi import att
from .scan_8idi import rheo_set_x_lup
from .scan_8idi import rheo_x_lup
from .scan_8idi import rheo_y_lup
from .scan_8idi import x_lup
from .scan_8idi import y_lup
from .util_8idi import get_machine_name
from .util_8idi import temp2str
