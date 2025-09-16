"""
Application entities module.
"""

from .catfact.version_1.catfact import CatFact
from .emaildelivery.version_1.emaildelivery import EmailDelivery
from .subscriber.version_1.subscriber import Subscriber
from .weeklyschedule.version_1.weeklyschedule import WeeklySchedule

__all__ = ["Subscriber", "CatFact", "EmailDelivery", "WeeklySchedule"]
