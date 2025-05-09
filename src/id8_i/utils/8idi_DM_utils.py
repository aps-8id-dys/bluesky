"""
Data Management utilities for the 8ID-I beamline.

This module provides utility functions for Data Management (DM) operations,
including machine selection and temperature string formatting.
"""

import random


def get_machine_name():
    """Returns the name of a randomly selected machine (A or B)."""
    machines = ["adamite", "amazonite"]
    return random.choice(machines)


def temp2str(temp: float) -> str:
    """Convert a temperature value to a formatted string.

    Args:
        temp: Temperature value to convert

    Returns:
        Formatted string with padded integer part and single decimal place
        Example: 20.5 -> "020p5"
    """
    temp_str = str(temp)
    parts = temp_str.split(".")
    integer_part = parts[0]
    padded_integer_part = integer_part.zfill(3)
    decimal_part = parts[1]
    decimal_part_cropped = decimal_part[0]

    temp_name = f"{padded_integer_part}p{decimal_part_cropped}"
    return temp_name
