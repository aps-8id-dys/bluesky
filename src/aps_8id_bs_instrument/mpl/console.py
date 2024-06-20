"""
Configure matplotlib in interactive mode for IPython console
"""

__all__ = [
    "plt",
]

import logging

import matplotlib.pyplot as plt

logger = logging.getLogger(__name__)
logger.info(__file__)

plt.ion()
