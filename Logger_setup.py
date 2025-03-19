from loguru import logger
import datetime

logger.add(f'error_logs/{datetime.date.today()}.log', rotation='1 day')
