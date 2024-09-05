# 8-ID-I XPCS Bluesky Instrument

## Installation Steps
*aps_8id_bs_instrument* can also use *conda* for dependency management, and
*setuptools* for installation and development.

First, download the package from github:

```bash
git clone https://github.com/aps-8id-dys/bluesky
cd bluesky
```

```bash
conda create -y -n your_env_name "python<13" "pyqt=5"
conda activate your_env_name
pip install -e ".[dev]"
```

## Sanity check test script
The below script will allow you to check if you are on the private subnet as
well as check if APS Data Management tools are installed properly.
```bash
python3 ./scripts/user/check_environment_test.py
```
## Running Bluesky Session
### With Ipython

```bash
./scripts/bs_ipy_starter.sh
```

Then Inside the ipython shell

```bash
RE(demo_sim_1d())
```

### With Queserver

Inside one terminal

```bash
./scripts/bs_qs_screen_starter.sh run
```

Inside another terminal

```bash
qserver environment open
```

```bash
qserver queue add plan '{"name": "demo_sim_1d"}'
qserver queue start
```

## Useful Bluesky Commands

command | description
--- | ---
`listObjects()` | show all ophyd devices available
`device_name.component_names` | show all parts of `device_name` (such as motors)
`device_name.summary()` | details of `device_name`

## SPEC to Bluesky Cheatsheet
Please refer to the cheatsheet below in case you need or desire to run commands directly through the ipython session
https://bcda-aps.github.io/bluesky_training/howto/bluesky_cheat_sheet.html
