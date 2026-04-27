"""
模型运行参数设定（参数包含在消息中）
从指定的conversation.json对话文件中读取全局默认设定 "genInfo"字段
"""
from pathlib import Path
from typing import Any
import json

class ModelSettings:
    __reference_file: Path
    model_settings: Any

    def __init__(self, path: Path):
        self.__reference_file = path
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        msgs = data["messages"]
        for msg in msgs:
            if "versions" not in msg:
                continue
            versions = msg["versions"]
            for version in versions:
                if "steps" not in version:
                    continue
                steps = version["steps"]
                for step in steps:
                    if "genInfo" in step:
                        self.model_settings = step["genInfo"]
                        return
        print(f"错误：未在文件 {str(path)} 中找到模型运行时参数")