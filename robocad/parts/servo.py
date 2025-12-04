from dataclasses import dataclass, field
import cadquery as cq

from robocad.core.part import Part


@dataclass
class ServoSpec:
    """
    Physical dimensions of a servo body.
    All units in millimeters.

    Coordinates:
      - X axis: front ↔ back (length direction)
      - Y axis: left ↔ right (width direction)
      - Z axis: bottom ↔ top (height)
    """
    body_width: float        # side-to-side (Y)
    body_length: float       # front-to-back (X)
    body_height: float       # bottom-to-top (Z)

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


@dataclass
class ServoMountPlate(Part):
    """
    A simple rectangular plate with:
      - a rectangular cutout where the servo body drops through
      - two inline mounting screw holes (front/back) along the centerline

    The servo:
      - body passes through the plate
      - flanges rest on top of the plate
    """

    # Use default factory so dataclasses don't complain about a mutable default
    # We treat SG90_SPEC as a constant (don't mutate it)
    spec: ServoSpec = field(default_factory=lambda: SG90_SPEC)

    thickness: float = 3.0      # plate thickness
    clearance: float = 0.3      # extra slack around the body so it actually fits
    hole_diameter: float = 2.2  # larger than screw for clearance
    flange_extra: float = 10.0  # extra length beyond the body for screw land
    body_extra: float = 6.0     # extra area beyond body

    def build(self) -> cq.Workplane:
        s = self.spec  # alias

        # 1) Compute the plate size based on servo dimensions.
        plate_width  = s.body_width + self.body_extra
        plate_length = s.body_length + self.flange_extra

        # 2) Create the solid plate: a simple rectangular prism.
        plate = (
            cq.Workplane("XY")
            .rect(plate_length, plate_width)  # centered at (0,0)
            .extrude(self.thickness)         # from z=0 up to z=thickness
        )

        # 3) Cut a through-hole where the servo body will sit.
        # We start from the TOP face and cut DOWN through the plate.
        body_cut_length = s.body_length + self.clearance
        body_cut_width  = s.body_width  + self.clearance

        plate = (
            plate
            .faces(">Z").workplane()  # top face
            .rect(body_cut_length, body_cut_width)
            .cutBlind(-self.thickness)  # cut downwards through plate
        )

        # 4) Add screw holes inline along X, centered in Y.
        # For SG90: two screws, one front, one back, both on Y=0.
        half_spacing = s.screw_spacing_x / 2.0

        plate = (
            plate
            .faces(">Z").workplane()  # still on top face
            .pushPoints([
                ( half_spacing,  0.0),  # front screw
                (-half_spacing,  0.0),  # back screw
            ])
            .hole(self.hole_diameter)
        )

        return plate


@dataclass
class ServoFrustumMount(Part):
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
    base_length: float = 42.0   # bottom footprint in X (mm)
    base_width: float = 32.0    # bottom footprint in Y (mm)
    height: float = 28.8        # total mount height (mm)

    wall_thickness: float = 2.5
    bottom_thickness: float = 3.0
    pocket_clearance: float = 0.4
    fillet_radius: float = 3.0

    # Bottom mounting holes (to bolt this to something)
    mount_hole_diameter: float = 3.0
    mount_hole_offset_x: float = 14.0
    mount_hole_offset_y: float = 10.0

    # Wire slot on one side
    wire_slot_width: float = 8.0
    wire_slot_height: float = 8.0

    def build(self) -> cq.Workplane:
        s = self.spec

        # 1) Compute top outer size
        # We want enough room for:
        # servo body + clearance + walls

        pocket_length = s.body_length + 2 * self.pocket_clearance
        pocket_width  = s.body_width  + 2 * self.pocket_clearance

        top_outer_length = pocket_length + 2 * self.wall_thickness
        top_outer_width  = pocket_width  + 2 * self.wall_thickness 

        # Check if base is at least as big as the top NOTE we should make this scale parametrically too
        assert self.base_length >= top_outer_length
        assert self.base_width  >= top_outer_width

        # 2) Outer frustum solid (loft between bottom and top rectangles)
        outer = (
            cq.Workplane("XY")
            .rect(self.base_length, self.base_width)    # bottom
            .workplane(offset=self.height)              # move up in height
            .rect(top_outer_length, top_outer_width)    # top
            .loft(combine=True)
        )

        # 3) Fillet vertical edges for curved look (NOTE |Z only works for edges parallel to Z axis)
        all_edges = outer.edges().vals()

        edges_to_fillet = [
            e for e in all_edges
            if (e.BoundingBox().zmax - e.BoundingBox().zmin) > 1.0
        ]

        outer = outer.newObject(edges_to_fillet).fillet(self.fillet_radius)

        # 4) Make it hollow NOTE by shelling with top face selected, there is nothing left to cut the servo pocket into
        shell = outer.faces(">Z").shell(-self.wall_thickness)

        # 5) Cut servo pocket from the top NOTE this step seems redundant to me. top of frustum is hollowed out from shell already
        # nvm, I think it creates a vertical part for the servo to slide into
        pocket_depth = self.height - self.bottom_thickness
        shell = (
            shell
            .faces(">Z").workplane()            # top opening
            .rect(pocket_length, pocket_width)
            .cutBlind(-pocket_depth)            # cut downward in Z
        )

        # 6) Wire slot on +X side NOTE this corresponds better with wire placement on servo.
        # Seems more robust to use a boolean cut
        cut_z_bottom = self.bottom_thickness
        cut_height   = self.wire_slot_height
        cut_width    = self.wire_slot_width

        center_z = cut_z_bottom + (cut_height / 2.0)

        cutter = (
            cq.Workplane("XZ")
            .rect(top_outer_length / 2, cut_height)
            .extrude(cut_width)
            .translate((self.base_length / 2, cut_width / 2, center_z))
        )

        shell = shell.cut(cutter)

        # 7) Bottom mounting holes (4 corners, symmetric)
        # NOTE the mounting holes are going to be inside the frustum? kind of inconvenient.
        shell = (
            shell.faces("<Z").workplane()
            .pushPoints([
                ( self.mount_hole_offset_x,  self.mount_hole_offset_y),
                ( self.mount_hole_offset_x, -self.mount_hole_offset_y),
                (-self.mount_hole_offset_x,  self.mount_hole_offset_y),
                (-self.mount_hole_offset_x, -self.mount_hole_offset_y),
            ])
            .hole(self.mount_hole_diameter)
        )

        return shell


