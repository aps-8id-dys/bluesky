"""
APS Data Management utility support.

.. automodule::

    ~build_run_metadata_dict
    ~dm_add_workflow
    ~dm_api_ds
    ~dm_api_proc
    ~dm_get_experiment_path
    ~dm_get_experiments
    ~dm_get_workflow
    ~dm_source_environ
    ~dm_station_name
    ~dm_update_workflow
    ~get_workflow_last_stage
    ~SECOND
    ~MINUTE
    ~HOUR
    ~DAY
    ~WEEK
    ~WorkflowCache

:see: https://git.aps.anl.gov/DM/dm-docs/-/wikis/DM/Beamline-Services/Workflow-Processing-Service
"""

__all__ = """
    build_run_metadata_dict
    dm_add_workflow
    dm_api_ds
    dm_api_proc
    dm_get_experiment_path
    dm_get_experiments
    dm_get_workflow
    dm_source_environ
    dm_station_name
    dm_update_workflow
    get_workflow_last_stage
    SECOND
    MINUTE
    HOUR
    DAY
    WEEK
    WorkflowCache
""".split()


import datetime
import json
import logging
import pathlib
from os import environ

import pyRestTable

from bluesky import plan_stubs as bps

logger = logging.getLogger(__name__)
logger.info(__file__)

from .._iconfig import iconfig  # noqa

SECOND = 1.0
MINUTE = 60 * SECOND
HOUR = 60 * MINUTE
DAY = 24 * HOUR
WEEK = 7 * DAY

DEFAULT_PERIOD = 10 * SECOND
DEFAULT_WAIT = False
DEFAULT_DM_EXPERIMENT_KEYS = """
    id name startDate experimentType experimentStation
""".split()

DM_SETUP_FILE = pathlib.Path(iconfig["DM_SETUP_FILE"])
_dm_env_sourced = False


def build_run_metadata_dict(user_md, **dm_kwargs):
    """Return the run metadata dictionary."""
    _md = {
        "title": "title placeholder",
        "description": "description placeholder",
        "datetime": str(datetime.datetime.now()),
        "data_management": dm_kwargs,
    }
    _md.update(user_md)
    return _md


def dm_add_workflow(workflow_file):
    """Add DM workflow from file."""
    return dm_api_proc().addWorkflow(json.loads(open(workflow_file).read()))


def dm_get_workflow(workflow_name):
    """Get named DM workflow."""
    api = dm_api_proc()
    return api.getWorkflowByName(api.username, workflow_name)


def dm_update_workflow(workflow_file):
    """Update DM workflow from file."""
    return dm_api_proc().updateWorkflow(json.loads(open(workflow_file).read()))


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


def dm_source_environ():
    """
    Add APS DM environment variable definitions to this process.

    BASH COMMAND SUGGESTIONS::

        source /home/dm/etc/dm.setup.sh
        source ~/DM/etc/dm.setup.sh
    """
    global _dm_env_sourced

    if _dm_env_sourced:
        return

    def chop(text):
        return text.strip().split()[-1].split("=")

    # fmt: off
    ev = {
        chop(line)[0]: chop(line)[-1]
        for line in open(iconfig["DM_SETUP_FILE"]).readlines()
        if line.startswith("export ")
    }
    environ.update(ev)
    _dm_env_sourced = True
    # fmt: on


def dm_station_name():
    """Get the DM station name."""
    dm_source_environ()
    return str(environ.get("DM_STATION_NAME")).lower()


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


def dm_get_experiment_path(experiment_name: str):
    """Return the storageDirectory for the named experiment as a path."""
    api = dm_api_ds()
    path = api.getExperimentByName(experiment_name).get("storageDirectory")
    if path is not None:
        path = pathlib.Path(path)
    return path


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


def get_workflow_last_stage(workflow_name):
    """
    Return the name of the last stage in the named workflow.
    """
    return list(dm_get_workflow(workflow_name)["stages"])[-1]


WORKFLOW_DONE_STATES = "done failed timeout aborted".split()


class WorkflowCache:
    """Keep track of one or more workflows for bluesky plans."""

    cache = {}

    def define_workflow(self, key, workflow):
        self.cache[key] = workflow

    def print_cache_summary(self, title="Summary"):
        """Summarize the DM workflow cache."""
        table = pyRestTable.Table()
        table.labels = "# process status runTime started id".split()
        for i, k in enumerate(self.cache, start=1):
            v = self.cache[k]
            job_id = v.job_id.get()
            started = datetime.datetime.fromtimestamp(v.start_time).isoformat(sep=" ")
            table.addRow(
                (
                    i,
                    k,
                    v.status.get(),
                    v.run_time.get(),
                    started,
                    job_id[:7],
                )
            )
        print(f"\n{title}\n{table}")

    def report_dm_workflow_output(self, final_stage_id):
        """Final (summary) report about DM workflow."""
        for wf in self.cache.values():
            job = wf.getJob()
            stage = job.getWorkflowStage(final_stage_id)  # example: "06-DONE"
            for process in stage.get("childProcesses", {}).values():
                for key in "stdOut stdErr".split():
                    value = str(process.get(key, "")).strip()
                    if len(value):
                        print(f"{final_stage_id}  {key}:\n{value}")
                        print("~" * 50)

    def _update_processing_data(self):
        for wf in self.cache.values():
            wf._update_processing_data()

    def wait_workflows(self, period=DEFAULT_PERIOD, wait=DEFAULT_WAIT):
        """(plan) Wait (if ``True``) for existing workflows to finish."""
        print(f"DEBUG: wait_workflows(): waiting={wait}")
        if wait:
            print(
                f"Waiting for all previous workflows ({len(self.cache)}) to finish..."
            )
            for workflow in self.cache.values():
                # wait for each workflow to end
                while workflow.status.get() not in WORKFLOW_DONE_STATES:
                    print(f"Waiting for {workflow=}")
                    yield from bps.sleep(period)
