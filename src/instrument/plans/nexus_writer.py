import h5py

from ...id8_i.devices.qnw_device import qnw_env1
from ...id8_i.devices.qnw_device import qnw_env2
from ...id8_i.devices.qnw_device import qnw_env3
from ...id8_i.devices.registers_device import pv_registers
from ..devices.ad_eiger_4M import eiger4M
from ..devices.aerotech_stages import detector
from ..devices.aerotech_stages import sample


def create_run_metadata_dict(det=eiger4M):
    md = {}

    # TODO use real numbers from EPICS for these fields
    md["energy"] = 10.0  # keV,
    md["absolute_cross_section_scale"] = 1
    md["beam_center_x"] = 1044  #
    md["beam_center_y"] = 1416
    md["detector_x_direct_beam"] = (
        1  # This will need to be read from the Reg. It's the position in select_detector()
    )
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
    md["beamline_id"] = "8-ID"

    # Are these necessary?
    md["concise"] = 1
    md["conda_prefix"] = "bluesky_2024_3"
    md["data_management"] = "DM"  # What is this?
    md["databroker_catalog"] = 1  # What is this?

    # Information that is read from EPICS
    md["cycle"] = pv_registers.cycle_name.get()
    md["detector_x"] = detector.x.position
    md["detector_y"] = detector.y.position
    md["count_time"] = det.cam.acquire_time.get()
    md["frame_time"] = det.cam.acquire_period.get()
    md["sam_det_dist"] = 12000
    # md["nexus_fullname"] = pv_registers.metadata_full_path.get()
    md["nexus_fullname"] = (
        "/home/8-id-i/2025-1/bluesky_metadata_test/A001_001/A001_001.hdf"
    )
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
    with h5py.File(md["nexus_fullname"], "w") as hf:
        nxentry = hf.create_group("entry")
        nxentry.attrs["NX_Class"] = "NXentry"

        nxinstrument = nxentry.create_group("instrument")
        nxinstrument.attrs["NX_Class"] = "NXinstrument"

        nxdetector = nxinstrument.create_group("detector")
        nxdetector.attrs["NX_Class"] = "NXdetector"
        ds_count_time = nxdetector.create_dataset("count_time", data=md["count_time"])
        ds_count_time.attrs["units"] = "second"
        ds_frame_time = nxdetector.create_dataset("frame_time", data=md["count_time"])
        ds_frame_time.attrs["units"] = "second"
        ds_beam_center_x = nxdetector.create_dataset(
            "beam_center_x", data=md["count_time"]
        )
        ds_beam_center_x.attrs["units"] = "None"
        ds_beam_center_y = nxdetector.create_dataset(
            "beam_center_y", data=md["count_time"]
        )
        ds_beam_center_y.attrs["units"] = "None"
        ds_detector_x_direct_beam = nxdetector.create_dataset(
            "detector_x_direct_beam", data=md["count_time"]
        )
        ds_detector_x_direct_beam.attrs["units"] = "mm"
        ds_detector_y_direct_beam = nxdetector.create_dataset(
            "detector_y_direct_beam", data=md["count_time"]
        )
        ds_detector_y_direct_beam.attrs["units"] = "mm"
        ds_detector_distance = nxdetector.create_dataset(
            "distance", data=md["sam_det_dist"]
        )
        ds_detector_distance.attrs["units"] = "mm"

        nxmonochromator = nxinstrument.create_group("monochromator")
        nxmonochromator.attrs["NX_Class"] = "NXmonochromator"
        ds_energy = nxmonochromator.create_dataset("energy", data=md["energy"])
        ds_energy.attrs["units"] = "kev"

        nxsample_x = nxinstrument.create_group("sample_x")
        nxsample_x.attrs["NX_Class"] = "NXpositioner"

        nxsample_y = nxinstrument.create_group("sample_y")
        nxsample_y.attrs["NX_Class"] = "NXpositioner"

        nxsample_z = nxinstrument.create_group("sample_z")
        nxsample_z.attrs["NX_Class"] = "NXpositioner"

        nxdetector_x = nxinstrument.create_group("detector_x")
        nxdetector_x.attrs["NX_Class"] = "NXpositioner"
        ds_detx_position = nxdetector_x.create_dataset(
            "position", data=md["detector_x"]
        )
        ds_detx_position.attrs["units"] = "mm"

        nxdetector_y = nxinstrument.create_group("detector_y")
        nxdetector_y.attrs["NX_Class"] = "NXpositioner"
        ds_dety_position = nxdetector_y.create_dataset(
            "position", data=md["detector_y"]
        )
        ds_dety_position.attrs["units"] = "mm"

        nxqnw_1 = nxinstrument.create_group("qnw_1")
        nxqnw_1.attrs["NX_Class"] = "NXenvironment"

        nxqnw_2 = nxinstrument.create_group("qnw_2")
        nxqnw_2.attrs["NX_Class"] = "NXenvironment"

        nxqnw_3 = nxinstrument.create_group("qnw_3")
        nxqnw_3.attrs["NX_Class"] = "NXenvironment"

        nxupstream_IC = nxinstrument.create_group("upstream_IC")
        nxupstream_IC.attrs["NX_Class"] = "NXmonitor"

        nxdownstream_IC = nxinstrument.create_group("downstream_IC")
        nxdownstream_IC.attrs["NX_Class"] = "NXmonitor"

        nxattenunator_8idi = nxinstrument.create_group("attenunator_8idi")
        nxattenunator_8idi.attrs["NX_Class"] = "NXattenuator"

        nxattenunator_8ide = nxinstrument.create_group("attenunator_8ide")
        nxattenunator_8ide.attrs["NX_Class"] = "NXattenuator"

        nxbeam = nxinstrument.create_group("beam")
        nxbeam.attrs["NX_Class"] = "NXbeam"

        nxbeamstop = nxinstrument.create_group("beamstop")
        nxbeamstop.attrs["NX_Class"] = "NXbeam_stop"

        nxupstream_ID = nxinstrument.create_group("upstream_ID")
        nxupstream_ID.attrs["NX_Class"] = "NXinsertion_device"

        nxdownstream_ID = nxinstrument.create_group("downstream_ID")
        nxdownstream_ID.attrs["NX_Class"] = "NXinsertion_device"

        nxmirror_1 = nxinstrument.create_group("mirror_1")
        nxmirror_1.attrs["NX_Class"] = "NXmirror"

        nxmirror_2 = nxinstrument.create_group("mirror_2")
        nxmirror_2.attrs["NX_Class"] = "NXmirror"

        nxcrl_1 = nxinstrument.create_group("crl_1")
        nxcrl_1.attrs["NX_Class"] = "NXxraylens"

        nxcrl_2 = nxinstrument.create_group("crl_2")
        nxcrl_2.attrs["NX_Class"] = "NXxraylens"

        si5 = nxinstrument.create_group("si5")
        si5.attrs["NX_Class"] = "NXslit"

        qnw_sam1 = nxinstrument.create_group("qnw_sam1")
        qnw_sam1.attrs["NX_Class"] = "NXsample"

        # All undefined variables go into bluesky metadata
        nxbluesky = nxinstrument.create_group("bluesky")
        nxbluesky.attrs["NX_Class"] = "NXnote"

        nxmetadata = nxbluesky.create_group("metadata")
        nxmetadata.attrs["NX_Class"] = "NXnote"
        ds_absolute_cross_section_scale = nxmetadata.create_dataset(
            "absolute_cross_section_scale", data=md["absolute_cross_section_scale"]
        )
        ds_absolute_cross_section_scale.attrs["units"] = "cm-1"
        ds_detector_x_direct_beam = nxmetadata.create_dataset(
            "detector_x_direct_beam", data=md["detector_x_direct_beam"]
        )
        ds_detector_x_direct_beam.attrs["units"] = "None"
        ds_detector_y_direct_beam = nxmetadata.create_dataset(
            "detector_y_direct_beam", data=md["detector_y_direct_beam"]
        )
        ds_detector_y_direct_beam.attrs["units"] = "None"
        ds_beamline_id = nxmetadata.create_dataset(
            "beamline_id", data=md["beamline_id"]
        )
        ds_beamline_id.attrs["units"] = "None"
        ds_concise = nxmetadata.create_dataset("concise", data=md["beamline_id"])
        ds_concise.attrs["units"] = "None"
        ds_conda_prefix = nxmetadata.create_dataset(
            "conda_prefix", data=md["conda_prefix"]
        )
        ds_conda_prefix.attrs["units"] = "None"
        ds_cycle = nxmetadata.create_dataset("cycle", data=md["cycle"])
        ds_cycle.attrs["units"] = "None"
        ds_data_management = nxmetadata.create_dataset(
            "data_management", data=md["cycle"]
        )
        ds_data_management.attrs["units"] = "None"
        ds_databroker_catalog = nxmetadata.create_dataset(
            "databroker_catalog", data=md["cycle"]
        )
        ds_databroker_catalog.attrs["units"] = "None"

        # # # Ion chambers, NXmonitor.
        # hf.create_dataset('/entry/instrument/upstream_IC/nominal', data=md['I0'])
        # hf.create_dataset('/entry/instrument/downstream_IC/nominal', data=md['I1'])

        # # # Motors, NXpositioner
        # hf.create_dataset('/entry/instrument/sample_x/position', data=md['sample_x'])
        # hf.create_dataset('/entry/instrument/sample_y/position', data=md['sample_y'])
        # hf.create_dataset('/entry/instrument/sample_z/position', data=md['sample_z'])
        # hf.create_dataset('/entry/instrument/detector_x/position', data=md['detector_x'])
        # hf.create_dataset('/entry/instrument/detector_y/position', data=md['detector_y'])

        # # # Temperature control, NXenvironment
        # hf.create_dataset('/entry/instrument/qnw1/readback_temp', data=md['qnw1_temp'])
        # hf.create_dataset('/entry/instrument/qnw2/readback_temp', data=md['qnw2_temp'])
        # hf.create_dataset('/entry/instrument/qnw3/readback_temp', data=md['qnw3_temp'])


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
