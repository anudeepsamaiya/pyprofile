import logging

logger = logging.getLogger("__name__")

def load_fixtures(fixtures: list, raw=False, file_type=None, *args, **kwargs):
    if raw and file_type:
        for item in fixures:
            with open(item, "r") as fd:
                return fd.read()
    else:
        logger.info("Invalid raw file type.")
    return value
