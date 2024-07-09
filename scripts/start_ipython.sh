# start_ipython.sh

#!/bin/bash

# Check if the initialize.py file exists
if [[ ! -f src/instrument/ipython_startup.py ]]; then
    echo "initialize.py not found!"
    exit 1
fi

# Start IPython and run the initialize function
ipython -i -c "%run ipython_startup.py"
