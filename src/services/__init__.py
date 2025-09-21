"""
Services package for WIZARD-2.1

Contains all service classes for business logic and external integrations.
"""

# Import Qt-free services first (always available)
from .analytics_service import AnalyticsService
from .encryption_service import EncryptionService
from .tob_service import TOBService

# Optional Qt-dependent services
try:
    from .axis_ui_service import AxisUIService

    PYQT6_SERVICES_AVAILABLE = True
except ImportError:
    AxisUIService = None
    PYQT6_SERVICES_AVAILABLE = False

try:
    from .data_service import DataService

    DATA_SERVICE_AVAILABLE = True
except ImportError:
    DataService = None
    DATA_SERVICE_AVAILABLE = False

try:
    from .error_service import ErrorService

    ERROR_SERVICE_AVAILABLE = True
except ImportError:
    ErrorService = None
    ERROR_SERVICE_AVAILABLE = False

try:
    from .plot_service import PlotService

    PLOT_SERVICE_AVAILABLE = True
except ImportError:
    PlotService = None
    PLOT_SERVICE_AVAILABLE = False

try:
    from .plot_style_service import PlotStyleService

    PLOT_STYLE_SERVICE_AVAILABLE = True
except ImportError:
    PlotStyleService = None
    PLOT_STYLE_SERVICE_AVAILABLE = False

try:
    from .ui_service import UIService

    UI_SERVICE_AVAILABLE = True
except ImportError:
    UIService = None
    UI_SERVICE_AVAILABLE = False

try:
    from .ui_state_manager import UIStateManager

    UI_STATE_MANAGER_AVAILABLE = True
except ImportError:
    UIStateManager = None
    UI_STATE_MANAGER_AVAILABLE = False

__all__ = [
    "AnalyticsService",
    "EncryptionService",
    "TOBService",
    # Optional services (may be None if PyQt6 not available)
    "AxisUIService",
    "DataService",
    "ErrorService",
    "PlotService",
    "PlotStyleService",
    "UIService",
    "UIStateManager",
]
