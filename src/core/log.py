import logging
from uvicorn.logging import DefaultFormatter

def configure_logging():
    formatter = DefaultFormatter(
        fmt="%(levelprefix)s %(asctime)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        use_colors=True,
    )

    # Общий root логгер
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    root_logger.handlers.clear()

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    root_logger.addHandler(stream_handler)

    # 🔹 Uvicorn логгер (опционально)
    uvicorn_logger = logging.getLogger("uvicorn")
    uvicorn_logger.handlers.clear()
    uvicorn_logger.addHandler(stream_handler)
    uvicorn_logger.setLevel(logging.INFO)

    # 🔸 SQLAlchemy engine
    sa_logger = logging.getLogger("sqlalchemy.engine")
    sa_logger.handlers.clear()
    sa_logger.addHandler(stream_handler)
    sa_logger.setLevel(logging.DEBUG)
