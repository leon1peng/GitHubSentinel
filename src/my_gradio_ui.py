# src/my_gradio_ui.py
"""
GitHub Sentinel - Gradio WebUI (Pseudo-code)
-------------------------------------------
Frontend for managing GitHub repository subscriptions, 
fetching updates, and generating AI-powered progress reports.
"""

from tkinter import E
import gradio as gr

from config import Config
from subscription_manager import SubscriptionManager
from github_client import GitHubClient
from hacker_news_client import HackerNewsClient
from report_generator import ReportGenerator
from llm import LLM
from logger import LOG

CONFIG = Config()
SUBSCRIPTION_MANAGER = SubscriptionManager(CONFIG.subscriptions_file)
LLM_ = LLM()
GITHUB_CLIENT = GitHubClient(CONFIG.github_token)
REPORT_GENERATOR = ReportGenerator(LLM_)


def add_subscription(repo_name: str):
    try:
        SUBSCRIPTION_MANAGER.add_subscription(repo_name) 
        LOG.info(f"add_subscription add {repo_name}.")
        return f"✅ 已成功添加订阅：{repo_name}"
    except Exception as e:
        LOG.error("add_subscription failed: {e}")
        return f"❌ 添加 「{repo_name}」 失败！！！"


def delete_subscription(repo_name: str):
    try:
        SUBSCRIPTION_MANAGER.remove_subscription(repo_name)
        LOG.info(f"delete_subscription add {repo_name}.")
        return f"🗑️ 已删除订阅：{repo_name}"
    except Exception as e:
        LOG.error("delete_subscription failed: {e}")
        return f"❌ 删除 「{repo_name}」 失败！！！"


def get_subscriptions():
    try:
        repos = SUBSCRIPTION_MANAGER.list_subscriptions()
        LOG.info(f"get_subscription add {repos}.")
        return repos
    except Exception as e:
        LOG.error("get_subscription failed: {e}")
        return f"拉取订阅列表失败！！！"


def get_project_info_on_git(repo_name: str, days: int):
    try:
        filepath = GITHUB_CLIENT.export_progress_by_date_range(repo_name, days)
        LOG.info(f"created project info file, filepaeh is {filepath}.")
        with open(filepath, "r", encoding="utf-8") as f:
            data = f.read()
        return data, filepath
    except Exception as e:
        LOG.error(f"get_project_info_on_github failed: {e}")
        return "", ""


def generate_report(repo_name: str, days: int, repo_filepath: str):
    try:
        if not repo_filepath:
            LOG.info(f"generate_report repo_filepath is empty.")
            repo_filepath = GITHUB_CLIENT.export_progress_by_date_range(repo_name, days)
        report, report_file_path = REPORT_GENERATOR.generate_report_by_date_range(repo_filepath, days)

        return report, report_file_path
    except Exception as e:
        LOG.error("generate_report failed: {e}")
        return "", ""


def hackernews_generate_report(page_index: int):
    client = HackerNewsClient()
    top_stories_num = 30 * page_index 
    top_stories = client.fetch_hackernews_top_stories(top_stories_num)
    report = LLM_.hackernews_report(top_stories)
    return report


# === 🎨 Gradio 界面定义 ===
# -----------------------
# Gradio UI
# -----------------------
with gr.Blocks(theme=gr.themes.Soft(), title="GitHub Sentinel WebUI") as demo:
    gr.Markdown(
        """
        <h1 style="text-align:center;">🛰️ GitHub Sentinel WebUI</h1>
        <p style="text-align:center;color:gray;">基于 OpenAI 的智能项目进展分析助手</p>
        """
    )

    # 页面 tag 1   =============== 📬 订阅管理 TAB ===============
    with gr.Tab("📬 订阅管理"):
        gr.Markdown("### 添加或删除订阅的 GitHub 仓库")

        with gr.Row():
            repo_input = gr.Textbox(label="📦 仓库名称（例如：langchain-ai/langchain）")
            add_btn = gr.Button("➕ 添加订阅", variant="primary")
            del_btn = gr.Button("🗑️ 删除订阅", variant="secondary")

        status_output = gr.Textbox(label="状态反馈", interactive=False)

        add_btn.click(fn=add_subscription, inputs=repo_input, outputs=status_output)
        del_btn.click(fn=delete_subscription, inputs=repo_input, outputs=status_output)

    # 页面 tag 2   =============== 📈 GitHub 报告 TAB ===============
    with gr.Tab("📈 生成报告"):
        gr.Markdown("### 当前订阅 & 生成报告（在同一视图操作）")

        gr.Markdown("### 当前订阅与报告生成")
        with gr.Row():
            # 左侧：仓库选择 + days + 生成按钮
            with gr.Column(scale=1):
                repo_dropdown = gr.Dropdown(
                    choices=get_subscriptions(),
                    label="选择订阅仓库",
                    interactive=True
                )

                days_slider = gr.Slider(minimum=1, maximum=30, step=1, value=7, label="时间范围（天）")
                repo_info = gr.Textbox(label="仓库详情（提示词）", lines=5, interactive=False)
                repo_md = gr.Markdown("", elem_id="repo_info")
                repo_filepath = gr.State()
                gen_btn = gr.Button("🚀 生成报告", variant="primary")

                repo_dropdown.change(fn=get_project_info_on_git, inputs=[repo_dropdown, days_slider], outputs=[repo_info, repo_filepath])

            # 右侧报告区域（优化样式）
            with gr.Column(scale=2):
                report_title = gr.Textbox(
                    label="AI 分析结果",
                    lines=1,
                    interactive=False,
                    value=""
                )

                report_md = gr.Markdown("", elem_id="report_output")
                download_file = gr.File(label="下载报告")

            gen_btn.click(
                fn=generate_report,
                inputs=[repo_dropdown, days_slider, repo_filepath],
                outputs=[report_md, download_file]
            )

    # 页面 tag 3   =============== 📰 HackerNews 报告 TAB ===============
    with gr.Tab("📰 HackerNews 热点分析"):
        gr.Markdown("### 获取 HackerNews 热榜趋势并生成 AI 分析报告")
        with gr.Row():
            # 左侧参数区
            with gr.Column(scale=1):
                hn_days_slider = gr.Slider(
                    minimum=1,
                    maximum=7,
                    step=1,
                    value=2,
                    label="时间范围（天）"
                )
                # 生成 AI 报告按钮
                hn_gen_btn = gr.Button("🚀 获取并生成 HN 报告", variant="primary")

                # 存储生成的文件路径
                hn_filepath = gr.State()


            # 右侧 AI 报告区
            with gr.Column(scale=2):
                hn_report_title = gr.Textbox(
                    label="AI 分析结果",
                    lines=1,
                    interactive=False,
                    value=""
                )

                hn_report_md = gr.Markdown("", elem_id="hn_report_output")
                # hn_download = gr.File(label="下载报告")  # 暂不支持下载

            hn_gen_btn.click(
                fn=hackernews_generate_report,
                inputs=[hn_days_slider],
                outputs=[hn_report_md]
            )


    gr.Markdown(
        """
        ---
        👨‍💻 **作者**: Leon  
        🌟 项目地址: [GitHub Sentinel](https://github.com/leon1peng/my-github-sentinel)
        """
    )


if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860, share=False)
