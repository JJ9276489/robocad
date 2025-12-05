from dataclasses import dataclass, field
from build123d import *
from robocad.core.part import Component


@dataclass
class ServoSpec:
    """
    Physical dimensions of a servo body.
    All units in millimeters.
    """
    body_width: float        # Y
    body_length: float       # X
    body_height: float       # Z

    flange_thickness: float  # thickness of the mounting ears
    flange_overhang: float   # how far the flanges extend past the body (in +X / -X)

    screw_spacing_x: float   # distance between the two mounting screw centers (along X)
    screw_diameter: float    # nominal screw diameter


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

# ---- PARTS ----

@dataclass
class ServoMountPlate(Component):
    """
    A simple rectangular plate with:
      - a rectangular cutout where the servo body drops through
      - two inline mounting screw holes (front/back) along the centerline

    Draw the profile (rectangle minus body minus screw holes) and extrude once.
    """

    # Use default factory so dataclasses don't complain about a mutable default
    # We treat SG90_SPEC as a constant (don't mutate it)
    spec: ServoSpec = field(default_factory=lambda: SG90_SPEC)

    thickness: float = 3.0      # plate thickness
    clearance: float = 0.3      # extra slack around the body so it actually fits
    margin: float = 6.0     # extra area beyond body

    def build(self):
        s = self.spec  # alias

        # 1) Compute the plate size based on servo dimensions.
        plate_width  = s.body_width + self.margin
        plate_length = s.body_length + self.margin

        # 2) Sketch the mounting plate
        with BuildPart() as part:
            with BuildSketch():
                # Step A: The Plate (Base)
                Rectangle(plate_length, plate_width)
                fillet(vertices(), radius=2)

                # Step B: Negative Shape (The cutout)
                # Stay in the same sketch, but subtract
                Rectangle(plate_length - self.margin,
                          plate_width - self.margin,
                          mode=Mode.SUBTRACT,)
                
                # Step C: Negative Shape (The screw holes)
                with Locations((s.screw_spacing_x / 2, 0), (-s.screw_spacing_x / 2, 0)):
                    Circle(s.screw_diameter / 2, mode=Mode.SUBTRACT)
            
            # 3) Extrude once
            extrude(amount=self.thickness)

            return part.part

@dataclass
class ServoFrustumMount(Component):
    '''
    Curved/tapered servo mount:
        - outer frustum (truncated pyramid with filleted edges)
        - hollow shell (lighter, space inside)
        - top pocket for SG90 style servo
        - side wire slot
        - bottom mounting holes
    
        Coordinate system:
            X: front <-> back (servo length)
            Y: left <-> right (servo width)
            Z: bottom <-> top
    '''
    spec: ServoSpec = field(default_factory=lambda: SG90_SPEC)

    # Overall mount geometry
    base_length: float = 42.0   # X
    base_width: float = 32.0    # Y
    height: float = 28.8        # Z

    wall_thickness: float = 2.5
    deck_thickness: float = 3.0     # thickness of top part holding the servo
    bottom_thickness: float = 3.0
    corner_radius: float = 3.0

    # Base mounting
    base_mount_hole_inset: float = 4.0
    mount_hole_diameter: float = 3.0

    # Wire slot on one side
    wire_slot_width: float = 8.0
    wire_slot_height: float = 8.0

    def build(self) -> Part:
        s = self.spec

        # 1) Compute top outer size
        # We want enough room for:
        # servo body + clearance + walls

        top_len = s.body_length + (2 * self.wall_thickness) + 2.0
        top_wid  = s.body_width  + (2 * self.wall_thickness) + 2.0

        # Check if base is at least as big as the top NOTE we should make this scale parametrically too
        assert self.base_length >= top_len
        assert self.base_width  >= top_wid

        # 2) Define the profiles (sketches)
        # fillet before lofting for cleaner geometry
        with BuildSketch() as top_profile:
            Rectangle(top_len, top_wid)
            fillet(vertices(), radius=self.corner_radius)
        
        with BuildSketch() as bottom_profile:
            Rectangle(self.base_length, self.base_width)
            fillet(vertices(), radius=self.corner_radius)
        
        # 3) Build the main solid
        with BuildPart() as main_body:
            # create frustum
            loft(sections=[bottom_profile.sketch, top_profile.sketch.moved(Location((0,0,self.height)))])
            
            # 4) Hollow it out
            # We will cut from bottom up stopping short of the top to leave a 'deck'
            interior_height = self.height - self.deck_thickness

            # a) Create a smaller version of the bottom profile for the hollow inside
            with BuildSketch(Plane.XY) as core_bottom:
                Rectangle(self.base_length - 2 * self.wall_thickness, 
                          self.base_width - 2 * self.wall_thickness)
                fillet(vertices(), radius=self.corner_radius - self.wall_thickness)
            
            # b) Create a smaller version of the top profile
            with BuildSketch(Plane.XY.offset(interior_height)) as core_top:
                Rectangle(top_len - 2 * self.wall_thickness,
                          top_wid - 2 * self.wall_thickness)
                fillet(vertices(), radius=self.corner_radius - self.wall_thickness)
            
            # c) Subtract the core
            loft(sections=[core_bottom.sketch, core_top.sketch], mode=Mode.SUBTRACT)

            # 5) Servo Pocket
            with BuildSketch(Plane.XY.offset(self.height)):
                Rectangle(s.body_length + 0.4, s.body_width + 0.4)
            extrude(amount=-self.deck_thickness, mode=Mode.SUBTRACT)

            # 6) Servo mounting screw holes
            with BuildSketch(Plane.XY.offset(self.height)):
                with Locations((s.screw_spacing_x / 2, 0), (-s.screw_spacing_x / 2, 0)):
                    Circle(s.screw_diameter / 2)
            extrude(amount=-self.deck_thickness, mode=Mode.SUBTRACT)

            # 7) Wire slot cut
            # Placed on the right side (I want to cut a slot offset from the bottom by about wall thickness on one side)
            with BuildSketch(Plane.YZ):
                with Locations((0, (self.wire_slot_height / 2) + self.wall_thickness)):
                    Rectangle(self.wire_slot_width, self.wire_slot_height)
            extrude(amount=self.base_length, mode=Mode.SUBTRACT)
            
            # 8) Base mounting holes
            # better to parametrically inset these
            with BuildSketch(Plane.XY):
                mounting_hole_locations = [
                    ( ((self.base_length / 2) - self.base_mount_hole_inset), -((self.base_width / 2) - self.base_mount_hole_inset)),
                    ( ((self.base_length / 2) - self.base_mount_hole_inset),  ((self.base_width / 2) - self.base_mount_hole_inset)),
                    (-((self.base_length / 2) - self.base_mount_hole_inset), -((self.base_width / 2) - self.base_mount_hole_inset)),
                    (-((self.base_length / 2) - self.base_mount_hole_inset),  ((self.base_width / 2) - self.base_mount_hole_inset))
                ]
                with Locations(mounting_hole_locations):
                    Circle(self.mount_hole_diameter / 2)
            extrude(amount=self.height, mode=Mode.SUBTRACT)
        
        return main_body.part

            

