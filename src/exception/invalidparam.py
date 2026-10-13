"""@file
@brief class for Invalid Parameters Exception
@author DBZash
@date 2026-10-13
@version 0.1.0
"""

class InvalidParamException(Exception):
    """exception thrown whenever a user gave an invalid parameter to a command """
    def __init__(self, param, validParams):
        super().__init__()
        self.param = param
        self.validParams = validParams

    def __str__(self):
        return f"gave an invalid param -> {self.param}, param should be -> {self.validParams}"

    def prompt(self):
        return (f"Sorry but you gave me an invalid param -> {self.param}.\n"
                f"Please try again, a valid param should be -> {self.validParams}")