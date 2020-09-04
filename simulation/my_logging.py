import platform, sys, logging

def log_metadata_and_start_message(num_processes, logger):
    python_version = "Python " + sys.version
    os_info = platform.platform()
    pc_name = platform.node()

    logger.info(python_version)
    logger.info("%s %s", pc_name, os_info)
    if num_processes > 1:
        logger.info("Start: Run simulations on with %d threads", num_processes)
    else:
        logger.info("Start: Run simulations on with %d thread", num_processes)


def setup_logging(filename=None, mode='a', print_log_messages=True, level=logging.INFO):
    """
    Setup logging: use `logging.info(msg)` or `logger.info(msg)` to log something into a file and console.
    """
    logger = logging.getLogger("")  # Use root logger   #  logging.getLogger(name) # or use a named one?
    # Clear previous handlers, if any
    if (logger.hasHandlers()):
        logger.handlers.clear()
    # Formatter
    _formatter = logging.Formatter('{asctime} {levelname} {threadName} {name} {message}', style='{')
    # Handler
    if filename is not None:
        log_handler = logging.FileHandler(filename, mode=mode)
        logger.addHandler(log_handler)
        log_handler.setFormatter(_formatter)
        log_handler.setLevel(level)
    if print_log_messages:
        stream_handler = logging.StreamHandler(sys.stdout)
        stream_handler.setFormatter(_formatter)
        logger.addHandler(stream_handler)
        stream_handler.setLevel(level)
    # Set level - pass all messages with level INFO or higher (WARNING, ERROR, CRITICAL)
    logger.setLevel(level)

    return logger