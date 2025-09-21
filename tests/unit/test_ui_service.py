"""
Unit tests for UIService

Tests the UI service functionality including font management and widget operations.
"""

from unittest.mock import MagicMock, patch

import pytest
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QCheckBox, QLabel, QLineEdit, QPushButton, QWidget

from src.services.ui_service import UIService


@pytest.mark.unit
class TestUIService:
    """Test cases for UIService class."""

    def test_init(self):
        """Test UIService initialization."""
        service = UIService()
        assert service.current_platform is not None
        assert service.logger is not None

    def test_get_platform_font(self):
        """Test platform font selection."""
        service = UIService()
        font = service._get_platform_font()

        assert isinstance(font, QFont)
        assert font.family() == "Arial"
        assert font.pointSize() == 11

    @patch("src.services.ui_service.QLabel")
    @patch("src.services.ui_service.QCheckBox")
    @patch("src.services.ui_service.QPushButton")
    @patch("src.services.ui_service.QLineEdit")
    def test_fix_ui_visibility(
        self, mock_line_edit, mock_button, mock_checkbox, mock_label
    ):
        """Test UI visibility fixing."""
        # Create mock widgets
        mock_widget = MagicMock(spec=QWidget)
        mock_widget.findChildren.return_value = [
            mock_label.return_value,
            mock_checkbox.return_value,
            mock_button.return_value,
            mock_line_edit.return_value,
        ]

        # Configure mock return values
        mock_label.return_value.styleSheet.return_value = ""
        mock_checkbox.return_value.styleSheet.return_value = ""
        mock_button.return_value.styleSheet.return_value = ""
        mock_line_edit.return_value.styleSheet.return_value = ""

        service = UIService()
        service.fix_ui_visibility(mock_widget)

        # Verify widgets were made visible and styled
        mock_label.return_value.setVisible.assert_called_with(True)
        mock_checkbox.return_value.setVisible.assert_called_with(True)
        mock_button.return_value.setVisible.assert_called_with(True)
        mock_line_edit.return_value.setVisible.assert_called_with(True)

    def test_setup_axis_controls(self):
        """Test axis controls setup."""
        import os

        # Skip this test in headless CI environment as Qt GUI operations may cause instability
        if os.environ.get("QT_QPA_PLATFORM") == "offscreen":
            import pytest

            pytest.skip("Skipping GUI-dependent test in headless environment")

        service = UIService()

        # Create mock comboboxes
        mock_y1_combo = MagicMock()
        mock_y2_combo = MagicMock()
        mock_x_combo = MagicMock()

        axis_combos = {
            "y1_axis_combo": mock_y1_combo,
            "y2_axis_combo": mock_y2_combo,
            "x_axis_combo": mock_x_combo,
        }

        service.setup_axis_controls(axis_combos)

        # Verify items were added
        assert mock_y1_combo.addItems.called
        assert mock_y2_combo.addItems.called
        assert mock_x_combo.addItems.called

        # Verify default selections
        mock_y1_combo.setCurrentText.assert_called_with("NTC01")
        mock_y2_combo.setCurrentText.assert_called_with("None")  # Default to no Y2 axis
        mock_x_combo.setCurrentText.assert_called_with("Seconds")

    def test_setup_axis_controls_with_none(self):
        """Test axis controls setup with None values."""
        service = UIService()

        axis_combos = {
            "y1_axis_combo": None,
            "y2_axis_combo": None,
            "x_axis_combo": None,
        }

        # Should not raise an exception
        service.setup_axis_controls(axis_combos)

    def test_reset_ui_widgets(self):
        """Test UI widgets reset."""
        service = UIService()

        # Create mock widgets
        mock_widget1 = MagicMock()
        mock_widget2 = MagicMock()
        mock_widget3 = MagicMock()

        widgets = {
            "mean_hp_power_value": mock_widget1,
            "max_v_accu_value": mock_widget2,
            "tilt_status_value": mock_widget3,
        }

        service.reset_ui_widgets(widgets)

        # Verify widgets were reset
        mock_widget1.setText.assert_called_with("-")
        mock_widget2.setText.assert_called_with("-")
        mock_widget3.setText.assert_called_with("-")

    def test_reset_ui_widgets_with_none(self):
        """Test UI widgets reset with None values."""
        service = UIService()

        widgets = {
            "mean_hp_power_value": None,
            "max_v_accu_value": None,
        }

        # Should not raise an exception
        service.reset_ui_widgets(widgets)

    @patch("src.services.ui_service.QFont")
    def test_get_available_fonts(self, mock_qfont):
        """Test getting available fonts."""
        mock_qfont.families.return_value = ["Arial", "Helvetica", "Times"]

        service = UIService()
        fonts = service.get_available_fonts()

        assert isinstance(fonts, list)
        assert "Arial" in fonts

    @patch("src.services.ui_service.QFont")
    def test_get_available_fonts_error(self, mock_qfont):
        """Test getting available fonts with error."""
        mock_qfont.families.side_effect = Exception("Font error")

        service = UIService()
        fonts = service.get_available_fonts()

        assert fonts == []

    @patch.object(UIService, "get_available_fonts")
    def test_test_font_availability(self, mock_get_fonts):
        """Test font availability testing."""
        mock_get_fonts.return_value = ["Arial", "Helvetica", "Times"]

        service = UIService()
        result = service.test_font_availability("Arial")

        assert result is True

    @patch("src.services.ui_service.QFont")
    def test_test_font_availability_error(self, mock_qfont):
        """Test font availability testing with error."""
        mock_qfont.side_effect = Exception("Font error")

        service = UIService()
        result = service.test_font_availability("Arial")

        assert result is False

    @patch("src.services.ui_service.QPainter")
    @patch("src.services.ui_service.QPixmap")
    @patch("src.services.ui_service.QPen")
    @patch("src.services.ui_service.QColor")
    def test_update_label_pixmap(
        self, mock_qcolor, mock_qpen, mock_qpixmap, mock_qpainter
    ):
        """Test updating label pixmap with style information."""
        # Mock QLabel
        mock_label = MagicMock(spec=QLabel)
        mock_label.width.return_value = 30
        mock_label.height.return_value = 16

        # Mock QPixmap and related classes
        mock_pixmap_instance = MagicMock()
        mock_qpixmap.return_value = mock_pixmap_instance

        mock_painter_instance = MagicMock()
        mock_qpainter.return_value = mock_painter_instance

        mock_color_instance = MagicMock()
        mock_qcolor.return_value = mock_color_instance

        mock_pen_instance = MagicMock()
        mock_qpen.return_value = mock_pen_instance

        service = UIService()
        style_info = {"color": "#FF0000", "line_style": "--", "line_width": 2.0}

        service.update_label_pixmap(mock_label, style_info)

        # Verify QPixmap was created with correct dimensions
        mock_qpixmap.assert_called_once_with(30, 16)
        mock_pixmap_instance.fill.assert_called_once()

        # Verify painter was used
        mock_qpainter.assert_called_once_with(mock_pixmap_instance)

        # Verify label.setPixmap was called
        mock_label.setPixmap.assert_called_once_with(mock_pixmap_instance)
        mock_label.setScaledContents.assert_called_once_with(True)

    def test_setup_label_indicator_logic_only(self):
        """Test setting up a label as style indicator - logic only."""
        import os

        # Skip this test in headless CI environment as Qt GUI operations may fail
        if os.environ.get("QT_QPA_PLATFORM") == "offscreen":
            import pytest

            pytest.skip("Skipping GUI test in headless environment")

        # Test only the logic without Qt GUI operations
        from unittest.mock import MagicMock, patch

        # Mock QLabel to avoid Qt GUI operations
        mock_label = MagicMock()

        service = UIService()
        style_info = {"color": "#00FF00", "line_style": "-", "line_width": 1.5}

        # Mock update_label_pixmap to avoid Qt operations
        with patch.object(service, "update_label_pixmap") as mock_update:
            result = service.setup_label_indicator(mock_label, style_info)

        # Verify return value
        assert result == mock_label

        # Verify style info was stored
        assert hasattr(mock_label, "_style_info")
        assert mock_label._style_info == style_info

        # Verify update_label_pixmap was called
        mock_update.assert_called_once_with(mock_label, style_info)

        # Verify resizeEvent was set
        assert hasattr(mock_label, "resizeEvent")
        assert callable(mock_label.resizeEvent)
