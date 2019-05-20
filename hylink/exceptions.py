
class ADKException(Exception):
    """ Base class for ADK exceptions """
    pass


class HYTBadSignature(ADKException):
    """ HRNP: Bad packet signature """
    pass


class HYTUnhandledType(ADKException):
    """ HRNP: Unrecognised/unhandled packet type """
    pass


class HYTPacketDataError(ADKException):
    """ Hytera data: packet is not valid """
    pass

