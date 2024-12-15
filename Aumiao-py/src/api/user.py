import json
from typing import Literal

import src.base.acquire as Acquire
from src.base.decorator import singleton


@singleton
class Obtain:
	def __init__(self) -> None:
		self.acquire = Acquire.CodeMaoClient()

	# 获取某人账号信息
	def get_user_details(self, user_id: str) -> dict:
		response = self.acquire.send_request(method="get", url=f"/api/user/info/detail/{user_id}")
		return response.json()

	# 获取用户荣誉
	def get_user_honor(self, user_id: str) -> dict:
		params = {"user_id": user_id}
		response = self.acquire.send_request(
			url="/creation-tools/v1/user/center/honor",
			method="get",
			params=params,
		)

		return response.json()

	# 获取用户精确数据
	def get_user_business(self, user_id: str) -> dict:
		params = {"user_id": user_id}
		response = self.acquire.send_request(url="/nemo/v2/works/business/total", method="get", params=params)
		return response.json()

	# 获取某人账号信息(简略)
	def get_user_info(self, user_id: str) -> dict:
		params = {"user_id": user_id}
		response = self.acquire.send_request(method="get", url="/nemo/v2/user/dynamic/info", params=params)
		return response.json()

	# 获取账户信息(详细)
	def get_data_details(self) -> dict:
		response = self.acquire.send_request(
			method="get",
			url="/web/users/details",
		)
		return response.json()

	# 获取账户信息(简略)
	def get_data_info(self) -> dict:
		response = self.acquire.send_request(
			method="get",
			url="/web/users/info",
		)

		return response.json()

	# 获取账户信息
	def get_data_profile(self, method: Literal["web", "app"]):
		response = self.acquire.send_request(method="get", url=f"/tiger/v3/{method}/accounts/profile")
		return response.json()

	# 获取账户安全信息
	def get_data_privacy(self):
		response = self.acquire.send_request(method="get", url="/tiger/v3/web/accounts/privacy")
		return response.json()

	# 获取账户信息
	def get_data_tiger(self):
		response = self.acquire.send_request(url="/tiger/user", method="get")
		return response.json()

	# 获取用户点赞,再创作,收藏分
	def get_data_score(self):
		response = self.acquire.send_request(url="/nemo/v3/user/grade/details", method="get")
		return response.json()

	# 获取用户等级
	def get_data_level(self):
		response = self.acquire.send_request(url="/nemo/v3/user/level/info", method="get")
		return response.json()

	# 获取用户姓名
	def get_data_name(self):
		response = self.acquire.send_request(url="/api/v2/pc/lesson/user/info", method="get")
		return response.json()

	# 获取个人作品列表的函数
	def get_user_works_web(self, user_id: str, type: Literal["newest", "hot"] = "newest") -> list[dict[str, str | int]]:
		params = {
			"type": type,
			"user_id": user_id,
			"offset": 0,
			"limit": 5,
		}
		works = self.acquire.fetch_data(
			url="/creation-tools/v2/user/center/work-list",
			params=params,
			total_key="total",
			data_key="items",
		)
		return works

	# 搜索用户作品
	def search_data_works_nemo(self, query: str, query_type: str = "name", page: int = 1, limit: int = 10):
		params = {
			"query": query,
			"query_type": query_type,
			"page": page,
			"limit": limit,
		}
		response = self.acquire.send_request(url="tiger/nemo/user/works/search", method="get", params=params)
		return response.json()

	# 获取用户云端作品
	def get_data_works_cloud(self, type: Literal["nemo", "kitten"], limit: int = 10, offset: int = 0):
		if type == "nemo":
			work_type = 8
		elif type == "kitten":
			work_type = 1
		params = {"limit": limit, "offset": offset, "work_type": work_type}
		response = self.acquire.send_request(url="/creation-tools/v1/works/list/user", params=params, method="get")
		return response

	# 获取用户nemo作品
	def get_data_works_nemo(self, method=Literal["published"]):
		params = {"limit": 15, "offset": 0}
		works = self.acquire.fetch_data(
			url=f"/nemo/v2/works/list/user/{method}",
			params=params,
			data_key="items",
		)
		return works

	# 获取用户KN作品
	def get_data_works_kn(
		self,
		method: Literal["published", "total"],
		extra_params: (
			dict[
				Literal["name", "limit", "offset", "status", "work_business_classify"],
				str | int,
			]
			| None
		) = None,
	):
		# kn获取全部作品示例链接:https://api-creation.codemao.cn/neko/works/v2/list/user?name=&limit=24&offset=0&status=1&work_business_classify=1
		if method == "published":
			url = "https://api-creation.codemao.cn/neko/works/list/user/published"
		elif method == "total":
			url = "https://api-creation.codemao.cn/neko/works/v2/list/user"
		params = {"offset": 0, "limit": 15}
		params.update(extra_params or {})  # type: ignore
		works = self.acquire.fetch_data(url=url, params=params, data_key="items")
		return works

	# 获取用户kitten作品列表
	def get_data_my_works_kitten(
		self,
		version: Literal["KITTEN_V4", "KITTEN_V3"],
		status: Literal["PUBLISHED", "UNPUBLISHED", "all"],
		work_status: Literal["SHOW"] = "SHOW",
	):
		params = {
			"offset": 0,
			"limit": 30,
			"version_no": version,
			"work_status": work_status,
			"published_status": status,
		}
		works = self.acquire.fetch_data(
			url="https://api-creation.codemao.cn/kitten/common/work/list2",
			params=params,
			data_key="items",
		)
		return works

	# 获取用户nemo作品列表
	def get_data_my_works_nemo(
		self,
		status: Literal["PUBLISHED", "UNPUBLISHED", "all"],
	):
		params = {"offset": 0, "limit": 30, "published_status": status}
		works = self.acquire.fetch_data(
			url="https://api.codemao.cn/creation-tools/v1/works/list",
			params=params,
			data_key="items",
		)
		return works

	# 获取用户海龟编辑器作品列表
	def get_data_my_works_wood(
		self,
		status: Literal["PUBLISHED", "UNPUBLISHED"],
		language_type: int = 0,
		work_status: Literal["SHOW"] = "SHOW",
	):
		params = {
			"offset": 0,
			"limit": 30,
			"language_type": language_type,
			"work_status": work_status,
			"published_status": status,
		}
		works = self.acquire.fetch_data(
			url="https://api-creation.codemao.cn/wood/comm/work/list",
			params=params,
			data_key="items",
		)
		return works

	# 获取用户box作品列表
	def get_data_my_works_box(
		self,
		status: Literal["all", "PUBLISHED", "UNPUBLISHED"],
		work_status: Literal["SHOW"] = "SHOW",
	):
		params = {
			"offset": 0,
			"limit": 30,
			"work_status": work_status,
			"published_status": status,
		}
		works = self.acquire.fetch_data(
			url="https://api-creation.codemao.cn/box/v2/work/list",
			params=params,
			data_key="items",
		)
		return works

	# 获取用户小说列表
	def get_data_my_works_fanfic(
		self,
		fiction_status: Literal["SHOW"] = "SHOW",
	):
		params = {"offset": 0, "limit": 30, "fiction_status": fiction_status}
		works = self.acquire.fetch_data(
			url="https://api.codemao.cn/web/fanfic/my/new",
			params=params,
			data_key="items",
		)
		return works

	# 获取用户coco作品列表 TODO:参数不确定
	def get_data_my_works_coco(
		self,
		status: int = 1,
		published: bool = True,
	):
		params = {
			"offset": 0,
			"limit": 30,
			"status": status,
			"published": published,
		}
		works = self.acquire.fetch_data(
			url="https://api-creation.codemao.cn/coconut/web/work/list",
			params=params,
			data_key="data.items",
			total_key="data.total",
		)
		return works

	# 获取粉丝列表
	def get_user_fans(self, user_id: str, limit: int = 15) -> list[dict[str, str]]:
		params = {
			"user_id": user_id,
			"offset": 0,
			"limit": 15,
		}
		fans = self.acquire.fetch_data(
			url="/creation-tools/v1/user/fans",
			params=params,
			total_key="total",
			data_key="items",
			limit=limit,
		)
		return fans

	# 获取关注列表
	def get_user_follows(self, user_id: str, limit: int = 15) -> list[dict[str, str]]:
		params = {
			"user_id": user_id,
			"offset": 0,
			"limit": 15,
		}
		follows = self.acquire.fetch_data(
			url="/creation-tools/v1/user/followers",
			params=params,
			total_key="total",
			data_key="items",
			limit=limit,
		)
		return follows

	# 获取用户收藏的作品的信息
	def get_user_collects(self, user_id: str, limit: int = 5) -> list[dict[str, str]]:
		params = {
			"user_id": user_id,
			"offset": 0,
			"limit": 5,
		}
		collects = self.acquire.fetch_data(
			url="/creation-tools/v1/user/center/collect/list",
			params=params,
			total_key="total",
			data_key="items",
			limit=limit,
		)
		return collects


@singleton
class Motion:
	def __init__(self) -> None:
		self.acquire = Acquire.CodeMaoClient()

	# 设置正在做的事
	def set_doing(self, doing: str):
		response = self.acquire.send_request(url="/nemo/v2/user/basic", method="put", data=json.dumps({"doing": doing}))
		return response.status_code == 200

	# 设置登录用户名(实验性功能)
	def set_username(self, username):
		response = self.acquire.send_request(
			url="/tiger/v3/web/accounts/username",
			method="patch",
			data=json.dumps({"username": username}),
		)
		return response.status_code

	# 验证手机号
	def verify_phone(self, phone_num: int):
		params = {"phone_number": phone_num}
		response = self.acquire.send_request(url="/web/users/phone_number/is_consistent", method="get", params=params)
		return response.json()

	# 修改密码
	def modify_password(self, old_password: str, new_password: str):
		data = json.dumps(
			{
				"old_password": old_password,
				"password": new_password,
				"confirm_password": new_password,
			}
		)
		response = self.acquire.send_request(
			url="/tiger/v3/web/accounts/password",
			method="patch",
			data=data,
		)
		return response.status_code == 204

	# 修改手机号(获取验证码)
	def modify_phonenum_captcha(self, old_phonenum: int, new_phonenum: int) -> bool:
		data = json.dumps({"phone_number": new_phonenum, "old_phone_number": old_phonenum})
		response = self.acquire.send_request(
			url="/tiger/v3/web/accounts/captcha/phone/change",
			method="post",
			data=data,
		)
		return response.status_code == 204

	# 修改手机号
	def modify_phonenum(self, captcha: int, phonenum: int) -> bool:
		data = json.dumps({"phone_number": phonenum, "captcha": captcha})
		response = self.acquire.send_request(
			url="/tiger/v3/web/accounts/phone/change",
			method="patch",
			data=data,
		)
		return response.json()
