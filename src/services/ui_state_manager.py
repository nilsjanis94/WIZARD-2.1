"""
UI State Manager for WIZARD-2.1

This service manages the UI state transitions between Welcome and Plot modes.
It provides a clean interface for switching between different UI states.
"""

import logging
from enum import Enum
from typing import Optional

from PyQt6.QtWidgets import QWidget


class UIState(Enum):
    """Enumeration of possible UI states."""

    WELCOME = "welcome"
    PLOT = "plot"


class UIStateManager:
    """
    Manages UI state transitions between Welcome and Plot modes.

    This service provides a clean interface for switching between different
    UI states and ensures consistent state management across the application.
    """

    def __init__(self):
        """Initialize the UI State Manager."""
        self.logger = logging.getLogger(self.__class__.__name__)
        self.current_state: Optional[UIState] = None

        # Container references (will be set by main window)
        self.welcome_container: Optional[QWidget] = None
        self.plot_container: Optional[QWidget] = None

        self.logger.info("UI State Manager initialized")

    def set_containers(
        self, welcome_container: QWidget, plot_container: QWidget
    ) -> None:
        """
        Set the container references for state management.

        Args:
            welcome_container: The welcome screen container
            plot_container: The plot area container
        """
        self.welcome_container = welcome_container
        self.plot_container = plot_container
        self.logger.debug("Container references set")

    def show_welcome_mode(self) -> None:
        """
        Switch to welcome mode.

        This is the initial state when no TOB file is loaded.
        Shows the welcome screen and hides the plot area.
        """
        if not self._validate_containers():
            return

        # Show welcome container
        if self.welcome_container:
            self.welcome_container.setVisible(True)
            # Ensure size policy allows expansion
            from PyQt6.QtWidgets import QSizePolicy
            self.welcome_container.setSizePolicy(
                QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
            )
            self.logger.debug("Welcome container shown")

        # Hide plot container
        if self.plot_container:
            self.plot_container.setVisible(False)
            # Reset height restrictions when hiding
            self.plot_container.setMaximumHeight(0)
            self.plot_container.setMinimumHeight(0)
            # Reset size policy
            from PyQt6.QtWidgets import QSizePolicy

            self.plot_container.setSizePolicy(
                QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred
            )
            self.logger.info("Plot container hidden and resized")

        self.current_state = UIState.WELCOME
        self.logger.info("Switched to welcome mode")

    def show_plot_mode(self) -> None:
        """
        Switch to plot mode.

        This state is active when a TOB file is loaded.
        Hides the welcome screen and shows the plot area.
        """
        if not self._validate_containers():
            return

        # Hide welcome container and show plot container
        if self.welcome_container and self.plot_container:
            # Copy size policy from welcome container to plot container
            self.plot_container.setSizePolicy(self.welcome_container.sizePolicy())

            # Hide welcome container
            self.welcome_container.setVisible(False)
            self.logger.info("Welcome container hidden")

            # Show plot container
            self.plot_container.setVisible(True)
            # Remove height restrictions to make container visible
            self.plot_container.setMaximumHeight(16777215)  # Qt's maximum value
            self.plot_container.setMinimumHeight(0)  # Allow flexible height
            # Ensure size policy allows expansion
            from PyQt6.QtWidgets import QSizePolicy
            self.plot_container.setSizePolicy(
                QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
            )
            self.logger.info("Plot container shown and resized")

        self.current_state = UIState.PLOT
        self.logger.info("Switched to plot mode")

    def get_current_state(self) -> Optional[UIState]:
        """
        Get the current UI state.

        Returns:
            The current UI state, or None if not initialized
        """
        return self.current_state

    def is_welcome_mode(self) -> bool:
        """
        Check if currently in welcome mode.

        Returns:
            True if in welcome mode, False otherwise
        """
        return self.current_state == UIState.WELCOME

    def is_plot_mode(self) -> bool:
        """
        Check if currently in plot mode.

        Returns:
            True if in plot mode, False otherwise
        """
        return self.current_state == UIState.PLOT

    def _validate_containers(self) -> bool:
        """
        Validate that container references are set.

        Returns:
            True if containers are valid, False otherwise
        """
        self.logger.info(
            "Validating containers - welcome: %s, plot: %s",
            self.welcome_container is not None,
            self.plot_container is not None,
        )

        if not self.welcome_container:
            self.logger.error("Welcome container not set")
            return False

        if not self.plot_container:
            self.logger.error("Plot container not set")
            return False

        self.logger.info("Container validation successful")
        return True

    def reset_to_initial_state(self) -> None:
        """
        Reset to the initial state (welcome mode).

        This is called when the application starts or when
        all data is cleared.
        """
        self.show_welcome_mode()
        self.logger.info("Reset to initial state (welcome mode)")

    def get_state_info(self) -> dict:
        """
        Get information about the current state.

        Returns:
            Dictionary with state information
        """
        return {
            "current_state": self.current_state.value if self.current_state else None,
            "welcome_visible": (
                self.welcome_container.isVisible() if self.welcome_container else False
            ),
            "plot_visible": (
                self.plot_container.isVisible() if self.plot_container else False
            ),
        }
