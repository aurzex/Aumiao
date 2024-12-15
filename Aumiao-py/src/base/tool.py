import time

from .decorator import singleton


@singleton
class CodeMaoProcess:
	def process_reject(
		self,
		data: list | dict,
		reserve: list | None = None,
		exclude: list | None = None,
	) -> list[dict[str, str | int | bool]] | dict[str, str | int | bool] | None:
		"""
		处理输入数据,根据 `reserve` 或 `exclude` 对键进行筛选.

		:param data: 要处理的输入数据,支持列表或字典.
		:param reserve: 需要保留的键列表(可选).
		:param exclude: 需要排除的键列表(可选).
		:return: 筛选后的数据,类型与输入一致(列表或字典).
		:raises ValueError: 如果同时提供了 `reserve` 和 `exclude` 参数,抛出异常.
		"""
		if reserve and exclude:
			raise ValueError("请仅提供 'reserve' 或 'exclude' 中的一个参数,不要同时使用.")

		def filter_keys(item) -> dict[str, str | int]:
			if reserve is not None:
				return {key: value for key, value in item.items() if key in reserve}
			elif exclude is not None:
				return {key: value for key, value in item.items() if key not in exclude}
			else:
				return {}

		if isinstance(data, list):
			return [filter_keys(item) for item in data]
		elif isinstance(data, dict):
			return filter_keys(data)
		else:
			raise ValueError("不支持的数据类型")

	def process_shielding(self, content: str) -> str:
		"""
		对输入字符串进行特殊字符插入处理(用于屏蔽).

		:param content: 输入字符串.
		:return: 处理后的字符串,插入了零宽字符.
		"""
		content_bytes = [item.encode("UTF-8") for item in content]
		result = b"\xe2\x80\x8b".join(content_bytes).decode("UTF-8")
		return result

	def process_timestamp(self, timestamp: int) -> str:
		"""
		将时间戳转换为人类可读的时间格式.

		:param timestamp: 时间戳(整数).
		:return: 格式化的时间字符串(如 'YYYY-MM-DD HH:MM:SS').
		"""
		time_array = time.localtime(timestamp)
		style_time = time.strftime("%Y-%m-%d %H:%M:%S", time_array)
		return style_time

	def process_path(self, data: dict, path: str | None) -> dict:
		"""
		通过点分隔的键路径,从嵌套字典中获取对应的值.

		:param data: 输入的嵌套字典.
		:param path: 点分隔的键路径(如 "key1.key2.key3").
		:return: 路径对应的值,若路径不存在,返回空字典.
		"""
		if path is None:
			return data

		keys = path.split(".")
		value = data
		for key in keys:
			value = value.get(key, {})
		return value

	def process_cookie(self, cookie: dict) -> str:
		"""
		将字典形式的 Cookie 转换为 HTTP 请求头中显示的字符串形式.

		:param cookie: 包含 Cookie 键值对的字典.
		:return: 转换后的 Cookie 字符串(如 "key1=value1; key2=value2").
		"""
		cookie_str = "; ".join([f"{key}={value}" for key, value in cookie.items()])
		return cookie_str


class CodeMaoRoutine:
	def get_timestamp(self) -> float:
		"""
		获取当前的时间戳(秒级).

		:return: 当前时间戳(浮点数).
		"""
		timestamp = time.time()
		return timestamp

	def print_changes(self, before_data: dict, after_data: dict, data: dict, date: str | None):
		"""
		打印数据变化情况,包括起始时间和变化内容.

		:param before_data: 开始时的数据字典.
		:param after_data: 结束时的数据字典.
		:param data: 需要比较的数据键值对,其中键为数据键,值为显示的标签.
		:param date: 用于转换时间戳的键(可选).
		"""
		if date:
			_before_date = CodeMaoProcess().process_timestamp(before_data[date])
			_after_date = CodeMaoProcess().process_timestamp(after_data[date])
			print(f"从{_before_date}到{_after_date}期间")

		for key, label in data.items():
			if key in before_data and key in after_data:
				change = after_data[key] - before_data[key]
				print(f"{label} 增加了 {change} 个")
			else:
				print(f"{key} 没有找到")

	def find_prefix(self, number: str | int, lst: list) -> int | None:
		"""
		在列表中找到给定数字前的前缀部分(以 "." 分隔).

		:param number: 目标数字,整数或字符串.
		:param lst: 包含字符串和整数的混合列表.
		:return: 前缀部分(整数),如果未找到返回 None.
		"""
		for item in lst:
			if isinstance(item, str) and f".{number}" in item:
				prefix = item.split(f".{number}")[0]
				if prefix.isdigit():
					return int(prefix)
		return None
