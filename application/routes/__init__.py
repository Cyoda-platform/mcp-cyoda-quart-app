"""
Application routes module.
"""

from .subscriber_routes import subscriber_bp
from .catfact_routes import catfact_bp
from .emaildelivery_routes import emaildelivery_bp
from .weeklyschedule_routes import weeklyschedule_bp
from .reporting_routes import reporting_bp

__all__ = [
    'subscriber_bp',
    'catfact_bp',
    'emaildelivery_bp',
    'weeklyschedule_bp',
    'reporting_bp'
]
