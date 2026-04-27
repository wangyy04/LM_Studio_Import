from pathlib import Path
import os
import re
import json
import secrets
from decimal import Decimal
import copy
from typing import Literal
from src.Message import Message
from src.TokensCounter import TokensCounter
from src.GenerateSpeedCounter import GenerateSpeedCounter
from src.ConversationInfo import ConversationInfo
from src.DefaultSettings import DefaultSettings
from src.ModelSettings import ModelSettings
from src.customTypes import FloatRx

def get_path_from_keyboard(path_type: Literal['directory', 'file'] = 'file',
                           prompt: str = "请输入路径：",
                           is_need_check: bool = True) -> Path | None:
    """
    获取从键盘输入的路径
    Args:
        path_type : 路径类型 'directory':文件夹 'file':文件
        prompt : 输入提示词，显示给用户用于提示输入内容
        is_need_check : 是否需要验证文件夹/文件是否存在 True:验证 False:不验证
    Return:
        若未要求验证、或要求验证且目录符合要求则返回Path型路径，否则返回None
    """
    raw_path = input(prompt).strip()
    # 去除可能的引号
    if len(raw_path) >= 2 and raw_path[0] == raw_path[-1] and raw_path[0] in ('"', "'"):
        raw_path = raw_path[1:-1]
    path = Path(raw_path)
    if is_need_check:
        if not path.exists():
            print(f"错误：{raw_path} 不存在")
            return None
        elif path_type=='file' and (not path.is_file()):
            print(f"错误：{raw_path} 不是合法的文件路径")
            return None
        elif path_type=='directory' and (not path.is_dir()):
            print(f"错误：{raw_path} 不是合法的目录路径")
            return None
    return path

def split_message(input_file: Path, output_dir: Path):
    """将对话记录中的每条消息拆分为单独的txt文件"""
    SEP_BASIC = "============================================================"
    SEP_MSG = "------------------------------------------------------------"
    with open(input_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    idx = 0
    total_lines = len(lines)
    # 寻找基本信息区起点
    while idx < total_lines and lines[idx].strip() != SEP_BASIC:
        idx += 1
    if idx >= total_lines:
        print("错误：未找到基本信息起始分隔符。")
        return
    idx += 1  # 进入基本信息内容区

    # 保存基本信息
    basic_info_lines = []
    while idx < total_lines and lines[idx].strip() != SEP_BASIC:
        basic_info_lines.append(lines[idx])
        idx += 1

    if idx >= total_lines:
        print("错误：未找到基本信息结束分隔符。")
        return

    # 保存基本信息到 info.txt
    info_path = os.path.join(output_dir, "info.txt")
    with open(info_path, 'w', encoding='utf-8') as f_info:
        f_info.writelines(basic_info_lines)
    # print(f"基本信息已保存：{info_path}")

    idx += 1  # 跳过结束分隔符，现在 idx 指向第一条消息的第一行

    # 分割消息
    messages = []
    current_msg_lines = []
    while idx < total_lines:
        line = lines[idx]
        if line.strip() == SEP_MSG:
            # 遇到消息分隔符 → 之前累积的行构成一条完整消息
            if current_msg_lines:
                messages.append(''.join(current_msg_lines))
                current_msg_lines = []
        else:
            # 普通内容行（包括第一条消息的所有行）
            current_msg_lines.append(line)
        idx += 1

    for i, msg_content in enumerate(messages, start=1):
        out_path = os.path.join(output_dir, f"msg_{i:04d}.txt")
        with open(out_path, 'w', encoding='utf-8') as f_out:
            f_out.write(msg_content)
        # print(f"已保存：{out_path}")

def natural_sort_key(filename):
    match = re.search(r'msg_(\d+)\.txt$', filename)
    if match:
        return int(match.group(1))
    return float('inf')

def get_msg_list(dir_path: Path, tokens_counter: TokensCounter) -> list[Message]:
    """将消息文件读取并转为Message列表"""
    msg_list = []
    pattern = re.compile(r'^msg_\d+\.txt$')
    files = [f.name for f in dir_path.iterdir() if f.is_file() and pattern.match(f.name)]
    files = sorted(files, key=natural_sort_key)
    for file in files:
        file_path = dir_path.joinpath(file)
        msg_list.append(Message(path=file_path, tokens_counter=tokens_counter))
    return msg_list

def generate_new_conversation(template_path: Path,
                              conversation_info: ConversationInfo,
                              default_settings: DefaultSettings,
                              model_settings: ModelSettings,
                              msg_list: list[Message],
                              generate_speed_counter: GenerateSpeedCounter):
    """
    生成新的对话文件json
    Args:
        template_path : 模板路径
        conversation_info : 对话基本信息
        default_settings : 默认全局设置
        model_settings : 模型运行参数 "genInfo"字段
        msg_list : 消息列表
        generate_speed_counter : 生成速度计算器
    """
    # 读取基本信息和整体结构模板
    text = None
    with open(template_path.joinpath("template_info.json"), 'r', encoding='utf-8') as f:
        text = f.read()

    total_num_tokens = 0            # 总token数
    time_last_user_msg = None       # 最后用户消息时间
    time_last_assistant_msg = None  # 最后助手消息时间
    for msg in reversed(msg_list):
        # 从后向前遍历消息列表，存储最后用户/助手消息时间，计算总token消耗
        total_num_tokens += msg.num_msg_token + msg.num_thk_token
        if (msg.role=="user"
                and time_last_user_msg is None):
            time_last_user_msg = msg.send_time
        elif (msg.role=="assistant"
                and time_last_assistant_msg is None):
            time_last_assistant_msg = msg.send_time

    # 替换模板中的变量占位符（str直接替换，数值先规范化再替换）
    text = text.replace("{{对话名称}}", conversation_info.conversation_name)
    replacement_fragment = json.dumps(conversation_info.time_create, ensure_ascii=False)
    text = text.replace("{{创建时间}}", replacement_fragment)
    replacement_fragment = json.dumps(total_num_tokens, ensure_ascii=False)
    text = text.replace("{{token总消耗}}", replacement_fragment)
    replacement_fragment = json.dumps(time_last_user_msg, ensure_ascii=False)
    text = text.replace("{{最后用户消息时间}}", replacement_fragment)
    replacement_fragment = json.dumps(time_last_assistant_msg, ensure_ascii=False)
    text = text.replace("{{最后助手消息时间}}", replacement_fragment)

    # 加载json格式并导入默认全局设置
    data = json.loads(text)
    data.update(default_settings.default_settings)

    # 读取消息模板
    msg_template = {}
    with open(template_path.joinpath("template_assistant_think_message.json"), 'r', encoding='utf-8') as f:
        text = f.read()
        msg_template["assistant_think"] = text
    with open(template_path.joinpath("template_assistant_nothink_message.json"), 'r', encoding='utf-8') as f:
        text = f.read()
        msg_template["assistant_no_think"] = text
    with open(template_path.joinpath("template_user_message.json"), 'r', encoding='utf-8') as f:
        text = f.read()
        msg_template["user"] = text

    # 将消息列表转为标准对话文件的格式
    msg_json_list = []
    model_id = model_settings.model_settings["identifier"]
    prev_msg = None
    for msg in msg_list:
        if msg.role=="user":
            text = msg_template["user"]
            msg_content = json.dumps(msg.msg_content, ensure_ascii=False)[1:-1]
            text = text.replace("{{用户消息}}", msg_content)
            msg_json = json.loads(text)
        else:
            # 随机生成4个时间戳后缀备用（16位小数，若小于0.1则为17位）
            timestamp_postfix = []
            for _ in range(3):
                rand_int = secrets.randbelow(10**17-1) + 1
                num = Decimal(rand_int) / Decimal(10 ** 17)
                if num > Decimal('0.1'):
                    num = num.quantize(Decimal('0.0000000000000001'))
                timestamp_postfix.append(str(num))

            # 计算思考/消息开始的时间
            time_used_msg = int(msg.num_msg_token / generate_speed_counter.get_speed() * 1000)  # 消息生成用时(ms)
            time_used_thk = int(msg.num_thk_token / generate_speed_counter.get_speed() * 1000)  # 思考生成用时(ms)
            time_msg_start = msg.send_time - time_used_msg  # 消息开始时间戳
            time_thk_start = time_msg_start - time_used_thk  # 思考开始时间戳

            if msg.is_include_think:
                text = msg_template["assistant_think"]
                # 填写模板内的占位符
                text = text.replace("{{思考时间戳}}", str(time_thk_start)+"-"+timestamp_postfix[0])
                thk_content = json.dumps(msg.thk_content, ensure_ascii=False)[1:-1]
                text = text.replace("{{助手思考内容}}", thk_content)
                replacement_fragment = json.dumps(msg.num_thk_token, ensure_ascii=False)
                text = text.replace("{{思考token消耗}}", replacement_fragment)
                time_used_thk_sec = time_used_thk/1000.0
                text = text.replace("{{思考用时}}",f"{time_used_thk_sec:.2f}")
            else:
                text = msg_template["assistant_no_think"]

            text = text.replace("{{模型id}}", model_id)
            text = text.replace("{{消息时间戳}}", str(time_msg_start)+"-"+timestamp_postfix[1])
            msg_content = json.dumps(msg.msg_content, ensure_ascii=False)[1:-1]
            text = text.replace("{{助手消息内容}}", msg_content)
            replacement_fragment = json.dumps(msg.num_msg_token, ensure_ascii=False)
            text = text.replace("{{消息token消耗}}", replacement_fragment)
            text = text.replace("{{调试信息时间戳}}", str(msg.send_time) + "-" + timestamp_postfix[2])
            text = text.replace("{{标题生成方式}}", "prompt")

            msg_json = json.loads(text)
            # 为助手消息添加"genInfo"字段
            for _ in msg_json["versions"][0]["steps"]:
                if "genInfo" in _:
                    _["genInfo"] = copy.deepcopy(model_settings.model_settings)
                    msg_stats = _["genInfo"]["stats"]
                    msg_stats["timeToFirstTokenSec"] = FloatRx(value=secrets.SystemRandom().uniform(0.2, 0.5),
                                                               decimal=3, rounding="half_even") # 确保序列化时保留3位小数
                    msg_stats["totalTimeSec"] = (time_used_msg+time_used_thk)/1000.0
                    msg_stats["tokensPerSecond"] = (msg.num_thk_token+msg.num_msg_token)/msg_stats["totalTimeSec"]
                    if prev_msg is None:
                        msg_stats["promptTokensCount"] = 0
                    else:
                        msg_stats["promptTokensCount"] = prev_msg.num_msg_token
                    msg_stats["predictedTokensCount"] = msg.num_thk_token+msg.num_msg_token
                    msg_stats["totalTokensCount"] = msg_stats["promptTokensCount"]+msg_stats["predictedTokensCount"]

        msg_json_list.append(msg_json)
        prev_msg = msg

    # 将规范的消息列表填入"message"字段
    data["messages"] = msg_json_list

    return data