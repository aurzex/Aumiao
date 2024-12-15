import json

import src.base.acquire as Acquire
from src.base.decorator import singleton


@singleton
class PickDuck:
	def __init__(self) -> None:
		self.acquire = Acquire.CodeMaoClient()

	def cookie_out(self, cookies):
		data = json.dumps({"cookie": cookies, "do": "apply"})
		response = self.acquire.send_request(url="https://shequ.pgaot.com/?mod=bcmcookieout", method="post", data=data)
		return response.status_code == 200
