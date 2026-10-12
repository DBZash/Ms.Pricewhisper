"""@file utility.py
@brief Common utility functions
@author DBZash
@date 2026-10-12
@version 0.1.0
"""

import datetime

#CONSTANTS
HOUR = 3600
DAY = 86400
WEEK = 604800

#UTILITIES FUNCTIONS
def delta_over_a_target(date1 : datetime.datetime, date2 : datetime.datetime, target : int):
    delta = abs(date2 - date1)
    return delta.total_seconds() > target