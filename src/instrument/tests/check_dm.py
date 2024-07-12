"""
Test to check if dm is working
"""

import os

for k, v in os.environ.items():
    if k.startswith("DM_"):
        print(f"{k=}  {v=}")
