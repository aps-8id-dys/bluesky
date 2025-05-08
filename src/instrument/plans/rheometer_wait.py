import datetime

from bluesky import plan_stubs as bps

from ..devices.rheometer_wait_signal import mcr_wait_signal


def wait_for_mcr(delay_time=0.01):
    print("Waiting for the MCR Rheometer to change FROM THE OLD STATE")
    print(datetime.datetime.now())

    current_value = mcr_wait_signal.pulse_count.get()

    while mcr_wait_signal.pulse_count.get() == current_value:
        yield from bps.sleep(0.1)

    print("MCR Rheometer changed to the NEW MEASUREMENT STATE")
    print(datetime.datetime.now())

    yield from bps.sleep(delay_time)
