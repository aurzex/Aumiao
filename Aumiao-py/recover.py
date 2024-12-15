import json
import os

DATA_FILE_PATH: str = os.path.join(os.getcwd(), "data/" "data.json")
CACHE_FILE_PATH: str = os.path.join(os.getcwd(), "data/" "cache.json")

__version__ = "2.0.0"


def write(
	path: str,
	text: str | dict,
	method: str = "w",
) -> None:
	check_file(path=path)
	with open(path, mode=method, encoding="utf-8") as file:
		if isinstance(text, str):
			file.write(text + "\n")
		elif isinstance(text, dict):
			file.write(json.dumps(text, ensure_ascii=False, indent=4, sort_keys=False))
		else:
			raise ValueError("不支持的写入方法")


# 检查文件
def check_file(path: str) -> bool:
	try:
		with open(path):
			return True
	except OSError as err:
		print(err)
		return False


data = {
	"PROGRAM_DATA": {
		"HEADERS": {
			"Content-Type": "application/json",
			"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 Edg/124.0.0.0",  # noqa: E501
		},
		"BASE_URL": "https://api.codemao.cn",
		"SLOGAN": "欢迎使用Aumiao-PY!\n你说的对,但是《Aumiao》是一款由Aumiao开发团队开发的编程猫自动化工具于2023年5月2日发布,工具以编程猫宇宙为舞台,玩家可以扮演扮演毛毡用户在这个答辩💩社区毛线🧶坍缩并邂逅各种不同的乐子人😋.在领悟了《猫站圣经》后,打败强敌扫厕所😡,在维护编程猫核邪铀删的局面的同时,逐步揭开编程猫社区的真相",  # noqa: E501
	},
	"ACCOUNT_DATA": {
		"identity": "identity",
		"password": "password",
		"id": "12770114",
		"nickname": "猫鱼a",
		"description": "咕咕咕()",
		"create_time": "1605554626",
		"author_level": "4",
	},
	"USER_DATA": {
		"black_room": {
			"user": ["114514", "1919810", "2233"],
			"work": ["114514", "1919810", "2233"],
			"post": ["114514", "1919810", "2233"],
		},
		"comments": ["666", "加油！:O", "针不戳:D", "前排:P", "沙发*/ω＼*", "不错不错"],
		"emojis": [
			"编程猫_666",
			"编程猫_爱心",
			"编程猫_棒",
			"编程猫_爱心",
			"编程猫_抱大腿",
			"编程猫_打call",
			"编程猫_点手机",
			"编程猫_好厉害",
			"编程猫_加油",
			"编程猫_我来啦",
			"魔术喵_魔术",
			"魔术喵_点赞",
			"魔术喵_开心",
			"魔术喵_魔术",
			"魔术喵_点赞",
			"魔术喵_收藏",
			"星能猫_耶",
			"星能猫_好吃",
			"雷电猴_围观",
			"雷电猴_哇塞",
			"雷电猴_哈哈哈",
			"雷电猴_嘻嘻嘻",
		],
		"answers": [
			"How are you? |I'm fine Thank you ",
			"Let's play,OK? |&Great!",
			"What's your name? |I'm {}",
		],
		"replies": [
			"这是{}的自动回复,不知道你在说啥(",
			"{}的自动回复来喽",
			"嗨嗨嗨!这事{}の自动回复鸭!",
			"{}很忙oh,机器人来凑热闹(*＾＾*)",
			"对不起,{}它又搞忘了时间,一定是在忙呢",
			"机器人要开始搅局了,{}说忙完就过来！",
		],
		"ads": [
			"scp",
			"互赞",
			"赞我",
			"点个",
			"转发",
			"关注",
			"招人",
			"广告",
			"交友",
			"cpdd",
			"处cp",
			"找闺",
			"自动",
			"扫厕所",
			"冲高手",
			"冲大佬",
			"冲传说",
			"戴雨默",
			"光头强",
			"基金会",
			"再创作",
			"找徒弟",
			"协作项目",
			"家族招人",
			"不喜可删",
			"有赞必回",
			"看看我的",
			"粘贴到别人作品",
			"codemao.cn",
		],
	},
}


cache = {}


write(path=DATA_FILE_PATH, text=data)
write(path=CACHE_FILE_PATH, text=cache)
