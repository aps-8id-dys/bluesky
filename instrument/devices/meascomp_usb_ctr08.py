"""
Measurement Computing USB CTR08 8-channel scaler

USB-CTR08 is running on glass


glass% pwd
/xorApps/epics/synApps_6_2_1/ioc/8idDAQ1/iocBoot/ioc8idDAQ1/softioc
glass% ./8idDAQ1.sh start
Starting 8idDAQ1

/net/s8iddserv/xorApps/epics/synApps_6_2_1/ioc/8idDAQ1/iocBoot/ioc8idDAQ1/digital-IO.iocsh
dbLoadTemplate("$(MEASCOMP)/db/USBCTR.substitutions", "P=$(PREFIX), PORT=MCCTR08")
dbLoadRecords("$(SCALER)/db/scaler.db", "P=$(PREFIX), S=scaler1, DTYP=Asyn Scaler, OUT=@asyn(MCCTR08), FREQ=10000000")
dbLoadRecords("$(MEASCOMP)/db/measCompMCS.template", "P=$(PREFIX)MCS01:, PORT=MCCTR08, MAX_POINTS=2048")

dbLoadRecords("$(MCA)/mcaApp/Db/SIS38XX_waveform.template", "P=$(PREFIX)MCS01:, R=mca1,  INP=@asyn(MCCTR08 0),  CHANS=2048")
dbLoadRecords("$(MCA)/mcaApp/Db/SIS38XX_waveform.template", "P=$(PREFIX)MCS01:, R=mca2,  INP=@asyn(MCCTR08 1),  CHANS=2048")
dbLoadRecords("$(MCA)/mcaApp/Db/SIS38XX_waveform.template", "P=$(PREFIX)MCS01:, R=mca3,  INP=@asyn(MCCTR08 2),  CHANS=2048")
dbLoadRecords("$(MCA)/mcaApp/Db/SIS38XX_waveform.template", "P=$(PREFIX)MCS01:, R=mca4,  INP=@asyn(MCCTR08 3),  CHANS=2048")
dbLoadRecords("$(MCA)/mcaApp/Db/SIS38XX_waveform.template", "P=$(PREFIX)MCS01:, R=mca5,  INP=@asyn(MCCTR08 4),  CHANS=2048")
dbLoadRecords("$(MCA)/mcaApp/Db/SIS38XX_waveform.template", "P=$(PREFIX)MCS01:, R=mca6,  INP=@asyn(MCCTR08 5),  CHANS=2048")
dbLoadRecords("$(MCA)/mcaApp/Db/SIS38XX_waveform.template", "P=$(PREFIX)MCS01:, R=mca7,  INP=@asyn(MCCTR08 6),  CHANS=2048")
dbLoadRecords("$(MCA)/mcaApp/Db/SIS38XX_waveform.template", "P=$(PREFIX)MCS01:, R=mca8,  INP=@asyn(MCCTR08 7),  CHANS=2048")
dbLoadRecords("$(MCA)/mcaApp/Db/SIS38XX_waveform.template", "P=$(PREFIX)MCS01:, R=mca9,  INP=@asyn(MCCTR08 8),  CHANS=2048")

"""


__all__ = """
    scaler1
    mca1
    mca2
    mca3
    mca4
    mca5
    mca6
    mca7
    mca8
""".split()

import logging

logger = logging.getLogger(__name__)

logger.info(__file__)

from ophyd import EpicsSignalRO
from ophyd.scaler import ScalerCH


IOC = "8idDAQ1:"
# The IOC has iocStats  f"{IOC}UPTIME" for example

scaler1 = ScalerCH(f"{IOC}scaler1", name="scaler1", labels=["scalers", "detectors"])
scaler1.wait_for_connection()
scaler1.select_channels()

# TODO: replace with triggerable devices?
mca1 = EpicsSignalRO(f"{IOC}MCS01:mca1", name="mca1")
mca2 = EpicsSignalRO(f"{IOC}MCS01:mca2", name="mca2")
mca3 = EpicsSignalRO(f"{IOC}MCS01:mca3", name="mca3")
mca4 = EpicsSignalRO(f"{IOC}MCS01:mca4", name="mca4")
mca5 = EpicsSignalRO(f"{IOC}MCS01:mca5", name="mca5")
mca6 = EpicsSignalRO(f"{IOC}MCS01:mca6", name="mca6")
mca7 = EpicsSignalRO(f"{IOC}MCS01:mca7", name="mca7")
mca8 = EpicsSignalRO(f"{IOC}MCS01:mca8", name="mca8")
