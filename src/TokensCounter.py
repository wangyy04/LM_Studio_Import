"""token计数器"""
import transformers
from pathlib import Path
from typing import Dict
import json

class TokensCounter:
    __llm_serial : str                      # LLM系列名称
    __tokenizer_path_list = {
        "DeepSeek-v3.2": "deepseek_v3.2_tokenizer",
        "DeepSeek-v3": "deepseek_v3_tokenizer",
        "DeepSeek-r1": "deepseek_r1_tokenizer",
        "Qwen3.5": "qwen3.5_tokenizer",
        "Qwen3": "qwen3_tokenizer"
    }                                       # LLM系列名称与分词器目录路径对应字典
    __tokenizer_path : Path                 # 分词器目录路径
    __estimated : bool = False              # 是否开启估算模式（不加载分词器，仅估计token数）
    __estimate_value : Dict[str, float]     # 一个中文、英文、其它字符对应的token数

    def __init__(self, llm: str = "", is_estimated: bool = False):
        if is_estimated:
            self.__estimated = True
            self.__llm_serial = llm
            self.__estimate_value = self.__import_estimate_value(llm)
            print("已开启估算模式，不加载分词器")
        else:
            self.__llm_serial = llm
            if llm not in self.__tokenizer_path_list:
                print(f"暂未收录模型 {llm} 的分词器，自动开启估算模式")
                self.__estimated = True
                self.__estimate_value = self.__import_estimate_value(llm)
            else:
                self.__estimated = False
                print(f"正在加载分词器 {self.__tokenizer_path_list[llm]}")
                script_dir = Path(__file__).resolve().parent
                tokenizer_parent_path = script_dir.parent / "tokenizers"
                self.__tokenizer_path = tokenizer_parent_path.joinpath(self.__tokenizer_path_list[llm])
                self.__tokenizer = transformers.AutoTokenizer.from_pretrained(
                    self.__tokenizer_path, trust_remote_code=True, local_files_only=True
                )
                print(f"分词器 {self.__tokenizer_path_list[llm]} 加载完成")

    def count_tokens(self, text: str) -> int:
        if self.__estimated:
            num_char = self.__count_char(text)
            # print(self.__estimate_value)
            num_tokens = (num_char["Chinese"] * self.__estimate_value["Chinese"] +
                          num_char["English"] * self.__estimate_value["English"] +
                          num_char["Others"] * self.__estimate_value["Others"])
            return int(num_tokens)
        else:
            result = self.__tokenizer.encode(text)
            # print(result)
            return len(result)

    @staticmethod
    def __count_char(text: str) -> Dict[str, int]:
        """统计中文、英文、其它字符数"""
        chinese = 0
        english = 0
        other = 0
        for ch in text:
            # 判断中文字符：Unicode 基本 CJK 统一表意字符范围 U+4E00 ~ U+9FFF
            if '\u4e00' <= ch <= '\u9fff':
                chinese += 1
            # 判断英文字符：A-Z 或 a-z
            elif ('a' <= ch <= 'z') or ('A' <= ch <= 'Z'):
                english += 1
            else:
                other += 1
        return {
            'Chinese': chinese,
            'English': english,
            'Others': other
        }

    @staticmethod
    def __import_estimate_value(llm: str) -> Dict[str, float]:
        """
        导入token估计值
        tokenizers/tokens_estimate.json中存储了不同LLM系列中，一个中文、英文、其它字符大约对应的token数
        """
        script_dir = Path(__file__).resolve().parent
        tokenizer_parent_path = script_dir.parent / "tokenizers"
        file_path = tokenizer_parent_path.joinpath("tokens_estimate.json")
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            for _llm in data:
                if _llm.lower() in llm.lower():
                    return data[_llm]
            return data["Others"]