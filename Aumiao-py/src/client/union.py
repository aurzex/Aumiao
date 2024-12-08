from typing import Literal, cast

from src.api import community, user, work
from src.base import acquire, data, file, tool


class Union:
	def __init__(self) -> None:
		self.acquire = acquire.CodeMaoClient()
		self.cache = data.CodeMaoCache()
		self.community_obtain = community.Obtain()
		self.data = data.CodeMaoData()
		self.file = file.CodeMaoFile()
		self.setting = data.CodeMaoSetting()
		self.tool_process = tool.CodeMaoProcess()
		self.tool_routine = tool.CodeMaoRoutine()
		self.user_motion = user.Motion()
		self.user_obtain = user.Obtain()
		self.work_motion = work.Motion()
		self.work_obtain = work.Obtain()

	# 清除作品广告的函数
	def clear_ad(self, keys) -> bool:
		works_list = self.user_obtain.get_user_works_web(self.data.ACCOUNT_DATA["id"])
		for works_item in works_list:
			work_id = works_item["id"]
			work_id = cast(int, work_id)
			works_item["id"] = cast(int, works_item["id"])
			comments: list = self.get_comments_detail(
				work_id=works_item["id"],
				method="comments",
			)
			for comments_item in comments:
				comment_id = comments_item["id"]
				content = comments_item["content"].lower()  # 转换小写
				if (
					any(item in content for item in keys) and not comments_item["is_top"]  # 取消置顶评论监测
				):
					print("在作品 {} 中发现广告: {} ".format(works_item["work_name"], content))
					response = self.work_motion.del_comment_work(
						work_id=work_id,
						comment_id=comment_id,
					)
					print("*" * 50)
					if not response:
						return False
				for replies_item in comments_item["replies"]:
					reply_id = replies_item["id"]
					reply = replies_item["content"].lower()  # 转换小写
					if any(item in reply for item in keys):
						print("在作品 {} 中 {} 评论中发现广告: {} ".format(works_item["work_name"], content, reply))
						response = self.work_motion.del_comment_work(
							work_id=work_id,
							comment_id=reply_id,
						)
						print("*" * 50)
						if not response:
							return False
		return True

	# 清除邮箱红点
	def clear_red_point(self, method: Literal["nemo", "web"]):
		item = 0
		while method == "web":
			counts = self.community_obtain.get_message_count("web")
			if len(set(counts[i]["count"] for i in range(3)) | {0}) == 1:
				return True
			params = {
				"query_type": "ANYTHING",
				"limit": 200,
				"offset": item,
			}
			query_types = ["LIKE_FORK", "COMMENT_REPLY", "SYSTEM"]
			responses = {}
			for query_type in query_types:
				params["query_type"] = query_type
				responses[query_type] = self.acquire.send_request(
					url="https://api.codemao.cn/web/message-record",
					method="get",
					params=params,
				).status_code
			item += 200
			if len(set(responses.values()) | {200}) != 1:
				return False
		while method == "nemo":
			counts = self.community_obtain.get_message_count("nemo")
			if (
				counts["like_collection_count"]
				+ counts["comment_count"]
				+ counts["re_create_count"]
				+ counts["system_count"]
				== 0
			):
				return True
			params = {
				"limit": 200,
				"offset": item,
			}
			extra_items = [1, 3]
			responses = {}
			for extra_url in extra_items:
				responses[extra_items] = self.acquire.send_request(
					url="/nemo/v2/user/message/{extra_url}",
					method="get",
					params=params,
				).status_code
			item += 200
			if len(set(responses.values()) | {200}) != 1:
				return False

	# 获取评论区特定信息
	def get_comments_detail(
		self,
		work_id: int,
		method: Literal["user_id", "comments"] = "user_id",
	):
		comments = self.work_obtain.get_work_comments(work_id=work_id)
		if method == "user_id":
			result = [item["user"]["id"] for item in comments]
		elif method == "comments":
			result = []
			for item in comments:
				comment_detail = {
					"id": item["id"],
					"content": item["content"],
					"is_top": item["is_top"],
					"replies": [],
				}
				if "replies" in item and "items" in item["replies"]:
					for reply in item["replies"]["items"]:
						reply_detail = {
							"id": reply["id"],
							"content": reply["content"],
						}
						comment_detail["replies"].append(reply_detail)
				result.append(comment_detail)
		else:
			raise ValueError("不支持的请求方法")
		return result

	# 给某人作品全点赞
	def like_all_work(self, user_id: str):
		works_list = self.user_obtain.get_user_works_web(user_id)
		for item in works_list:
			item["id"] = cast(int, item["id"])
			if not self.work_motion.like_work(work_id=item["id"]):
				return False
		return True

	# 获取新回复(传入参数就获取前*个回复,若没传入就获取新回复数量, 再获取新回复数量个回复)
	def get_new_replies(self, limit: int = 0) -> list[dict[str, str | int]]:
		_list = []
		reply_num = self.community_obtain.get_message_count(method="web")[0]["count"]
		if reply_num == limit == 0:
			return [{}]
		result_num = reply_num if limit == 0 else limit
		offset = 0
		while True:
			limit = sorted([5, result_num, 200])[1]
			response = self.community_obtain.get_replies(type="COMMENT_REPLY", limit=limit, offset=offset)
			_list.extend(response["items"][:result_num])
			result_num -= limit
			offset += limit
			if result_num <= 0:
				break
		return _list

	# 新增粉丝提醒
	def message_report(self, user_id: str):
		response = self.user_obtain.get_user_honor(user_id=user_id)
		timestamp = self.community_obtain.get_timestamp()["data"]
		user_data = {
			"user_id": response["user_id"],
			"nickname": response["nickname"],
			"level": response["author_level"],
			"fans": response["fans_total"],
			"collected": response["collected_total"],
			"liked": response["liked_total"],
			"view": response["view_times"],
			"timestamp": timestamp,
		}
		before_data = self.cache.CACHE
		if before_data != {}:
			self.tool_routine.print_changes(
				before_data=before_data,
				after_data=user_data,
				data={
					"fans": "粉丝",
					"collected": "被收藏",
					"liked": "被赞",
					"view": "被预览",
				},
				date="timestamp",
			)
		before_data.update(user_data)

	# 猜测手机号码(暴力枚举)
	def guess_phonenum(self, phonenum: str) -> int | None:
		for i in range(10000):
			guess = f"{i:04d}"  # 格式化为四位数，前面补零
			test_string = int(phonenum.replace("****", guess))
			print(test_string)
			if self.user_motion.verify_phone(test_string):
				return test_string

	# 打印slogan
	def index(self):
		print(self.setting.PROGRAM["SLOGAN"])
		print(f"版本号: {self.setting.PROGRAM["VERSION"]}")
