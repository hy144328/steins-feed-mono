import io
import logging
import os
import sys
import time
import typing

class LoggerFactory:
    @classmethod
    def get_logger(cls, name: str) -> logging.Logger:
        return logging.getLogger(name)

    @classmethod
    def add_stream_handler(
        cls,
        logger: logging.Logger = logging.getLogger(),
        stream: typing.TextIO = sys.stdout,
        level: int = logging.NOTSET,
        fmt: typing.Optional[str] = None,
    ):
        handler = logging.StreamHandler(stream)
        handler.setLevel(level)
        cls.add_formatter(handler, fmt)

        logger.addHandler(handler)

    @classmethod
    def add_string_handler(
        cls,
        logger: logging.Logger = logging.getLogger(),
        level: int = logging.NOTSET,
        fmt: typing.Optional[str] = None,
    ):
        handler = logging.StreamHandler(io.StringIO())
        handler.setLevel(level)
        cls.add_formatter(handler, fmt)

        logger.addHandler(handler)

    @classmethod
    def add_file_handler(
        cls,
        logger: logging.Logger = logging.getLogger(),
        file_pointer: typing.Optional[typing.TextIO] = None,
        level: int = logging.NOTSET,
        fmt: typing.Optional[str] = None,
    ):
        if file_pointer is None:
            try:
                os.mkdir("logs.d")
            except FileExistsError:
                pass

            with open(f"logs.d/{time.time_ns()}.log", "w") as file_pointer:
                pass

        handler = logging.FileHandler(file_pointer.name)
        handler.setLevel(level)
        cls.add_formatter(handler, fmt)

        logger.addHandler(handler)

    @classmethod
    def add_formatter(
        cls,
        handler: logging.Handler,
        fmt: typing.Optional[str] = None,
    ):
        fmt = fmt or "[%(asctime)s] %(levelname)s:%(name)s: %(message)s"
        formatter = logging.Formatter(fmt)
        handler.setFormatter(formatter)

    @classmethod
    def set_level(
        cls,
        logger: logging.Logger = logging.getLogger(),
        level: int = logging.WARNING,
    ):
        logger.setLevel(level)
