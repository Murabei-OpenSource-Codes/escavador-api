"""Auxiliary module.

Implements the funcionalities as mixins added to main module."""
from .base import BaseMixin
from .general import GeneralMixin
from .process import ProcessMixin
from .related_process import RelatedProcessMixin


__all__ = [
    "BaseMixin", "GeneralMixin", "ProcessMixin",
    "RelatedProcessMixin"]