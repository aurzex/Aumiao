import json

import src.base.acquire as Acquire

version = "2024.7.14"

HEADERS = Acquire.CodeMaoClient().HEADERS


class Login:
	def __init__(self) -> None:
		self.acquire = Acquire.CodeMaoClient()

	def login(self, phonenum: int, password: str):
		data = json.dumps({"phonenum": phonenum, "password": password})
		response = self.acquire.send_request(url="https://x.chatmindai.net/api/user/login", method="post", data=data)
		return response.json()

	def update_token(self, token):
		global HEADERS  # noqa: PLW0602
		HEADERS["Authorization"] = f"Bearer {token}"


class User:
	def __init__(self) -> None:
		self.acquire = Acquire.CodeMaoClient()

	def get_balance(self):
		response = self.acquire.send_request(
			url="https://x.chatmindai.net/api/apiCount/query",
			method="get",
			headers=HEADERS,
		)
		return response.json()

	def get_details(self):
		response = self.acquire.send_request(
			url="https://x.chatmindai.net/api/user/getUserSelfBigData",
			method="post",
			data=json.dumps({}),
			headers=HEADERS,
		)
		return response.json()


class Explore:
	def __init__(self) -> None:
		self.acquire = Acquire.CodeMaoClient()

	def get_models(
		self,
		page: int = 1,
		limit: int = 6,
		category: str = "recommend",
		originpage: str = "",
		searchValue: str = "",  # noqa: N803
	):
		originpage = originpage if originpage != "" else category
		data = json.dumps(
			{
				"pageIndex": page,
				"pageSize": limit,
				"data": {
					"categoryName": category,
					"orderType": originpage,
					"searchValue": searchValue,
				},
			}
		)
		response = self.acquire.send_request(
			url="https://x.chatmindai.net/api/model/query",
			method="post",
			data=data,
			headers=HEADERS,
		)
		return response.json()

	def get_rank(self, method: str):
		if method == "user":
			url = "https://x.chatmindai.net/api/market/userRank"

		elif method == "model":
			url = "https://x.chatmindai.net/api/market/modelRank"
		elif method == "today":
			url = "https://x.chatmindai.net/api/market/modelHeatAddRank"
		else:
			url = ""

		response = self.acquire.send_request(url=url, method="post", data=json.dumps({}), headers=HEADERS)
		return response.json()


class Chat:
	def __init__(self) -> None:
		self.acquire = Acquire.CodeMaoClient()

	def get_chats(self):
		response = self.acquire.send_request(
			url="https://x.chatmindai.net/api/chat/queryChats",
			method="get",
			headers=HEADERS,
		)
		return response.json()

	def get_chat_history(self, id: str, page: int = 1, limit: int = 15):
		data = json.dumps(
			{
				"data": {"chatid": id},
				"pageIndex": page,
				"pageSize": limit,
			}
		)
		response = self.acquire.send_request(
			url="https://x.chatmindai.net/api/chat/queryPagesChatItems",
			method="post",
			data=data,
			headers=HEADERS,
		)
		return response.json()

	def chat(self, chatid: str, modelid: str, message: str, context_analyse: int = 1):
		# context_analyse为上下文分析,开启为1,关闭为0
		data = json.dumps(
			{
				"message": message,
				"chatid": chatid,
				"roleid": modelid,
				"isContextEnabled": context_analyse,
			}
		)

		response = self.acquire.send_request(
			url="https://x.chatmindai.net/api/chat-process",
			method="post",
			data=data,
			headers=HEADERS,
		)
		return response.text

	def save_chat(self):
		data = json.dumps(
			{
				"chatid": "",  # ai回答
				"humanid": "",  # 随机生成：p938bndy9lvueh5fok61721280190544
				"assistantid": "",  # 随机生成：fiz55pci3fobe7g00j91721280158062
				"chattitle": "",  # 默认为首次对话prompt
				"prompt": "",  # 人类提问内容
				"answer": "",  # 机器人回答
				"chattime": "2024-07-17 16:51:02",  # 时间
				"humantime": "2024-07-17 16:50:58",  # 时间
				"assistanttime": "2024-07-17 16:51:02",  # 时间
				"model": "qwen2-72B-Instruct",  # 模型
				"questionList": [],  # 未知
				"roleAvatar": "https://cravatar.cn/avatar/ef166b47449cc7e4e71cec1a2f826a70?s=200&d=mp",
				# ai头像可以随便上传
				"roleId": "bmi5aruzldsb1za2m5d1718161196283",  # 每个角色被赋予唯一id
				"sensitive": False,  # 未知
			}
		)
		response = self.acquire.send_request(
			url="https://x.chatmindai.net/api/chat/saveConversation",
			method="post",
			data=data,
			headers=HEADERS,
		)
		return response.json()


class Model:
	def __init__(self) -> None:
		self.acquire = Acquire.CodeMaoClient()

	def get_model_details(self, id: str):
		response = self.acquire.send_request(
			url="https://x.chatmindai.net/api/model/getModelDetailsInfo",
			method="post",
			data=json.dumps({"roleId": id}),
			headers=HEADERS,
		)
		return response.json()
