# layoutc

[![PyPI](https://img.shields.io/pypi/v/layoutc.svg)](https://pypi.org/project/layoutc/)
[![Changelog](https://img.shields.io/github/v/release/infimalabs/layoutc?include_prereleases&label=changelog)](https://github.com/infimalabs/layoutc/releases)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/infimalabs/layoutc/blob/main/LICENSE)

`layoutc` is a command-line utility and Python library for encoding and decoding spatial entity layouts in speedball arena formats. It supports converting between JSON-based layout representations and PNG-based splatmap atlases.

Speedball is a competitive paintball format featuring symmetrical field layouts with inflatable bunkers. This tool helps manage and convert layout data between different formats used by tournament software, game engines, and visualization tools.

## Features

- Encode spatial entities from JSON layouts into PNG splatmap atlases.
- Decode spatial entities from PNG splatmap atlases into JSON layouts.
- Support for TSV (Tab-Separated Values) format for tabular data exchange.
- Customizable color depth and pixel pitch for encoding/decoding.
- Support for different spatial units (meters, degrees, turns).
- Quadrant-based spatial representation for efficient encoding/decoding.
- Automatic format detection based on file extensions and content.
- Extensible architecture for adding support for additional file formats.

## Installation

For development, clone the repository and install in editable mode:

```sh
git clone https://github.com/infimalabs/layoutc.git
cd layoutc
pip install -e .
```

Otherwise, install via PyPI:

```sh
pip install layoutc
```

## Quick Start

The most common use case is converting tournament layout files:

```sh
# Convert a JSON layout to PNG atlas for efficient storage
layoutc tournament_layout.json compact_atlas.png

# Convert PNG atlas back to JSON for editing
layoutc compact_atlas.png editable_layout.json

# Convert multiple layouts into a single atlas
layoutc layout1.json layout2.json layout3.json combined_atlas.png
```

For Python integration:

```python
from layoutc.codec import Codec

# Simple conversion example
codec = Codec()

# Load from any format (auto-detected)
with open("layout.json", "rb") as fp:
    codec.load(fp)

# Save to any format (auto-detected)
with open("atlas.png", "wb") as fp:
    codec.dump(fp)
```

## Usage

### Command-Line Interface

The `layoutc` command-line tool supports conversion between JSON, PNG, and TSV formats.

To encode multiple JSON layouts into a single PNG atlas:

```sh
layoutc layout1.json layout2.json atlas.png
```

To decode a PNG atlas into a JSON layout:

```sh
layoutc atlas.png layout.json
```

To convert a layout to TSV format:

```sh
layoutc layout.json layout.tsv
```

#### Command Syntax

```
layoutc [input ...] [output]
```

The last argument is treated as the output file, and all preceding arguments are input files. Use `-` for stdin/stdout.

#### Options

- `--depth {254,127}`: Set the color depth (default: 254).
- `--pitch {762,381}`: Set the pixel pitch in mm/px (default: 762).
- `--from ENTITY`: Set the input entity type (default: auto-detect).
- `--into ENTITY`: Set the output entity type (default: auto-detect).
- `-v, --verbose`: Show verbose traceback on error.

#### Format Detection

Input and output formats are automatically detected based on file extensions and content:
- `.json` files are treated as JSON layouts
- `.png` files are treated as PNG atlases
- `.tsv` files are treated as Tab-Separated Values
- Use `--from` and `--into` options to override auto-detection

### Python API

The `layoutc` library provides a `Codec` class for encoding and decoding spatial entities:

```python
from layoutc.codec import Codec
from layoutc.entity import Entity
from layoutc import Unit

# Create a codec with default settings
codec = Codec()

# === Common Use Case: Load and convert layout files ===
# Load from any supported format (JSON, PNG, TSV)
with open("tournament_layout.json", "rb") as fp:
    codec.load(fp)  # Automatically detects JSON format

# Save to any supported format
with open("atlas.png", "wb") as fp:
    codec.dump(fp)  # Automatically detects PNG format

# === Working with multiple layouts ===
codec.clear()
layout_files = ["layout1.json", "layout2.json", "layout3.json"]

for filename in layout_files:
    with open(filename, "rb") as fp:
        codec.load(fp)

# Save combined atlas
with open("combined_atlas.png", "wb") as fp:
    codec.dump(fp)

# === Displaying entity information ===
# Entities are stored in internal units but can be displayed in meters/degrees
print("Layout entities:")
for entity_data in codec:
    entity = Entity(*entity_data)
    # Convert to user-friendly units for display
    display_entity = entity.unfold(Unit.METER, Unit.DEGREE)
    print(f"Bunker at ({display_entity.x:.1f}m, {display_entity.y:.1f}m, {display_entity.z:.0f}°)")
```

#### Advanced: Format-specific handling

<details>
<summary>Click to expand advanced usage details</summary>

Different file formats have different unit assumptions:

- **JSON format**: Coordinates in meters and degrees (tournament data format)
- **TSV format**: Coordinates in internal units (millimeters and arc minutes)
- **PNG format**: Stores data in internal units

```python
from layoutc.entity import json as json_entity

# === Working directly with JSON data ===
json_data = {"xPosition": 1.5, "zPosition": 2.0, "yRotation": 90, "bunkerID": 2}
entity = json_entity.Entity.make(json_data)
codec.add(entity)

# === Working with TSV/internal units ===
entity = Entity(x=1500, y=2000, z=5400)  # 1.5m, 2m, 90° in internal units
codec.add(entity)

# === Unit conversion ===
# @ operator converts FROM internal units TO display units
display_entity = internal_entity @ Unit.METER @ Unit.DEGREE

# fold() method converts FROM display units TO internal units
internal_entity = Entity(x=1, y=1, z=90).fold(Unit.METER, Unit.DEGREE)
```

</details>
```

The `Entity` class represents a spatial entity (bunker) with `x`, `y`, `z` coordinates and metadata attributes `g` (group), `v` (version), and `k` (kind/bunker ID).

**Key concepts:**
- **JSON files**: Store coordinates in meters and degrees (tournament standard)
- **PNG atlases**: Efficient binary storage format for multiple layouts
- **TSV files**: Tab-separated format for debugging and data analysis
- **Automatic conversion**: The library handles unit conversions between formats transparently

#### Technical Details

<details>
<summary>Internal representation and unit conversion</summary>

The system uses internal units (millimeters and arc minutes) for storage and computation:

- **@ operator**: Converts FROM internal units TO display units (e.g., `entity @ Unit.METER @ Unit.DEGREE`)
- **fold() method**: Converts FROM display units TO internal units (e.g., `.fold(Unit.METER, Unit.DEGREE)`)
- **unfold() method**: Like @ operator but also handles quadrants properly

</details>

The `layoutc` module also provides enums and constants for working with spatial units, quadrants, and dimensions:

- `Unit`: Conversion factors (METER=1000, DEGREE=60, TURN=21600)
- `Quadrant`: Spatial quadrants (NE, NW, SW, SE)
- `Pitch`: Pixel resolution (LORES=762mm/px, HIRES=381mm/px)
- `Depth`: Color depth (LORES=127, HIRES=254)
- `GVK`: Group/Version/Kind attributes for entity classification
- `Order`: Atlas ordering for multi-layout collections

## Extending layoutc

`layoutc` can be extended to support additional file formats.

First, create an appropriately-named module under `layoutc.entity` (ie. `*.png` is `--from=layoutc.entity.png` and `*.json` is `--from=layoutc.entity.json`). Then, create an Entity subclass in the module and implement its `[auto]dump` and `[auto]load` classmethods.

Unless `--from` or `--into` is used, `layoutc.codec.Codec` selects the most-appropriate entity class for each input or output file based on either its extension (dump) or its magic (load).

## Development

This project uses Python >=3.10 and pip for dependency management and packaging.

To set up a development environment:

```sh
# Clone the repository
git clone https://github.com/infimalabs/layoutc.git
cd layoutc

# Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install in development mode with dev dependencies
pip install -e '.[dev]'

# Run tests
pytest -v
```

## License

`layoutc` is released under the MIT License. See [LICENSE](https://github.com/infimalabs/layoutc/blob/main/LICENSE) for more information.

## Troubleshooting

### Common Issues

**"No valid entities found in input files"**
- Check that your JSON file contains valid layout data with `xPosition`, `zPosition`, `yRotation`, and `bunkerID` fields
- Ensure PNG files contain non-zero alpha channel values (entities are stored in the alpha channel)
- Verify file format is supported (JSON, PNG, or TSV)

**"Atlas limit exceeded: cannot create more than 256 layout groups"**
- `layoutc` supports up to 256 separate layout groups in a single atlas
- Split large collections into multiple smaller atlas files
- Consider combining similar layouts into single groups if appropriate

**"X coordinate seems unusually large"**
- JSON format expects coordinates in meters and rotations in degrees
- TSV format uses internal units (millimeters and arc minutes)

**"Invalid PNG dimensions"**
- PNG atlases must have specific aspect ratios: 5:4 (standard), 4:3 (large), or 1:1 (maximum)
- Supported resolutions depend on pitch setting (762 or 381 mm/pixel)

**Format auto-detection issues**
- Use `--from` and `--into` options to override automatic format detection
- Ensure file extensions match content (.json for JSON, .png for PNG, .tsv for TSV)

### Performance Tips

- Use PNG format for storage of large layout collections (more efficient than JSON)
- Higher pitch values (762mm/px) create smaller files but lower spatial resolution
- Lower depth values (127 colors) create smaller files but may reduce precision
