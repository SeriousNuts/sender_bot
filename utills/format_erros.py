import traceback


def format_error_traceback(error):
    return "".join(traceback.format_exception(etype=type(error), value=error, tb=error.__traceback__))
