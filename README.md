# layoutc

[![PyPI](https://img.shields.io/pypi/v/layoutc.svg)](https://pypi.org/project/layoutc/)
[![Changelog](https://img.shields.io/github/v/release/infimalabs/layoutc?include_prereleases&label=changelog)](https://github.com/infimalabs/layoutc/releases)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/infimalabs/layoutc/blob/main/LICENSE)

`layoutc` is a command-line utility and Python library for encoding and decoding spatial entity layouts in speedball arena formats. It supports converting between JSON-based layout representations and PNG-based splatmap atlases.

## Features

- Encode spatial entities from JSON layouts into PNG splatmap atlases.
- Decode spatial entities from PNG splatmap atlases into JSON layouts.
- Customizable color depth and pixel pitch for encoding/decoding.
- Support for different spatial units (meters, degrees, turns).
- Quadrant-based spatial representation for efficient encoding/decoding.
- Extensible architecture for adding support for additional file formats.

## Installation

Install `layoutc` using `pip`:

```sh
pip install layoutc
```

## Usage

### Command-Line Interface

To encode multiple JSON layouts into a single PNG atlas:

```sh
layoutc layout1.json layout2.json --output atlas.png
```

To decode a PNG atlas into a JSON layout:

```sh
layoutc atlas.png --output layout.json
```

Options:
- `--depth DEPTH`: Set the color depth (default: 254 colors).
- `--pitch PITCH`: Set the pixel pitch (default: 762 mm/px).
- `--from ENTITY`: Set the input entity (default: auto-detect).
- `--into ENTITY`: Set the output entity (default: auto-detect).
- `--output FILE`: Set the output file (default: layout.png).

### Python API

The `layoutc` library provides a `Codec` class for encoding and decoding spatial entities:

```python
from layoutc.codec import Codec
from layoutc.entity import Entity
from layoutc.entity import png

# Create a codec with default settings
codec = Codec()

# Add spatial entities to codec
codec.add(Entity(x=0, y=0, z=0))
codec.add(Entity(x=1, y=1, z=90))

# Manually encode entities as "PNGGG" atlas
with open("atlas.pnggg", "wb") as fp:
    codec.dump(fp, png.Entity)

# Access decoded entities
for entity in codec:
    print(entity)

# Clear codec of all entities
codec.clear()

# Manually decode "PNGGG" atlas back into entities
with open("atlas.pnggg", "rb") as fp:
    codec.load(fp, png.Entity)

# Automatically encode entities as PNG atlas
with open("atlas.png", "wb") as fp:
    codec.dump(fp)

# Access decoded entities
for entity in codec:
    print(entity)

# Clear codec of all entities
codec.clear()

# Automatically decode PNG atlas back into entities
with open("atlas.png", "rb") as fp:
    codec.load(fp)

# Access decoded entities
for entity in codec:
    print(entity)

# Clear codec of all entities
codec.clear()
```

The `Entity` class represents a spatial entity with `x`, `y`, `z` coordinates, as well as `g` (group), `v` (version), and `k` (kind) attributes.

The `layoutc` module also provides enums and constants for working with spatial units, quadrants, and PNG atlas sizes.

## Extending layoutc

`layoutc` can be extended to support additional file formats.

First, create an appropriately-named module under `layoutc.entity` (ie. `*.png` is `--from=layoutc.entity.png` and `*.json` is `--from=layoutc.entity.json`). Then, create an Entity subclass in the module and implement its `[auto]dump` and `[auto]load` classmethods.

Unless `--from` or `--into` is used, `layoutc.codec.Codec` selects the most-appropriate entity class for each input or output file based on either its extension (dump) or its magic (load).

## Development

This project uses Python >=3.10 and pip for dependency management and packaging.

Create and activate a virtualenv, install `layoutc` as an editable development package, and run tests with:

```sh
python3 -m venv .venv
. .venv/bin/activate
pip install -e '.[dev]'
pytest -v
```

## License

`layoutc` is released under the MIT License. See [LICENSE](https://github.com/infimalabs/layoutc/blob/main/LICENSE) for more information.
