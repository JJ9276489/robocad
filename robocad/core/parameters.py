from dataclasses import dataclass

# ---- Class Definitions ----

@dataclass
class ServoSpec:
    body_width: float        # Y
    body_length: float       # X
    body_height: float       # Z
    flange_thickness: float  # thickness of the mounting ears
    flange_overhang: float   # how far the flanges extend past the body (in +X / -X)
    screw_spacing_x: float   # distance between the two mounting screw centers (along X)
    screw_diameter: float    # nominal screw diameter


@dataclass
class HCSR04Spec:
    board_width: float      # PCB width (X)
    board_height: float     # PCB height (Z)
    board_thickness: float
    mount_hole_spacing_x: float   # center-to-center horizontally
    mount_hole_spacing_y: float   # center-to-center vertically
    mount_hole_diameter: float    # M2-ish
    windows_separation: float     # slot for the two cans
    window_diameter: float

# ---- Measurements ----

# Approximate SG90 defaults (treat as placeholders; refine with calipers later)
SG90_SPEC = ServoSpec(
    body_width=12.2,
    body_length=23.5,
    body_height=22.5,
    flange_thickness=2.0,
    flange_overhang=2.0,
    screw_spacing_x=27.0,
    screw_diameter=2.0,
)

# Varies depending on exact dimension of PCB
HCSR04_PCB_SPEC = HCSR04Spec(
    board_width=45.0,
    board_height=30.0,     
    board_thickness=2.0,
    mount_hole_spacing_x=40.0,  
    mount_hole_spacing_y=16.0, 
    mount_hole_diameter=2.5,    
    windows_separation=25.0,
    window_diameter=11.0,
)

