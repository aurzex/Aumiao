import json
import os
from typing import Any, cast

from . import file as File
from .decorator import singleton

DATA_FILE_PATH: str = os.path.join(os.getcwd(), "data/" "data.json")
CACHE_FILE_PATH: str = os.path.join(os.getcwd(), "data/" "cache.json")
SETTING_FILE_PATH: str = os.path.join(os.getcwd(), "data/" "setting.json")


# 该字典不可单例
class SyncDict(dict[str, Any]):
	"""
	自定义字典类,用于在修改内容时自动同步到文件中.
	"""

	def __init__(self, file_path: str, parent_ref: dict[str, Any], key: str | None, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.file_path = file_path
		self.parent_ref = parent_ref  # 父级字典的引用
		self.key = key  # 当前 SyncDict 在父字典中的键

	def _sync_to_file(self):
		# 更新父级字典的当前键
		if self.key is None:
			self.parent_ref = self
		else:
			self.parent_ref[self.key] = self
		# 将完整父级字典保存到文件
		with open(self.file_path, "w", encoding="utf-8") as f:
			json.dump(self.parent_ref, f, ensure_ascii=False, indent=4)

	def __setitem__(self, key, value):
		super().__setitem__(key, value)
		self._sync_to_file()

	def __delitem__(self, key):
		super().__delitem__(key)
		self._sync_to_file()

	def update(self, *args, **kwargs):
		super().update(*args, **kwargs)
		self._sync_to_file()

	def clear(self):
		super().clear()
		self._sync_to_file()


@singleton
class CodeMaoData:
	def __init__(self) -> None:
		_data = File.CodeMaoFile().file_load(path=DATA_FILE_PATH, type="json")
		_data = cast(dict[str, Any], _data)
		# 父级字典引用
		self.data = _data
		# 用 SyncDict 包装子字典
		self.ACCOUNT_DATA = SyncDict(
			file_path=DATA_FILE_PATH, parent_ref=self.data, key="ACCOUNT_DATA", **self.data["ACCOUNT_DATA"]
		)
		self.USER_DATA = SyncDict(
			file_path=DATA_FILE_PATH, parent_ref=self.data, key="USER_DATA", **self.data["USER_DATA"]
		)
		self.INFO = SyncDict(file_path=DATA_FILE_PATH, parent_ref=self.data, key="INFO", **self.data["INFO"])


@singleton
class CodeMaoCache:
	def __init__(self) -> None:
		_cache = File.CodeMaoFile().file_load(path=CACHE_FILE_PATH, type="json")
		_cache = cast(dict[str, Any], _cache)
		# 父级字典引用
		self.cache = _cache
		# 用 SyncDict 包装子字典
		self.CACHE = SyncDict(file_path=CACHE_FILE_PATH, parent_ref=self.cache, key=None, **self.cache)


@singleton
class CodeMaoSetting:
	def __init__(self) -> None:
		data = File.CodeMaoFile().file_load(path=SETTING_FILE_PATH, type="json")
		data = cast(dict[str, Any], data)
		self.DEFAULT = data["DEFAULT"]
		self.PARAMETER = data["PARAMETER"]
		self.PLUGIN = data["PLUGIN"]
		self.PROGRAM = data["PROGRAM"]
