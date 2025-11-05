# src/llm.py

import os
from openai import OpenAI
from config import Config

# Config 改造成立一个单例模式
CONFIG = Config()

class LLM:
    def __init__(self):
        self.client = OpenAI(base_url=CONFIG.base_url)

    def generate_daily_report(self, markdown_content, dry_run=False):
        prompt = f"以下是项目的最新进展，根据功能合并同类项，形成一份简报，至少包含：1）新增功能；2）主要改进；3）修复问题；:\n\n{markdown_content}"
        if dry_run:
            with open("daily_progress/prompt.txt", "w+") as f:
                f.write(prompt)
            return "DRY RUN"

        print("Before call GPT")
        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        print("After call GPT")
        print(response)
        return response.choices[0].message.content


if __name__ == "__main__":
    # 使用 github_client.py 拉取 langchain-ai/langchain 最新的 git 信息，并生成文件
    filename = "daily_progress/langchain-ai_langchain_2025-11-05.md"
    with open(filename, "r+", encoding="utf-8") as f:
        data = f.read()
    llm = LLM()
    report_content = llm.generate_daily_report(data)
    print(report_content)

    """ 测试打印结果
    (ai_agent) ****@****-MB0 GitHubSentinel % python3 src/llm.py
    Before call GPT
    After call GPT
    ## Simplified Project Update Brief - LangChain AI\n\n### 新增功能\n1. 支持适用于Qwen兼容模型的reasoning_content解析。 (PR #33836)\n2. 在SummarizationMiddleware中，新增模型上下文窗口的使用以触发总结。 (PR #33825)\n3. 在中间件中增加了get_config()以访问RunnableConfig。 (PR #33823)\n4. 添加语言针对R编程的支持到langchain_text_splitters.Language。 (Issue #33824)\n5. 增加动态工具添加/移除在代理创建和中间件之后的支持。 (Issue #33808)\n6. 引入PythonREPLTool到LangChain v1，此前在langchain_experimental中。 (Issue #33800)\n7. Agent运行时包括agent名称的功能。 (PR #33689)\n\n### 主要改进\n1. 支持服务器端工具调用的即时流媒体。 (Issue #33810)\n2. 支持序列化状态传播以便于批量工具调用。 (Issue #33832)\n3. 使用重入保护Guard到RootListenersTracer以防止递归监听器调用。 (PR #33745)\n4. 提高了HIL (Human in the Loop) 中间件在编辑决策后正确持续编辑的功能。 (Fix #33789)\n5. 添加了为代理实现名称和参数的自动计算和存储元信息的功能。 (PR #33756)\n\n### 修复问题\n1. 修复了create_agent中与langgraph-prebuilt的依赖项问题。 (Issue #33804)\n2. 解决了langchain包中的版本冲突问题。 (Fixes #33816, #33815)\n3. 解决了加载Hugging Face模型时的初始问题。 (Fix #33786)\n4. 修复了数据关键边缘情况下的bugs，如空字符串问题。 (Fix #33779)\n5. 更新了langchain-core依赖版本以修复依赖性的问题。 (Fix #33775)\n6. 修复了在AIMessage响应中设置代理名称的功能。 (Fix #33778)\n7. 修复了工具调用ID添加到on_tool_error事件数据中的问题。 (Fix #33731)\n\n此简报总结了项目的主要更新，包括新功能的添加、主要的性能提升和关键问题的修复，以促进软件的发展和问题解决。
    (ai_agent) ****@****-MB0 GitHubSentinel % 
    """
