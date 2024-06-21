"""Instrument registry"""

import logging

from ophydregistry import Registry as InstrumentRegistry

__all__ = ["InstrumentRegistry", "registry"]

log = logging.getLogger(__name__)


registry = InstrumentRegistry(auto_register=True, use_typhos=False)
