# ID8 Bluesky Instrument

**Caution**:  If you will use the [bluesky queueserver (QS)](./qserver.md), note
that _every_ Python file in this directory will be executed when QS starts the
RunEngine. Don't add extra Python files to this directory.  Instead, put them in
`user/` or somewhere else.

Contains:

description | item(s)
--- | ---
Introduction | [`intro2bluesky.md`](https://bcda-aps.github.io/bluesky_training/reference/_intro2bluesky.html)
IPython console startup | [`./console/`](#bluesky-ipython-console-session)
Bluesky queueserver `*QS*` support | [introduction](#introduction-to-the-bluesky-queueserver)
Instrument package | [`./instrument/`](#bluesky-instrument-description)
Conda environments | [`./environments/`](#managing-the-bluesky-environments)
Unit tests | [`./tests/`](./tests/README.md)
Documentation | [How-to, examples, tutorials, reference](https://bcda-aps.github.io/bluesky_training)

## Bluesky IPython Console Session

Loads the `instrument` [package](https://bcda-aps.github.io/bluesky_training/instrument) for use in an interactive IPython console session (or Jupyter notebook).

Copy or link the `__start_bluesky_instrument__.py` file to the appropriate IPython profile `startup` directory, such as: `~/.ipython-bluesky/profile_bluesky/startup/__start_bluesky_instrument__.py`

## Introduction to the Bluesky Queueserver

All of the commands below (unless noted) require use of the `bash` command shell
and the bluesky conda environment to be activated: `become_bluesky`.

**VERY IMPORTANT**:  When the queueserver starts, it **must** find only one
`.py` file in the `~/bluesky` directory and it must find `instrument/` in the
same directory.  Attempts to place the qserver files in a sub directory result
in `'instrument/' directory not found` as queueserver starts.

#### (Re)Start the bluesky queueserver server process

NOTE: Unless you are testing, use `~/bluesky/qserver.sh restart`

The QS (bluesky queueserver) process will only start on workstation
`amber.xray.aps.anl.gov`.  (Ensures there is only ONE QS process running
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
        run       run process in console (not screen) for debugging only
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
Must manage queueserver process on amber.xray.aps.anl.gov.  This is agate.xray.aps.anl.gov.
```

Please only use the `run` command for interactive debugging sessions.  When done,
run the queueserver using the `restart` command.

#### Start the bluesky queueserver client GUI

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

### Watch (monitor) the QS console

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


## Bluesky Instrument description

Describes the devices, plans, and other Python code supporting an instrument for data acquisition with Bluesky.

description | configuration file
--- | ---
instrument customizations | `iconfig.yml`
interactive data collection | `collection.py`
bluesky-queueserver | `queueserver.py`



## Managing the Bluesky Environments

This directory contains the [YAML](https://yaml.org) files that define the
package requirements (and possibly the acceptable versions) for a conda
environment.

### YAML files

This directory contains the master source for these YAML files.
The repository is: https://github.com/BCDA-APS/bluesky_training/

version | file
--- | ---
2023-2 (latest) | [`environment_2023_2.yml`](./environment_2023_2.yml)
2023-1 | [`environment_2023_1.yml`](./environment_2023_1.yml)
2022_3 | [`environment_2022_3.yml`](./environment_2022_3.yml)
2022_2 | [`environment_2022_2.yml`](./environment_2022_2.yml)
2022_1 | [`environment_2022_1.yml`](./environment_2022_1.yml)
2021_2 | [`environment_2021_2.yml`](./environment_2021_2.yml)
2021_1 | [`environment_2021_1.yml`](./environment_2021_1.yml)

_note_: Prior to the 2023-2 version, the master source for these YAML files was the
[BCDA Bluesky
configuration](https://github.com/BCDA-APS/use_bluesky/tree/main/install)
repository.

### Managing environments

First you must activate the conda
[environment](https://bcda-aps.github.io/bluesky_training/reference/_conda_environment.html)
you will use (if not already activated). Such as:

```bash
(base) prjemian@zap:~$ conda activate bluesky_2023_2
(bluesky_2023_2) prjemian@zap:~$
```

## NOTES of the next things to do for bluesky

revised: 2024-02-23 (prj)

Add to BDP demo plan:

- (bool) "mesh" : random sample position (as done before in 2023 and earlier)
- (bool) "fly" : move sample axis (? x ?) during measurement

Add new plan to control QNW temperature controller.  This will be a good starting point for initial operations.  We can add features from this.

- (float) setpoint
- (float) ramp rate
- (bool) wait
