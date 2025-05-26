__version__ = "2.2.0"

from enum import Enum

__all__ = ["PfsArm"]


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
