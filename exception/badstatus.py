"""
@file badstatus.py
@brief Class for badstatus exception
@author DBZash
@date 2026-10-01
@version 0.1.0
"""

class BadStatus(Exception):
    """@brief Exception thrown whenever a bad status is detected from the API
    @author DBZash
    """

    def __init__(self, message, status_code):
        """@brief Constructor for BadStatus exception
        :param message  The message to be displayed in the error message
        :param status_code  The status code to be displayed in the error message"""
        super().__init__(message)
        self.message = message
        self.status_code = status_code

    def __str__(self):
        """@brief String representation of the BadStatus Exception
        :return: The string representation associated with a specific instance of BadStatus"""
        return f"{self.message} (Error Code: {self.status_code})"
