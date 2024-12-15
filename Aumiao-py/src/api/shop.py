import json
from typing import Literal

import src.base.acquire as Acquire
from src.base.decorator import singleton


@singleton
class Obtain:
	def __init__(self) -> None:
		self.acquire = Acquire.CodeMaoClient()

	# 获取工作室简介(简易,需登录工作室成员账号)
	def get_shops_simple(self):
		response = self.acquire.send_request(url="/web/work_shops/simple", method="get")
		result = response.json()["work_shop"]
		return result

	# 获取工作室简介
	def get_shop_details(self, id: str) -> dict:
		response = self.acquire.send_request(url=f"/web/shops/{id}", method="get")
		return response.json()

	# 获取工作室列表的函数
	def get_shops(
		self,
		level: int = 4,
		limit: int = 14,
		works_limit: int = 4,
		offset: int = 0,
		sort: list[Literal["-latest_joined_at", "-created_at"]] = [
			"-created_at",
			"-latest_joined_at",
		],
	):  # 不要问我limit默认值为啥是14,因为api默认获取14个
		if isinstance(sort, list):
			_sort = ",".join(sort)
		params = {
			"level": level,
			"works_limit": works_limit,
			"limit": limit,
			"offset": offset,
			"sort": _sort,
		}
		shops = self.acquire.send_request(
			url="/web/work-shops/search",
			params=params,
			method="get",
		)
		return shops

	# 获取工作室成员
	def get_shops_members(
		self,
		id: int,
	):
		params = {"limit": 40, "offset": 0}
		members = self.acquire.fetch_data(
			url=f"/web/shops/{id}/users",
			params=params,
			total_key="total",
			data_key="items",
		)
		return members

	# 获取工作室列表,包括工作室成员,工作室作品
	def get_shops_details(
		self,
		levels: list[int] | int = [1, 2, 3, 4],
		max_number: int = 4,
		works_limit: int = 4,
		sort: list[str] | str = ["-ordinal,-updated_at"],
	):
		_levels: str = ""
		_sort: str = ""
		if isinstance(levels, list):
			_levels = ",".join(map(str, levels))
		if isinstance(sort, list):
			_sort = ",".join(sort)
		params = {
			"levels": _levels,
			"max_number": max_number,
			"works_limit": works_limit,
			"sort": _sort,
		}
		response = self.acquire.send_request(url="/web/shops", method="get", params=params)
		return response.json()


@singleton
class Motion:
	def __init__(self) -> None:
		self.acquire = Acquire.CodeMaoClient()

	# 更新工作室简介
	def update_shop_details(self, description: str, id: str, name: str, preview_url: str) -> bool:
		response = self.acquire.send_request(
			url="/web/work_shops/update",
			method="post",
			data=json.dumps(
				{
					"description": description,
					"id": id,
					"name": name,
					"preview_url": preview_url,
				}
			),
		)
		return response.status_code == 200

	# 创建工作室
	def create_shop(self, name: str, description: str, preview_url: str):
		response = self.acquire.send_request(
			url="/web/work_shops/create",
			method="post",
			data=json.dumps(
				{
					"name": name,
					"description": description,
					"preview_url": preview_url,
				}
			),
		)
		return response.json()

	# 解散工作室
	def dissolve_shop(self, shop_id: int):
		response = self.acquire.send_request(
			url="/web/work_shops/dissolve",
			method="post",
			data=json.dumps({"id": shop_id}),
		)
		return response.status_code == 200

	# 在指定工作室投稿作品
	def contribute_work(self, shop_id: int, work_id: int):
		response = self.acquire.send_request(
			url="/web/work_shops/works/contribute",
			method="post",
			data=json.dumps({"id": shop_id, "work_id": work_id}),
		)
		return response.status_code == 200

	# 在指定工作室删除作品
	def remove_work(self, shop_id: int, work_id: int):
		response = self.acquire.send_request(
			url="/web/work_shops/works/remove",
			method="post",
			data=json.dumps({"id": shop_id, "work_id": work_id}),
		)
		return response.status_code == 200

	# 申请加入工作室
	def apply_join(self, shop_id: int, qq: str | None = None):
		response = self.acquire.send_request(
			url="/web/work_shops/users/apply/join",
			method="post",
			data=json.dumps({"id": shop_id, "qq": qq}),
		)
		return response.status_code == 200

	# 审核已经申请加入工作室的用户
	def audit_join(self, shop_id: int, status: Literal["UNACCEPTED", "ACCEPTED"], user_id: int):
		response = self.acquire.send_request(
			url="/web/work_shops/users/audit",
			method="post",
			data=json.dumps({"id": shop_id, "status": status, "user_id": user_id}),
		)
		return response.status_code == 200
