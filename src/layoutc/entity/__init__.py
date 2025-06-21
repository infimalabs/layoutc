"""Spatial base entity"""

import typing, collections, csv, io

from .. import Depth, Pitch, Unit, Order, Quadrant, GVK

if typing.TYPE_CHECKING:
    from .. import codec as _codec


class Entity(collections.namedtuple('Entity', (*'oqxyzgvk',), defaults=(Order.DEFAULT, Quadrant.DEFAULT, 0.0, 0.0, 0.0, GVK.DEFAULT, GVK.DEFAULT, GVK.DEFAULT))):
    """Spatial base entity."""

    o:Order
    q:Quadrant
    x:float
    y:float
    z:float
    g:GVK
    v:GVK
    k:GVK

    def __matmul__(self, /, *scales:Unit):
        """Scale the entity to the specified units."""
        match scales:
            case () | (Unit.UNIT,):
                return self
            case (Unit.UNIT, *froms):
                intos = Unit.UNIT,
            case (*intos, Unit.UNIT) | (*intos,):
                froms = Unit.UNIT,
        for a in froms:
            for b in intos:
                scale = a / b
                match a, b:
                    case (Unit.METER, _) | (_, Unit.METER):
                        self = self._replace(x=self.x * scale, y=self.y * scale)
                    case (Unit.DEGREE, _) | (_, Unit.DEGREE):
                        self = self._replace(z=self.z * scale)
        return self

    def __round__(self, /, ndigits:None|int=None, *, limit:None|Unit=None, angle:None|Unit=None):
        """Round the entity to the specified digits."""
        if limit is not None:
            self = self._replace(x=round(self.x / limit) * limit, y=round(self.y / limit) * limit)
        if angle is not None:
            self = self._replace(z=round(self.z / angle) * angle)
        if ndigits is not None:
            self = self._replace(x=round(self.x, ndigits), y=round(self.y, ndigits), z=round(self.z, ndigits))
        return self

    def fold(self, /, *froms:Unit, ndigits:None|int=6, limit:None|Unit=None, angle:None|Unit=None):
        """Fold the entity."""
        self = self.__matmul__(Unit.UNIT, *froms).__round__(ndigits)
        if self.q == Quadrant.DEFAULT:
            q = Quadrant(((self.x < 0) ^ (3 * (self.y < 0))) + 1)
            x, y, z = abs(self.x), abs(self.y), q.Z(self.z) % Unit.TURN
            g, v, k = GVK(self.g & GVK.GROUP), GVK(self.v & GVK.VERSION), GVK(self.k & GVK.KIND)
            self = self._replace(q=q, x=x, y=y, z=z, g=g, v=v, k=k)
        self = self.__round__(limit=limit, angle=angle)
        return self

    def unfold(self, /, *intos:Unit, ndigits:None|int=6, limit:None|Unit=None, angle:None|Unit=None):
        """Unfold the entity."""
        self = self.__round__(limit=limit, angle=angle)
        if self.q != Quadrant.DEFAULT:
            q = Quadrant.DEFAULT
            x, y, z = self.q.X(self.x), self.q.Y(self.y), self.q.Z(self.z) % Unit.TURN
            g, v, k = GVK(self.g & GVK.GROUP), GVK(self.v & GVK.VERSION), GVK(self.k & GVK.KIND)
            self = self._replace(q=q, x=x, y=y, z=z, g=g, v=v, k=k)
        self = self.__matmul__(*intos, Unit.UNIT).__round__(ndigits)
        return self

    def uv(self, pitch:Pitch, /, *, xaxis=0, yaxis=0) -> tuple[int, int]:
        """Return the UV coordinates."""
        u = int(self.q.X(self.x) + yaxis) // pitch - (self.q.NWSW and self.x % pitch == 0)
        v = int(self.q.Y(self.y) + xaxis) // pitch - (self.q.SWSE and self.y % pitch == 0)
        return u, v

    def rgba(self, pitch:Pitch, /) -> tuple[int, int, int, int]:
        """Return the RGBA color."""
        r = int(round(self.x % pitch / pitch * Depth.HIRES))
        g = int(round(self.y % pitch / pitch * Depth.HIRES))
        b = int(round(self.z % Unit.TURN / Unit.TURN * 2**8))
        a = int(GVK(self.g + self.v + self.k))
        return r, g, b, a

    def data(self, /) -> dict:
        """Return the entity data."""
        return self._asdict()

    @classmethod
    def make(cls, *args, **kwds):
        """Make an entity from data or keywords."""
        return cls(*args)._replace(**kwds) if kwds else cls(*args)

    @classmethod
    def dump(cls, fp:io.BufferedWriter, codec:typing.Union['_codec.Codec', None]=None, /, **kwds):
        """Save entities into a file pointer."""
        if codec is None:
            return bool(fp.name)

        with io.TextIOWrapper(fp, encoding="utf-8") as txtio:
            txtio.write("\t".join(cls._fields)+"\n")
            for args in codec:
                txtio.write("\t".join(map(str, args))+"\n")

    @classmethod
    def load(cls, fp:io.BufferedReader, codec:typing.Union['_codec.Codec', None]=None, /, **kwds):
        """Load entities from a file pointer."""
        if codec is None:
            peek = fp.peek(256)
            return bool(peek and peek[0] in (*b"0123456789", *map(ord, cls._fields)))

        peek = fp.peek(256)
        delimiter = "\t" if b"\t" in peek else "," if b"," in peek else " "
        with io.TextIOWrapper(fp, encoding="utf-8", newline='') as txtio:
            fields = cls._fields if peek and peek[0] in b"0123456789" else txtio.readline().split()
            for line in csv.reader(txtio, delimiter=delimiter):
                data = dict()
                for i, field in enumerate(fields):
                    match field:
                        case "o":
                            data["o"] = Order(int(line[i]))
                        case "q":
                            data["q"] = Quadrant(int(line[i]))
                        case "x" | "y" | "z":
                            data[field] = float(line[i])
                        case "g" | "v" | "k":
                            data[field] = GVK(int(line[i]))
                codec.add(cls(**data))
