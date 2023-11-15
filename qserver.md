# Introduction to the Bluesky Queueserver

## 2023-11-14

All of the commands below (unless noted) require use of the `bash` command shell
and the bluesky conda environment to be activated: `become_bluesky`.

**VERY IMPORTANT**:  When the queueserver starts, it **must** find only one
`.py` file in the `~/bluesky` directory and it must find `instrument/` in the
same directory.  Attempts to place the qserver files in a sub directory result
in `'instrument/' directory not found` as queueserver starts.

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
information.

Use this simple command: `run_qs_gui`

<details>

Actually, it's a bash shell alias command for this much longer command:

```bash
queue-monitor \
    --zmq-control-addr "tcp://${QS_HOST}:60615" \
    --zmq-info-addr "tcp://${QS_HOST}:60625" &
```

</details>

These are the steps you might use with the GUI:

- connect to the server
- open the environment
- add tasks to the queue
- run the queue

## Watch (monitor) the QS console

Use this simple command: `monitor_qs_console`

<details>

Actually, it's a bash shell alias command for this much longer command:

```bash
qserver-console  --zmq-info-addr "tcp://${QS_HOST}:60625"
```

</details>

**NOTE**: This does not work at the moment.  Researching the issue.  Expect
(later) it should work from any workstation on the subnet.  For now, expand the
console history section on the GUI.
