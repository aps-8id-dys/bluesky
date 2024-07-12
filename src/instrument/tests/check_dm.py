import os
for k, v in os.environ.items():
    if k.startswith("DM_"):
        print(f"{k=}  {v=}")
 