import warnings
import h5py 
import time
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
from .APS8IDI_xpcs_schema import xpcs_schema
from .APS8IDI_default_metadata import default_metadata


default_units_keymap = {
    "NX_COUNT": "one",         # Used for frame_sum, frame_average, delay_difference
    "NX_DIMENSIONLESS": "dim.less",  # Used for g2, g2_derr, dynamic_roi_map, static_roi_map
    "NX_LENGTH": "m",          # Used for beam_center_x, beam_center_y, distance, x_pixel_size, y_pixel_size, extent
    "NX_TIME": "s",            # Used for count_time, frame_time
    "NX_ENERGY": "keV",        # Used for incident_energy, incident_energy_spread
    "NX_PER_LENGTH": "1/Å",    # Used for dynamic_phi_list, dynamic_q_list, static_q_list
    "NX_TEMPERATURE": "K",     # Used for temperature, temperature_set
    "NX_CURRENT": "mA",        # Used for current, milliamper
    "NX_ANY": "any",           # Used for G2_unnormalized, two_time_corr_func
    "NX_ANGLE": "degree"       # Used for rotation_x, rotation_y, rotation_z, rotation_angle 
}


default_storage_dtype = {
    "NX_CHAR": "S1",
    "NX_NUMBER": "f8",
    "NX_INT": "i8",
}


def create_nexus_entry(group_or_fhdl, runtime_schema, ignore=False):
    """
    Create a NeXus entry from a dictionary that represents a Nexus format.
    Parameters
    ----------
    group_or_fhdl : h5py.Group or h5py.File
        The group or file handle to create the entry in.
    runtime_schema : dict
        The dictionary that represents the Nexus format.
    ignore : bool, optional
        If True, ignore optional fields. The default is False.
    """
    for key, val in runtime_schema.items():
        if key == "attributes":
            for attr_key, attr_val in val.items():
                group_or_fhdl.attrs[attr_key] = attr_val["data"]
        elif key not in ("type", "required", "deprecated", "units", "description"):
            required = val.pop("required", False)
            if ignore and not required:
                continue

            if "data" in val:
                data_item = val.pop("data")
                if data_item is not None:
                    handle = group_or_fhdl.create_dataset(key, data=data_item)
                else:
                    handle = group_or_fhdl.create_dataset(key, shape=(0,))
            else:
                handle = group_or_fhdl.create_group(key)

            dtype = val.pop("type", None)
            if dtype is not None:
                handle.attrs["NX_Class"] = dtype
            units = val.pop("units", None)
            if units is not None:
                handle.attrs["unit"] = default_units_keymap.get(units, "any") 
            description = val.pop("description", None)
            if description is not None:
                handle.attrs["description"] = description
            
            create_nexus_entry(handle, val, ignore=ignore)


def update_schema_at_runtime(schema, runtime_metadata):
    """
    Update the metadata dictionary with runtime data.
    Parameters
    ----------
    schema : dict
        The metadata dictionary.
    runtime_metadata : dict
        The runtime metadata dictionary.
    Returns
    -------
    dict
        The updated schema with runtime metadata.
    """
    for path, value in runtime_metadata.items():
        components = path.lstrip("/").split("/")
        current = schema 
        for comp in components:
            current = current[comp]
        current["data"] = value
    return schema


def create_runtime_metadata_dict(det=None, additional_metadata=None):
    """
    Create a dictionary with runtime metadata. A full list of possible metadata
    is given in the default_metadata dictionary. This function should be maintained 
    by beamline staff to include all relevant metadata as needed for the experiment.
    Parameters
    ----------
    det : Detector, optional
        The detector object. If None, the default detector is used.
    additional_metadata : dict, optional
        A dictionary with additional metadata to be included in the runtime metadata.
    Returns
    -------
    dict
        The runtime metadata dictionary.
    """
    # Create a copy of the default metadata dictionary
    runtime_metadata = default_metadata.copy()

    # Update the metadata with runtime values
    runtime_updates = {
        # Entry level metadata
        "/entry/entry_identifier": "xpcs_20240214_120000",
        "/entry/entry_identifier_uuid": "550e8400-e29b-41d4-a716-446655440000",
        "/entry/scan_number": 1,
        "/entry/user/cycle": pv_registers.cycle_name.get(),
        "/entry/start_time": time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()),
        "/entry/end_time": time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()), # fixme later
    
        "/entry/instrument/detector_1/beam_center_x": 1024.0,
        "/entry/instrument/detector_1/beam_center_y": 1024.0,
        "/entry/instrument/detector_1/count_time":  det.cam.acquire_time.get(),
        "/entry/instrument/detector_1/frame_time": det.cam.acquire_period.get(),
        "/entry/instrument/detector_1/detector_name": det.name,
        "/entry/instrument/detector_1/distance": 12.0, 
    
        "/entry/instrument/incident_beam/incident_energy": 12.0,    # fixme later
        "/entry/instrument/incident_beam/incident_energy_spread": 0.0001,   # fixme later
    
        "/entry/sample/position_x": sample.x.position,
        "/entry/sample/position_y": sample.y.position,
        "/entry/sample/position_z": sample.z.position,
        "/entry/sample/qnw1_temperature": qnw_env1.readback.get(),
        "/entry/sample/qnw1_temperature_set": qnw_env1.setpoint.get(),
        "/entry/sample/qnw2_temperature": qnw_env2.readback.get(),
        "/entry/sample/qnw2_temperature_set": qnw_env2.setpoint.get(),
        "/entry/sample/qnw3_temperature": qnw_env3.readback.get(),
        "/entry/sample/qnw3_temperature_set": qnw_env3.setpoint.get(),
    }
    # update the runtime metadata with the runtime updates
    runtime_metadata.update(runtime_updates)
    if additional_metadata is not None:
        runtime_metadata.update(additional_metadata)
    return runtime_metadata


def create_nexus_format_metadata(filename, det, additional_metadata=None):
    """
    Create a nexus file with the metadata for the xpcs experiment.
    Parameters
    ----------
    filename: str
        name of the nexus file to create
    det: detector object
        detector object to get the metadata from
    additional_metadata: dict
        additional metadata to add to the nexus file
        (optional)
    Returns
    -------
    None
    """
    # create a copy of schema from the template, tree-structure of the nexus file
    runtime_schema = xpcs_schema.copy()
    # create a dictionary of the runtime metadata
    runtime_metadata = create_runtime_metadata_dict(det, additional_metadata)
    # update the schema with the metadata
    runtime_schema = update_schema_at_runtime(runtime_schema, runtime_metadata)  

    # save the schema to a nexus file
    with h5py.File(filename, "w") as f:
        create_nexus_entry(f, runtime_schema)
    return


if __name__ == "__main__":
    # create_nexus_template(filename="template_metadata.hdf")
    create_nexus_format_metadata("test02.hdf")
