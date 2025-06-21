"""Spatial entities from/into JSON layouts."""

import io, json, typing

from .. import GVK, Unit, Quadrant
from .. import entity

if typing.TYPE_CHECKING:
    from .. import codec


class Entity(entity.Entity):

    def data(self, /) -> dict:
        """Return the data from the entity."""
        q, self = self.q, self.unfold(Unit.METER, Unit.DEGREE)
        # Offset negative zero by 1/2**20 towards its negative dimension, requiring 7 significant
        # digits in base-10. Since folding only retains 6-of-the-7 significant digits, this offset
        # both communicates the quadrant and ensures the X and Y components re-round back to zero.
        if q.NWSW and not self.x:
            self = self._replace(x=q.X(1/2**20))
        if q.SWSE and not self.y:
            self = self._replace(y=q.Y(1/2**20))
        aliases = dict(x='xPosition', y='zPosition', z='yRotation', k='bunkerID')
        data = {aliases[name]: getattr(value, 'value', value)
            for name, value in super().data().items() if name in aliases if aliases[name] is not None}
        return data | dict(xRotation=0.0, zRotation=0.0, yPosition=0.0)

    @classmethod
    def make(cls, data, **aliases):
        """Return the entity from the specified data."""
        aliases = aliases or dict(xPosition="x", zPosition="y", yRotation="z", bunkerID="k")
        kwds = {aliases[name]: value for name, value in data.items() if aliases.get(name) is not None}
        self = super().make(g=GVK.OVERLAY, **kwds).fold(Unit.METER, Unit.DEGREE)
        return self

    @classmethod
    def dump(cls, fp:io.BufferedWriter, codec:"codec.Codec|None"=None, /, **kwds):
        """Save JSON entities to a file pointer."""
        if codec is None:
            return fp.name.split('.')[-1] == cls.__module__.split('.')[-1]

        items = [[cls(*args).data() for args in codec.__iter__(o=o)] for o in range(1, len(codec.atlas)+1)]
        items = items[0] if len(items) == 1 else items
        with io.TextIOWrapper(fp, encoding='utf-8') as txtio:
            json.dump(items, txtio, sort_keys=True, indent=2)

    @classmethod
    def load(cls, fp:io.BufferedReader, codec:"codec.Codec|None"=None, /, **kwds):
        """Load JSON entities from a file pointer."""
        if codec is None:
            return fp.peek(256).translate(None, delete=b' \t\r\n').startswith((b'[[', b'[{'))

        li = json.load(fp, object_hook=cls.make)
        li = li if isinstance(li, list) else [li]
        li = li if isinstance(li[0], list) else [li]
        for es in li:
            codec.update(es)
