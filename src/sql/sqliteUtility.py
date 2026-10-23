"""@file sqliteUtility.py
@brief Common utility functions for SQLiteManager
@author DBZash
@date 2026-10-14
@version 0.2.0
"""

import datetime

# CONSTANTS
HOUR = 3600
FRESH_GAME = 10800
DAY = 86400
WEEK = 604800

# FUNCTIONS
def delta_over_a_target(date1 : datetime.datetime, date2 : datetime.datetime, target : int) -> bool:
    delta = abs(date2 - date1)
    return delta.total_seconds() > target

def delta_under_a_target(date1 : datetime.datetime, date2 : datetime.datetime, target : int) -> bool:
    delta = abs(date2 - date1)
    return delta.total_seconds() < target

def title_formatting(title : str) -> tuple:
    title_words = title.split()
    capitalized_title = []
    all_caps_title = []
    for word in title_words:
        capitalized_title.append(word.capitalize())
        all_caps_title.append(word.upper())
    titleA = " ".join(capitalized_title)
    titleB = " ".join(all_caps_title)
    return titleA, titleB
