import warnings
import h5py 
import time
import warnings
import numpy as np
import h5py 

from APS8IDI_xpcs_schema import xpcs_schema
from APS8IDI_default_metadata import default_metadata


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


def create_nexus_entry(group_or_fhdl, runtime_schema, ignore=False, detector_index=1):
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
            if dtype:
                handle.attrs["NX_Class"] = dtype
            units = val.pop("units", None)
            if units:
                handle.attrs["unit"] = default_units_keymap.get(units, "any") 

            if dtype == 'NXdetector':
                # create a hardlink
                group_or_fhdl[f'detector_{detector_index}'] = handle
                group_or_fhdl[f'detector_{detector_index}'].attrs['NX_Class'] = 'NXdetector'
                detector_index += 1

            create_nexus_entry(handle, val, ignore=ignore, 
                               detector_index=detector_index)


def update_metadata(metadata, runtime_metadata):
    """
    Update the metadata dictionary with runtime metadata.
    The runtime metadata is a dictionary with keys that are paths to the
    metadata in the metadata dictionary. The values are the values to update
    the metadata with.
    """
    for path, value in runtime_metadata.items():
        components = path.lstrip("/").split("/")
        current = metadata 
        for comp in components:
            current = current[comp]
        current["data"] = value


def create_runtime_metadata_dict(det=None):
    """
    Create a dictionary with runtime metadata. A full list of possible metadata
    is given in the default_metadata dictionary. This function should be maintained 
    by beamline staff to include all relevant metadata as needed for the experiment.
    """
    # Create a copy of the default metadata dictionary
    runtime_metadata = default_metadata.copy()

    # Update the metadata with runtime values
    runtime_updates = {
        "/entry/start_time": time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()),
        "/entry/end_time": time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()), # fixme later
    }
    runtime_metadata.update(runtime_updates)
    return runtime_metadata


def create_nexus_format_metadata(filename):
    # create a copy of schema from the template, tree-structure of the nexus file
    runtime_schema = xpcs_schema.copy()
    # create a dictionary of the runtime metadata
    runtime_metadata = create_runtime_metadata_dict()
    # update the schema with the metadata
    update_metadata(runtime_schema, runtime_metadata)  

    # save the schema to a nexus file
    with h5py.File(filename, "w") as f:
        create_nexus_entry(f, runtime_schema)
    return


if __name__ == "__main__":
    # create_nexus_template(filename="template_metadata.hdf")
    create_nexus_format_metadata("test03.hdf")
