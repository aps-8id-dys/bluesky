
import warnings

import numpy as np
import h5py 

from ..devices.registers_device import pv_registers
from ..devices.filters_8id import filter_8ide, filter_8idi
from ..devices.ad_eiger_4M import eiger4M
from ..devices.aerotech_stages import sample, detector
from ..devices.softglue import softglue_8idi
from ..devices.slit import sl4
from ..devices.qnw_device import qnw_env1, qnw_env2, qnw_env3


def create_run_metadata_dict(det=eiger4M):
    md = {}

    #TODO use real numbers from EPICS for these fields
    md["energy"] = 10.0  # keV, 
    md["absolute_cross_section_scale"] = 1
    md["beam_center_x"] = 1044  # 
    md["beam_center_y"] = 1416
    md["detector_x_direct_beam"] = 1  # This will need to be read from the Reg. It's the position in select_detector()
    md["detector_y_direct_beam"] = 1 
    md["det_dist"] = 12.5
    md["I0"] = 1
    md["I1"] = 1
    md["pix_dim_x"] = 75e-6
    md["pix_dim_y"] = 75e-6
    md["incident_beam_size_nm_xy"] = 10_000
    md["incident_energy_spread"] = 1
    md["xdim"] = 1  # What is this?
    md["ydim"] = 1  # What is this?

    # Information that is hard-coded
    md['beamline_id'] = '8-ID'

    # Are these necessary?
    md['concise'] = 1
    md['conda_prefix'] = 'bluesky_2024_3'
    md['data_management'] = 'DM'  # What is this?
    md['databroker_catalog'] = 1  # What is this?

    # Information that is read from EPICS
    md['cycle'] = pv_registers.cycle_name.get()
    md["detector_x"] = detector.x.position
    md["detector_y"] = detector.y.position
    md["count_time"] = det.cam.acquire_time.get()
    md["frame_time"] = det.cam.acquire_period.get()
    md["nexus_fullname"] = pv_registers.metadata_full_path.get()
    md["file_name"] = pv_registers.file_name.get()
    md["file_path"] = pv_registers.file_path.get()
    md["sample_x"] = sample.x.position
    md["sample_y"] = sample.y.position
    md["sample_z"] = sample.z.position
    md["qnw1_temp"] = qnw_env1.readback.get()
    md["qnw2_temp"] = qnw_env2.readback.get()
    md["qnw3_temp"] = qnw_env3.readback.get()
    return md

def write_nexus_file(md):

    with h5py.File(md['nexus_fullname'], 'w') as hf:

        nxentry = hf.create_group("entry")
        nxentry.attrs["NX_Class"] = "NXentry"

        nxinstrument = nxentry.create_group("instrument")
        nxinstrument.attrs["NX_Class"]="NXinstrument"
        
        nxbluesky = nxinstrument.create_group("bluesky")
        nxbluesky.attrs["NX_Class"] = "NXnote"
        
        nxmetadata = nxbluesky.create_group("metadata")
        nxmetadata.attrs["NX_Class"] = "NXnote"
        
        nxdetector = nxinstrument.create_group("detector")
        nxdetector.attrs["NX_Class"] = "NXdetector"

        # hf["/entry/instrument/attenunator"].attrs["NX_class"] = "NXattenuator"
        # hf["/entry/instrument/beam"].attrs["NX_class"] = "NXbeam"
        # hf["/entry/instrument/beamstop"].attrs["NX_class"] = "NXbeam_stop"

        # hf["/entry/instrument/qnw1"].attrs["NX_class"] = "NXenvironment"
        # hf["/entry/instrument/qnw2"].attrs["NX_class"] = "NXenvironment"
        # hf["/entry/instrument/qnw3"].attrs["NX_class"] = "NXenvironment"
        # # hf["/entry/instrument/insertion_device"].attrs["NX_class"] = "NXinsertion_device"
        # # hf["/entry/instrument/mirror"].attrs["NX_class"] = "NXmirror"
        # hf["/entry/instrument/incoming_IC"].attrs["NX_class"] = "NXmonitor"
        # hf["/entry/instrument/outgoing_IC"].attrs["NX_class"] = "NXmonitor"
        # hf["/entry/instrument/monochromator"].attrs["NX_class"] = "NXmonochromator"
        # hf["/entry/instrument/sample_x"].attrs["NX_class"] = "NXpositioner"
        # hf["/entry/instrument/sample_y"].attrs["NX_class"] = "NXpositioner"
        # hf["/entry/instrument/sample_z"].attrs["NX_class"] = "NXpositioner"
        # hf["/entry/instrument/detector_x"].attrs["NX_class"] = "NXpositioner"
        # hf["/entry/instrument/detector_y"].attrs["NX_class"] = "NXpositioner"


        # All undefined variables go into bluesky metadata
        hf.create_dataset('/entry/instrument/bluesky/metadata/absolute_cross_section_scale', 
                          data=md["absolute_cross_section_scale"])
        hf.create_dataset('/entry/instrument/bluesky/metadata/detector_x_direct_beam', 
                          data=md['detector_x_direct_beam'])
        hf.create_dataset('/entry/instrument/bluesky/metadata/detector_y_direct_beam', 
                          data=md['detector_y_direct_beam'])    
        hf.create_dataset('/entry/instrument/bluesky/metadata/beamline_id', 
                          data=md['beamline_id'])
        hf.create_dataset('/entry/instrument/bluesky/metadata/concise', data=md['concise'])
        hf.create_dataset('/entry/instrument/bluesky/metadata/conda_prefix', data=md['conda_prefix'])
        hf.create_dataset('/entry/instrument/bluesky/metadata/cycle', data=md['cycle'])
        hf.create_dataset('/entry/instrument/bluesky/metadata/data_management', data=md['data_management'])
        hf.create_dataset('/entry/instrument/bluesky/metadata/databroker_catalog', data=md['databroker_catalog'])

        # # Mono, NXmonochromator
        # hf.create_dataset('/entry/instrument/monochromator/energy', data=md['energy'])

        # # Ion chambers, NXmonitor
        # hf.create_dataset('/entry/instrument/incoming_IC/nominal', data=md['I0'])
        # hf.create_dataset('/entry/instrument/outgoing_IC/nominal', data=md['I1'])  

        # # Motors, NXpositioner
        # hf.create_dataset('/entry/instrument/sample_x/position', data=md['sample_x'])
        # hf.create_dataset('/entry/instrument/sample_y/position', data=md['sample_y'])
        # hf.create_dataset('/entry/instrument/sample_z/position', data=md['sample_z'])
        # hf.create_dataset('/entry/instrument/detector_x/position', data=md['detector_x'])
        # hf.create_dataset('/entry/instrument/detector_y/position', data=md['detector_x'])

        # # Temperature control, NXenvironment
        # hf.create_dataset('/entry/instrument/qnw1/readback_temp', data=md['qnw1_temp'])
        # hf.create_dataset('/entry/instrument/qnw2/readback_temp', data=md['qnw2_temp'])
        # hf.create_dataset('/entry/instrument/qnw3/readback_temp', data=md['qnw3_temp'])     

        # Detector (just Eiger for now), NXdetector
        hf.create_dataset('/entry/instrument/detector/count_time', data=md['count_time'])
        hf.create_dataset('/entry/instrument/detector/frame_time', data=md['frame_time'])
        hf.create_dataset('/entry/instrument/detector/beam_center_x', data=md['beam_center_x'])
        hf.create_dataset('/entry/instrument/detector/beam_center_y', data=md['beam_center_y'])
        hf.create_dataset('/entry/instrument/detector/detector_x_direct_beam', data=md['detector_x_direct_beam'])
        hf.create_dataset('/entry/instrument/detector/detector_y_direct_beam', data=md['detector_y_direct_beam'])


        # hf["/entry/instrument/sample"].attrs["NX_class"] = "NXsample"
        # hf["/entry/instrument/slits"].attrs["NX_class"] = "NXslit"
        # hf["/entry/instrument/xraylens"].attrs["NX_class"] = "NXxraylens"


# /entry/instrument/bluesky/metadata/datetime Dataset {SCALAR}
# /entry/instrument/bluesky/metadata/description Dataset {SCALAR}
# /entry/instrument/bluesky/metadata/det_dist Dataset {SCALAR}
# /entry/instrument/bluesky/metadata/detector_name Dataset {SCALAR}
# /entry/instrument/bluesky/metadata/detectors Dataset {SCALAR}
# /entry/instrument/bluesky/metadata/header Dataset {SCALAR}
# /entry/instrument/bluesky/metadata/hints Dataset {SCALAR}
# /entry/instrument/bluesky/metadata/iconfig Dataset {SCALAR}
# /entry/instrument/bluesky/metadata/incident_beam_size_nm_xy Dataset {SCALAR}
# /entry/instrument/bluesky/metadata/incident_energy_spread Dataset {SCALAR}
# /entry/instrument/bluesky/metadata/index Dataset {SCALAR}
# /entry/instrument/bluesky/metadata/instrument_name Dataset {SCALAR}
# /entry/instrument/bluesky/metadata/login_id Dataset {SCALAR}
# /entry/instrument/bluesky/metadata/metadatafile Dataset {SCALAR}
# /entry/instrument/bluesky/metadata/num_capture Dataset {SCALAR}
# /entry/instrument/bluesky/metadata/num_exposures Dataset {SCALAR}
# /entry/instrument/bluesky/metadata/num_images Dataset {SCALAR}
# /entry/instrument/bluesky/metadata/num_intervals Dataset {SCALAR}
# /entry/instrument/bluesky/metadata/num_points Dataset {SCALAR}
# /entry/instrument/bluesky/metadata/num_triggers Dataset {SCALAR}
# /entry/instrument/bluesky/metadata/owner Dataset {SCALAR}
# /entry/instrument/bluesky/metadata/pid Dataset {SCALAR}
# /entry/instrument/bluesky/metadata/pix_dim_x Dataset {SCALAR}
# /entry/instrument/bluesky/metadata/pix_dim_y Dataset {SCALAR}
# /entry/instrument/bluesky/metadata/plan_args Dataset {SCALAR}
# /entry/instrument/bluesky/metadata/plan_name Dataset {SCALAR}
# /entry/instrument/bluesky/metadata/plan_type Dataset {SCALAR}
# /entry/instrument/bluesky/metadata/proposal_id Dataset {SCALAR}
# /entry/instrument/bluesky/metadata/qmap_file Dataset {SCALAR}
# /entry/instrument/bluesky/metadata/run_start_uid Dataset, same as /entry/entry_identifier
# /entry/instrument/bluesky/metadata/safe_title Dataset {SCALAR}
# /entry/instrument/bluesky/metadata/title Dataset {SCALAR}
# /entry/instrument/bluesky/metadata/versions Dataset {SCALAR}
# /entry/instrument/bluesky/metadata/workflow Dataset {SCALAR}
# /entry/instrument/bluesky/metadata/xdim Dataset {SCALAR}
# /entry/instrument/bluesky/metadata/xpcs_header Dataset {SCALAR}
# /entry/instrument/bluesky/metadata/xpcs_index Dataset {SCALAR}
# /entry/instrument/bluesky/metadata/ydim Dataset {SCALAR}