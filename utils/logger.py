from loguru import logger

logger.add(
    "logs/app.log",
    rotation="1 MB",
    retention="10 days",
    level="INFO",  # 可以根据需要调整日志级别
    compression="zip"  # 压缩旧日志文件以节省空间
)