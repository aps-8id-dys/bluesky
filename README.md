# 8-ID-I XPCS Bluesky Instrument

## Installation Steps
*aps_8id_bs_instrument* can also use *conda* for dependency management, and
*setuptools* for installation and development.

First, download the package from github:

```
git clone https://github.com/aps-8id-dys/bluesky 8id_bluesky_instrument
cd 8id_bluesky_instrument
git checkout dev-er
```

```
conda create -n your_env_name python=3.10
conda activate your_env_name
pip install -e ".[dev]"
```

## Running Bluesky Session
### With Ipython

```
cd scripts
./bs_ipy_starter.sh
```

Then Inside the ipython shell
```
RE(demo_sim_1d())
```

### With Queserver

Inside one terminal
```
cd scripts
./bs_qs_screen_starter.sh
```

Inside another terminal
```
qserver environment open
qserver queue add plan '{"name": "demo_sim_1d"}'
qserver queue start
```

## Spec to Bluesky Cheatsheet
Please Reference the below cheatsheet in case you need or desire to run commands directly through the ipython session
https://bcda-aps.github.io/bluesky_training/howto/bluesky_cheat_sheet.html
