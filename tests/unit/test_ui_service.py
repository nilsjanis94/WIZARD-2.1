"""
Unit tests for UIService

Tests the UI service functionality including font management and widget operations.
"""

import pytest
from unittest.mock import MagicMock, patch
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QWidget, QLabel, QCheckBox, QPushButton, QLineEdit

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

    @patch('src.services.ui_service.QLabel')
    @patch('src.services.ui_service.QCheckBox')
    @patch('src.services.ui_service.QPushButton')
    @patch('src.services.ui_service.QLineEdit')
    def test_fix_ui_visibility(self, mock_line_edit, mock_button, mock_checkbox, mock_label):
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
        mock_y2_combo.setCurrentText.assert_called_with("Temp")  # PT100 data is in 'Temp' column
        mock_x_combo.setCurrentText.assert_called_with("Time")

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

    @patch('src.services.ui_service.QFont')
    def test_get_available_fonts(self, mock_qfont):
        """Test getting available fonts."""
        mock_qfont.families.return_value = ["Arial", "Helvetica", "Times"]
        
        service = UIService()
        fonts = service.get_available_fonts()
        
        assert isinstance(fonts, list)
        assert "Arial" in fonts

    @patch('src.services.ui_service.QFont')
    def test_get_available_fonts_error(self, mock_qfont):
        """Test getting available fonts with error."""
        mock_qfont.families.side_effect = Exception("Font error")
        
        service = UIService()
        fonts = service.get_available_fonts()
        
        assert fonts == []

    @patch.object(UIService, 'get_available_fonts')
    def test_test_font_availability(self, mock_get_fonts):
        """Test font availability testing."""
        mock_get_fonts.return_value = ["Arial", "Helvetica", "Times"]
        
        service = UIService()
        result = service.test_font_availability("Arial")
        
        assert result is True

    @patch('src.services.ui_service.QFont')
    def test_test_font_availability_error(self, mock_qfont):
        """Test font availability testing with error."""
        mock_qfont.side_effect = Exception("Font error")
        
        service = UIService()
        result = service.test_font_availability("Arial")
        
        assert result is False
