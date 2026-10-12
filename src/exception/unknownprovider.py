"""@file
@brief class for UnknownProviderException
@author DBZash
@date 2026-10-12
@version 0.1.0
"""

class UnknownProviderException(Exception):
    """exception thrown whenever the reported provider is unknown"""
    def __init__(self, provider):
        super().__init__()
        self.provider = provider

    def __str__(self):
        return f"Couldn't resolve the API linked with the following reported provider: {self.provider}."