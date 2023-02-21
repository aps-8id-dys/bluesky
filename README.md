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

Start QS _server_ process in a screen session. (choices include
`start`, `stop`, `status`, `restart`, `console`, & `usage`)

```bash
./qserver.sh start
```

Start client GUI to observe and control the QS server.

```bash
queue-monitor &
```

**Related**: Notes for the (similar) BDP [QS](https://github.com/BCDA-APS/bdp_controls/blob/main/qserver/README.md) installation are on GitHub.  Plans and devices _will_ be different.

## Legacy

The previous instrument configuration is stored in the
[ipython-8idiuser](https://github.com/aps-8id-dys/ipython-8idiuser),
which has been archived (made read-only so no new contributions,
issues, pull requests, ... in that repo now).
