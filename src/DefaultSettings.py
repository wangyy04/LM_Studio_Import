"""
全局默认设定
从指定的conversation.json对话文件中读取全局默认设定
"""
from pathlib import Path
from typing import Dict
import json

class DefaultSettings:
    __reference_file : Path
    default_settings : Dict

    def __init__(self, path: Path):
        self.__reference_file = path
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        fields_to_keep = ["usePerChatPredictionConfig",
                          "perChatPredictionConfig",
                          "clientInput",
                          "clientInputFiles",
                          "userFilesSizeBytes",
                          "lastUsedModel",
                          "notes",
                          "plugins",
                          "pluginConfigs",
                          "disabledPluginTools",
                          "looseFiles"]
        self.default_settings = {key: data[key] for key in fields_to_keep if key in data}