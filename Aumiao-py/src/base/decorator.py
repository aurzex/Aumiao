from collections.abc import Callable
from functools import wraps
from locale import Error
from time import sleep
from typing import Any


def singleton(cls):
	_instance = {}

	def _singleton(*args, **kwargs):
		if cls not in _instance:
			_instance[cls] = cls(*args, **kwargs)
		return _instance[cls]

	return _singleton


def retry(retries: int = 3, delay: float = 1) -> Callable:
	if retries < 1 or delay <= 0:
		raise ValueError("Are you high, mate?")

	def decorator(func: Callable) -> Callable:
		@wraps(func)
		def wrapper(*args, **kwargs) -> Any:
			for i in range(1, retries + 1):
				try:
					return func(*args, **kwargs)
				except Exception as e:
					if i == retries:
						print(f"Error: {repr(e)}.")
						print(f'"{func.__name__}()" failed after {retries} retries.')
						break
					else:
						print(f"Error: {repr(e)} -> Retrying...")
						sleep(delay)
			raise Error()

		return wrapper

	return decorator
