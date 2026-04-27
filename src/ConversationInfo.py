"""
对话基本信息类
"""
from pathlib import Path
from datetime import datetime

class ConversationInfo:
    conversation_name : str     # 对话标题
    time_create : int           # 对话创建时unix时间戳（*1000后取整）
    time_update : int           # 对话最后更新时unix时间戳（*1000后取整）

    def __init__(self, path: Path):
        with open(path, 'r', encoding='utf-8') as f:
            for line in f:
                cleaned_line = line.strip()
                if "Chat Export:" in cleaned_line:
                    self.conversation_name = cleaned_line.replace("Chat Export:", "").strip()
                elif "Created:" in cleaned_line:
                    time_create_str = cleaned_line.replace("Created:", "").strip()
                    dt = datetime.strptime(time_create_str, "%Y-%m-%d %H:%M:%S.%f")
                    self.time_create = int(dt.timestamp()*1000)
                elif "Updated:" in cleaned_line:
                    time_update_str = cleaned_line.replace("Updated:", "").strip()
                    dt = datetime.strptime(time_update_str, "%Y-%m-%d %H:%M:%S.%f")
                    self.time_update = int(dt.timestamp() * 1000)