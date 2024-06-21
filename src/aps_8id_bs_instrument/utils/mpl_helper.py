"""
configure matplotlib for console or notebook session
MUST be run BEFORE other initializations
"""


def isnotebook():  # noqa D103
    try:
        from IPython import get_ipython  # noqa

        _ipython = get_ipython()
        if _ipython is not None:
            shell = _ipython.__class__.__name__
            return shell == "ZMQInteractiveShell"
        return False
    except NameError:
        return False


if isnotebook():  # noqa D103
    # %matplotlib notebook
    _ipython = get_ipython()  # noqa F821
    if _ipython is not None:
        # _ipython.magic("matplotlib notebook")
        _ipython.magic("matplotlib inline")
    import matplotlib.pyplot as plt

    plt.ion()
else:
    import matplotlib.pyplot as plt

    plt.ion()
