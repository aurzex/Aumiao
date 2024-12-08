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

	# 对评论内容进行处理的函数
	def process_shielding(self, content: str) -> str:
		content_bytes = [item.encode("UTF-8") for item in content]
		result = b"\xe2\x80\x8b".join(content_bytes).decode("UTF-8")
		return result

	# 时间戳转换为时间
	def process_timestamp(self, timestamp: int) -> str:
		time_array = time.localtime(timestamp)
		style_time = time.strftime("%Y-%m-%d %H:%M:%S", time_array)
		return style_time

	# 通过点分隔的键路径从嵌套字典中获取值
	def process_path(self, data: dict, path: str | None) -> dict:
		if path is None:
			return data
		keys = path.split(".")
		value = data
		for key in keys:
			value = value.get(key, {})
		return value

	# 将cookie转换为headers中显示的形式
	def process_cookie(self, cookie):
		cookie_str = "; ".join([f"{key}={value}" for key, value in cookie.items()])
		return cookie_str


class CodeMaoRoutine:
	def get_timestamp(self):
		timestamp = time.time()
		return timestamp

	def print_changes(self, before_data: dict, after_data: dict, data: dict, date: str | None):
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
