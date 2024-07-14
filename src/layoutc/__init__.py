"""Spatial types."""

import enum


class Size:
    """Maximum size 97.536 x 97.536 m (320 x 320 ft)."""
    WIDTH, HEIGHT = 97536, 97536


class Small(Size, enum.IntEnum):
    """Standard size 45.72 x 36.576 m (150 x 120 ft)."""
    WIDTH, HEIGHT = 45720, 36576


class Large(Size, enum.IntEnum):
    """Extended size 60.96 x 45.72 m (200 x 150 ft)."""
    WIDTH, HEIGHT = 60960, 45720


class Unit(enum.IntEnum):
    """Spatial units conversion factors."""
    UNIT, METER, DEGREE, TURN = 1, 1000, 60, 21600


class Pitch(enum.IntEnum):
    """Spatial pixel resolution (millimeters)."""
    LORES, HIRES = 762, 381


class Depth(enum.IntEnum):
    """Spatial channel resolution (colors)."""
    HIRES, LORES = 254, 127


class GVK(enum.IntEnum):
    """Group, Version, Kind (GVK) for encoding spatial entities."""
    ALTERNATE, DEFAULT = 32, 0
    OVERLAY, FEATURE, TERRAIN = 192, 128, 64
    GVK, GROUP, VERSION, KIND = 255, 192, 32, 31
    locals().update((f'N{n}', n) for n in range(1, 256))


class Order(enum.IntEnum):
    """Spatial atlas order."""
    DEFAULT = 0; locals().update((f'N{n}', n) for n in range(1, 2**8+1))


class Quadrant(enum.IntEnum):
    """Spatial quadrant."""

    DEFAULT = 0; NE, NW, SW, SE = range(1, 5)

    NENW:bool = property(lambda self: self and self in (self.NE, self.NW))
    NESW:bool = property(lambda self: self and self in (self.NE, self.SW))
    NESE:bool = property(lambda self: self and self in (self.NE, self.SE))
    NWSW:bool = property(lambda self: self and self in (self.NW, self.SW))
    NWSE:bool = property(lambda self: self and self in (self.NW, self.SE))
    SWSE:bool = property(lambda self: self and self in (self.SW, self.SE))

    X:float = lambda self, x=1.0: 0.0 if not self else x if self.NESE else -x
    Y:float = lambda self, y=1.0: 0.0 if not self else y if self.NENW else -y
    Z:float = lambda self, z=1.0: 0.0 if not self else z if self.NESW else -z
