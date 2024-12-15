from json import loads
from random import choice
from typing import Literal, cast

from src.api import community, user, work
from src.base import acquire, data, decorator, file, tool


@decorator.singleton
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


@decorator.singleton
class Tool(Union):
	def __init__(self) -> None:
		super().__init__()

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
			guess = f"{i:04d}"  # 格式化为四位数,前面补零
			test_string = int(phonenum.replace("****", guess))
			print(test_string)
			if self.user_motion.verify_phone(test_string):
				return test_string


@decorator.singleton
class Index(Union):
	def __init__(self) -> None:
		super().__init__()

	# 打印slogan
	def index(self):
		print(self.setting.PROGRAM["SLOGAN"])
		print(f"版本号: {self.setting.PROGRAM["VERSION"]}")


@decorator.singleton
class Obtain(Union):
	def __init__(self) -> None:
		super().__init__()

	# 获取新回复(传入参数就获取前*个回复,若没传入就获取新回复数量, 再获取新回复数量个回复)
	def get_new_replies(
		self, limit: int = 0, type_item: Literal["LIKE_FORK", "COMMENT_REPLY", "SYSTEM"] = "COMMENT_REPLY"
	) -> list[dict[str, str | int | dict]]:
		_list = []
		reply_num = self.community_obtain.get_message_count(method="web")[0]["count"]
		if reply_num == limit == 0:
			return [{}]
		result_num = reply_num if limit == 0 else limit
		offset = 0
		while result_num >= 0:
			limit = sorted([5, result_num, 200])[1]
			response = self.community_obtain.get_replies(type=type_item, limit=limit, offset=offset)
			_list.extend(response["items"][:result_num])
			result_num -= limit
			offset += limit
		return _list

	# 获取评论区特定信息
	def get_comments_detail(
		self,
		work_id: int,
		method: Literal["user_id", "comments", "comment_id"] = "user_id",
	):
		comments = self.work_obtain.get_work_comments(work_id=work_id, limit=200)
		if method == "user_id":
			result = []
			# 添加评论用户的 ID
			result.extend(comment_item["user"]["id"] for comment_item in comments)
			# 添加回复用户的 ID
			result.extend(
				reply_item["reply_user"]["id"]
				for comment_item in comments
				if "replies" in comment_item and "items" in comment_item["replies"]
				for reply_item in comment_item["replies"]["items"]
			)
		elif method == "comment_id":
			result = []
			# 添加评论ID
			result.extend(item["id"] for item in comments)
			# 添加回复ID
			result.extend(
				f"{item['id']}.{reply['id']}"
				for item in comments
				if "replies" in item and "items" in item["replies"]
				for reply in item["replies"]["items"]
			)

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


@decorator.singleton
class Motion(Union):
	def __init__(self) -> None:
		super().__init__()

	# 清除作品广告的函数
	def clear_ad(self, keys) -> bool:
		works_list = self.user_obtain.get_user_works_web(self.data.ACCOUNT_DATA["id"])
		for works_item in works_list:
			work_id = works_item["id"]
			work_id = cast(int, work_id)
			works_item["id"] = cast(int, works_item["id"])
			comments: list = Obtain().get_comments_detail(
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

	# 给某人作品全点赞
	def like_all_work(self, user_id: str):
		works_list = self.user_obtain.get_user_works_web(user_id)
		for item in works_list:
			item["id"] = cast(int, item["id"])
			if not self.work_motion.like_work(work_id=item["id"]):
				return False
		return True

	# 自动回复
	def reply_work(self):
		new_replies = Obtain().get_new_replies()
		_answers = [
			{question: answer.format(**self.data.INFO) for question, answer in answer_dict.items()}
			for answer_dict in self.data.USER_DATA["answers"]
		]
		_replies = [reply.format(**self.data.INFO) for reply in self.data.USER_DATA["replies"]]

		def get_response(comment, answers):
			for answer_dict in answers:
				for key, value in answer_dict.items():
					if key in comment:
						return value

		if new_replies == [{}]:
			return True
		for item in new_replies:
			type_item = item["type"]
			content = loads(cast(str, item["content"]))
			message = content["message"]
			if type_item in ["WORK_COMMENT", "WORK_REPLY", "WORK_REPLY_REPLY"]:
				comment_text = message["comment"] if type_item == "WORK_COMMENT" else message["reply"]
				_answer = get_response(comment=comment_text, answers=_answers)
				comment = _answer if _answer else choice(_replies)
				if type_item == "WORK_COMMENT":
					self.work_motion.reply_work(
						work_id=message["business_id"],
						comment_id=message["comment_id"],
						comment=comment,
						return_data=True,
					)
				else:
					parent_id = cast(int, item.get("reference_id", message["replied_id"]))
					id_list = Obtain().get_comments_detail(work_id=message["business_id"], method="comment_id")
					comment_id = cast(int, self.tool_routine.find_prefix(number=message["reply_id"], lst=id_list))
					self.work_motion.reply_work(
						work_id=message["business_id"],
						comment_id=comment_id,
						comment=comment,
						parent_id=parent_id,
						return_data=True,
					)


# "WORK_REPLY",路人a评论{user}在某个作品的评论
# "WORK_REPLY_REPLY_FEEDBACK",路人a回复{user}在某个作品下发布的评论的路人b/a的回复
# "WORK_COMMENT",路人a评论{user}的作品
# "WORK_REPLY_REPLY_AUTHOR",路人a回复{user}作品下路人b/a对某条评论的回复
# "WORK_REPLY_REPLY",路人a回复{user}作品下路人b/a的评论下{user}的回复
# "POST_REPLY",
# "POST_REPLY_REPLY_AUTHOR",
# "POST_REPLY_AUTHOR",
# "POST_COMMENT",
# "POST_REPLY_REPLY_FEEDBACK",
# "POST_REPLY_REPLY",
# "WORK_REPLY_AUTHOR",路人a回复{user}作品下路人b的某条评论
# "WORK_DISCUSSION_LIKED",
# "WORK_LIKE",
# "POST_DISCUSSION_LIKED",
# "POST_COMMENT_DELETE_FEEDBACK",
# "POST_DELETE_FEEDBACK",
# "WORK_SHOP_USER_LEAVE",
