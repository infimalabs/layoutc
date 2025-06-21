# Entity Encoding Scheme

## Coordinate System and Quadrants

The Entity class uses a quadrant-based coordinate system to represent spatial entities. The space is divided into four quadrants:

- NE (Quadrant.NE): x > 0, y > 0
- NW (Quadrant.NW): x < 0, y > 0
- SW (Quadrant.SW): x < 0, y < 0
- SE (Quadrant.SE): x > 0, y < 0

In the folded state, all coordinates are positive, with the quadrant information determining the actual position in space. This approach allows for consistent rounding and mirroring transformations regardless of the entity's position.

## Internal Units and Conversions

The Entity class uses the following internal units:
- Distance: millimeters
- Rotation: arc minutes (1 degree = 60 arc minutes)

## Folding and Unfolding Operations

### Folding

The Fold operation converts external coordinates (typically in meters and degrees) to internal coordinates (millimeters and arc minutes) and determines the appropriate quadrant.

Example:
- Input: (1m, 1m, 90°)
- Folded: (Quadrant.NE, 1000mm, 1000mm, 5400 arc minutes)

### Unfolding

The Unfold operation reverses the folding process, converting internal coordinates back to external units and applying the quadrant information to determine sign.

Example:
- Input: (Quadrant.NW, 1000mm, 1000mm, 10800 arc minutes)
- Unfolded: (-1m, 1m, 180°)

### Rotation Handling

Rotation is affected by the quadrant:
- NE and SW: Positive rotation
- NW and SE: Negative rotation

This quadrant-based rotation system ensures consistent behavior across all quadrants, analogous to labeling quadrants on a square cloth and folding all negatives beneath the positives, or similarly, meshing gears from each quadrant and rotating NE/SW in the positive direction (counterclockwise) and NW/SE in the negative direction (clockwise). Additionally, southern-quadrant entities are stored using angles offset by π (180˚), as if 0˚ simply started there instead of where it does. These two rotational corrections significantly reduce the total pixel variance, and thus reduces the overall file size.

## RGBA Encoding

The RGBA method encodes entity information into a 4-tuple of 8-bit unsigned integers:

- R: x-coordinate modulo pitch
- G: y-coordinate modulo pitch
- B: z-coordinate (rotation) mapped to 0-255 range
- A: GVK (Group, Version, Kind) information

For the z-coordinate, 360 degrees (21600 arc minutes) is mapped to the 0-255 range.

## UV Mapping

UV mapping converts the entity's coordinates to pixel coordinates in an image, accounting for pitch (pixel size) and axis offsets.

Calculation:
- U = (entity.x + xaxis) // pitch
- V = (entity.y + yaxis) // pitch

The UV coordinates are adjusted based on the quadrant to ensure correct positioning.

## GVK (Group, Version, Kind) Encoding

GVK information is encoded in the alpha channel of the RGBA tuple:
- Group: First 2 bits
- Version: Next 1 bit
- Kind: Last 5 bits

This bit-level encoding allows for categorization and versioning of entities within a compact representation.

## Order Attribute

The Order attribute is used when entities are part of an atlas collection. Entities with the same Order value are grouped into the same image within the atlas.

## Unit Declaration and Conversion

### The fold() Method

The `fold()` method converts entity coordinates from external units (meters and degrees) to internal units (millimeters and arc minutes) and determines the appropriate quadrant. This is the primary method for converting user-friendly coordinates to the internal representation.

Example:
```python
entity = Entity(x=1, y=1, z=90).fold(Unit.METER, Unit.DEGREE)
# Internal representation becomes:
# x: 1000 mm, y: 1000 mm, z: 5400 arc minutes, q: Quadrant.NE
```

### The @ (matmul) Operator

The `@` operator converts FROM internal units TO display units. It's primarily used for displaying internal coordinates in user-friendly formats:

```python
# Entity with coordinates in internal units (millimeters and arc minutes)
internal_entity = Entity(x=1000, y=2000, z=5400)

# Convert TO meters and degrees for display
display_entity = internal_entity @ Unit.METER @ Unit.DEGREE
# Result: x=1.0, y=2.0, z=90.0
```

The `@` operator performs unit scaling:
- `entity @ Unit.METER` converts x,y coordinates from millimeters to meters
- `entity @ Unit.DEGREE` converts z coordinate from arc minutes to degrees

### Format-Specific Unit Handling

Different file formats have different unit assumptions:

- **JSON format**: Input coordinates are in meters and degrees (game data format). The JSON loader automatically calls `.fold(Unit.METER, Unit.DEGREE)` to convert to internal units.
- **TSV format**: Coordinates are stored directly in internal units (millimeters and arc minutes).
- **PNG format**: Stores data in internal representation.

### Practical Usage

**For JSON-like data (coordinates in meters/degrees):**
```python
# Game data format - coordinates in meters and degrees
entity = Entity(x=1.5, y=2.0, z=90).fold(Unit.METER, Unit.DEGREE)
```

**For TSV-like data (coordinates in internal units):**
```python
# Internal representation - coordinates in millimeters and arc minutes
entity = Entity(x=1500, y=2000, z=5400)
```

**For display (convert internal to user-friendly):**
```python
# Convert internal representation to display units
display_entity = internal_entity @ Unit.METER @ Unit.DEGREE
# or
display_entity = internal_entity.unfold(Unit.METER, Unit.DEGREE)  # Also handles quadrants
```

## Angle Wrapping

Angles are wrapped to the range 0-360 degrees (0-21600 arc minutes) during folding and unfolding operations. This ensures consistent representation regardless of input values.

For example, 450° wraps to 90° but is stored as 5400 arc minutes internally.

## Error Handling and Validation

The Entity class includes validation to help catch common mistakes:

### Coordinate Validation

```python
# This will raise a validation error - too large for a speedball field
entity = Entity(x=500, y=100, z=90).fold(Unit.METER, Unit.DEGREE)  # 500m is huge!

# Normal coordinates work fine
entity = Entity(x=15, y=10, z=90).fold(Unit.METER, Unit.DEGREE)  # 15m x 10m field
```

### Order Limits

The system enforces a maximum of 256 layout groups per atlas:

```python
codec = Codec()
# Adding 256 groups works fine
for i in range(256):
    codec.update([])

# This will raise: "Atlas limit exceeded"
codec.update([])  # Group 257 fails
```

### File Format Errors

The loading system provides helpful error messages for common file issues:
- Invalid JSON syntax
- PNG files with wrong dimensions
- Empty or corrupted files
- Missing required fields in layout data

## Precision and Rounding

The Entity class supports rounding operations for managing precision in calculations or display. Rounding is particularly important when converting between internal and external representations to maintain consistent behavior.

## Pitch and Resolution

The system supports different pitch values which affect the resolution of the spatial representation:

- LORES: 762 mm/pixel
- HIRES: 381 mm/pixel

The choice of pitch affects UV mapping and RGBA encoding, allowing for different levels of spatial resolution as needed.

## Compatibility with External Formats

The encoding scheme is compatible with common file formats:
- JSON for human-readable representation
- PNG for efficient storage in image atlases

This allows for versatile storage and transmission of spatial entity data.
