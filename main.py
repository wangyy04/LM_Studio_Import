from src.init import set_tokens_counter, set_generate_speed_counter, clear_workspace, get_settings
from src.utils import get_path_from_keyboard, split_message, get_msg_list, generate_new_conversation
from src.ConversationInfo import ConversationInfo
from pathlib import Path
import json

if __name__=="__main__":
    tokens_counter = set_tokens_counter()       # 设置token计数器
    generate_speed_counter = set_generate_speed_counter()   # 设置生成速度计算器
    script_dir = Path(__file__).resolve().parent
    workspace_path = script_dir / ".tmp"
    reference_path = script_dir / "reference"
    template_path = script_dir / "template"
    clear_workspace(path=workspace_path)        # 清理工作区临时目录
    raw_txt_path = get_path_from_keyboard(path_type='file', is_need_check=True,
                                          prompt="请输入原始对话文件(*.txt)的路径：")    # 从键盘输入对话文件路径
    if raw_txt_path is None:
        print(f"错误：{raw_txt_path} 文件不是合法的原始对话文件")
    split_message(input_file=raw_txt_path, output_dir=workspace_path)    # 拆分对话txt到工作目录
    msg_list = get_msg_list(dir_path=workspace_path, tokens_counter=tokens_counter)
    default_settings, model_settings = get_settings(dir_path=reference_path)    # 从reference/下的参考对话文件获取默认全局设定和模型运行参数
    c = ConversationInfo(path=workspace_path.joinpath("info.txt"))      # 读取对话基本信息
    data = generate_new_conversation(template_path=template_path, conversation_info=c,
                                     default_settings=default_settings, model_settings=model_settings,
                                     msg_list=msg_list, generate_speed_counter=generate_speed_counter)
    outputfile_name = str(c.time_create)+".conversation.json"
    with open(outputfile_name, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    clear_workspace(path=workspace_path)        # 清理工作区临时目录