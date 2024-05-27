'''
Created on Sep 2, 2013

@author: Sven
'''


class UssError(RuntimeError):
    """Every UssError error extends this exception."""

class UssPortError(UssError):
    """Use this exception for uss interface port errors."""

class UssStatusError(UssError):
    """Use this exception for uss interface errors while retrieving status
    informations.
    """

class UssServiceNotSupportedError(UssError):
    """Use this exception if service is not supported."""

class UssServiceReponseError(UssError):
    """Use this exception for uss interface service response errors."""

class UssPortReadError(UssError):
    """Use this exception for uss interface port errors while reading."""

class UssResponseChecksumError(UssServiceReponseError):
    """Use this exception if the received service has wrong checksum."""

class UssInvalidLengthError(UssServiceReponseError):
    """Use this exception if the received service has wrong length."""

class UssInvalidAddressError(UssServiceReponseError):
    """Use this exception if the received service has wrong address."""

class UssInvalidResponseError(UssServiceReponseError):
    """Use this exception if the received service has wrong response code."""

class UssRemoteChecksumError(UssError):
    """Use this exception to indicate a checksum failure on the client site."""

class UssRemoteUnknownError(UssError):
    """Use this exception to indicate a not known error code got from client.
    """


