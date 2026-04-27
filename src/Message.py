"""
消息类
"""
from typing import Literal
from datetime import datetime
from pathlib import Path
import secrets
from src.TokensCounter import TokensCounter

class Message:
    send_time : int | None                      # 消息发送时unix时间戳（*1000后取整）（是生成完毕一次性发送的时间，不是生成开始的时间）
    role : Literal["user", "assistant"]         # 消息发送方
    is_include_think : bool | None              # 是否包含think内容
    msg_content : str                           # 消息内容
    thk_content : str | None                    # 思考内容
    num_msg_token : int                         # 消息token数
    num_thk_token : int = 0                     # 思考token数（要加2，因为包含<think>和</think>标签）

    def __init__(self, path: Path, tokens_counter: TokensCounter):
        with open(path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, start=1):
                start_idx = line.find('[')
                end_idx = line.find(']', start_idx + 1)
                if start_idx != -1 and end_idx != -1:
                    # print(f"找到第一对中括号，位于第 {line_num} 行：")
                    first_line = line.rstrip('\n')
                    send_time_str = line[start_idx + 1: end_idx]
                    remaining_content = f.read()
                    break
        # print(first_line)
        # print(send_time_str)
        dt = datetime.strptime(send_time_str, "%Y-%m-%d %H:%M:%S")
        self.send_time = int(dt.timestamp()*1000+secrets.randbelow(1000))     # 将发送时间转为unix时间戳
        if "assistant" in first_line.lower():
            self.role = "assistant"
            thk_end_idx = remaining_content.find("</think>")
            if thk_end_idx==-1:
                # 若无</think>标签
                self.is_include_think = False
                self.thk_content = None
                self.num_thk_token = 0
                self.msg_content = remaining_content
            else:
                self.is_include_think = True
                # 查找并截取可能存在的<think>标签
                thk_start_idx = remaining_content[:thk_end_idx].find("<think>")
                if thk_start_idx != -1:
                    # 包含 '<think>'，截取中间内容
                    self.thk_content = remaining_content[start_idx+len("<think>") : thk_end_idx]
                else:
                    # 不包含 '<think>'，返回 '</think>' 之前的所有内容
                    self.thk_content = remaining_content[:thk_end_idx]
                self.num_thk_token = tokens_counter.count_tokens(self.thk_content)+2
                self.msg_content = remaining_content[thk_end_idx+len("</think>"):]      # </think>之后为消息内容
            self.num_msg_token = tokens_counter.count_tokens(self.msg_content)
        else:
            self.role = "user"
            self.msg_content = remaining_content
            self.num_msg_token = tokens_counter.count_tokens(self.msg_content)