from dataclasses import dataclass, field
from build123d import *
from robocad.core.part import Component
from robocad.core.parameters import HCSR04Spec, HCSR04_PCB_SPEC

@dataclass
class UltrasonicSensorMount(Component):
    '''
    L - shaped bracket for a HC-SR04-style ultrasonic module:
        - Vertical plate with:
            * circular cutouts for the two ultrasonic transducers
            * 4 corner screw holes to fasten the PCB
        - 90 degree bottom flange with screw holes to attach to servo arm

    Coordinate system:
        X: left <-> right (sensor board width)
        Y: top <-> bottom (sensor board height)
        Z: front <-> back (sensor board thickness)
    '''

    spec: HCSR04Spec = field(default_factory=lambda: HCSR04_PCB_SPEC)

    mount_thickness: float = 3.0
    clearance: float = 0.3

    margin_y: float = 4.0              # margin beyond HCSR04 PCB
    margin_x: float = 4.0

    flange_thickness: float = 3.0 
    flange_length: float = 11.0

    mount_screw_diameter: float = 2.0
    flange_screw_diameter: float = 2.0

    flange_hole_spacing: float = 24.0

    def build(self):
        s = self.spec

        plate_width = s.board_width + 2 * self.margin_x
        plate_height = s.board_height + 2 * self.margin_y
        with BuildPart() as combined_part:
            with BuildSketch(Plane.XY):
                Rectangle(plate_width, plate_height)
                with Locations((s.windows_separation / 2, 0), (-(s.windows_separation / 2), 0)):
                    Circle(s.window_diameter / 2, mode=Mode.SUBTRACT)
                with Locations(
                    ( (s.mount_hole_spacing_x / 2),  (s.mount_hole_spacing_y / 2)),
                    ( (s.mount_hole_spacing_x / 2), -(s.mount_hole_spacing_y / 2)),
                    (-(s.mount_hole_spacing_x / 2),  (s.mount_hole_spacing_y / 2)),
                    (-(s.mount_hole_spacing_x / 2), -(s.mount_hole_spacing_y / 2)),
                ):
                    Circle(s.mount_hole_diameter / 2, mode=Mode.SUBTRACT)
            
            extrude(amount=self.mount_thickness)

            with BuildSketch(Plane.XZ.offset(-plate_height / 2)):
                with Locations((0, self.flange_length / 2)):
                    Rectangle(plate_width, self.flange_length)
                    with Locations(
                        ( (self.flange_hole_spacing / 2), 0),
                        (-(self.flange_hole_spacing / 2), 0)
                    ):
                        Circle(self.flange_screw_diameter / 2, mode=Mode.SUBTRACT)
            
            extrude(amount=-self.flange_thickness)
        
        return combined_part.part



