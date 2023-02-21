"""
Test the Lambda2M area detector.

Load this file::

    %run -i ./user/Lambda2M_Test_bps.py
"""
import numpy as np

from bluesky import plan_stubs as bps
from bluesky import plans as bp
from instrument.collection import *  # Yikes!  Starts the bluesky instrument!
# from instrument.devices import *  # imported with collection
# from instrument.framework import RE  # imported with collection


def Rep_Acq(acq_rep=3):

    yield from prepare_count(
        lambda2M.hdf1,
        "Test",
        0.001,
        0.001,
        n_images=10000,
        compression="None",
        auto_save="No",
    )

    lambda2M.hdf1.file_number.put(0)
    lambda2M.hdf1.file_template.put("%s%s_%6.6d.h5")
    lambda2M.hdf1.file_path.put("/home/8ididata/2023-1/bluesky202301")

    for ii in range(acq_rep):
        print(ii)
        yield from bp.count([lambda2M])
