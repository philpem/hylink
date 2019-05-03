

class ADKException(Exception):
    """ Base class for ADK exceptions """
    pass

class HRNPBadSignature(ADKException):
    """ HRNP: Bad packet signature """
    pass

class HRNPUnhandledType(ADKException):
    """ HRNP: Unrecognised/unhandled packet type """
    pass

class HRNPCannotCreate(ADKException):
    """ HRNP: Cannot create packets of this type """
    pass

class HYTPacketDataError(ADKException):
    """ Hytera data: packet is not valid """
    pass

