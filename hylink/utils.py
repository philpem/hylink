# ADK - DMR utilities


def dmrIPtoID(x):
    # TODO type check
    return x & 0xFFFFFF


def dmrIPtoStr(x):
    a = (x >> 24) & 0xFF
    b = (x >> 16) & 0xFF
    c = (x >>  8) & 0xFF
    d =  x        & 0xFF
    return "%d.%d.%d.%d" % (a, b, c, d)

