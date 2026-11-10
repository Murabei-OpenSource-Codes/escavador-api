"""Auxiliary module.

Implements the funcionalities as mixins added to main module."""
from .base import FetchBaseMixin
from .general import FetchGeneralMixin
from .process import FetchProcessMixin
from .related_process import FetchRelatedProcessMixin


__all__ = [
    "FetchBaseMixin", "FetchGeneralMixin", "FetchProcessMixin",
    "FetchRelatedProcessMixin"]