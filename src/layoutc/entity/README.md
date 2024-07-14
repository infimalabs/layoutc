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

## Unit Declaration with __matmul__

The `__matmul__` method (@) declares the units of an entity and converts them to internal units. For example:

- entity @ Unit.METER converts x and y values from meters to millimeters
- entity @ Unit.DEGREE converts z value from degrees to arc minutes

This operation allows users to define entities in familiar units (like meters and degrees) and then convert them to the internal representation.

Example:
```python
entity = Entity(x=1, y=1, z=90) @ Unit.METER @ Unit.DEGREE
# Internal representation becomes:
# x: 1000 mm, y: 1000 mm, z: 5400 arc minutes
```

## Angle Wrapping

Angles are wrapped to the range 0-360 degrees (0-21600 arc minutes) during folding and unfolding operations. This ensures consistent representation regardless of input values.

For example, 450° wraps to 90° but is stored as 5400 arc minutes internally.

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
