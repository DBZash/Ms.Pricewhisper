"""@file
@brief class for Too many requests exception
@author DBZash
@date 2026-10-12
@version 0.1.0
"""

class TooManyRequestsException(Exception):
    """exception thrown whenever too many requests are made by a user"""
    def __init__(self, user):
        super().__init__()
        self.user = user

    def __str__(self):
        return f"Too many requests from {self.user} : ddos flag limit reached"