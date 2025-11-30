from robocad.parts.servo import ServoMount, SG90_SPEC

mount = ServoMount(
    spec=SG90_SPEC,
    thickness=3.0,
    clearance=0.3,
    hole_diameter=2.2,
    flange_extra=6.0,
)

mount.export_stl("sg90_mount.stl")