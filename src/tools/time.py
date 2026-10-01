from functools import wraps
from src.tools.logger import get_logger
import time

LOGGER = get_logger('EXEC_TIME')

def measure_time(func):
  @wraps(func)
  def wrapper(*args, **kwargs):
    start_time = time.perf_counter()
    result = func(*args, **kwargs)
    end_time = time.perf_counter()

    exec_time = end_time - start_time
    LOGGER.info(f"Function '{func.__name__}' used {exec_time:.6f} time ")
    return result

  return wrapper