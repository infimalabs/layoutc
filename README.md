# layoutc

[![PyPI](https://img.shields.io/pypi/v/layoutc.svg)](https://pypi.org/project/layoutc/)
[![Changelog](https://img.shields.io/github/v/release/infimalabs/layoutc?include_prereleases&label=changelog)](https://github.com/infimalabs/layoutc/releases)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/infimalabs/layoutc/blob/main/LICENSE)

> **Copy-Paste Ready**: All Python examples work with `pip install -e .` and can be copied (or piped) directly into `python3`. Examples use the included tournament layout files.

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

To test any code block:

1. **Windows**: Copy the code, then paste into `python3`
2. **macOS**: Copy the code, then run `pbpaste | python3` in Terminal or paste into `python3`
3. **Linux**: Copy the code, then run `xclip -o | python3` in a terminal or paste into `python3`

If any example doesn't work, ensure you have:
- Python 3.10+ installed
- The `layoutc` repository cloned locally
- Your terminal is in the `layoutc` project directory
- Installed the package in editable mode: `pip install -e .`
- Tried `python3 -m layoutc …` instead if `layoutc …` fails
- Ensure your paste buffer contains what you expect

One use case is converting tournament layout files:

```sh
# Convert a single layout to PNG atlas for efficient storage
layoutc src/layouts/NXL-World-Cup-2021.json world_cup_2021.png

# Convert PNG atlas back to JSON for editing
layoutc world_cup_2021.png world_cup_2021_copy.json

# Convert all World Cup layouts into a single combined atlas
layoutc src/layouts/*World-Cup*.json all_world_cups.png

# Output all layouts as TSV to stdout (pipe-friendly)
layoutc src/layouts/*.json -
```

**Copy-paste test:**
```python
from layoutc.codec import Codec

codec = Codec()
with open("src/layouts/NXL-World-Cup-2021.json", "rb") as fp:
    codec.load(fp)

entities = list(codec)
print(f"✓ Loaded {len(entities)} entities from World Cup 2021")
print(f"✓ First entity: {entities[0]}")
```

**Complete workflow example:**
```python
from layoutc.codec import Codec
from layoutc.entity import Entity
from layoutc import Unit
import glob
import json

# Load and analyze tournament data
with open("src/layouts/NXL-Texas-2019.json", "r") as f:
    texas_data = json.load(f)
print(f"Loaded Texas 2019: {len(texas_data)} bunkers")

# Convert to different formats
codec = Codec()
with open("src/layouts/NXL-Texas-2019.json", "rb") as fp:
    codec.load(fp)

with open("texas_atlas.png", "wb") as fp:
    codec.dump(fp)

# Work with entities directly
for i, entity_data in enumerate(list(codec)[:3]):
    entity = Entity(*entity_data)
    display = entity.unfold(Unit.METER, Unit.DEGREE)
    print(f"Bunker {i+1}: ({display.x:.1f}m, {display.y:.1f}m, {display.z:.0f}°)")

# Create multi-layout atlas
codec.clear()
world_cup_files = glob.glob("src/layouts/NXL-World-Cup-*.json")
for filename in world_cup_files:
    with open(filename, "rb") as fp:
        codec.load(fp)

with open("all_world_cups.png", "wb") as fp:
    codec.dump(fp)
print(f"Created atlas from {len(world_cup_files)} World Cup layouts")
```

For Python integration:

```python
from layoutc.codec import Codec

codec = Codec()

with open("src/layouts/NXL-World-Cup-2021.json", "rb") as fp:
    codec.load(fp)

with open("world_cup_atlas.png", "wb") as fp:
    codec.dump(fp)

print("Converted NXL World Cup 2021 layout to PNG atlas!")
```

## Usage

### Command-Line Interface

The `layoutc` command-line tool supports conversion between JSON, PNG, and TSV formats.

To encode multiple JSON layouts into a single PNG atlas:

```sh
# Combine 4 years of World Cup tournament layouts into one atlas
layoutc src/layouts/NXL-World-Cup-{2018,2019,2020,2021}.json world_cups_atlas.png
```

To decode a PNG atlas into a JSON layout:

```sh
# Convert back from PNG to JSON
layoutc world_cups_atlas.png decoded_layouts.json
```

To convert a layout to TSV format:

```sh
# Convert single layout to TSV
layoutc src/layouts/NXL-Barcelona-2019.json barcelona.tsv
```

#### Command Syntax

```
layoutc [input ...] [output]
```

The last argument is treated as the output file, and all preceding arguments are input files. Use `-` for stdin/stdout.

Examples using the 23 included tournament layouts:
```sh
# Process all 23 tournament layouts to stdout as TSV
layoutc src/layouts/*.json -

# Create atlas from subset of tournaments
layoutc src/layouts/NXL-*2021*.json tournaments_2021.png

# Convert first layout to different formats
layoutc src/layouts/NXL-Amsterdam-2019.json amsterdam.png
layoutc src/layouts/NXL-Amsterdam-2019.json amsterdam.tsv

# Pipe to other tools (all examples work with pbpaste | python)
layoutc src/layouts/*.json - | head -10  # Show first 10 lines
```

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
import glob

# Create a codec with default settings
codec = Codec()

# Load and convert layout files
with open("src/layouts/NXL-European-Champs-2021.json", "rb") as fp:
    codec.load(fp)

with open("european_champs.png", "wb") as fp:
    codec.dump(fp)

# Working with multiple layouts
codec.clear()
layout_files = glob.glob("src/layouts/NXL-*2022*.json")

for filename in layout_files:
    with open(filename, "rb") as fp:
        codec.load(fp)

with open("tournaments_2022.png", "wb") as fp:
    codec.dump(fp)

print(f"Combined {len(layout_files)} 2022 tournament layouts into atlas!")

# Displaying entity information
codec.clear()
with open("src/layouts/NXL-Las-Vegas-2019.json", "rb") as fp:
    codec.load(fp)

print("Las Vegas 2019 Layout entities:")
for entity_data in codec:
    entity = Entity(*entity_data)
    display_entity = entity.unfold(Unit.METER, Unit.DEGREE)
    print(f"Bunker {entity.k} at ({display_entity.x:.1f}m, {display_entity.y:.1f}m, {display_entity.z:.0f}°)")
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
from layoutc.codec import Codec
from layoutc.entity import Entity
from layoutc import Unit
import json

codec = Codec()

# Working directly with JSON data
with open("src/layouts/NXL-Prague-2019.json", "r") as f:
    tournament_data = json.load(f)

first_bunker = tournament_data[0]
entity = json_entity.Entity.make(first_bunker)
codec.add(entity)

# Working with TSV/internal units
entity = Entity(x=1500, y=2000, z=5400)  # 1.5m, 2m, 90° in internal units
codec.add(entity)

# Unit conversion
display_entity = entity @ Unit.METER @ Unit.DEGREE
print(f"Display units: x={display_entity.x}m, y={display_entity.y}m, z={display_entity.z}°")

internal_entity = Entity(x=1, y=1, z=90).fold(Unit.METER, Unit.DEGREE)
print(f"Internal units: x={internal_entity.x}mm, y={internal_entity.y}mm, z={internal_entity.z} arc-min")
```

</details>

The `Entity` class represents a spatial entity (bunker) with `x`, `y`, `z` coordinates and metadata attributes `g` (group), `v` (version), and `k` (kind/bunker ID).

**Key concepts:**
- **JSON files**: Store coordinates in meters and degrees (tournament standard)
- **PNG atlases**: Efficient binary storage format for multiple layouts
- **TSV files**: Tab-separated format for debugging and data analysis
- **Automatic conversion**: The library handles unit conversions between formats transparently

#### Practical Examples

Here are complete, copy-pasteable examples using the included tournament data:

**Convert all tournaments to different formats:**
```python
from layoutc.codec import Codec
import glob

codec = Codec()
world_cup_files = glob.glob("src/layouts/NXL-World-Cup-*.json")
for filename in world_cup_files:
    with open(filename, "rb") as fp:
        codec.load(fp)

with open("world_cups_atlas.png", "wb") as fp:
    codec.dump(fp)
print(f"Created atlas from {len(world_cup_files)} World Cup layouts")
```

**Analyze tournament layout data:**
```python
import json

with open("src/layouts/NXL-Chicago-2019.json", "r") as f:
    layout_data = json.load(f)

print(f"Chicago 2019 has {len(layout_data)} bunkers:")
for bunker in layout_data[:3]:
    print(f"  Bunker {bunker['bunkerID']}: ({bunker['xPosition']:.1f}m, {bunker['zPosition']:.1f}m, {bunker['yRotation']:.0f}°)")
```

**Create atlas and convert back:**
```python
from layoutc.codec import Codec

# Round-trip conversion: JSON -> PNG -> JSON
codec = Codec()

with open("src/layouts/NXL-Barcelona-2019.json", "rb") as fp:
    codec.load(fp)

with open("barcelona_atlas.png", "wb") as fp:
    codec.dump(fp)

codec.clear()
with open("barcelona_atlas.png", "rb") as fp:
    codec.load(fp)

with open("barcelona_restored.json", "wb") as fp:
    codec.dump(fp)

# Save back as JSON
with open("barcelona_restored.json", "wb") as fp:
    codec.dump(fp)

print("Successfully round-tripped Barcelona layout: JSON -> PNG -> JSON")
```

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

# Try the examples with the included tournament data
layoutc src/layouts/*.json all_tournaments.png
layoutc src/layouts/NXL-World-Cup-2021.json world_cup.tsv
```

**Quick development test:**
```python
from layoutc.codec import Codec

codec = Codec()
with open("src/layouts/NXL-Amsterdam-2019.json", "rb") as fp:
    codec.load(fp)

print(f"Loaded {len(list(codec))} entities from Amsterdam 2019 layout")
for entity_data in list(codec)[:3]:
    print(f"  Entity: {entity_data}")
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
