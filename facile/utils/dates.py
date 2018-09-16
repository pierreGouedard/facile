# Global import
from pandas import Timestamp, Timedelta

# Local import
import settings


def get_bound_from_business_year(b_year):
    d_dates = {'start': Timestamp(settings.facile_business_closing_date.format(b_year)),
               'end': Timestamp(settings.facile_business_closing_date.format(b_year = 1))}

    return d_dates


def get_business_year_from_date(date):
    date_closing = Timestamp(settings.facile_business_closing_date.format(2000))
    if date.month >= date_closing.month:
        b_year = date.year
    else:
        b_year = date.year - 1

    return b_year


def get_bound_dates(date):
    return get_bound_from_business_year(get_business_year_from_date(date))


def get_current_bound_dates():
    return get_bound_dates(Timestamp.now())


def get_current_start_date():
    t_now = Timestamp.now()
    return (t_now - Timedelta(days=t_now.weekday())).date()


def get_current_week():
    return str(get_current_start_date())


