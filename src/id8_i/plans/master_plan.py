from apsbits.core.instrument_init import oregistry
from bluesky import plan_stubs as bps
from bluesky import plans as bp
from pathlib import Path
import json
import re

from id8_i.plans.nexus_acq_eiger_int_test import eiger_acq_int_series 
from id8_i.plans.sample_info_unpack import select_sample
from id8_i.plans.scan_8idi import att
from id8_i.plans.select_detector import select_detector

def run_measurement_info(file_name='measurement_info.json'):
    file_path = '/home/beams10/8IDIUSER/bluesky/src/user_plans/'

    try:
        with open(file_path+file_name, 'r') as f:
            measurement_info = json.load(f)

        for block_key, block_value in measurement_info.items():

            match = re.search(r'_(\d+)', block_key)
            sam_index = int(match.group(1))
            det_name = block_value.get("detector")
            att_list = block_value.get("att_list")
            acq_time_list = block_value.get("acq_time_list")
            acq_period_list = block_value.get("acq_period_list")
            num_frames_list = block_value.get("num_frames_list")
            num_reps_list = block_value.get("num_reps_list")
            fly_scan_yes_list = block_value.get("fly_scan_yes_list")

            print(f'\n --- Measurement Block {block_key} ---')

            print(f'Sample index: {sam_index}')
            yield from select_sample(sam_index)

            print(f'Detector name: {det_name}')
            # yield from select_detector(det_name)

            for ii in range(len(att_list)):

                print(f'\n At Attenuation Ratio {att_list[ii]}:\n')
                yield from att(att_list[ii])

                for jj in range(len(acq_time_list[ii])):

                    print(f'    Acquisition Time: {acq_time_list[ii][jj]}')
                    print(f'    Acquisition Period: {acq_period_list[ii][jj]}')
                    print(f'    Number of Frames: {num_frames_list[ii][jj]}')
                    print(f'    Number of Repeats: {num_reps_list[ii][jj]}')
                    print(f"    Fly Scan? {'Yes' if fly_scan_yes_list[ii][jj] == 1 else 'No'}\n")  

                    yield from  eiger_acq_int_series(
                                                        acq_time=acq_time_list[ii][jj],
                                                        num_frames=num_frames_list[ii][jj],
                                                        num_rep=num_reps_list[ii][jj],
                                                        wait_time=0,
                                                        process=True,
                                                        sample_move=True,
                                                    )
    except KeyboardInterrupt:
        raise RuntimeError("\n Bluesky plan stopped by user (Ctrl+C).")
    except Exception as e:
        print(f"Error occurred during measurement: {e}")
    finally:
        pass






