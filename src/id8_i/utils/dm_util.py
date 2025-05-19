"""
DM code from Hannah Parraga.
Set up DM and submit jobs
"""

from apsbits.core.instrument_init import oregistry
from dm.common.utility.configurationManager import ConfigurationManager
from dm.proc_web_service.api.workflowProcApi import WorkflowProcApi

from .util_8idi import get_machine_name

pv_registers = oregistry["pv_registers"]


def dm_setup(process: bool) -> tuple:
    """Set up the Data Management workflow API.

    Args:
        process: Whether to initialize the workflow API

    Returns:
        Tuple containing (workflowProcApi, dmuser) if process is True,
        otherwise (None, None)
    """
    if process:
        # Object that tracks beamline-specific configuration
        configManager = ConfigurationManager.getInstance()
        dmuser, password = configManager.parseLoginFile()
        serviceUrl = configManager.getProcWebServiceUrl()
        # user/password/url info passed to DM API
        workflowProcApi = WorkflowProcApi(dmuser, password, serviceUrl)
    return workflowProcApi, dmuser


def dm_run_job(
    det_name: str,
    process: bool,
    workflowProcApi: WorkflowProcApi,
    dmuser: str,
    filename: str,
):
    """Submit a data processing job to the Data Management system.

    Args:
        det_name: Name of the detector ("rigaku" or "eiger")
        process: Whether to submit the job
        workflowProcApi: Workflow API instance
        dmuser: DM username
        filename: Base name of the data file
    """
    if process:
        exp_name = pv_registers.experiment_name.get()
        qmap_file = pv_registers.qmap_file.get()
        workflow_name = pv_registers.workflow_name.get()
        # analysis_machine = pv_registers.analysis_machine.get()
        analysis_machine = get_machine_name()

        if det_name == "rigaku":
            filepath = f"{filename}.bin.000"
        elif det_name == "eiger":
            filepath = f"{filename}.h5"
        else:
            pass
        argsDict = {
            "experimentName": exp_name,
            "filePath": filepath,
            "qmap": f"{qmap_file}",
            "analysisMachine": f"{analysis_machine}",
            "gpuID": -2,
        }
        job = workflowProcApi.startProcessingJob(
            dmuser, f"{workflow_name}", argsDict=argsDict
        )
        print(f"Job {job['id']} processing {filename}")
