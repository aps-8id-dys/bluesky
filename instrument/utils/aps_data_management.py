"""
APS Data Management utility support.

.. automodule::

    ~dm_api_ds
    ~dm_api_proc
    ~dm_get_experiment_directory
    ~dm_get_experiments
    ~dm_source_environ

:see: https://git.aps.anl.gov/DM/dm-docs/-/wikis/DM/Beamline-Services/Workflow-Processing-Service
"""

__all__ = """
    dm_api_ds
    dm_api_proc
    dm_get_experiment_directory
    dm_get_experiments
    dm_source_environ
""".split()


import logging
import pathlib
from os import environ
import pyRestTable

logger = logging.getLogger(__name__)
logger.info(__file__)

from .._iconfig import iconfig  # noqa

DEFAULT_DM_EXPERIMENT_KEYS = """
    id name startDate experimentType experimentStation
""".split()

DM_SETUP_FILE = pathlib.Path(iconfig["DM_SETUP_FILE"])
_dm_env_sourced_ = False


def dm_source_environ():
    """
    Add APS DM environment variable definitions to this process.

    BASH COMMAND SUGGESTIONS::

        source /home/dm/etc/dm.setup.sh
        source ~/DM/etc/dm.setup.sh
    """
    global _dm_env_sourced_

    if _dm_env_sourced_:
        return

    def chop(text):
        return text.strip().split()[-1].split("=")

    # fmt: off
    ev = {
        chop(line)[0]: chop(line)[-1]
        for line in open(DM_SETUP_FILE).readlines()
        if line.startswith("export ")
    }
    environ.update(ev)
    _dm_env_sourced_ = True
    # fmt: on


def dm_api_ds():
    """Return the storage API object."""
    from dm import DsApiFactory

    dm_source_environ()
    api = DsApiFactory.getExperimentDsApi()
    return api


def dm_api_proc():
    """Return the process API object."""
    from dm import ProcApiFactory

    dm_source_environ()
    api = ProcApiFactory.getWorkflowProcApi()
    return api


# def dm_add_experiment(experiment_name, typeName=None, **kwargs):
#     """Create a new experiment.  (Use sparingly, if ever.)"""
#     typeName = typeName or "BDP"  # TODO: generalize, TEST, XPCS8, ...
#     dm_api_ds().addExperiment(experiment_name, typeName=typeName, **kwargs)


# def dm_delete_experiment(reference):
#     """Delete ALL of an existing experiment.  (No recovering from this!)"""
#     api = dm_api_ds()
#     if isinstance(reference, int):
#         api.deleteExperimentById(reference)
#     elif isinstance(reference, str):
#         api.deleteExperimentByName(reference)


def dm_get_experiment_directory(experiment_name: str):
    """Return the storageDirectory for the named experiment."""
    api = dm_api_ds()
    exp = api.getExperimentByName(experiment_name)
    return exp.get("storageDirectory")


def dm_get_experiments(
    keys=DEFAULT_DM_EXPERIMENT_KEYS, table=False, default_value="-na-"
):
    """
    Get the most recent experiments (for the current station) from DM.

    Return result as either a list or a pyRestTable object (see ``table``).

    PARAMETERS:

    keys *[str]*:
        Data keys to be shown in the table.
    table *bool*:
        If ``False`` (default), return a Python list.
        If ``True``, return a pyRestTable ``Table()`` object.
    default_value *str*:
        Table value if no data available for that key.
    """
    experiments = dm_api_ds().getExperimentsByStation()
    if table and len(experiments) > 0:
        if not isinstance(keys, (list, tuple)) or len(keys) == 0:
            keys = experiments[0].DEFAULT_KEY_LIST
        tbl = pyRestTable.Table()
        tbl.labels = keys
        for entry in experiments:
            row = []
            for key in keys:
                value = entry.data.get(key, default_value)
                if isinstance(value, dict):
                    value = value.get("description", value)
                # do this in steps, value might be modified (ts2iso, for example)
                row.append(value)
            # datetime
            tbl.addRow(row)
        return tbl
    else:
        return experiments
