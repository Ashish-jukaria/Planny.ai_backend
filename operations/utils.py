from datetime import datetime


def miliSecondToDateTime(miliSeconds):
    return datetime.fromtimestamp(miliSeconds / 1000.0)
