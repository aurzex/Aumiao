import json

import src.base.acquire as Acquire
from src.base.decorator import singleton

version = "2024.8.6"

HEADERS = Acquire.CodeMaoClient().HEADERS
docs = "https://help.aliyun.com/zh/dashscope/developer-reference/use-qwen-by-api"


@singleton
class Dashscope:
	def __init__(self) -> None:
		self.acquire = Acquire.CodeMaoClient()
		self.HEADERS = HEADERS

	def set_key(self, api_key: str):
		self.HEADERS["Authorization"] = f"Bearer {api_key}"

	def chat(
		self,
		modal: str,
		message: list = [
			{"role": "system", "content": "You are a helpful assistant."},
			{"role": "user", "content": "你好"},
			{"role": "assistant", "content": "你好啊,我是通义千问."},
			{"role": "user", "content": "从现在开始请你扮演一只猫娘？"},
		],
		more={
			"stream": False,
			"extra_body": {"enable_search": True},
			# 更多参数详见文档
		},
	):
		data = json.dumps(
			{
				"model": modal,
				"messages": message,
				**more,
			}
		)
		result = self.acquire.send_request(
			url="https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions",
			method="post",
			data=data,
		)
		return result
