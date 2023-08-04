import logging
import logging.config
import os.path
import pathlib

class AppCore:
    name = "ihl"

    def __init__(self, name=None):
        if name is not None:
            self.name = name

    def home_directory(self):
        return str(pathlib.Path.home())
        # from os.path import expanduser
        # home = expanduser("~")

    def app_directory(self):
        return os.path.join(self.home_directory(), self.name)

    def extended_help_path(self, filename="extended.help.txt"):
        return os.path.join(self.app_directory(), filename)

    def app_log_path(self):
        return os.path.join(self.app_directory(), "log.txt")

    def read_extended_help(self):
        try:
            if os.path.exists(self.extended_help_path()):
                with open(self.extended_help_path(), "r") as h:
                    self.logger().debug(f"Reading extended help '{self.extended_help_path()}'.")
                    return h.read()
            else:
                self.logger().debug(f"Extended help file does not exists on expected path '{self.extended_help_path()}'.")
                return ""
        except Exception as e:
            self.logger().error(f"Reading extended help file from '{self.extended_help_path()}' failed")
            return ""

    def logger(self):
        return logging.getLogger(self.name)

    def set_standard_logger(self):
        os.makedirs(os.path.dirname(self.app_log_path()), exist_ok=True)
        logging.config.dictConfig(self.logger_config())

    def logger_config(self):
        return {
            'version': 1,
            'disable_existing_loggers': False,
            'loggers': {
                f"{self.name}": {
                    'level': logging.DEBUG,
                    'propagate': False,
                    'handlers': ['console_handler', 'time_rotating_file_handler'],
                },
            },

            'handlers': {
                'console_handler': {
                    'level': logging.INFO,
                    'formatter': 'simple',
                    'class': 'logging.StreamHandler',
                    'stream': 'ext://sys.stdout',
                },

                'time_rotating_file_handler': {
                    'level': logging.DEBUG,
                    'formatter': 'generic',
                    'class': 'logging.handlers.TimedRotatingFileHandler',
                    'filename': self.app_log_path(),
                    'when': 'midnight',
                    'backupCount': 5
                },
            },

            'formatters': {
                'generic': {
                    'format': '%(asctime)s %(levelname)s %(message)s'
                },
                'simple': {
                    'format': '%(message)s'
                }
            },
        }