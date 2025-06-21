"""Test codec."""

import pytest
import numpy
from PIL import Image

from layoutc import Depth, Pitch, Unit, GVK, Small
from layoutc.codec import Codec
from layoutc.entity import Entity


@pytest.mark.parametrize("pitch, depth, size, expected", [
    (Pitch.HIRES, Depth.HIRES, (120, 96), [
        ((60, 48), (  1,   1,   1, 192)),
        ((61, 48), (  0,   1,   1, 192)),
        ((60, 49), (  1,   0,   1, 192)),
        ((61, 49), (  0,   0,  64, 193)),
        ((62, 50), (  0,   0, 128, 194)),
        ((63, 51), (253, 253, 192, 195)),
        ((64, 52), (  1,   1,   0, 196)),
        ((65, 53), (  1,   1, 192, 197)),
        ((66, 54), (  2,   2, 128, 198)),
        ((67, 55), (  3,   3,  64, 199)),
        ((68, 56), (  3,   3,   0, 200)),
    ]),
    (Pitch.HIRES, Depth.LORES, (120, 96), [
        ((60, 48), (  0,   0,   0, 192)),
        ((61, 48), (  0,   0,   0, 192)),
        ((60, 49), (  0,   0,   0, 192)),
        ((61, 49), (  0,   0,  64, 193)),
        ((62, 50), (  0,   0, 128, 194)),
        ((63, 51), (252, 252, 192, 195)),
        ((64, 52), (  0,   0,   0, 196)),
        ((65, 53), (  2,   2, 192, 197)),
        ((66, 54), (  2,   2, 128, 198)),
        ((67, 55), (  2,   2,  64, 199)),
        ((68, 56), (  4,   4,   0, 200)),
    ]),
    (Pitch.LORES, Depth.HIRES, (60, 48), [
        ((30, 24), (  0,   0,   1, 192)),
        ((31, 24), (  0,   0,   1, 192)),
        ((30, 25), (  0,   0,   1, 192)),
        ((31, 25), (  0,   0,  64, 193)),
        ((32, 26), (  0,   0, 128, 194)),
        ((33, 27), (253, 253, 192, 195)),
        ((34, 28), (  0,   0,   0, 196)),
        ((35, 29), (  1,   1, 192, 197)),
        ((36, 30), (  1,   1, 128, 198)),
        ((37, 31), (  1,   1,  64, 199)),
        ((38, 32), (  2,   2,   0, 200)),
    ]),
    (Pitch.LORES, Depth.LORES, (60, 48), [
        ((30, 24), (  0,   0,   0, 192)),
        ((31, 24), (  0,   0,   0, 192)),
        ((30, 25), (  0,   0,   0, 192)),
        ((31, 25), (  0,   0,  64, 193)),
        ((32, 26), (  0,   0, 128, 194)),
        ((33, 27), (252, 252, 192, 195)),
        ((34, 28), (  0,   0,   0, 196)),
        ((35, 29), (  0,   0, 192, 197)),
        ((36, 30), (  0,   0, 128, 198)),
        ((37, 31), (  2,   2,  64, 199)),
        ((38, 32), (  2,   2,   0, 200)),
    ]),
])
def test_codec(request, pitch, depth, size, expected):
    """Test codec with a list of entities."""

    codec = Codec(depth=depth, pitch=pitch)

    assert codec.pitch == pitch
    assert codec.limit == pitch / depth
    assert codec.angle == 2**8 // depth / 2**8 * Unit.TURN

    codec.update(
        Entity(**kwds).fold(Unit.DEGREE)
        for j in range(-1, 2, 2) for i in range(-1, 2, 2) for kwds in (
            {"x": i, "y": j, "z": i*j, "g": GVK.OVERLAY, "k": 0},
            {"x": i, "y": j*pitch, "z": i*j, "g": GVK.OVERLAY, "k": 0},
            {"x": i*pitch, "y": j, "z": i*j, "g": GVK.OVERLAY, "k": 0},
            {"x": i*pitch, "y": j*pitch, "z": i*j*90, "g": GVK.OVERLAY, "k": 1},
            {"x": i*pitch*2, "y": j*pitch*2, "z": i*j*180, "g": GVK.OVERLAY, "k": 2},
            {"x": i*(pitch*4-pitch/depth), "y": j*(pitch*4-pitch/depth), "z": i*j*270, "g": GVK.OVERLAY, "k": 3},
            {"x": i*(pitch*4+1), "y": j*(pitch*4+1), "z": i*j*360, "g": GVK.OVERLAY, "k": 4},
            {"x": i*(pitch*5+2), "y": j*(pitch*5+2), "z": i*j*-90, "g": GVK.OVERLAY, "k": 5},
            {"x": i*(pitch*6+3), "y": j*(pitch*6+3), "z": i*j*-180, "g": GVK.OVERLAY, "k": 6},
            {"x": i*(pitch*7+4), "y": j*(pitch*7+4), "z": i*j*-270, "g": GVK.OVERLAY, "k": 7},
            {"x": i*(pitch*8+5), "y": j*(pitch*8+5), "z": i*j*-360, "g": GVK.OVERLAY, "k": 8},
        )
    )

    image = Image.fromarray(numpy.flipud(codec.array()), "RGBA")

    if request.config.getoption("--save"):
        image.save(request.node.name + ".png")

    assert image.mode == "RGBA"
    assert image.size == size

    pixels = image.load()

    xaxis, yaxis = size[1]//2, size[0]//2
    for (u, v), pixel in expected:
        n, m = u - yaxis, v - xaxis
        assert pixels[u, v] == pixel
        assert pixels[u-1-2*n, v] == pixel
        assert pixels[u, v-1-2*m] == pixel
        assert pixels[u-1-2*n, v-1-2*m] == pixel


def test_order_limit_validation():
    """Test that Order limit is enforced."""
    codec = Codec()

    # Should work up to 256
    for i in range(1, 257):
        codec.update([])
        assert len(codec.atlas) == i

    # Should fail at 257
    with pytest.raises(Codec.AtlasLimitExceededError, match="Atlas limit exceeded"):
        codec.update([])


if __name__ == "__main__":
    pytest.main([__file__])
