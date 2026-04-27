<div align="center">

# LM Studio对话导入工具

[![GitHub 仓库](https://img.shields.io/badge/GitHub-Repo-yellow.svg?logo=github)](https://github.com/wangyy04/LM_Studio_Import)
[![Python 版本](https://img.shields.io/badge/python-%20%3E3.10-blue.svg?logo=python&label=Python)](https://www.python.org/downloads/)

</div>

用于将其它LLM运行程序导出的txt格式的对话文件转换为LM Studio使用的json文件，并且格式完全符合LM Studio的要求。
目前仅支持LM mini导出的txt文件。

---

## 项目文件结构
可从GitHub等渠道下载完整的项目文件，文件结构如下所示。
```
LM_Studio_Import/
├── README.md                       # 本说明文档
├── requirements.txt                # 依赖清单
├── main.py                         # 主程序入口脚本
├── src/                            # 各函数、类的实现代码
│   ├── ConversationInfo.py         # 对话基本信息类
│   ├── customTypes.py              # 自定义数据类型类
│   ├── DefaultSettings.py          # 默认全局设置类
│   ├── GenerateSpeedCounter.py     # 生成速度计算器类
│   ├── init.py                     # 初始化相关函数
│   ├── Message.py                  # 消息类
│   ├── ModelSettings.py            # 模型运行参数类
│   ├── TOkensCounter.py            # Token计数器类
│   └── utils.py                    # 功能函数
├── tokenizers/                     # 分词器
│   ├── tokens_estimate.json        # Token计数估算规则
│   ├── deepseek_r1_tokenizer/      # DeepSeek-r1的分词器
│   └── ......                      # 各系列LLM的分词器
├── template/                       # LM Studio格式的json对话文件模板
│   ├── template_assistant_nothink_message.json
│   ├── template_assistant_think_message.json
│   ├── template_info.json
│   └── template_user_message.json
├── .tmp/                           # 工作区临时文件存放目录（默认情况下为空）
├── reference/                      # 默认全局设置和模型运行参数的参考文件目录（默认情况下为空，需要用户在此存放文件）
└── example/                        # 待导入的LM mini对话文件和典型的LM Studio对话文件样例
```

## 使用方法
### 0. 下载项目并安装依赖
首先下载项目文件并确认各目录下文件完整。第一次运行前需要先在项目根目录下运行`pip install -r requirements.txt`命令安装所有依赖项，或者根据`requirements.txt`中列出的依赖项手动安装。

### 1. 准备设置模板
在LM Studio中，选择所需的LLM，以所需默认全局设置和模型运行参数，创建一个新的对话，对话内容任意，但必须是一个**完整**的对话，即至少包含一条用户消息和一条LLM生成的回答，若有多轮对话，以第一轮对话生成参数为准。  
将LM Studio自动生成的对话文件（文件名形如`*.conversation.json`）复制到本项目中`reference/`目录下以供参考，该目录下可存储多个参考对话文件，可在运行时选择指定的文件作为默认全局设置或模型运行参数的参考。

> **默认全局设置**：是否使用使用全局的默认推理预设、默认LLM推理温度、默认系统提示词、客户端输入内容、上一次使用的LLM参数（LLM文件路径、LLM的Huggingface ID、GPU选择设置、GPU防过载策略、CPU线程池大小、上下文长度、是否开启快速注意力、是否尝试使用直接 I/O 读取模型文件、模型层卸载到 GPU 的比例）等  
> **模型运行参数**：当前消息是否作为上下文参与后续生成、本次生成使用的LLM参数（LLM文件路径、LLM的Huggingface ID、GPU选择设置、GPU防过载策略、CPU线程池大小、上下文长度、是否开启快速注意力、是否尝试使用直接I/O读取模型文件、模型层卸载到 GPU 的比例、模型聊天模板）、LLM推理温度、对话标题生成方式等

**注意**：由于LM Studio默认根据对话文件中的设置继续对话的推理，为了避免错误，强烈建议使用相同的模型设置 **（特别是模型的选择）** 创建对话作为参考。例如，在LM mini中使用Qwen3.5系列模型产生的txt对话文件，在需要转换导入LM Studio时，建议同样使用Qwen3.5系列模型生成作为参考的对话文件。

### 2. 准备需要导入的txt对话文件
从LM mini中导出txt格式的对话文件，该对话文件将被导入到LM Studio中。LM mini对话文件格式如下所示，可查看example/目录下的样例。
```text
============================================================
Chat Export: <对话名称>
Created: <对话创建时间>
Updated: <对话更新时间>
============================================================

[<时间>] You:
<用户消息内容>

------------------------------------------------------------

[<时间>] Assistant:
<LLM消息内容>

------------------------------------------------------------
```
将该文件存储于任意允许读取的位置，记录下其路径。

### 3. 运行工具
运行项目根目录下的`main.py`脚本，若在IDE中运行，请配置“在输出控制台中模拟终端”，否则可能交互功能不能正常工作。

### 4. 设置token计数器
token计数器用于计算各条消息的token数，使用键盘上的方向键选择LLM提供商和LLM系列。若所用的LLM不在选项中，请选择“其它”，然后输入使用的LLM系列名称。  
然后选择是否开启估算模式。若选择不开启估算模式，并且所用LLM系列的分词器已存储在`tokenizers/`目录下，则会加载所用的分词器，以精确地计算token数；否则使用估算模式，根据`tokenizers/tokens_estimate.json`中设定的估算规则估算token数。

### 5. 设置生成速度计算器
输入模型生成速度的基准值（单位为tokens/s）和生成速度波动范围（单位为tokens/s，若不填则默认为基准值的20%）。各条消息/内容块的生成速度根据这两个值，在`基准值±波动范围`的范围内随机选取，以模拟真实的对话文件记录内容。

### 6. 选择待导入的对话文件
输入之前记录下的待导入的txt格式对话文件的完整路径，无需对斜杠转义。输入后按下回车键继续。

### 7. 选取参考文件
程序提示将参考用的json对话文件复制到reference/目录下，若已复制则直接按下回车键继续。  
若该目录下没有符合要求的.conversation.json文件，则会提示“请确认文件是否存在、文件名是否正确”，将对话文件按要求存储在该目录下后按下回车键重新检测；若该目录下有多个符合要求的.conversation.json文件，则会提示用户分别选择作为默认全局设置参考的和作为模型运行参数参考的对话文件；若该目录下仅有一个符合要求的.conversation.json文件，则会自动将该文件作为默认全局设置和模型运行参数参考的对话文件。

### 8. 生成并导入LM Studio对话文件
选取参考文件后，按下回车继续运行，若无报错将会在项目根目录下生成名为`<时间戳>.conversation.json`的文件，将它复制到LM Studio对话文件目录下，即可完成导入。  
接下来可以在LM Studio中查看导入的对话、继续生成后续对话等各项操作。