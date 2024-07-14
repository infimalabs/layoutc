"""Spatial entities from/into PNG layouts."""

import io, numpy
from PIL import Image, PngImagePlugin

from .. import Size, Small, Large, GVK, Order, Quadrant, Unit, Depth
from .. import codec, entity


class Entity(entity.Entity):

    @classmethod
    def dump(cls, fp:io.BufferedWriter, codec:codec.Codec|None=None, /, **kwds):
        """Save PNG entities to a file pointer."""
        if codec is None:
            return fp.name.split('.')[-1] == cls.__module__.split('.')[-1]

        kwds = dict(
            creator="Infima Labs",
            date="2024-06-18T12:00:00-06:00",
            description="A collection of speedball layouts for VR tournaments.",
            title="Speedball Layout Pack",
        ) | kwds
        xmpmeta = ''.join(map(str.strip, f"""
            <x:xmpmeta xmlns:x="adobe:ns:meta/" xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#" xmlns:dc="http://purl.org/dc/elements/1.1/">
            <rdf:RDF><rdf:Description>{"".join(f"<dc:{k}>{kwds[k]}</dc:{k}>" for k in sorted(kwds))}</rdf:Description></rdf:RDF>
            </x:xmpmeta>
        """.split("\n")))

        pnginfo = PngImagePlugin.PngInfo()
        pnginfo.add_itxt("XML:com.adobe.xmp", xmpmeta, zip=True)
        image = Image.fromarray(numpy.flipud(codec.array()), "RGBA")
        image.save(fp, "PNG", optimize=True, pnginfo=pnginfo)

    @classmethod
    def load(cls, fp:io.BufferedReader, codec:codec.Codec|None=None, /, **kwds):
        """Load PNG entities from a file pointer."""
        if codec is None:
            return fp.peek(len(PngImagePlugin._MAGIC)).startswith(PngImagePlugin._MAGIC)

        with Image.open(fp) as image:
            array = numpy.flipud(numpy.array(image))

        match (array.shape[1] / array.shape[0]).as_integer_ratio():
            case 5, 4: size = Small
            case 4, 3: size = Large
            case 1, 1: size = Size
            case _: raise ValueError(f"Invalid PNG dimensions for spatial entities: {array.shape[1]}x{array.shape[0]}")

        h, w, s = -(-size.HEIGHT//codec.pitch), -(-size.WIDTH//codec.pitch), -(-array.shape[0]*codec.pitch//size.HEIGHT)
        h, w = h + 1 if h % 2 else h, w + 1 if w % 2 else w
        if array.shape[0] != s * h or array.shape[1] != s * w:
            raise ValueError(f"Invalid PNG dimensions for spatial entities: {array.shape[1]}x{array.shape[0]}")

        for j in range(s):
            for i in range(s):
                tile = array[h*j:h*(j+1), w*i:w*(i+1)]
                for v in range(h):
                    for u in range(w):
                        r, g, b, a = tile[v, u]
                        if a != GVK.DEFAULT:
                            o = Order(s*j+i+1)
                            q = Quadrant(((u < w // 2) ^ (3 * (v < h // 2))) + 1)
                            xyz = (abs(u - w//2) + r/Depth.HIRES - q.NWSW)*codec.pitch, (abs(v - h//2) + g/Depth.HIRES - q.SWSE)*codec.pitch, b/2**8*Unit.TURN
                            gvk = GVK(a & GVK.GROUP), GVK(a & GVK.VERSION), GVK(a & GVK.KIND)
                            codec.add(cls(o, q, *xyz, *gvk))
