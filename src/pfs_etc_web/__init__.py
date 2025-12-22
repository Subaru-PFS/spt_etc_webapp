try:
    from ._version import __version__
except ImportError:
    # Fallback for editable installs without build
    try:
        from setuptools_scm import get_version
        __version__ = get_version(root='../..', relative_to=__file__)
    except (ImportError, LookupError):
        __version__ = "0.0.0+unknown"

from enum import Enum

__all__ = ["PfsArm", "__version__"]


class PfsArm(Enum):
    """
    Enum for PFS arms.
    """

    def __new__(cls, value, label):
        obj = object.__new__(cls)  # bytes.__new__(cls, [value])
        obj._value_ = value
        obj.label = label
        return obj

    b = 0, "Blue"
    r = 1, "Red"
    n = 2, "Near-IR"
    m = 3, "Medium resolution"
