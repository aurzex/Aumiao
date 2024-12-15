import json
from typing import Literal

import src.base.acquire as Acquire
from src.base.decorator import singleton

select = Literal["post", "delete"]


@singleton
class CartoonObtain:
	def __init__(self):
		self.acquire = Acquire.CodeMaoClient()

	# 获取全部漫画
	def get_all_cartoon(self):
		response = self.acquire.send_request(url="/api/comic/list/all", method="get")
		return response.json()

	# 获取漫画信息
	def get_cartoon_info(self, comic_id):
		response = self.acquire.send_request(url=f"/api/comic/{comic_id}", method="get")
		return response.json()

	# 获取漫画某个章节信息(每个章节会分配一个唯一id)
	def get_cartoon_chapters(self, chapter_id):
		response = self.acquire.send_request(url=f"/api/comic/page/list/{chapter_id}", method="get")
		return response.json()


@singleton
class NovelObtain:
	def __init__(self) -> None:
		self.acquire = Acquire.CodeMaoClient()

	# 获取小说分类列表
	def get_novel_categories(self):
		response = self.acquire.send_request(url="/api/fanfic/type", method="get")
		return response.json()

	# 获取小说列表
	def get_novel_list(
		self,
		method: Literal["all", "recommend"],
		sort_id: Literal[0, 1, 2, 3],
		type_id: Literal[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11],
		status: Literal[0, 1, 2],
		page: int = 1,
		limit: int = 20,
	):
		# sort_id: 0:默认排序 1:最多点击 2:最多收藏 3:最近更新
		# type_id: 0:不限 1:魔法 2:科幻 3:游戏 4:推理 5:治愈 6:冒险 7:日常 8:校园 9:格斗 10:古风 11:恐怖
		# status: 0:全部 1:连载中 2:已完结
		# method: all:全部 recommend:推荐
		# 经测试recommend返回数据不受params影响 recommend TODO: 待确认
		params = {
			"sort_id": sort_id,
			"type_id": type_id,
			"status": status,
			"page": page,
			"limit": limit,
		}
		# params中的type_id与fanfic_type_id可互换
		response = self.acquire.send_request(url=f"/api/fanfic/list/{method}", method="get", params=params)
		return response.json()

	# 获取收藏的小说列表
	def get_novel_collection(self, page: int = 1, limit: int = 10):
		params = {"page": page, "limit": limit}
		response = self.acquire.send_request(
			url="/web/fanfic/collection",
			method="get",
			params=params,
		)
		return response.json()

	# 获取小说详情
	def get_novel_detail(self, novel_id: int):
		response = self.acquire.send_request(url=f"/api/fanfic/{novel_id}", method="get")
		return response.json()

	# 获取小说章节信息
	def get_chapter_detail(self, chapter_id: int):
		response = self.acquire.send_request(
			url=f"/api/fanfic/section/{chapter_id}",
			method="get",
		)
		return response.json()

	# 获取小说评论
	def get_novel_comment(self, novel_id: int, page: int = 0, limit: int = 10):
		# page从0开始
		params = {"page": page, "limit": limit}
		response = self.acquire.send_request(
			url=f"/api/fanfic/comments/list/{novel_id}",
			method="get",
			params=params,
		)
		return response.json()

	# 获取搜索小说结果
	def search_novel(self, keyword: str, page: int = 0, limit: int = 10):
		# page从0开始
		params = {"searchContent": keyword, "page": page, "limit": limit}
		response = self.acquire.send_request(
			url="/api/fanfic/list/search",
			method="get",
			params=params,
		)
		return response.json()


class NovelMotion:
	def __init__(self) -> None:
		self.acquire = Acquire.CodeMaoClient()

	# 收藏小说
	def collect_novel(self, novel_id: int, method: select):
		response = self.acquire.send_request(
			url=f"/web/fanfic/collect/{novel_id}",
			method=method,
		)
		return response.json()

	# 评论小说
	def comment_novel(self, comment: str, novel_id: int, return_data: bool = False) -> bool | dict:
		response = self.acquire.send_request(
			url=f"/api/fanfic/comments/{novel_id}",
			method="post",
			data=json.dumps(
				{
					"content": comment,
				}
			),
		)
		return response.json() if return_data else response.status_code == 200

	# 点赞小说评论
	def like_comment(self, method: select, comment_id: int, return_data: bool = False) -> bool | dict:
		response = self.acquire.send_request(
			url=f"/api/fanfic/comments/praise/{comment_id}",
			method=method,
		)
		return response.json() if return_data else response.status_code == 200

	# 删除小说评论
	def delete_comment(self, comment_id: int, return_data: bool = False) -> bool | dict:
		response = self.acquire.send_request(
			url=f"/api/fanfic/comments/{comment_id}",
			method="delete",
		)
		return response.json() if return_data else response.status_code == 200


@singleton
class BookObtain:
	def __init__(self) -> None:
		self.acquire = Acquire.CodeMaoClient()

	# 获取全部图鉴
	def get_all_book(self):
		response = self.acquire.send_request(url="/api/sprite/list/all", method="get")
		return response.json()

	# 获取所有属性
	def get_all_attr(self):
		response = self.acquire.send_request(url="/api/sprite/factio", method="get")
		return response.json()

	# 按星级获取图鉴
	def get_book_by_star(self, star: Literal[1, 2, 3, 4, 5, 6]):
		# 1:一星 2:二星 3:三星 4:四星 5:五星 6:六星
		return self._get_book_by_params({"star": star})

	# 按属性获取图鉴
	def get_book_by_attr(self, attr_id: Literal[2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]):
		# 2:普通 3:草 4:地 5:电 6:虫 7:水 8:火 9:机械 10:飞行 11:超能 12:神圣
		return self._get_book_by_params({"faction_id": attr_id})

	# 通用获取图鉴方法
	def _get_book_by_params(self, params: dict):
		response = self.acquire.send_request(
			url="https://api.codemao.cn/api/sprite/list/all",
			method="get",
			params=params,
		)
		return response.json()

	# 获取指定图鉴详情
	def get_book_detail(self, book_id: int):
		response = self.acquire.send_request(
			url=f"/api/sprite/{book_id}",
			method="get",
		)
		return response.json()

	# 点赞图鉴
	def like_book(self, method: select, book_id: int, return_data: bool = False) -> bool | dict:
		response = self.acquire.send_request(
			url=f"/api/sprite/praise/{book_id}",
			method=method,
		)
		return response.json() if return_data else response.status_code == 200
