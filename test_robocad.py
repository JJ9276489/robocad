"""Tests for robocad components."""

import pytest
from robocad.core.parameters import SG90_SPEC, ServoSpec, HCSR04_PCB_SPEC
from robocad.parts.servo import ServoMountPlate, ServoFrustumMount


class TestServoSpec:
    """Test servo specification dataclass."""

    def test_sg90_spec_exists(self):
        """SG90 specification should be defined."""
        assert SG90_SPEC.body_width == 12.2
        assert SG90_SPEC.body_length == 23.5

    def test_custom_spec(self):
        """Custom servo specs should work."""
        spec = ServoSpec(
            body_width=10.0,
            body_length=20.0,
            body_height=15.0,
            flange_thickness=2.0,
            flange_overhang=1.5,
            screw_spacing_x=25.0,
            screw_diameter=2.0,
        )
        assert spec.body_width == 10.0
        assert spec.screw_spacing_x == 25.0


class TestServoMountPlate:
    """Test servo mount plate component."""

    def test_default_mount(self):
        """Default parameters should create valid mount."""
        mount = ServoMountPlate()
        assert mount.thickness == 3.0
        assert mount.clearance == 0.3

    def test_custom_mount(self):
        """Custom parameters should work."""
        mount = ServoMountPlate(
            spec=SG90_SPEC,
            thickness=2.0,
            clearance=0.5,
            margin_y=5.0,
            margin_x=8.0,
        )
        assert mount.thickness == 2.0
        assert mount.margin_y == 5.0

    def test_export_stl_creates_file(self, tmp_path):
        """export_stl should create a file."""
        mount = ServoMountPlate(spec=SG90_SPEC)
        output_path = tmp_path / "test_mount.stl"
        mount.export_stl(str(output_path))
        assert output_path.exists()


class TestServoFrustumMount:
    """Test servo frustum mount component."""

    def test_default_parameters(self):
        """Default parameters should be reasonable."""
        mount = ServoFrustumMount()
        assert mount.height == 28.8
        assert mount.wall_thickness == 2.5
        assert mount.base_length >= mount.base_width

    def test_base_larger_than_top(self):
        """Base should be larger than top for frustum."""
        mount = ServoFrustumMount(
            spec=SG90_SPEC,
            base_length=50.0,
            base_width=40.0,
        )
        assert mount.base_length > SG90_SPEC.body_length
        assert mount.base_width > SG90_SPEC.body_width

    def test_wall_thickness_constraint(self):
        """Wall thickness should not exceed base dimensions."""
        mount = ServoFrustumMount(
            spec=SG90_SPEC,
            wall_thickness=100.0,  # Too thick
        )
        # The build() should handle this gracefully
        with pytest.raises(AssertionError):
            mount.build()


class TestExportFormats:
    """Test different export formats."""

    def test_export_stl(self, tmp_path):
        """STL export should work."""
        mount = ServoMountPlate(spec=SG90_SPEC)
        path = tmp_path / "test.stl"
        mount.export_stl(str(path))
        assert path.exists()
        assert path.stat().st_size > 0

    def test_export_step(self, tmp_path):
        """STEP export should work."""
        mount = ServoMountPlate(spec=SG90_SPEC)
        path = tmp_path / "test.step"
        mount.export_step(str(path))
        assert path.exists()
        assert path.stat().st_size > 0
