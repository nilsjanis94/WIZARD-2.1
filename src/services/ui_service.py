"""
UI Service for WIZARD-2.1

Cross-platform UI styling and font management.
"""

import logging
import platform
from typing import Optional

from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QWidget


class UIService:
    """
    Service for managing UI styling and fonts across platforms.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.current_platform = platform.system()
        
    def setup_fonts(self, widget: QWidget) -> bool:
        """
        Set up cross-platform fonts for a widget and all its children.
        
        Args:
            widget: The widget to apply fonts to
            
        Returns:
            True if fonts were applied successfully, False otherwise
        """
        try:
            # Get platform-appropriate font
            font = self._get_platform_font()
            
            # Apply font to widget and all children
            self._apply_font_recursively(widget, font)
            
            self.logger.info(f"Fonts applied successfully: {font.family()} on {self.current_platform}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to setup fonts: {e}")
            return False
    
    def _get_platform_font(self) -> QFont:
        """
        Get the appropriate font for the current platform.
        Uses fonts that actually work based on testing.
        
        Returns:
            QFont configured for the current platform
        """
        font = QFont()
        
        # Use fonts that actually work (based on testing)
        if self.current_platform == "Darwin":  # macOS
            # Arial works reliably on macOS
            font.setFamily("Arial")
        elif self.current_platform == "Windows":
            # Arial works on Windows
            font.setFamily("Arial")
        elif self.current_platform == "Linux":
            # Arial works on Linux
            font.setFamily("Arial")
        else:
            # Generic fallback
            font.setFamily("Arial")
        
        # Set consistent properties
        font.setPointSize(11)  # Slightly larger for better visibility
        font.setWeight(QFont.Weight.Normal)
        font.setStyleHint(QFont.StyleHint.SansSerif)
        
        return font
    
    def _apply_font_recursively(self, widget: QWidget, font: QFont) -> None:
        """
        Apply font to widget and all its children recursively.
        
        Args:
            widget: The widget to apply font to
            font: The font to apply
        """
        try:
            # Apply font to current widget
            widget.setFont(font)
            
            # Apply font to all child widgets
            for child in widget.findChildren(QWidget):
                child.setFont(font)
                
        except Exception as e:
            self.logger.debug(f"Could not apply font to widget: {e}")
    
    def get_available_fonts(self) -> list[str]:
        """
        Get list of available fonts on the current system.
        
        Returns:
            List of available font family names
        """
        try:
            return QFont.families()
        except Exception as e:
            self.logger.error(f"Could not get available fonts: {e}")
            return []
    
    def test_font_availability(self, font_name: str) -> bool:
        """
        Test if a specific font is available on the system.
        
        Args:
            font_name: Name of the font to test
            
        Returns:
            True if font is available, False otherwise
        """
        try:
            available_fonts = self.get_available_fonts()
            return font_name in available_fonts
        except Exception as e:
            self.logger.error(f"Could not test font availability: {e}")
            return False
