# robocad

Parametric CAD system for designing customizable robot components in Python.

## Overview

robocad uses [build123d](https://github.com/gumadesarrollo/build123d) to generate 3D models programmatically. Define components using dataclasses with specifications, then export to STL or STEP for 3D printing or CAD software.

## Installation

```bash
pip install -r requirements.txt
```

## Quick Start

```python
from robocad.core.parameters import SG90_SPEC
from robocad.parts.servo import ServoMountPlate

# Create a servo mount plate
mount = ServoMountPlate(
    spec=SG90_SPEC,
    thickness=3.0,
    clearance=0.3,
    margin_y=3.0,
    margin_x=5.0,
)

# Export to STL for 3D printing
mount.export_stl("sg90_mount.stl")
```

## Components

### Servo Mount Plate

Simple rectangular plate with mounting holes:

```python
from robocad.parts.servo import ServoMountPlate
from robocad.core.parameters import SG90_SPEC

mount = ServoMountPlate(
    spec=SG90_SPEC,  # Servo specification
    thickness=3.0,    # Plate thickness in mm
    clearance=0.3,    # Slack around servo body
    margin_y=3.0,     # Extra width beyond servo
    margin_x=5.0,     # Extra length beyond servo
)
mount.export_stl("mount.stl")
```

### Servo Frustum Mount

Curved/tapered mount with hollow interior:

```python
from robocad.parts.servo import ServoFrustumMount
from robocad.core.parameters import SG90_SPEC

mount = ServoFrustumMount(
    spec=SG90_SPEC,
    base_length=42.0,     # X dimension
    base_width=32.0,      # Y dimension
    height=28.8,          # Z dimension
    wall_thickness=2.5,   # Shell thickness
)
mount.export_stl("frustum_mount.stl")
```

## Available Specifications

### ServoSpec

| Parameter | Description |
|-----------|-------------|
| `body_width` | Y dimension of servo body |
| `body_length` | X dimension of servo body |
| `body_height` | Z dimension of servo body |
| `flange_thickness` | Thickness of mounting ears |
| `flange_overhang` | Flange extension past body |
| `screw_spacing_x` | Distance between mounting screws |
| `screw_diameter` | Screw hole diameter |

### HCSR04Spec

For ultrasonic distance sensors (HC-SR04):

```python
from robocad.core.parameters import HCSR04_PCB_SPEC
from robocad.parts.ultrasonic import UltrasonicMount

mount = UltrasonicMount(spec=HCSR04_PCB_SPEC)
mount.export_stl("ultrasonic_mount.stl")
```

## Export Formats

All components support multiple export formats:

```python
component.export_stl("output.stl")   # STL for 3D printing
component.export_step("output.step")  # STEP for CAD software
```

## Creating Custom Components

Extend the `Component` base class:

```python
from robocad.core.part import Component
from build123d import *

@dataclass
class MyComponent(Component):
    size: float = 10.0
    
    def build(self) -> Part:
        with BuildPart() as part:
            Box(self.size, self.size, self.size)
        return part.part
```

## Project Structure

```
robocad/
├── core/
│   ├── part.py         # Component base class
│   ├── parameters.py   # Spec dataclasses
│   └── geometry.py     # Geometry utilities
├── parts/
│   ├── servo.py        # Servo mounts
│   └── ultrasonic.py   # Ultrasonic mounts
├── example_use.py      # Usage examples
├── requirements.txt    # Dependencies
└── README.md
```

## Development

```bash
# Install dev dependencies
pip install pytest ruff black mypy

# Run tests
pytest

# Format code
black robocad/
ruff check robocad/

# Type checking
mypy robocad/ --ignore-missing-imports
```

## TODO

See [TODO](TODO) for planned features and improvements.

## License

MIT

## Credits

Built with [build123d](https://github.com/gumadesarrollo/build123d) — a Python library for topological solid modeling.
