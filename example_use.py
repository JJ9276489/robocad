from robocad.core.parameters import SG90_SPEC
from robocad.parts.servo import ServoMountPlate

mount = ServoMountPlate(
    spec=SG90_SPEC,
    thickness=3.0,
    clearance=0.3,
    margin_y=3.0,
    margin_x=5.0,
)

mount.export_stl("sg90_mount.stl")