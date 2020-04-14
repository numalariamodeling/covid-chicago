import numpy as np
from datetime import date, timedelta

# Simlation setup
def load_setting_parameter ():
    populations = {
        'IL': 12830632,
        'NMH_catchment': 315000,
        'Chicago': 2700000,
        'EMS_3': 560165
    }
    Kis = {
        'NMH_catchment': np.linspace(1.5e-6, 2e-6, 3),
        'Chicago': np.linspace(2e-7, 3e-7, 3),
        'EMS_3': np.linspace(5e-7, 9e-7, 3),
        'IL': np.linspace(3.5e-8, 5.3e-8, 3)
    }
    startdate = {
        'NMH_catchment': date(2020, 2, 28),
        'Chicago': date(2020, 2, 20),
        'EMS_3': date(2020, 2, 28),
        'IL': date(2020, 2, 28)
    }

    return populations, Kis, startdate
