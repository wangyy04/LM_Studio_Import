import questionary
from src.TokensCounter import TokensCounter
from src.GenerateSpeedCounter import GenerateSpeedCounter
from src.DefaultSettings import DefaultSettings
from src.ModelSettings import ModelSettings
import colorama
from pathlib import Path
import os
import shutil

def set_tokens_counter() -> TokensCounter:
    """设置token计数器"""
    llm_list = {
        "Qwen": ["Qwen3.5", "Qwen3"],
        "DeepSeek": ["DeepSeek-v3.2", "DeepSeek-v3", "DeepSeek-r1"]
    }
    colorama.init(autoreset=True)       # 设置彩色输出后自动重置
    print(colorama.Fore.CYAN + "==============设置token计数器==============")
    provider = questionary.select(
        "请选择使用的LLM提供商：",
        choices=["Qwen", "DeepSeek", "其它"]
    ).ask()
    if provider == "其它":
        option = input("请输入使用的LLM系列：")
    else:
        option = questionary.select(
            "请选择使用的LLM系列：",
            choices=llm_list[provider] + ["其它"]
        ).ask()
    if option == "其它":
        option = input("请输入使用的LLM系列：")
    is_estimated_chn = questionary.select(
        "是否开启估算模式？（估算模式下，不加载分词器，仅估算token数）",
        choices=["否", "是"]
    ).ask()
    print(colorama.Fore.CYAN + "===========================================")
    if is_estimated_chn == "否":
        is_estimated = False
    else:
        is_estimated = True
    return TokensCounter(llm=option, is_estimated=is_estimated)

def set_generate_speed_counter() -> GenerateSpeedCounter:
    """设置生成速度计算器"""
    colorama.init(autoreset=True)  # 设置彩色输出后自动重置
    print(colorama.Fore.CYAN + "=============设置生成速度计算器=============")
    base_speed = float(input("请输入模型生成速度的基准值（单位为tokens/s）："))
    speed_range = input("请输入生成速度波动范围（单位为tokens/s，若不填则默认为基准值的20%）：")
    print(colorama.Fore.CYAN + "============================================")
    if speed_range=="":
        speed_range = None
    else:
        speed_range = float(speed_range)
    return GenerateSpeedCounter(base=base_speed, speed_range=speed_range)

def clear_workspace(path: Path):
    """清空工作目录文件夹"""
    for item in os.listdir(path):
        item_path = os.path.join(path, item)
        if os.path.isfile(item_path) or os.path.islink(item_path):
            os.unlink(item_path)        # 删除文件或符号链接
        elif os.path.isdir(item_path):
            shutil.rmtree(item_path)    # 递归删除子文件夹

def get_settings(dir_path: Path) -> tuple:
    """
    从dir_path目录下的参考对话文件获取设置
    返回一个tuple，(DefaultSettings, ModelSettings)
    """
    colorama.init(autoreset=True)  # 设置彩色输出后自动重置
    print(colorama.Fore.CYAN + "=============选择作为参考的对话文件=============")
    print("请先在LM Studio中进行一轮简单的对话，然后将生成的名称形如 *.conversation.json 的文件复制到reference/目录下。\n" +
          "该文件中包含的设置（例如全局设置参数、使用的模型、模型生成参数等）将会作为生成的新对话文件中的设置。\n" +
          "完成上述操作后，请按下 " + colorama.Fore.YELLOW + "回车键" + colorama.Fore.RESET + " 继续")
    input()
    while True:
        files = [
            f for f in os.listdir(dir_path)
            if os.path.isfile(os.path.join(dir_path, f)) and f.endswith(".conversation.json")
        ]
        if len(files)>0:
            break
        print(colorama.Fore.RED + "检测到reference/目录下不存在 *.conversation.json 文件，请确认文件是否存在、文件名是否正确。\n" +
              colorama.Fore.RED + "确认后请按下 " + colorama.Fore.YELLOW + "回车键" + colorama.Fore.RED + " 继续")
        input()
    if len(files)>1:
        file_default_ref = questionary.select(
            "检测到reference/目录下存在多个 *.conversation.json 文件，请选择一个作为全局设置参考对象",
            choices=files
        ).ask()
        file_model_ref = questionary.select(
            "检测到reference/目录下存在多个 *.conversation.json 文件，请选择一个作为运行参数设置参考对象",
            choices=files
        ).ask()
    else:
        file_default_ref = files[0]
        file_model_ref = files[0]
    default_settings = DefaultSettings(path=dir_path.joinpath(file_default_ref))
    model_settings = ModelSettings(path=dir_path.joinpath(file_model_ref))
    return default_settings, model_settings