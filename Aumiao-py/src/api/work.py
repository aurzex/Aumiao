import json
from typing import Literal

from src.base import acquire, tool
from src.base.decorator import singleton

select = Literal["post", "delete"]


@singleton
class Motion:
	def __init__(self) -> None:
		self.acquire = acquire.CodeMaoClient()

	# 新建kitten作品
	def create_work_kitten(
		self,
		name: str,
		work_url: str,
		preview: str,
		version: str,
		orientation: int = 1,
		sample_id: str = "",
		work_source_label: int = 1,
		save_type: int = 2,
	):
		data = json.dumps(
			{
				"name": name,
				"work_url": work_url,
				"preview": preview,
				"orientation": orientation,
				"sample_id": sample_id,
				"version": version,
				"work_source_label": work_source_label,
				"save_type": save_type,
			}
		)
		response = self.acquire.send_request(
			url="https://api-creation.codemao.cn/kitten/r2/work",
			method="post",
			data=data,
		)
		return response.json()

	# 发布kitten作品
	def publish_work_kitten(
		self,
		work_id: int,
		name: str,
		description: str,
		operation: str,
		labels: list,
		cover_url: str,
		bcmc_url: str,
		work_url: str,
		fork_enable: Literal[0, 1],
		if_default_cover: Literal[1, 2],
		version: str,
		cover_type: int = 1,
		user_labels: list = [],
	):
		# fork_enable: 0表示不开源,1表示开源
		# if_default_cover: 1表示使用默认封面,2表示自定义封面
		# description: 作品描述,operation:操作说明
		data = json.dumps(
			{
				"name": name,
				"description": description,
				"operation": operation,
				"labels": labels,
				"cover_url": cover_url,
				"bcmc_url": bcmc_url,
				"work_url": work_url,
				"fork_enable": fork_enable,
				"if_default_cover": if_default_cover,
				"version": version,
				"cover_type": cover_type,
				"user_labels": user_labels,
			}
		)
		response = self.acquire.send_request(
			url=f"https://api-creation.codemao.cn/kitten/r2/work/{work_id}/publish",
			method="put",
			data=data,
		)
		return response.status_code == 200

	# 新建KN作品/更新作品信息
	# 更新作品时会在更新之前运行该函数,之后再publish
	def create_work_kn(
		self,
		name: str,
		bcm_version: str,
		preview_url: str,
		work_url: str,
		save_type: int = 1,
		stage_type: int = 1,
		work_classify: int = 0,
		hardware_mode: int = 1,
		blink_mode: str = "",
		n_blocks: int = 0,
		n_roles: int = 2,
	):
		data = json.dumps(
			{
				"name": name,
				"bcm_version": bcm_version,
				"preview_url": preview_url,
				"work_url": work_url,
				"save_type": save_type,
				"stage_type": stage_type,
				"work_classify": work_classify,
				"hardware_mode": hardware_mode,
				"blink_mode": blink_mode,
				"n_blocks": n_blocks,
				"n_roles": n_roles,
			}
		)
		response = self.acquire.send_request(
			url="https://api-creation.codemao.cn/neko/works",
			method="post",
			data=data,
		)
		return response.json()

	# 发布KN作品
	def publish_work_kn(
		self,
		work_id: int,
		name: str,
		preview_url: str,
		description: str,
		operation: str,
		fork_enable: Literal[0, 1, 2],
		if_default_cover: Literal[1, 2],
		bcmc_url: str,
		work_url: str,
		bcm_version: str,
		cover_url: str = "",
	):
		# fork_enable: 0表示不开源,1表示开源,2表示对粉丝开源
		# if_default_cover: 1表示使用默认封面,2表示自定义封面
		# description: 作品描述,operation:操作说明
		data = json.dumps(
			{
				"name": name,
				"preview_url": preview_url,
				"description": description,
				"operation": operation,
				"fork_enable": fork_enable,
				"if_default_cover": if_default_cover,
				"bcmc_url": bcmc_url,
				"work_url": work_url,
				"bcm_version": bcm_version,
				"cover_url": cover_url,
			}
		)
		response = self.acquire.send_request(
			url=f"https://api-creation.codemao.cn/neko/community/work/publish/{work_id}",
			method="post",
			data=data,
		)
		return response.status_code == 200

	# 关注的函数
	def follow_work(self, user_id: int, method: select = "post") -> bool:
		response = self.acquire.send_request(
			url=f"/nemo/v2/user/{user_id}/follow",
			method=method,
			data=json.dumps({}),
		)

		return response.status_code == 204

	# 收藏的函数
	def collection_work(self, work_id: int, method: select = "post") -> bool:
		response = self.acquire.send_request(
			url=f"/nemo/v2/works/{work_id}/collection",
			method=method,
			data=json.dumps({}),
		)
		return response.status_code == 200

	# 对某个作品进行点赞的函数
	def like_work(self, work_id: int, method: select = "post") -> bool:
		# 对某个作品进行点赞
		response = self.acquire.send_request(
			url=f"/nemo/v2/works/{work_id}/like",
			method=method,
			data=json.dumps({}),
		)
		return response.status_code == 200

	# 对某个作品进行评论的函数
	def comment_work(self, work_id: int, comment, emoji=None, return_data: bool = False) -> bool | dict:
		response = self.acquire.send_request(
			url=f"/creation-tools/v1/works/{work_id}/comment",
			method="post",
			data=json.dumps(
				{
					"content": comment,
					"emoji_content": emoji,
				}
			),
		)
		return response.json() if return_data else response.status_code == 201

	# 对某个作品下评论进行回复
	def reply_work(
		self,
		comment,
		work_id: int,
		comment_id: int,
		parent_id: int = 0,
		return_data: bool = False,
	) -> bool | dict:
		data = json.dumps({"parent_id": parent_id, "content": comment})
		response = self.acquire.send_request(
			url=f"/creation-tools/v1/works/{work_id}/comment/{comment_id}/reply",
			method="post",
			data=data,
		)
		return response.json() if return_data else response.status_code == 201

	# 删除作品某个评论或评论的回复(评论和回复都会分配一个唯一id)
	def del_comment_work(self, work_id: int, comment_id: int) -> bool:
		response = self.acquire.send_request(
			url=f"/creation-tools/v1/works/{work_id}/comment/{comment_id}",
			method="delete",
		)
		return response.status_code == 204

	# 对某个作品举报
	def report_work(self, describe: str, reason: str, work_id: int):
		data = json.dumps(
			{
				"work_id": work_id,
				"report_reason": reason,
				"report_describe": describe,
			}
		)
		response = self.acquire.send_request(url="/nemo/v2/report/work", method="post", data=data)
		return response.status_code == 200

	# 设置某个评论置顶
	def set_comment_top(
		self,
		method: Literal["put", "delete"],
		work_id: int,
		comment_id: int,
		return_data: bool = False,
	) -> bool:
		response = self.acquire.send_request(
			url=f"/creation-tools/v1/works/{work_id}/comment/{comment_id}/top",
			method=method,
			data=json.dumps({}),
		)
		return response.json() if return_data else response.status_code == 204

	# 点赞作品的评论
	def like_comment_work(self, work_id: int, comment_id: int, method: select = "post"):
		response = self.acquire.send_request(
			url=f"/creation-tools/v1/works/{work_id}/comment/{comment_id}/liked",
			method=method,
			data=json.dumps({}),
		)
		return response.status_code == 201

	# 举报作品的评论
	def report_comment_work(self, work_id: int, comment_id: int, reason: str):
		data = json.dumps(
			{
				"comment_id": comment_id,
				"report_reason": reason,
			}
		)
		response = self.acquire.send_request(
			url=f"/creation-tools/v1/works/{work_id}/comment/report",
			method="post",
			data=data,
		)
		return response.status_code == 200

	# 将一个作品设置为协作作品
	def set_coll_work(self, work_id: int) -> bool:
		response = self.acquire.send_request(
			url=f"https://socketcoll.codemao.cn/coll/kitten/{work_id}",
			method="post",
			data=json.dumps({}),
		)
		return response.status_code == 200

	# 删除一个未发布的作品
	def delete_temp_work_kitten(self, work_id: int) -> bool:
		response = self.acquire.send_request(
			url=f"https://api-creation.codemao.cn/kitten/common/work/{work_id}/temporarily",
			method="delete",
		)
		return response.status_code == 200

	# 删除一个已发布的作品
	def delete_temp_work_kn(self, work_id: int):
		params = {"force": 1}
		response = self.acquire.send_request(
			url=f"https://api-creation.codemao.cn/neko/works/{work_id}",
			method="delete",
			params=params,
		)
		return response.status_code == 200

	# 取消发布一个已发布的作品
	def unpublish_work(self, work_id: int) -> bool:
		response = self.acquire.send_request(
			url=f"/tiger/work/{work_id}/unpublish",
			method="patch",
			data=json.dumps({}),
		)
		return response.status_code == 204

	# 取消发布一个已发布的作品
	def unpublish_work_web(self, work_id: int) -> bool:
		response = self.acquire.send_request(
			url=f"/web/works/r2/unpublish/{work_id}",
			method="put",
			data=json.dumps({}),
		)
		return response.status_code == 200

	# 取消发布一个已发布的KN作品
	def unpublish_kn_work(self, work_id: int) -> bool:
		response = self.acquire.send_request(
			url=f"https://api-creation.codemao.cn/neko/community/work/unpublish/{work_id}",
			method="put",
		)
		return response.status_code == 200

	# 清空回收站kitten作品
	def clear_recycle_kitten_works(self):
		response = self.acquire.send_request(
			url="https://api-creation.codemao.cn/work/user/works/permanently",
			method="delete",
		)

		return response.status_code == 204

	#  清空回收站KN作品
	def clear_recycle_kn_works(self):
		response = self.acquire.send_request(
			url="https://api-creation.codemao.cn/neko/works/permanently",
			method="delete",
		)

		return response.status_code == 200


@singleton
class Obtain:
	def __init__(self) -> None:
		self.acquire = acquire.CodeMaoClient()
		self.tool = tool.CodeMaoProcess()

	# 获取评论区评论
	def get_work_comments(self, work_id: int, limit: int = 15):
		params = {"limit": 15, "offset": 0}
		comments = self.acquire.fetch_data(
			url=f"/creation-tools/v1/works/{work_id}/comments",
			params=params,
			total_key="page_total",
			data_key="items",
			limit=limit,
		)
		return comments

	# 获取作品信息
	def get_work_detail(self, work_id: int):
		response = self.acquire.send_request(
			url=f"/creation-tools/v1/works/{work_id}",
			method="get",
		)
		return response.json()

	# 获取kitten作品信息
	def get_kitten_work_detail(self, work_id: int):
		response = self.acquire.send_request(
			url=f"https://api-creation.codemao.cn/kitten/work/detail/{work_id}",
			method="get",
		)
		return response.json()

	# 获取KN作品信息
	def get_kn_work_detail(self, work_id: int):
		response = self.acquire.send_request(
			url=f"https://api-creation.codemao.cn/neko/works/{work_id}",
			method="get",
		)
		return response.json()

	# 获取KN作品信息
	# KN作品发布需要审核,发布后该接口不断定时获取数据
	# #若接口数据返回正常,则表示发布成功,并将KN作品编辑页面的发布按钮改为更新
	def get_kn_work_info(self, work_id: int):
		response = self.acquire.send_request(
			url=f"https://api-creation.codemao.cn/neko/community/work/detail/{work_id}",
			method="get",
		)
		return response.json()

	# 获取KN作品状态
	def get_kn_work_status(self, work_id: int):
		response = self.acquire.send_request(
			url=f"https://api-creation.codemao.cn/neko/works/status/{work_id}",
			method="get",
		)
		return response.json()

	# 获取其他作品推荐_web端
	def get_other_recommended_web(self, work_id: int):
		response = self.acquire.send_request(
			url=f"/nemo/v2/works/web/{work_id}/recommended",
			method="get",
		)
		return response.json()

	# 获取其他作品推荐_nemo端
	def get_other_recommended_nemo(self, work_id: int):
		params = {"work_id": work_id}
		response = self.acquire.send_request(
			url="/nemo/v3/work-details/recommended/list",
			method="get",
			params=params,
		)
		return response.json()

	# 获取作品信息(info)
	def get_work_info(self, work_id: int):
		response = self.acquire.send_request(url=f"/api/work/info/{work_id}", method="get")
		return response.json()

	# 获取作品标签
	def get_work_label(self, work_id: int):
		params = {"work_id": work_id}
		response = self.acquire.send_request(
			url="/creation-tools/v1/work-details/work-labels",
			method="get",
			params=params,
		)
		return response.json()

	# 获取所有kitten作品标签
	def get_kitten_work_label(self):
		response = self.acquire.send_request(url="https://api-creation.codemao.cn/kitten/work/labels", method="get")
		return response.json()

	# 获取所有kitten默认封面
	def get_kitten_default_cover(self):
		response = self.acquire.send_request(
			url="https://api-creation.codemao.cn/kitten/work/cover/defaultCovers",
			method="get",
		)
		return response.json()

	# TODO 功能未知
	def get_works_recent_cover(self, work_id: int):
		response = self.acquire.send_request(
			url=f"https://api-creation.codemao.cn/kitten/work/cover/{work_id}/recentCovers",
			method="get",
		)
		return response.json()

	# 检查作品名称是否可用
	def check_work_name(self, name: str, work_id: int):
		params = {"name": name, "work_id": work_id}
		response = self.acquire.send_request(url="/tiger/work/checkname", method="get", params=params)
		return response.json()

	# 获取作者更多作品
	def get_author_work(self, user_id: str):
		response = self.acquire.send_request(url=f"/web/works/users/{user_id}", method="get")
		return response.json()

	# 获取作品源码
	def get_work_source(self, work_id: int):
		response = self.acquire.send_request(
			url=f"/creation-tools/v1/works/{work_id}/source/public",
			method="get",
		)
		return response.json()

	# 获取最新作品
	def discover_works_new_web(self, limit: int, offset: int = 0, origin: bool = False):
		extra_params = {"work_origin_type": "ORIGINAL_WORK"} if origin else {}
		params = {**extra_params, "limit": limit, "offset": offset}
		response = self.acquire.send_request(
			url="/creation-tools/v1/pc/discover/newest-work",
			method="get",
			params=params,
		)  # 为防止封号,limit建议调大
		return response.json()

	# 获取最新或最热作品
	def discover_works_subject_web(self, limit: int, offset: int = 0, subject_id: int = 0):
		extra_params = {"subject_id": subject_id} if subject_id else {}
		params = {**extra_params, "limit": limit, "offset": offset}
		response = self.acquire.send_request(
			url="/creation-tools/v1/pc/discover/subject-work",
			method="get",
			params=params,
		)  # 为防止封号,limit建议调大
		return response.json()

	# 获取推荐作品(nemo端)
	def discover_works_nemo(self):
		response = self.acquire.send_request(url="/creation-tools/v1/home/discover", method="get")
		return response.json()

	# 获取nemo端最新作品
	def discover_works_new_nemo(
		self,
		type: Literal["course-work", "template", "original", "fork"],
		limit: int = 15,
		offset=0,
	):
		params = {"limit": limit, "offset": offset}
		response = self.acquire.send_request(url=f"/nemo/v3/newest/work/{type}/list", method="get", params=params)
		return response.json()

	# 获取随机作品主题
	def get_subject_random_nemo(self) -> list[int]:
		response = self.acquire.send_request(url="/nemo/v3/work-subject/random", method="get")
		return response.json()

	# 获取作品主题介绍
	def get_subject_info_nemo(self, id: int):
		response = self.acquire.send_request(url=f"/nemo/v3/work-subject/{id}/info", method="get")
		return response.json()

	# 获取作品主题下作品
	def get_subject_work_nemo(self, id: int, limit: int = 15, offset: int = 0):
		params = {"limit": limit, "offset": offset}
		response = self.acquire.send_request(url=f"/nemo/v3/work-subject/{id}/works", method="get", params=params)
		return response.json()

	# 获取协作邀请码
	def get_coll_code(self, work_id: int, method: Literal["get", "delete"] = "get"):
		response = self.acquire.send_request(
			url=f"https://socketcoll.codemao.cn/coll/kitten/collaborator/code/{work_id}",
			method=method,
		)
		return response.json()

	# 获取协作者列表
	def get_coll_list(self, work_id: int):
		params = {"current_page": 1, "page_size": 100}
		list = self.acquire.fetch_data(
			url=f"https://socketcoll.codemao.cn/coll/kitten/collaborator/{work_id}",
			params=params,
			total_key="data.total",
			data_key="data.items",
			method="page",
			args={"amount": "current_page", "remove": "page_size"},
		)
		return list

	# TODO 功能存疑
	# 获取kitten作品合作者
	def get_collaboration(self, work_id: int):
		response = self.acquire.send_request(
			url=f"https://api-creation.codemao.cn/collaboration/user/{work_id}",
			method="get",
		)
		return response.json()

	# 获取作品再创作情况_web端
	def get_recreate_info_web(self, work_id: int):
		response = self.acquire.send_request(
			url=f"/tiger/work/tree/{work_id}",
			method="get",
		)
		return response.json()

	# 获取作品再创作情况_nemo端
	def get_recreate_info_nemo(self, work_id: int):
		response = self.acquire.send_request(
			url=f"/nemo/v2/works/root/{work_id}",
			method="get",
		)
		return response.json()

	# 获取KN作品历史版本
	def get_works_kn_archive(self, work_id: int):
		response = self.acquire.send_request(
			url=f"https://api-creation.codemao.cn/neko/works/archive/{work_id}",
			method="get",
		)
		return response

	# 获取回收站作品列表
	def get_recycle_kitten_works(
		self,
		version_no: Literal["KITTEN_V3", "KITTEN_V4"],
		work_status: str = "CYCLED",
	):
		params = {
			"limit": 30,
			"offset": 0,
			"version_no": version_no,
			"work_status": work_status,
		}
		works = self.acquire.fetch_data(
			url="https://api-creation.codemao.cn/tiger/work/recycle/list",
			data_key="items",
			params=params,
		)
		return works

	# 获取回收站海龟编辑器作品列表
	def get_recycle_wood_works(
		self,
		language_type: int = 0,
		work_status: str = "CYCLED",
		published_status: str = "undefined",
	):
		params = {
			"limit": 30,
			"offset": 0,
			"language_type": language_type,
			"work_status": work_status,
			"published_status": published_status,
		}
		works = self.acquire.fetch_data(
			url="https://api-creation.codemao.cn/wood/comm/work/list",
			params=params,
			data_key="items",
		)
		return works

	# 获取代码岛回收站作品列表
	def get_recycle_box_works(
		self,
		work_status: str = "CYCLED",
	):
		params = {
			"limit": 30,
			"offset": 0,
			"work_status": work_status,
		}
		works = self.acquire.fetch_data(
			url="https://api-creation.codemao.cn/box/v2/work/list",
			params=params,
		)
		return works

	# 获取回收站小说列表
	def get_recycle_fanfic_works(
		self,
		fiction_status: str = "CYCLED",
	):
		params = {
			"limit": 30,
			"offset": 0,
			"fiction_status": fiction_status,
		}
		fanfic = self.acquire.fetch_data(
			url="https://api.codemao.cn/web/fanfic/my/new",
			params=params,
			data_key="items",
		)
		return fanfic

	# 获取回收站KN作品列表
	def get_recycle_kn_works(
		self,
		name: str = "",
		work_business_classify: int = 1,
	):
		params = {
			"name": name,
			"limit": 24,
			"offset": 0,
			"status": -99,
			"work_business_classify": work_business_classify,
		}
		works = self.acquire.fetch_data(
			url="https://api-creation.codemao.cn/neko/works/v2/list/user",
			params=params,
			data_key="items",
		)
		return works

	# 按关键词搜索KN全部作品
	def search_works_kn(self, name: str, status: int = 1, work_business_classify: int = 1):
		params = {
			"name": name,
			"limit": 24,
			"offset": 0,
			"status": status,
			"work_business_classify": work_business_classify,
		}
		works = self.acquire.fetch_data(
			url="https://api-creation.codemao.cn/neko/works/v2/list/user",
			params=params,
			data_key="items",
		)
		return works

	# 按关键词搜索KN已发布作品
	def search_works_kn_published(self, name: str, work_business_classify: int = 1):
		params = {
			"name": name,
			"limit": 24,
			"offset": 0,
			"work_business_classify": work_business_classify,
		}
		works = self.acquire.fetch_data(
			url="https://api-creation.codemao.cn/neko/works/list/user/published",
			params=params,
			data_key="items",
		)
		return works

	# TODO 待确认
	# 获取KN作品变量列表
	def get_works_kn_variables(self, work_id: int):
		response = self.acquire.send_request(
			url=f"https://socketcv.codemao.cn/neko/cv/list/variables/{work_id}",
			method="get",
		)
		return response.json()

	# 获取积木/角色背包列表
	def get_block_character_package(self, types: Literal["block", "character"], limit: int = 16, offset: int = 0):
		if types == "block":
			type = 1
		elif types == "character":
			type = 0
		# type 1 角色背包 0 积木背包
		# limit 获取积木默认16个,角色默认20个
		params = {
			"type": type,
			"limit": limit,
			"offset": offset,
		}
		response = self.acquire.send_request(
			url="https://api-creation.codemao.cn/neko/package/list",
			method="get",
			params=params,
		)
		return response.json()
