"""Spatial entity codec."""

import io, numpy, collections

from . import Size, Depth, Pitch, Unit, Order, Small
from .entity import Entity


class Codec:
    """Spatial entity codec."""

    def __init__(self, *tiles:dict, depth:None|Depth=None, pitch:None|Pitch=None, size:None|Size=Small):
        """Initialize the codec with optional depth, pitch, and atlas."""
        depth = Depth.HIRES if depth is None else depth
        pitch = Pitch.HIRES if pitch is None else pitch
        size = Small if size is None else size
        self.atlas: list[dict[tuple[int, int, int, int, int, int], set[int]]] = list(tiles)
        self.angle: float = 2**8 // depth / 2**8 * Unit.TURN
        self.limit: float = pitch / depth
        self.pitch: Pitch = pitch
        self.size: Size = size

    def __iter__(self, /, *, o:Order=Order.DEFAULT):
        """Iterate over the atlas."""
        s = slice(0, None) if o is Order.DEFAULT else slice(o-1, o)
        for i, tile in enumerate(self.atlas[s], s.start):
            for xyzgvk in tile:
                for q in tile[xyzgvk]:
                    yield Order(i+1), q, *xyzgvk

    def add(self, /, *es:Entity, o:Order=Order.DEFAULT):
        """Add a spatial entity to the atlas."""
        self.update(es, o=o==Order.DEFAULT and len(es)==1 and es[0].o or o)

    def remove(self, e:Entity, /, *, o:Order=Order.DEFAULT):
        """Remove a spatial entity from the atlas."""
        self.atlas[o==Order.DEFAULT and e.o or o-1][e.x, e.y, e.z, e.g, e.v, e.k].remove(e.q)

    def update(self, entities:list[Entity], /, *scales:Unit, o:Order=Order.DEFAULT):
        """Update the atlas with the provided spatial entities."""
        if o == Order.DEFAULT or o-1 == len(self.atlas):
            self.atlas.append(collections.defaultdict(set))
            o = Order(len(self.atlas))
        for e in entities:
            e = e.fold(*scales, limit=self.limit, angle=self.angle)
            self.atlas[o-1][e.x, e.y, e.z, e.g, e.v, e.k].add(e.q)

    def clear(self, *, o:Order=Order.DEFAULT):
        """Clear the atlas."""
        self.atlas.clear() if o is Order.DEFAULT else self.atlas[o-1].clear()

    def array(self, cls:type[Entity]=Entity, /) -> numpy.ndarray:
        """Encode the atlas as an array."""
        h, w, s = -(-self.size.HEIGHT//self.pitch), -(-self.size.WIDTH//self.pitch), -int(-len(self.atlas)**0.5//1)
        h, w = h + 1 if h % 2 else h, w + 1 if w % 2 else w
        xaxis, yaxis = h * self.pitch // 2, w * self.pitch // 2
        array = numpy.zeros((s**2, h, w, 4), dtype=numpy.uint8)
        for args in self:
            e = cls(*args)
            if e.x < yaxis and e.y < xaxis:
                u, v = e.uv(self.pitch, xaxis=xaxis, yaxis=yaxis)
                array[e.o-1, v, u] = e.rgba(self.pitch)
        array = array.reshape(s, s, *array.shape[1:])
        array = numpy.concatenate(array, axis=1)
        array = numpy.concatenate(array, axis=1)
        return array

    def dump(self, fp:io.BufferedWriter, cls:type[Entity]|None=None, /, **kwds):
        """Dump entities into a file pointer."""
        if cls is not None:
            return cls.dump(fp, self, **kwds)
        for cls in Entity.__subclasses__():
            if cls.dump(fp):
                return cls.dump(fp, self, **kwds)
        return Entity.dump(fp, self, **kwds)

    def load(self, fp:io.BufferedReader, cls:type[Entity]|None=None, /, **kwds):
        """Load entities from a file pointer."""
        if cls is not None:
            return cls.load(fp, self, **kwds)
        for cls in Entity.__subclasses__():
            if cls.load(fp):
                return cls.load(fp, self, **kwds)
        return Entity.load(fp, self, **kwds)
