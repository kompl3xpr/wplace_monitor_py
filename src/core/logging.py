import logging

class StatusBarHandler(logging.Handler):
    def __init__(self, status_bar_widget):
        super().__init__()
        self.status_bar_widget = status_bar_widget

    def emit(self, record):
        log_entry = self.format(record)
        self.status_bar_widget.set_logging_info(log_entry)

def init_logger(status_bar_widget, level=logging.INFO):
    logger = logging.getLogger("wplace_monitor")
    logger.setLevel(level)
    logger.propagate = False

    # Terminal handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(message)s'))
    logger.addHandler(console_handler)

    # Status bar handler
    status_bar_handler = StatusBarHandler(status_bar_widget)
    status_bar_handler.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(message)s'))
    logger.addHandler(status_bar_handler)

def logger():
    return logging.getLogger("wplace_monitor")