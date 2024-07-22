# 8-ID-I XPCS Bluesky Instrument

## Installation Steps
*aps_8id_bs_instrument* can also use *conda* for dependency management, and
*setuptools* for installation and development.

First, download the package from github:

```bash
$ git clone https://github.com/aps-8id-dys/bluesky 8id_bluesky_instrument
$ cd 8id_bluesky_instrument
$ git checkout dev-er
```

Then create the conda environment with mamba:

```bash
$ export ENV_NAME="aps_bs_env"
$ conda create -n $ENV_NAME -f environment.yml
$ conda activate $ENV_NAME
$ pip install -e ".[dev]"
```

## At! This will later on be merged into main, as such the readme is still under construction