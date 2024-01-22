"""
APS Data Management utility support.

.. automodule::

    ~build_run_metadata_dict
    ~dm_add_workflow
    ~dm_api_cat
    ~dm_api_daq
    ~dm_api_dataset_cat
    ~dm_api_ds
    ~dm_api_file
    ~dm_api_proc
    ~dm_files_ready_to_process
    ~dm_get_daq
    ~dm_get_experiment_path
    ~dm_get_experiments
    ~dm_get_workflow
    ~dm_isDaqActive
    ~dm_source_environ
    ~dm_start_daq
    ~dm_start_daq
    ~dm_station_name
    ~dm_stop_daq
    ~dm_stop_daq
    ~dm_update_workflow
    ~get_workflow_last_stage
    ~share_bluesky_metadata_with_dm
    ~ts2iso
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
    dm_api_cat
    dm_api_daq
    dm_api_dataset_cat
    dm_api_ds
    dm_api_file
    dm_api_proc
    dm_files_ready_to_process
    dm_get_daq
    dm_get_experiment_path
    dm_get_experiments
    dm_get_workflow
    dm_isDaqActive
    dm_source_environ
    dm_start_daq
    dm_start_daq
    dm_station_name
    dm_stop_daq
    dm_stop_daq
    dm_update_workflow
    get_workflow_last_stage
    share_bluesky_metadata_with_dm
    ts2iso
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

SECOND = 1
MINUTE = 60 * SECOND
HOUR = 60 * MINUTE
DAY = 24 * HOUR
WEEK = 7 * DAY

DEFAULT_PERIOD = 10 * SECOND
DEFAULT_WAIT = True
DEFAULT_DM_EXPERIMENT_KEYS = """
    id name startDate experimentType experimentStation
""".split()

DM_SETUP_FILE = pathlib.Path(iconfig["DM_SETUP_FILE"])
_dm_env_sourced = False
WORKFLOW_DONE_STATES = "done failed timeout aborted".split()


def build_run_metadata_dict(user_md: dict, **dm_kwargs) -> dict:
    """Return a dictionary for use as Bluesky run metadata."""
    _md = {
        "title": "title placeholder",
        "description": "description placeholder",
        "datetime": str(datetime.datetime.now()),
        "data_management": dm_kwargs,
    }
    _md.update(user_md)
    return _md


def dm_add_workflow(workflow_file):
    """Add APS Data Management workflow from file."""
    return dm_api_proc().addWorkflow(json.loads(open(workflow_file).read()))


def dm_get_workflow(workflow_name: str):
    """Get named APS Data Management workflow."""
    api = dm_api_proc()
    return api.getWorkflowByName(api.username, workflow_name)


def dm_update_workflow(workflow_file):
    """Update APS Data Management workflow from file."""
    return dm_api_proc().updateWorkflow(json.loads(open(workflow_file).read()))


def dm_api_cat():
    """Return the APS Data Management Catalog API object."""
    from dm import CatApiFactory

    dm_source_environ()
    return CatApiFactory.getRunCatApi()


def dm_api_dataset_cat():
    """Return the APS Data Management Dataset Metadata Catalog API object."""
    from dm import CatApiFactory

    dm_source_environ()
    return CatApiFactory.getDatasetCatApi()


def dm_api_daq():
    """Return the APS Data Management Data Acquisition API object."""
    from dm import DaqApiFactory

    dm_source_environ()
    api = DaqApiFactory.getExperimentDaqApi()
    return api


def dm_api_ds():
    """Return the APS Data Management Data Storage API object."""
    from dm import DsApiFactory

    dm_source_environ()
    api = DsApiFactory.getExperimentDsApi()
    return api


def dm_api_file():
    """Return the APS Data Management File API object."""
    from dm import DsApiFactory

    dm_source_environ()
    api = DsApiFactory.getFileDsApi()
    return api


def dm_api_proc():
    """Return the APS Data Management Processing API object."""
    from dm import ProcApiFactory

    dm_source_environ()
    api = ProcApiFactory.getWorkflowProcApi()
    return api


def dm_get_daq(experimentName: str):
    """
    Return named APS Data Management experiment DAQ.

    PARAMETERS

    experimentName *str*:
        Name of the APS Data Management experiment.

    RETURNS

        DAQ ``dict`` result or ``None`` if not found.
    """
    api = dm_api_daq()
    for daq in api.listDaqs():
        if daq.get("experimentName") == experimentName:
            return daq


def dm_isDaqActive(experimentName: str) -> bool:
    """
    Return if a DAQ is active for the named APS Data Management experiment.

    PARAMETERS

    experimentName *str*:
        Name of the APS Data Management experiment.

    RETURNS

        Boolean
    """
    from dm.common.constants import dmProcessingStatus

    active_statuses = (
        dmProcessingStatus.DM_PROCESSING_STATUS_PENDING,
        dmProcessingStatus.DM_PROCESSING_STATUS_RUNNING,
    )
    daq = dm_get_daq(experimentName)
    if daq is not None:
        return daq.get("status") in active_statuses
    return False  # not found is same as not active


def dm_files_ready_to_process(
    experimentFilePath: str,  # path (abs or rel) to a file
    experimentName: str,
    compression: str = "",
    retrieveMd5Sum: bool = False,
) -> bool:
    """
    Does DM determine the named file is ready for processing?
    """
    return dm_api_file().statFile(
        experimentFilePath, experimentName, compression, retrieveMd5Sum
    ).get("readyForProcessing", False)


def dm_source_environ():
    """
    Add APS Data Management environment variable definitions to this process.

    This function reads the bash script, searching for lines that start with
    "export ". Such lines define bash shell environment variables in the bash
    script.  This function adds those environment variables to the current
    environment.

    BASH COMMAND SUGGESTIONS::

        source /home/dm/etc/dm.setup.sh

        source ~/DM/etc/dm.setup.sh

    The suggestions follow a pattern: ``${DM_ROOT}/etc/dm.setup.sh`` where
    ``DM_ROOT`` is the location of the DM tools as installed in the current user
    account.
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


def dm_start_daq(experimentName: str, dataDirectory: str, **daqInfo):
    """
    Start APS DM data acquisition (real-time directory monitoring and file upload).

    PARAMETERS

    experimentName *str*:
        Name of the APS Data Management experiment.
    dataDirectory:
        data directory URL
    daqInfo *dict*:
        Dictionary of optional metadata (key/value pairs) describing data acquisition.
        See https://git.aps.anl.gov/DM/dm-docs/-/wikis/DM/Beamline-Services/API-Reference/DAQ-Service#dm.daq_web_service.api.experimentDaqApi.ExperimentDaqApi.startDaq
        for details.

    """
    dm_api_daq().startDaq(experimentName, dataDirectory, **daqInfo)


def dm_stop_daq(experimentName: str, dataDirectory: str):
    """
    Stop APS DM data acquisition (real-time directory monitoring and file upload).

    PARAMETERS

    experimentName *str*:
        Name of the APS Data Management experiment.
    dataDirectory:
        data directory URL

    """
    dm_api_daq().stopDaq(experimentName, dataDirectory)


def dm_station_name():
    """Return the APS Data Management station name or ``None`` if not found."""
    dm_source_environ()
    nm = environ.get("DM_STATION_NAME")
    if nm is not None:
        return str(nm).lower()


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
    """
    Return the storageDirectory for the named APS Data Management experiment as a path.

    PARAMETERS

    experiment_name *str*:
        Name of the APS Data Management experiment.  The experiment must exist.

    RETURNS

    Data directory for the experiment, as pathlib.Path object.

    RAISES

    dm.ObjectNotFound:
        When experiment is not found.
    """
    api = dm_api_ds()
    path = api.getExperimentByName(experiment_name).get("storageDirectory")
    if path is not None:
        path = pathlib.Path(path)
    return path


def dm_get_experiments(
    keys=DEFAULT_DM_EXPERIMENT_KEYS, table=False, default_value="-na-"
):
    """
    Get the most recent APS Data Management experiments (for the current station).

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
    Return the name of the last stage in the named APS Data Management workflow.
    """
    return list(dm_get_workflow(workflow_name)["stages"])[-1]


def share_bluesky_metadata_with_dm(
    experimentName: str, workflow_name: str, run, should_raise: bool = False
):
    """
    Once a bluesky run ends, share its metadata with APS DM.

    Only upload if we have a workflow.
    """
    import uuid

    from dm import InvalidArgument

    api = dm_api_dataset_cat()

    datasetInfo = {
        "experimentName": experimentName,
        "datasetName": f"run_uid8_{run.metadata['start']['uid'][:8]}",  # first part of run uid
        "workflow_name": workflow_name,
        "time_iso8601": ts2iso(run.metadata.get("start", {}).get("time", 0)),
        "bluesky_metadata": {k: getattr(run, k).metadata for k in run},  # all streams
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        "_id": str(uuid.uuid4()),  # FIXME: dm must fix this upstream
    }

    try:
        dm_md = api.addExperimentDataset(datasetInfo)
        logger.debug("Metadata shared to DM: %s", dm_md)
        return dm_md
    except InvalidArgument as ex:
        logger.error(ex)
        if should_raise:
            raise ex


def ts2iso(ts: float, sep: str = " ") -> str:
    """Convert Python timestamp (float) to IS8601 time in current time zone."""
    return datetime.datetime.fromtimestamp(ts).isoformat(sep=sep)


class WorkflowCache:
    """
    Keep track of one or more APS Data Management workflows for bluesky plans.

    .. automodule::

        ~define_workflow
        ~print_cache_summary
        ~report_dm_workflow_output
        ~wait_workflows
        ~_update_processing_data
    """

    cache = {}

    def define_workflow(self, key: str, connector):
        """
        Add a DM_WorkflowConnector object to be managed.

        PARAMETERS

        key *str*:
            Identifying text for this workflow object.
        connector *object*:
            Instance of DM_WorkflowConnector.
        """
        if key in self.cache:
            raise KeyError(f"Key already exists: {key!r}")
        # TODO: validate connector
        self.cache[key] = connector

    def print_cache_summary(self, title: str = "Summary"):
        """Summarize (in a table) the DM workflows in the cache."""
        table = pyRestTable.Table()
        table.labels = "# process status runTime started id".split()
        for i, k in enumerate(self.cache, start=1):
            v = self.cache[k]
            job_id = v.job_id.get()
            started = ts2iso(v.start_time)
            table.addRow((i, k, v.status.get(), v.run_time.get(), started, job_id[:7]))
        print(f"\n{title}\n{table}")

    def report_dm_workflow_output(self, final_stage_id: str):
        """
        Print a final (summary) report about a single DM workflow.

        PARAMETERS

        final_stage_id *str*:
            Text key of the last stage in the workflow.
        """
        for wf in self.cache.values():
            job = wf.getJob()
            stage = job.getWorkflowStage(final_stage_id)  # example: "06-DONE"
            for process in stage.get("childProcesses", {}).values():
                for key in "stdOut stdErr".split():
                    value = str(process.get(key, "")).strip()
                    if len(value):
                        print(f"{final_stage_id}  {key}:\n{value}")
                        print("~" * 50)

    def wait_workflows(self, period: float = DEFAULT_PERIOD, wait: bool = DEFAULT_WAIT):
        """
        (plan) Wait (if ``True``) for existing workflows to finish.

        PARAMETERS

        period *float*:
            Time between reports while waiting for all workflows to finish processing.
            Default: 10 seconds.
        wait *bool*:
            Should RE wait for all workflows to finish?
            Default: ``True``
        """
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

    def _update_processing_data(self):
        """Update all the workflows in the cache (from the DM server)."""
        for wf in self.cache.values():
            wf._update_processing_data()
