# Introduction to the Bluesky Queueserver

## 2023-11-14

Some of the old notes may still apply.  This is not guaranteed.

### (Re)Start the bluesky queueserver server process

The QS (bluesky queueserver) process will only start on workstation
`8idpixirad.xray.aps.anl.gov`.  (Ensures there is only ONE QS process running
for XPCS.)  This steps requires the `CONDA_EXE` environment variable to be
defined, such as by having *some* conda environment activated.

```bash
~/bluesky/qserver.sh restart
```

More commands are available:

```bash
$ ./qserver.sh usage
Usage: qserver.sh {start|stop|restart|status|checkup|console|run} [NAME]

    COMMANDS
        console   attach to process console if process is running in screen
        checkup   check that process is running, restart if not
        restart   restart process
        run       run process in console (not screen)
        start     start process
        status    report if process is running
        stop      stop process

    OPTIONAL TERMS
        NAME      name of process (default: bluesky_queueserver-8idi_xpcs)
```

If you try to manage (start/stop/ ...) the queueserver on the wrong workstation
(such as agate), you'll get this reply:

```bash
agate% ./qserver.sh status
Must manage queueserver process on 8idpixirad.xray.aps.anl.gov.  This is agate.xray.aps.anl.gov.
```

### Start the bluesky queueserver client GUI

Since the server runs on a different workstation, we must supply additional
information.  (Could be bundled into shell script.)

```bash
queue-monitor \
    --zmq-control-addr "tcp://${QS_HOST}:60615" \
    --zmq-info-addr "tcp://${QS_HOST}:60625" &
```

- connect to the server
- open the environment
- add tasks to the queue
- run the queue

## Watch (monitor) the QS console

```bash
qserver-console  --zmq-control-addr "tcp://${QS_HOST}:60615"
```

## old notes from 2022

work-in-progress: *very* basic notes for now

- [Introduction to the Bluesky Queueserver](#introduction-to-the-bluesky-queueserver)
  - [2023-11-14](#2023-11-14)
    - [(Re)Start the bluesky queueserver server process](#restart-the-bluesky-queueserver-server-process)
    - [Start the bluesky queueserver client GUI](#start-the-bluesky-queueserver-client-gui)
  - [Watch (monitor) the QS console](#watch-monitor-the-qs-console)
  - [old notes from 2022](#old-notes-from-2022)
  - [Run the queuserver](#run-the-queuserver)
    - [operations](#operations)
    - [diagnostics and testing](#diagnostics-and-testing)
  - [graphical user interface](#graphical-user-interface)

**IMPORTANT**:  When the queueserver starts, it **must** find only one `.py` file in this directory and it must find `instrument/` in the same directory.  Attempts to place the qserver files in a sub directory result in `'instrument/' directory not found` as queueserver starts.

## Run the queuserver

### operations

Run in a background screen session.

`./qserver.sh start`

Stop this with

`./qserver.sh stop`

### diagnostics and testing

`./qserver.sh run`

## graphical user interface

`queue-monitor &`

- connect to the server
- open the environment
- add tasks to the queue
- run the queue
