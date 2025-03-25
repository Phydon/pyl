import os
import logging.config
import atexit

NAME: str = "pyl"
LOG_DIR: str = "logs/"


def create_log_dir():
    os.makedirs(LOG_DIR, exist_ok=True)


class NonErrorFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool | logging.LogRecord:
        return record.levelno <= logging.INFO


def init_logger():
    log_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "filters": {"no_errors": {"()": "pyl.NonErrorFilter"}},
        "formatters": {
            "simple": {"format": "%(levelname)s: %(message)s"},
            "detailed": {
                "format": "[%(asctime)s] %(levelname)s [%(module)s] %(pathname)s:%(lineno)d: %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S %z",
            },
        },
        "handlers": {
            "stdout": {
                "class": "logging.StreamHandler",
                "formatter": "simple",
                "stream": "ext://sys.stdout",
                "filters": ["no_errors"],
            },
            "stderr": {
                "class": "logging.StreamHandler",
                "level": "WARNING",
                "formatter": "simple",
                "stream": "ext://sys.stderr",
            },
            "file": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": "INFO",
                "formatter": "detailed",
                "filename": f"{LOG_DIR}/{NAME}.log",
                "maxBytes": 10_000_000,  # 10 MB, max file size before creating new file
                "backupCount": 10,  # number of kept backups before overriding oldest one first
            },
            "queue_handler": {
                "class": "logging.handlers.QueueHandler",
                "handlers": ["stdout", "stderr", "file"],
                "respect_handler_level": True,
            },
        },
        "loggers": {
            "root": {
                "level": "DEBUG",
                "handlers": ["queue_handler"],
            }
        },
    }

    logging.config.dictConfig(log_config)

    queue_handler = logging.getHandlerByName("queue_handler")
    if queue_handler is not None:
        queue_handler.listener.start()
        atexit.register(queue_handler.listener.stop)


def main():
    create_log_dir()

    log = logging.getLogger(NAME)
    init_logger()

    log.debug("debug")
    log.info("info")
    log.warning("warning")
    log.error("error")
    log.critical("critical")


if __name__ == "__main__":
    main()
