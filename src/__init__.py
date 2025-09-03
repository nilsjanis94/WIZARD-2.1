"""
WIZARD-2.1 - Scientific Data Analysis and Visualization Tool

A professional desktop application for processing and analyzing .TOB temperature data files
from scientific instruments. Built with PyQt6 and following enterprise-grade development
standards.

Author: FIELAX Development Team
Version: 2.1.0
License: Proprietary
"""

__version__ = "2.1.0"
__author__ = "FIELAX Development Team"
__email__ = "dev@fielax.com"
__description__ = "Scientific Data Analysis and Visualization Tool"

# Package imports for easy access
from .models import *
from .views import *
from .controllers import *
from .services import *
from .utils import *
from .exceptions import *
