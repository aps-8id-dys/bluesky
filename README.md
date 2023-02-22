# README.md

XPCS bluesky instrument configuration

Advanced Photon Source, Argonne National Laboratory

**NOTE**:  To enable the bluesky queueserver (QS), this directory
must have only one `.py` file and that file is used to start the
QS session.  Any files user support files should go into the
`user/` directory.

## Interactive sessions

From either tcsh or bash shell, this linux command should start an
interactive session (using the present working directory for any
file storage, such as logs):

```bash
blueskyStarter.sh
```

## Jupyter notebook

Jupyter notebook sessions are not used commonly for bluesky controls.

## Bluesky Queueserver

The [_QS_](./instrument/README.md) is being configured for
initial demonstration at this time.

**Note**: The QS _server_ must run on the same workstation as the `redis`
software for reasons of the `redis` configuration.  Only the
QS _server_ needs to communicate directly with `redis`.

We have selected workstation `lapis.xray.aps.anl.gov` to run
both `redis` and the QS _server_.

You'll need to have the `bluesky_2023_1` conda/micromamba environment
activated and change your working directory to `~/bluesky` to run the
QS _server_.

Start QS _server_ process in a screen session. (choices include
`start`, `stop`, `status`, `restart`, `console`, & `usage`)

```bash
./qserver.sh start
```

**Note**: The script will stop if you try to run this on any other
workstation than the one designated above.

Start QS demo (client) GUI to observe and control the QS server.

```bash
queue-monitor &
```

**Related**: Notes for the (similar) BDP
[QS](https://github.com/BCDA-APS/bdp_controls/blob/main/qserver/README.md)
installation are on GitHub.  Plans and devices _will_ be different.

### First job

Try submitting and running the `hello_plan()` plan.  It does not need any arguments.

<details>
<summary>hello_plan()</summary>

```
[I 2023-02-22 11:34:19,130 bluesky_queueserver.manager.manager] Adding new item to the queue ...
[I 2023-02-22 11:34:19,131 bluesky_queueserver.manager.manager] Item added: success=True item_type='plan' name='hello_plan' item_uid='40b04ad8-a4a1-49b9-8828-b111c99196ce' qsize=1.
[I 2023-02-22 11:34:19,133 bluesky_queueserver.manager.manager] Returning current queue and running plan ...
[I 2023-02-22 11:34:27,127 bluesky_queueserver.manager.manager] Starting queue processing ...
[I 2023-02-22 11:34:27,128 bluesky_queueserver.manager.manager] Processing the next queue item: 1 plans are left in the queue.
[I 2023-02-22 11:34:27,129 bluesky_queueserver.manager.manager] Starting the plan:
{'name': 'hello_plan',
'args': [],
'kwargs': {},
'user': 'GUI Client',
'user_group': 'primary',
'meta': {},
'item_uid': '40b04ad8-a4a1-49b9-8828-b111c99196ce'}.
[I 2023-02-22 11:34:27,129 bluesky_queueserver.manager.worker] Starting execution of a plan ...
[I 2023-02-22 11:34:27,129 bluesky_queueserver.manager.worker] Starting a plan 'hello_plan'.
[I 2023-02-22 11:34:27,257 bluesky_queueserver.manager.plan_monitoring] New run was open: 'cb838ec8-3812-4a0f-8b54-5130c1eca54f'
Run was closed: 'cb838ec8-3812-4a0f-8b54-5130c1eca54f'
[I 2023-02-22 11:34:27,512 bluesky_queueserver.manager.worker] The plan was exited. Plan state: completed
[I 2023-02-22 11:34:27,886 bluesky_queueserver.manager.manager] No items are left in the queue.
[I 2023-02-22 11:34:27,886 bluesky_queueserver.manager.manager] Queue is empty.
[I 2023-02-22 11:34:27,931 bluesky_queueserver.manager.manager] Returning current queue and running plan ...
[I 2023-02-22 11:34:27,932 bluesky_queueserver.manager.manager] Returning the list of runs for the running plan ...
[I 2023-02-22 11:34:27,933 bluesky_queueserver.manager.manager] Returning plan history ...
```

The run looks like:

```
In [7]: run
Out[7]:
BlueskyRun
  uid='cb838ec8-3812-4a0f-8b54-5130c1eca54f'
  exit_status='success'
  2023-02-22 11:34:27.228 -- 2023-02-22 11:34:27.272
  Streams:
    * primary
In [8]: run.primary.read()
Out[8]:
<xarray.Dataset>
Dimensions:     (time: 1)
Coordinates:
  * time        (time) float64 1.677e+09
Data variables:
    hello       (time) int64 1
    hello_text  (time) <U13 'Hello, World!'
```

</details>

![QS demo GUI](./instrument/_resources/2023-02-22-QS-lapis.png)

## Legacy

The previous instrument configuration is stored in the
[ipython-8idiuser](https://github.com/aps-8id-dys/ipython-8idiuser),
which has been archived (made read-only so no new contributions,
issues, pull requests, ... in that repo now).
