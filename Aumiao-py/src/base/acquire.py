import time
from typing import Literal

import requests
from requests.exceptions import ConnectionError, HTTPError, RequestException, Timeout

from . import data as Data
from . import tool as Tool
from .decorator import singleton

session = requests.session()


@singleton
class CodeMaoClient:
	def __init__(self) -> None:
		self.data = Data.CodeMaoSetting()
		self.tool_process = Tool.CodeMaoProcess()
		self.HEADERS = self.data.PROGRAM["HEADERS"]
		self.BASE_URL = self.data.PROGRAM["BASE_URL"]
		global session  # noqa: PLW0602

	def send_request(
		self,
		url: str,
		method: Literal["post", "get", "delete", "patch", "put"],
		params=None,
		data=None,
		headers=None,
		sleep=0,
	):
		headers = headers or self.HEADERS
		url = url if "http" in url else f"{self.BASE_URL}{url}"
		time.sleep(sleep)
		try:
			response = session.request(method=method, url=url, headers=headers, params=params, data=data)
			response.raise_for_status()
			return response
		except (HTTPError, ConnectionError, Timeout, RequestException) as err:
			print(f"网络请求异常: {err}")
			print(f"错误码: {response.status_code} 错误信息: {response.text}")  # type: ignore
			return response  # type: ignore

	def fetch_data(
		self,
		url: str,
		params: dict,
		data=None,
		limit: int | None = None,
		fetch_method: Literal["get", "post"] = "get",
		total_key: str = "total",
		data_key: str | None = "item",
		method: Literal["offset", "page"] = "offset",
		args: dict[Literal["amount", "remove", "res_amount_key", "res_remove_key"], str] = {
			"amount": "limit",
			"remove": "offset",
			"res_amount_key": "limit",
			"res_remove_key": "offset",
		},
	) -> list[dict]:
		initial_response = self.send_request(url=url, method=fetch_method, params=params, data=data)
		total_items = int(
			self.tool_process.process_path(initial_response.json(), total_key)  # type: ignore
		)
		# 尝试从 params 中获取 items_per_page,如果没有则使用初始响应中的值
		items_per_page = (
			params[args["amount"]] if "amount" in args.keys() else initial_response.json()[args["res_amount_key"]]
		)
		total_pages = (total_items + items_per_page - 1) // items_per_page  # 向上取整
		all_data = []
		fetch_count = 0
		for page in range(total_pages):
			if method == "offset":
				params[args["remove"]] = page * items_per_page
			elif method == "page":
				params[args["remove"]] = page + 1
			response = self.send_request(url=url, method=fetch_method, params=params)
			data = self.tool_process.process_path(response.json(), data_key)
			all_data.extend(data)
			fetch_count += len(data)
			if limit and fetch_count >= limit:
				return all_data[:limit]
		return all_data

	def update_cookie(self, cookie: str):
		if isinstance(cookie, requests.cookies.RequestsCookieJar):  # type: ignore
			cookie = requests.utils.dict_from_cookiejar(cookie)
		elif isinstance(cookie, dict):
			pass
		else:
			raise ValueError("不支持的数据类型")
		session.cookies.update(cookie)  # type: ignore
		return True
