import json
from typing import Literal

from src.base import acquire
from src.base.decorator import singleton


@singleton
class Obtain:
	def __init__(self) -> None:
		self.acquire = acquire.CodeMaoClient()

	# 获取多个帖子信息
	def get_posts_details(self, ids: int | list[int]):
		if isinstance(ids, int):
			params = {"ids": ids}
		elif isinstance(ids, list):
			params = {"ids": ",".join(map(str, ids))}
		response = self.acquire.send_request(url="/web/forums/posts/all", method="get", params=params)
		return response.json()

	# 获取单个帖子信息
	def get_single_post_details(self, id: int):
		response = self.acquire.send_request(url=f"/web/forums/posts/{id}/details", method="get")
		return response.json()

	# 获取帖子回帖
	def get_post_replies_posts(self, id: int, sort: str = "-created_at"):
		params = {"page": 1, "limit": 10, "sort": sort}
		replies = self.acquire.fetch_data(
			url=f"/web/forums/posts/{id}/replies",
			params=params,
			total_key="total",
			data_key="items",
			method="page",
			args={"amount": "limit", "remove": "page"},
		)
		return replies

	# 获取回帖评论
	def get_reply_post_comments(
		self,
		post_id: int,
		limit: int = 10,
	):
		params = {"page": 1, "limit": 10}
		comments = self.acquire.fetch_data(
			url=f"/web/forums/replies/{post_id}/comments",
			params=params,
			data_key="items",
			limit=limit,
			method="page",
			args={"amount": "limit", "remove": "page"},
		)
		return comments

	# 获取我的帖子或回复的帖子
	def get_post_mine_all(
		self,
		method: Literal["created", "replied"],
	):
		params = {"page": 1, "limit": 10}
		posts = self.acquire.fetch_data(
			url=f"/web/forums/posts/mine/{method}",
			params=params,
			data_key="items",
			method="page",
			args={"amount": "limit", "remove": "page"},
		)
		return posts

	# 获取论坛帖子各个栏目
	def get_post_boards(self):
		response = self.acquire.send_request(url="/web/forums/boards/simples/all", method="get")
		return response.json()

	# 获取论坛单个版块详细信息T
	def get_board_details(self, board_id: int):
		response = self.acquire.send_request(url=f"/web/forums/boards/{board_id}", method="get")
		return response.json()

	# 获取社区所有热门帖子
	def get_hot_posts(self):
		response = self.acquire.send_request(url="/web/forums/posts/hots/all", method="get")
		return response.json()

	# 获取论坛顶部公告
	def get_top_notice(self, limit: int = 4):
		params = {"limit": limit}
		response = self.acquire.send_request(url="/web/forums/notice-boards", method="get", params=params)
		return response.json()

	# 获取论坛本周精选帖子 TODO: 待完善
	def get_key_content(self, content_key: Literal["forum.index.top.recommend"], limit: int = 4):
		params = {"content_key": content_key, "limit": limit}
		response = self.acquire.send_request(url="/web/contents/get-key", method="get", params=params)
		return response.json()

	# 获取社区精品合集帖子
	def get_selection_posts(self, limit: int = 20, offset: int = 0):
		params = {"limit": limit, "offset": offset}
		response = self.acquire.send_request(
			url="/web/forums/posts/selections",
			method="get",
			params=params,
		)
		return response.json()

	# 获取社区求帮助帖子
	def get_help_posts(self, limit: int = 20, page: int = 1):
		params = {"limit": limit, "page": page}
		response = self.acquire.send_request(
			url="/web/forums/boards/posts/ask-help",
			method="get",
			params=params,
		)
		return response.json()

	# 获取论坛举报原因
	def get_report_reasons(self):
		response = self.acquire.send_request(url="/web/reports/posts/reasons/all", method="get")
		return response.json()

	# 通过标题搜索帖子
	def search_posts(self, title: str, limit: int = 20):
		params = {"title": title, "limit": 20, "page": 1}
		response = self.acquire.fetch_data(
			url="/web/forums/posts/search",
			method="page",
			params=params,
			data_key="items",
			limit=limit,
			args={"amount": "limit", "remove": "page"},
		)

		return response


@singleton
class Motion:
	def __init__(self) -> None:
		self.acquire = acquire.CodeMaoClient()

	# 对某个帖子回帖
	def reply_post(
		self,
		post_id: int,
		content: str,
		return_data: bool = False,
	):
		data = json.dumps({"content": content})
		response = self.acquire.send_request(
			url=f"/web/forums/posts/{post_id}/replies",
			method="post",
			data=data,
		)
		return response.json() if return_data else response.status_code == 201

	# 对某个回帖评论进行回复
	def reply_comment(self, reply_id: int, parent_id: int, content: str, return_data: bool = False):
		data = json.dumps({"content": content, "parent_id": parent_id})
		response = self.acquire.send_request(url=f"/web/forums/replies/{reply_id}/comments", method="post", data=data)
		return response.json() if return_data else response.status_code == 201

	# 点赞某个回帖或评论
	def like_comment_or_reply(
		self,
		method: Literal["put", "delete"],
		id: int,
		source: Literal["REPLY", "COMMENT"],
	):
		# 每个回帖都有唯一id
		params = {"source": source}
		response = self.acquire.send_request(
			url=f"/web/forums/comments/{id}/liked",
			method=method,
			params=params,
		)
		return response.status_code == 204

	# 举报某个回帖
	def report_reply_or_comment(
		self,
		comment_id: int,
		reason_id: Literal[0, 1, 2, 3, 4, 5, 6, 7, 8],
		description: str,
		source: Literal["REPLY", "COMMENT"],
		return_data: bool = False,
	):
		# get_report_reasons()仅返回1-8的reason_id,其中description与reason_id一一对应 0为自定义举报理由
		data = json.dumps(
			{
				"reason_id": reason_id,
				"description": description,
				"discussion_id": comment_id,
				"source": source,
			}
		)
		response = self.acquire.send_request(
			url="/web/reports/posts/discussions",
			method="post",
			data=data,
		)
		return response.json() if return_data else response.status_code == 201

	# 举报某个帖子
	def report_post(
		self,
		post_id: int,
		reason_id: Literal[1, 2, 3, 4, 5, 6, 7, 8],
		description: str,
		return_data: bool = False,
	):
		# description与reason_id并不对应,可以自定义描述
		data = json.dumps(
			{
				"reason_id": reason_id,
				"description": description,
				"post_id": post_id,
			}
		)
		response = self.acquire.send_request(
			url="/web/reports/posts",
			method="post",
			data=data,
		)
		return response.json() if return_data else response.status_code == 201

	# 删除某个回帖或评论或帖子
	def delete_comment_post_reply(self, id: int, type: Literal["replies", "comments", "posts"]):
		response = self.acquire.send_request(
			url=f"/web/forums/{type}/{id}",
			method="delete",
		)
		return response.status_code == 204

	# 置顶某个回帖
	def top_comment(self, comment_id: int, method: Literal["put", "delete"]):
		response = self.acquire.send_request(
			url=f"/web/forums/replies/{comment_id}/top",
			method=method,
		)
		return response.status_code == 204

	# 发布帖子
	def create_post(
		self,
		method: Literal["board", "work_shop"],
		title: str,
		content: str,
		board_id: None | Literal[17, 2, 10, 5, 3, 6, 27, 11, 26, 13, 7, 4, 28] = None,
		work_shop_id: None | int = None,
		return_data: bool = False,
	):
		# board_id类型可从get_post_categories()获取
		data = json.dumps({"title": title, "content": content})
		if method == "board":
			url = f"/web/forums/boards/{board_id}/posts"
		elif method == "work_shop":
			url = f"/web/works/subjects/{work_shop_id}/post"
		response = self.acquire.send_request(
			url=url,
			method="post",
			data=data,
		)
		return response.json() if return_data else response.status_code == 201
