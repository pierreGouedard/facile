# Global import
from pandas import Timestamp, Timedelta


def get_current_start_date():
    t_now = Timestamp.now()
    return (t_now - Timedelta(days=t_now.weekday())).date()


def get_current_week():
    return str(get_current_start_date())


