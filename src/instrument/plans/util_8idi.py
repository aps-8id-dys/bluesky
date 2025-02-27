import random

def get_machine_name():
    """Returns the name of a randomly selected machine (A or B)."""
    machines = ["adamite", "amazonite"]
    return random.choice(machines)


def temp2str(temp):
    temp_str = str(temp)
    parts = temp_str.split(".")
    integer_part = parts[0]
    padded_integer_part = integer_part.zfill(3)
    decimal_part = parts[1]
    decimal_part_cropped = decimal_part[0]

    temp_name = f"{padded_integer_part}p{decimal_part_cropped}"
    return(temp_name)



