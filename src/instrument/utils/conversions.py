"""
Miscellaneous conversion functions.

.. automodule::

    ~ts2iso
"""

import datetime


def ts2iso(ts: float, sep: str = " ") -> str:
    """Convert Python timestamp (float) to IS8601 time in current time zone."""
    return datetime.datetime.fromtimestamp(ts).isoformat(sep=sep)
