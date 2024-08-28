import logging
import logging.config
import sys
from pathlib import Path
from loguru import logger
import json
import inspect
import uuid



class InterceptHandler(logging.Handler):
    loglevel_mapping = {
        50: 'CRITICAL',
        40: 'ERROR',
        30: 'WARNING',
        20: 'INFO',
        10: 'DEBUG',
        5:  'TRACE',
        0:  'NOTSET'
    }
    def emit(self, record: logging.LogRecord):
        request_id = str(uuid.uuid4())
        # Get the corresponding Loguru if it exists
        level: str | int
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = self.loglevel_mapping.get(record.levelno, record.levelname)

        # Find caller from where originated the logged message.
        frame, depth = inspect.currentframe(), 0
        while frame and (depth == 0 or frame.f_code.co_filename == logging.__file__):
            frame = frame.f_back
            depth += 1

        log = logger.bind(request_id=request_id)
        log.opt(
            depth=depth,
            exception=record.exc_info
        ).log(level, record.getMessage())

class CustomizeLogger:

    @classmethod
    def make_logger(cls, config_path: Path):
        config = cls.load_logging_config(config_path)
        logging_config = config.get("logger", {})

        # Ensure that 'filepath' points to the directory and 'filename' is the log file name
        # TODO: Implement the commented for production use.
        # log_directory = Path(logging_config.get('filepath', '/var/log/cron_interpreter'))
        # log_filename = logging_config.get('filename', 'access.log')

        log_directory = Path(logging_config.get('filepath', 'crontab_interpreter'))
        log_filename = logging_config.get('filename', 'app.log')

        customized_logger = cls.customize_logging(
            filepath=log_directory,
            filename=log_filename,
            level=logging_config.get('level', 'INFO'),
            retention=logging_config.get('retention', '20 days'),
            rotation=logging_config.get('rotation', '1 month'),
            format_str=logging_config.get(
                'format',
                "<level>{level: <8}</level> <green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> request id: {extra[request_id]} - "
                "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
            )
        )
        return customized_logger


    @classmethod
    def customize_logging(cls, filepath: Path, filename: str, level: str, rotation: str, retention: str, format_str: str):
        logger.remove()

        log_dir = filepath
        if not  log_dir.exists():
            log_dir.mkdir(parents=True, exist_ok=True)

        log_file_path = filepath / filename
        logger.add(
            sys.stdout,
            enqueue=True,
            backtrace=True,
            level=level.upper(),
            format=format_str
        )
        logger.add(
            str(log_file_path),
            rotation=rotation,
            retention=retention,
            enqueue=True,
            backtrace=True,
            level=level.upper(),
            format=format_str
        )

        # Custom color for each level
        logger.level("INFO", color="<blue>")
        logger.level("WARNING", color="<yellow>")
        logger.level("ERROR", color="<red>")
        logger.level("CRITICAL", color="<red>")


        # Redirect standard logging to loguru
        cls._configure_standard_logging()

        return logger.bind(request_id=None, method=None)

    @staticmethod
    def _configure_standard_logging():
        logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)
        logging.getLogger("uvicorn.access").handlers = [InterceptHandler()]
        for _log in ['uvicorn', 'uvicorn.error', 'fastapi']:
            _logger = logging.getLogger(_log)
            _logger.handlers = [InterceptHandler()]

    @classmethod
    def load_logging_config(cls, config_path: Path) -> dict:
        """
        Load the logging configuration from a JSON file and return it as a dictionary.

        Args:
            config_path (Path): The path to the JSON configuration file.

        Returns:
            dict: The loaded logging configuration.

        Raises:
            FileNotFoundError: If the JSON configuration file is not found.
            json.JSONDecodeError: If the JSON file contains invalid JSON.
            Exception: For any other unforeseen errors.
        """
        try:
            with open(config_path, "r") as config_file:
                return json.load(config_file)
        except FileNotFoundError as e:
            logger.error(f"Logging configuration file not found at {config_path}: {e}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in logging configuration file at {config_path}: {e}")
            raise
        except Exception as e:
            logger.exception(f"An unexpected error occurred while loading logging configuration from {config_path}: {e}")
            raise
