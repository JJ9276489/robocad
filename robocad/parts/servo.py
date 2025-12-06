from dataclasses import dataclass, field
from build123d import *
from robocad.core.part import Component
from robocad.core.parameters import ServoSpec, SG90_SPEC
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
    margin_y: float = 3.0       # extra area beyond body in Y (width)
    margin_x: float = 4.0       # extra area beyond body in X (length)

    def build(self):
        s = self.spec  # alias

        # 1) Compute the plate size based on servo dimensions.
        plate_width  = s.body_width + self.margin_y * 2
        plate_length = s.body_length + self.margin_x * 2

        # 2) Sketch the mounting plate
        with BuildPart() as part:
            with BuildSketch():
                # Step A: The Plate (Base)
                Rectangle(plate_length, plate_width)
                fillet(vertices(), radius=2)

                # Step B: Negative Shape (The cutout)
                # Stay in the same sketch, but subtract
                Rectangle(s.body_length + 2 * self.clearance,
                          s.body_width + 2 * self.clearance,
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

    # Debugging
    debug_view: bool = False

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

        top_len = s.body_length + (2 * self.wall_thickness) + 4.0
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
            # We will cut from bottom up stopping short of the top and bottom to leave a hollow inside
            z_top_inner = self.height - self.deck_thickness

            inner_len0, inner_wid0 = self._inner_dims_at_z(self.bottom_thickness, top_len, top_wid)
            inner_len1, inner_wid1 = self._inner_dims_at_z(z_top_inner, top_len, top_wid)

            inner_corner_radius = max(self.corner_radius - self.wall_thickness, 0)

            with BuildSketch(Plane.XY.offset(self.bottom_thickness), mode=Mode.PRIVATE) as core_bottom:
                Rectangle(inner_len0, inner_wid0)
                fillet(vertices(), radius=inner_corner_radius)
            
            with BuildSketch(Plane.XY.offset(z_top_inner), mode=Mode.PRIVATE) as core_top:
                Rectangle(inner_len1, inner_wid1)
                fillet(vertices(), radius=inner_corner_radius)

            core_cutout = loft(sections=[core_bottom.sketch, core_top.sketch], mode=Mode.PRIVATE)

            if self.debug_view:
                return core_cutout

            add(core_cutout, mode=Mode.SUBTRACT)

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
            # Placed on the front face (I want to cut a slot offset from the bottom by bottom thickness on one side)
            with BuildSketch(Plane.YZ):
                with Locations((0, (self.wire_slot_height / 2) + self.bottom_thickness)):
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
    
    def _lerp(self, bottom_value: float, top_value: float, z: float) -> float:
        """
        Linearly interpolate between bottom_value and top_value at height z,
        where z is measured from base (0) to self.height.
        """
        t = z / self.height
        return bottom_value - (bottom_value - top_value) * t

    def _outer_dims_at_z(self, z: float, top_len: float, top_wid: float):
        L = self._lerp(self.base_length, top_len, z)
        W = self._lerp(self.base_width,  top_wid, z)
        return L, W

    def _inner_dims_at_z(self, z: float, top_len: float, top_wid: float):
        L, W = self._outer_dims_at_z(z, top_len, top_wid)
        return L - 2 * self.wall_thickness, W - 2 * self.wall_thickness





