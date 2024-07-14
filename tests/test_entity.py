"""
Test suite for the Entity class in the layoutc module.

This module contains tests for various methods and behaviors of the Entity class,
including folding/unfolding, UV mapping, RGBA encoding, and unit conversions.
"""

import pytest
from unittest import mock

import layoutc.entity
import layoutc.entity.png
import layoutc.entity.json
from layoutc import GVK, Unit, Quadrant, Pitch, Order


@pytest.mark.parametrize("input_coords, expected", [
    ((0, 0, 0), (Quadrant.NE, 0, 0, 0)),
    ((1, 1, 90), (Quadrant.NE, 1000, 1000, 5400)),
    ((-1, 1, 180), (Quadrant.NW, 1000, 1000, 10800)),
    ((-1, -1, 270), (Quadrant.SW, 1000, 1000, 16200)),
    ((1, -1, 360), (Quadrant.SE, 1000, 1000, 0)),
    ((0.5, -0.5, 450), (Quadrant.SE, 500, 500, 16200)),
])
def test_entity_fold(input_coords, expected):
    """Test Entity.Fold() method with various input coordinates."""
    e = layoutc.entity.Entity(x=input_coords[0], y=input_coords[1], z=input_coords[2])
    folded = e.fold(Unit.METER, Unit.DEGREE)
    assert (folded.q, folded.x, folded.y, folded.z) == expected


@pytest.mark.parametrize("input_data, expected", [
    ((Quadrant.NE, 1000, 1000, 5400), (1, 1, 90)),
    ((Quadrant.NW, 1000, 1000, 10800), (-1, 1, 180)),
    ((Quadrant.SW, 1000, 1000, 16200), (-1, -1, 270)),
    ((Quadrant.SE, 1000, 1000, 21600), (1, -1, 0)),
    ((Quadrant.SE, 500, 500, 27000), (0.5, -0.5, 270)),
])
def test_entity_unfold(input_data, expected):
    """Test Entity.Unfold() method with various input quadrants and coordinates."""
    e = layoutc.entity.Entity(q=input_data[0], x=input_data[1], y=input_data[2], z=input_data[3])
    unfolded = e.unfold(Unit.METER, Unit.DEGREE)
    assert (unfolded.x, unfolded.y, unfolded.z) == expected


@pytest.mark.parametrize("pitch, xaxis, yaxis, expected", [
    (Pitch.LORES, 19050, 22860, (31, 26)),
    (Pitch.HIRES, 19050, 22860, (62, 52)),
    (Pitch.LORES, 0, 0, (1, 1)),
])
def test_entity_uv(pitch, xaxis, yaxis, expected):
    """Test Entity.UV() method with different pitches and axis values."""
    e = layoutc.entity.Entity(q=Quadrant.NE, x=1000, y=1000)
    u, v = e.uv(pitch, xaxis=xaxis, yaxis=yaxis)
    assert (u, v) == expected


@pytest.mark.parametrize("x, y, z, g, v, k, pitch, expected", [
    (381, 381, 5400, GVK.OVERLAY, GVK.N1, GVK.N2, Pitch.LORES, (127, 127, 64, 195)),
    (0, 0, 0, GVK.DEFAULT, GVK.DEFAULT, GVK.DEFAULT, Pitch.LORES, (0, 0, 0, 0)),
    (762, 762, 10800, GVK.FEATURE, GVK.N2, GVK.N3, Pitch.LORES, (0, 0, 128, 133)),
])
def test_entity_rgba(x, y, z, g, v, k, pitch, expected):
    """Test Entity.RGBA() method with various input values."""
    e = layoutc.entity.Entity(x=x, y=y, z=z, g=g, v=v, k=k)
    rgba = e.rgba(pitch)
    assert rgba == expected


@pytest.mark.parametrize("input_data, units, expected", [
    ((1000, 1000, 5400), (Unit.METER,), (1, 1, 5400)),
    ((1, 1, 90), (Unit.UNIT,), (1, 1, 90)),
    ((500, 500, 10800), (Unit.METER, Unit.DEGREE), (0.5, 0.5, 180)),
])
def test_entity_matmul(input_data, units, expected):
    """Test Entity.__matmul__() method for unit conversions."""
    e = layoutc.entity.Entity(x=input_data[0], y=input_data[1], z=input_data[2])
    scaled = e
    for unit in units:
        scaled = scaled @ unit
    assert (scaled.x, scaled.y, scaled.z) == expected


def test_entity_round():
    """Test Entity.__round__() method."""
    e = layoutc.entity.Entity(x=1.23456, y=2.34567, z=89.6)
    rounded = round(e, 2)
    assert (rounded.x, rounded.y, rounded.z) == (1.23, 2.35, 89.6)


def test_entity_defaults():
    """Test Entity default values."""
    e = layoutc.entity.Entity()
    assert e == (Order.DEFAULT, Quadrant.DEFAULT, 0.0, 0.0, 0.0, GVK.DEFAULT, GVK.DEFAULT, GVK.DEFAULT)


def test_entity_dump_load():
    """Test Entity.dump() and Entity.load()."""
    fp = mock.MagicMock()

    fp.name = ""
    fp.peek.return_value = b""
    assert layoutc.entity.Entity.dump(fp) == False
    assert layoutc.entity.Entity.load(fp) == False

    fp.name = "layout.json"
    fp.peek.return_value = b"["
    assert layoutc.entity.Entity.dump(fp) == True
    assert layoutc.entity.Entity.load(fp) == False

    fp.name = "layout.png"
    fp.peek.return_value = layoutc.entity.png.PngImagePlugin._MAGIC
    assert layoutc.entity.Entity.dump(fp) == True
    assert layoutc.entity.Entity.load(fp) == False

    fp.name = "layout.tsv"
    for field in layoutc.entity.Entity._fields:
        fp.peek.return_value = bytes(field, "utf-8")
        assert layoutc.entity.Entity.dump(fp) == True
        assert layoutc.entity.Entity.load(fp) == True


def test_entity_dump_load_png():
    """Test Entity.dump() and Entity.load() for PNG entities."""
    fp = mock.MagicMock()

    fp.name = ""
    fp.peek.return_value = b""
    assert layoutc.entity.png.Entity.dump(fp) == False
    assert layoutc.entity.png.Entity.load(fp) == False

    fp.name = "layout.tsv"
    fp.peek.return_value = b""
    assert layoutc.entity.png.Entity.dump(fp) == False
    assert layoutc.entity.png.Entity.load(fp) == False

    fp.name = "layout.png"
    fp.peek.return_value = b""
    assert layoutc.entity.png.Entity.dump(fp) == True
    assert layoutc.entity.png.Entity.load(fp) == False

    fp.peek.return_value = layoutc.entity.png.PngImagePlugin._MAGIC
    assert layoutc.entity.png.Entity.dump(fp) == True
    assert layoutc.entity.png.Entity.load(fp) == True


def test_entity_dump_load_json():
    """Test Entity.dump() and Entity.load() for JSON entities."""
    fp = mock.MagicMock()

    fp.name = ""
    fp.peek.return_value = b""
    assert layoutc.entity.json.Entity.dump(fp) == False
    assert layoutc.entity.json.Entity.load(fp) == False

    fp.name = "layout.tsv"
    fp.peek.return_value = b""
    assert layoutc.entity.json.Entity.dump(fp) == False
    assert layoutc.entity.json.Entity.load(fp) == False

    fp.name = "layout.json"
    fp.peek.return_value = b""
    assert layoutc.entity.json.Entity.dump(fp) == True
    assert layoutc.entity.json.Entity.load(fp) == False

    fp.peek.return_value = b"["
    assert layoutc.entity.json.Entity.dump(fp) == True
    assert layoutc.entity.json.Entity.load(fp) == False

    fp.peek.return_value = b"[0"
    assert layoutc.entity.json.Entity.dump(fp) == True
    assert layoutc.entity.json.Entity.load(fp) == False

    fp.peek.return_value = b"[{"
    assert layoutc.entity.json.Entity.dump(fp) == True
    assert layoutc.entity.json.Entity.load(fp) == True

    fp.peek.return_value = b"[["
    assert layoutc.entity.json.Entity.dump(fp) == True
    assert layoutc.entity.json.Entity.load(fp) == True
