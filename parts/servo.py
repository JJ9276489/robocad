from dataclasses import dataclass
import cadquery as cq
from robocad.core.part import Part

@dataclass
class ServoSpec:
    body_width: float
    body_length: float
    body_height: float
    flange_thickness: float
    flange_overhang: float
    screw_spacing: float
    screw_diameter: float

SG90_SPEC = ServoSpec(
    body_width=12.2,
    body_length=23.5,
    body_height=22.5,
    flange_thickness=2.0,
    flange_overhang=2.0,
    screw_spacing=27.0,
    screw_diameter=2.0,
)

@dataclass
class ServoMount(Part):
    spec: ServoSpec = SG90_SPEC
    thickness: float = 3.0     # plate thickness
    clearance: float = 0.3     # extra width/length for fit
    hole_diameter: float = 0.2 # slightly > screw diameter
    flange_extra: float = 5.0  # extra material around screws

    def build(self):
        s = self.spec

        plate_width = s.body_width + 2 * self.clearance
        plate_length = s.body_length + self.flange_extra

        # base plate
        plate = (
            cq.Workplane("XY")
            .rect(plate_length, plate_width)
            .extrude(self.thickness)
        )

        # cut the servo body rectangular pocket
        pocket = {
            cq.Workplane("XY")
            .rect(s.body_length + self.clearance, s.body_width + self.clearance)
            .extrude(self.body_cut_depth())
        }

        plate = plate.cut(pocket)

        # add screw holes near front (flange area)
        screw_x_offset = (s.body_length / 2) - (s.flange_overhang / 2)
        screw_y_spacing = s.screw_spacing

        plate = (
            plate.faces(">Z").workplane()
            .pushpoints([
                ( screw_x_offset,  screw_y_spacing / 2),
                ( screw_x_offset, -screw_y_spacing / 2),
            ])
            .hole(self.hole_diameter)
        )

        return plate
    
    def body_cut_depth(self):
        # how deep the pocket goes into the plate
        return min(self.thickness - 0.5, self.spec.body_height / 2)
