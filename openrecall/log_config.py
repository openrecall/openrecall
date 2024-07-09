import logging
from logging.handlers import RotatingFileHandler
  
def setup_logging(log_file='openrecall.log', max_bytes=10000, backup_count=1):
    # Configure the root logger
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    # Create a file handler
    file_handler = RotatingFileHandler(log_file, maxBytes=max_bytes, backupCount=backup_count)
    file_handler.setLevel(logging.NOTSET)

    # Create a console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.NOTSET)

    # Create a logging format
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    # Add the handlers to the root logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    logger.setLevel(logging.WARNING)

def log_always (*args):
    logger = logging.getLogger()
    old_level=logger.getEffectiveLevel()
    logger.setLevel(logging.INFO)
    logger.info(" ".join(map(str,args)))
    logger.setLevel(old_level)

def set_logging_level (loglevel):
    mp=logging.getLevelNamesMapping()
    if loglevel in mp.keys():
        root_logger=logging.getLogger()
        old_level=root_logger.getEffectiveLevel()
        root_logger.setLevel(mp[loglevel])
        log_always("set DEBUGLEVEL=",logging.getLevelName(loglevel),"from",logging.getLevelName(old_level))
    else: 
        logging.error("Debug level not known: "+loglevel)
        logging.error("use one of: "+" ".join(mp.keys()))
