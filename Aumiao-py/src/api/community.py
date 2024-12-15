import json
import uuid
from typing import Literal

import src.base.acquire as Acquire
import src.base.tool as Tool
from src.base.decorator import singleton


# 编程猫所有api中若包含v2等字样,表示第几版本,同样比它低的版本也可使用
@singleton
class Login:
	def __init__(self) -> None:
		self.acquire = Acquire.CodeMaoClient()
		self.tool_process = Tool.CodeMaoProcess()

	# 密码登录函数
	def login_password(
		self,
		identity: str,
		password: str,
		pid: str = "65edCTyg",
	) -> str | None:
		# cookies = utils.dict_from_cookiejar(response.cookies)

		#   soup = BeautifulSoup(
		#       send_request("https://shequ.codemao.cn", "get").text,
		#       "html.parser",
		#   )
		#   见https://api.docs.codemao.work/user/login?id=pid
		#   pid = loads(soup.find_all("script")[0].string.split("=")[1])["pid"]
		response = self.acquire.send_request(
			url="/tiger/v3/web/accounts/login",
			method="post",
			data=json.dumps(
				{
					"identity": identity,
					"password": password,
					"pid": pid,
				}
			),
		)
		self.check_login(response)

	# cookie登录
	def login_cookie(self, cookies: str) -> None | bool:
		try:
			dict([item.split("=", 1) for item in cookies.split("; ")])
			# 检查是否合规,不能放到headers中
		except (KeyError, ValueError) as err:
			print(f"表达式输入不合法 {err}")
			return False
		response = self.acquire.send_request(
			url="/nemo/v2/works/174408420/like",
			method="post",
			data=json.dumps({}),
			headers={**self.acquire.HEADERS, "cookie": cookies},
		)
		self.check_login(response)

	# token登录(毛毡最新登录方式)
	def login_token(self, identity: str, password: str, pid: str = "65edCTyg"):
		timestamp = Obtain().get_timestamp()["data"]
		response = self.get_login_ticket(identity=identity, timestamp=timestamp, pid=pid)
		ticket = response["ticket"]
		response = self.get_login_security(identity=identity, password=password, ticket=ticket, pid=pid)

	# 返回完整鉴权cookie
	def get_login_auth(self, token):
		# response = src.base_acquire.send_request(url="https://shequ.codemao.cn/",method="get",)
		# aliyungf_tc = response.cookies.get_dict()["aliyungf_tc"]
		uuid_ca = uuid.uuid1()
		token_ca = {"authorization": token, "__ca_uid_key__": str(uuid_ca)}
		cookie_str = self.tool_process.process_cookie(token_ca)
		headers = {**self.acquire.HEADERS, "cookie": cookie_str}
		response = self.acquire.send_request(method="get", url="/web/users/details", headers=headers)
		_auth = response.cookies.get_dict()
		auth_cookie = {**token_ca, **_auth}
		return auth_cookie

	# 检查并保存登录状态
	def check_login(self, response, cookie=None):
		if response.status_code == 200:
			up_cookie = cookie if cookie else response.cookies
			self.acquire.update_cookie(up_cookie)  # 确保cookies被更新
			return True
		elif response.status_code == 403:
			return "Wrong"
		else:
			print(f"登录失败惹,错误码: {response.status_code}")
			return False

	# 退出登录
	def logout(self):
		response = self.acquire.send_request(url="/tiger/v3/web/accounts/logout", method="post", data=json.dumps({}))
		return response.status_code == 204

	# 登录信息
	def get_login_security(
		self,
		identity: str,
		password: str,
		ticket: str,
		pid: str = "65edCTyg",
		agreement_ids: list = [-1],
		cookies_ali: dict = {"ca": "", "acw_tc": "", "aliyungf_tc": ""},
	):
		data = json.dumps(
			{
				"identity": identity,
				"password": password,
				"pid": pid,
				"agreement_ids": agreement_ids,
			}
		)
		_ca = {
			"__ca_uid_key__": str(cookies_ali["ca"]),
			"acw_tc": cookies_ali["acw_tc"],
			"aliyungf_tc": cookies_ali["aliyungf_tc"],
		}
		cookie_str = self.tool_process.process_cookie(_ca)
		headers_auth = {**self.acquire.HEADERS, "cookie": cookie_str}
		response = self.acquire.send_request(
			url="/tiger/v3/web/accounts/login/security",
			method="post",
			data=data,
			headers={**headers_auth, "x-captcha-ticket": ticket},
		)
		self.check_login(response)
		return response.json()

	#
	# 登录ticket获取
	def get_login_ticket(
		self,
		identity,
		timestamp: int,
		cookies_ca=None,
		scene=None,
		pid: str = "65edCTyg",
		deviced=None,
	):
		_ca = {"__ca_uid_key__": str(cookies_ca)}
		cookie_str = self.tool_process.process_cookie(_ca)
		headers = {**self.acquire.HEADERS, "cookie": cookie_str}
		data = json.dumps(
			{
				"identity": identity,
				"scene": scene,
				"pid": pid,
				"deviceId": deviced,
				"timestamp": timestamp,
			}
		)
		response = self.acquire.send_request(
			url="https://open-service.codemao.cn/captcha/rule/v3",
			method="post",
			data=data,
			headers=headers,
		)
		return response.json()


@singleton
class Obtain:
	def __init__(self) -> None:
		self.acquire = Acquire.CodeMaoClient()

	# 获取随机昵称
	def get_name_random(self) -> str:
		response = self.acquire.send_request(
			method="get",
			url="/api/user/random/nickname",
		)
		return response.json()["data"]["nickname"]

	# 获取新消息数量
	def get_message_count(self, method: Literal["web", "nemo"]):
		if method == "web":
			url = "/web/message-record/count"
		elif method == "nemo":
			url = "/nemo/v2/user/message/count"
		else:
			raise ValueError("不支持的方法")
		record = self.acquire.send_request(
			url=url,
			method="get",
		)
		return record.json()

	# 获取回复
	def get_replies(
		self,
		type: Literal["LIKE_FORK", "COMMENT_REPLY", "SYSTEM"],
		limit: int = 15,
		offset: int = 0,
	):
		params = {"query_type": type, "limit": limit, "offset": offset}
		# 获取前*个回复
		response = self.acquire.send_request(
			url="/web/message-record",
			method="get",
			params=params,
		)
		return response.json()

	# 获取nemo消息
	def get_nemo_message(self, method: Literal["fork", "like"]):
		extra_url = 1 if method == "like" else 3
		url = f"/nemo/v2/user/message/{extra_url}"
		response = self.acquire.send_request(url=url, method="get")
		return response.json()

	# 清除邮箱红点
	def all_read(self, query_types: list[Literal["LIKE_FORK", "COMMENT_REPLY", "SYSTEM"]]) -> bool:
		offset = 0
		while True:
			record = self.get_message_count(method="web")
			type_to_count = {item["query_type"]: item["count"] for item in record}
			if all(type_to_count.get(type, 0) == 0 for type in query_types):
				return True  # 所有消息类型处理完毕
			# 如果还有未处理的消息,按类型查询并清理
			for query_type in query_types:
				self.get_replies(type=query_type, limit=200, offset=offset)
			offset += 200

	# 获取点个猫更新
	def get_update_message(self):
		response = self.acquire.send_request(url="https://update.codemao.cn/updatev2/appsdk", method="get")
		return response.json()

	# 获取时间戳
	def get_timestamp(self):
		response = self.acquire.send_request(url="/coconut/clouddb/currentTime", method="get")
		return response.json()

	# 获取推荐头图
	def get_banner_web(
		self,
		type: (None | Literal["FLOAT_BANNER", "OFFICIAL", "CODE_TV", "WOKE_SHOP", "MATERIAL_NORMAL"]) = None,
	):
		# 所有:不设置type,首页:OFFICIAL, 工作室页:WORK_SHOP
		# 素材页:MATERIAL_NORMAL, 右下角浮动区域:FLOAT_BANNER, 编程TV:CODE_TV
		params = {"type": type}
		response = self.acquire.send_request(url="/web/banners/all", method="get", params=params)
		return response.json()

	# 获取推荐头图
	def get_banner_nemo(self, type: Literal[1, 2, 3]):
		# 1:点个猫推荐页 2:点个猫主题页 3:点个猫课程页
		params = {"banner_type": type}
		response = self.acquire.send_request(url="/nemo/v2/home/banners", method="get", params=params)
		return response.json()

	# 获取举报类型
	def get_report_reason(self):
		response = self.acquire.send_request(url="/web/reports/reasons/all", method="get")
		return response.json()

	# 获取nemo配置 TODO:待完善
	def get_nemo_config(self) -> str:
		response = self.acquire.send_request(url="https://nemo.codemao.cn/config", method="get")
		return response.json()

	# 获取社区网络服务
	def get_community_config(self):
		response = self.acquire.send_request(url="https://c.codemao.cn/config", method="get")
		return response.json()

	# 获取编程猫网络服务
	def get_client_config(self):
		response = self.acquire.send_request(url="https://player.codemao.cn/new/client_config.json", method="get")
		return response.json()

	# 获取编程猫首页作品
	def discover_works_recommended_home(self, type: Literal[1, 2]):
		# 1为点猫精选,2为新作喵喵看
		params = {"type": type}
		response = self.acquire.send_request(
			url="/creation-tools/v1/pc/home/recommend-work",
			method="get",
			params=params,
		)
		return response.json()

	# 获取编程猫首页推荐channel
	def get_channels_list(self, type: Literal["KITTEN", "NEMO"]):
		params = {"type": type}
		response = self.acquire.send_request(
			url="/web/works/channels/list",
			method="get",
			params=params,
		)
		return response.json()

	# 获取指定channel
	def get_channel(self, id: int, type: Literal["KITTEN", "NEMO"], limit=5, page=1):
		params = {"type": type, "page": 1, "limit": 5}
		response = self.acquire.send_request(
			url=f"/web/works/channels/{id}/works",
			method="get",
			params=params,
		)
		return response.json()

	# 获取推荐作者
	def get_user_recommended(self):
		response = self.acquire.send_request(url="/web/users/recommended", method="get")
		return response.json()

	# 获取训练师小课堂
	def get_post_lesion(self):
		response = self.acquire.send_request(url="https://backend.box3.fun/diversion/codemao/post", method="get")
		return response.json()

	# 获取KN课程
	def get_kn_course(self):
		response = self.acquire.send_request(url="/creation-tools/v1/home/especially/course", method="get")
		return response.json()

	# 获取KN公开课
	# https://api-creation.codemao.cn/neko/course/publish/list?limit=10&offset=0
	def get_kn_publish_course(self, limit=10):
		params = {"limit": 10, "offset": 0}
		course = self.acquire.fetch_data(
			url="https://api-creation.codemao.cn/neko/course/publish/list",
			params=params,
			limit=limit,
			total_key="total_course",
			# total_key也可设置为"course_page.total",
			data_key="course_page.items",
		)
		return course

	# 获取社区各个部分开启状态 TODO:待完善
	def get_community_status(self, type: Literal["WEB_FORUM_STATUS", "WEB_FICTION_STATUS"]):
		response = self.acquire.send_request(url=f"/web/config/tab/on-off/status?config_type={type}", method="get")
		return response.json()

	# 获取kitten编辑页面精选活动
	def get_kitten_activity(self):
		response = self.acquire.send_request(
			url="https://api-creation.codemao.cn/kitten/activity/choiceness/list",
			method="get",
		)
		return response.json()

	# 获取nemo端教程合集
	def get_nemo_course_package(self, platform: int = 1):
		params = {"limit": 50, "offset": 0, "platform": platform}
		courses = self.acquire.fetch_data(
			url="/creation-tools/v1/course/package/list",
			params=params,
			data_key="items",
		)
		return courses

	# 获取nemo教程
	def get_nemo_package(self, course_package_id: int, limit: int = 50, offset: int = 0):
		# course_package_id由get_nemo_course_package中获取
		params = {
			"course_package_id": course_package_id,
			"limit": limit,
			"offset": offset,
		}
		response = self.acquire.fetch_data(
			url="/creation-tools/v1/course/list/search",
			params=params,
			data_key="course_page.items",
			# 参数中total_key也可用total_course
		)
		return response


@singleton
class Motion:
	def __init__(self) -> None:
		self.acquire = Acquire.CodeMaoClient()

	# 签订友好协议
	def sign_nature(self) -> bool:
		response = self.acquire.send_request(url="/nemo/v3/user/level/signature", method="post")
		return response.status_code == 200

	# 获取用户协议
	def get_nature(self):
		response = self.acquire.send_request(url="/tiger/v3/web/accounts/agreements", method="get")
		return response.json()

	# 注册
	def register(
		self,
		identity: str,
		password: str,
		captcha: str,
		pid: str = "65edCTyg",
		agreement_ids: list = [186, 13],
	):
		data = json.dumps(
			{
				"identity": identity,
				"password": password,
				"captcha": captcha,
				"pid": pid,
				"agreement_ids": agreement_ids,
			}
		)

		response = self.acquire.send_request(
			url="/tiger/v3/web/accounts/register/phone/with-agreement",
			method="post",
			data=data,
		)

		return response.json()
