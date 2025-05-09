from apsbits.core.instrument_init import oregistry
from bluesky import plan_stubs as bps
from dm.common.utility.configurationManager import ConfigurationManager
from dm.proc_web_service.api.workflowProcApi import WorkflowProcApi

from .nexus_utils import create_nexus_format_metadata

rigaku3M = oregistry["rigaku3M"]
pv_registers = oregistry["pv_registers"]


def submit_Nexus_DM():
    while True:
        bluesky_start = pv_registers.start_bluesky.get()
        if bluesky_start == "Yes":
            # DM workflow setup.
            # configManager is an object that tracks beamline-specific configuration.
            # In WorkflowProcApi, user/password/url info is passed to DM API
            configManager = ConfigurationManager.getInstance()
            dmuser, password = configManager.parseLoginFile()
            serviceUrl = configManager.getProcWebServiceUrl()
            workflowProcApi = WorkflowProcApi(dmuser, password, serviceUrl)

            # Spec will need to write these fields in StrReg.
            # exp_name, workflow_name, analysis_machine need to be written only once per user.
            # metadata_fname and filename needs to be written per measurement.
            # Change qmap file when needed.
            exp_name = pv_registers.experiment_name.get()
            workflow_name = pv_registers.workflow_name.get()
            analysis_machine = pv_registers.analysis_machine.get()
            qmap_file = pv_registers.qmap_file.get()
            metadata_fname = pv_registers.metadata_full_path.get()
            filename = pv_registers.file_name.get()

            # Miaoqi's code that writes the metadata
            create_nexus_format_metadata(metadata_fname, det=rigaku3M)

            # Code that starts DM workflow
            argsDict = {
                "experimentName": exp_name,
                "filePath": f"{filename}.h5",
                "qmap": f"{qmap_file}",
                "analysisMachine": f"{analysis_machine}",
                "gpuID": -2,
                "analysis_type": "Both",
            }
            job = workflowProcApi.startProcessingJob(
                dmuser, f"{workflow_name}", argsDict=argsDict
            )
            print(f"Job {job['id']} processing {filename}")
            print(filename)

            pv_registers.start_bluesky.put("No")
        else:
            yield from bps.sleep(0.1)
