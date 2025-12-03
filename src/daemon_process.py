import schedule # 导入 schedule 实现定时任务执行器
import time  # 导入time库，用于控制时间间隔
import signal  # 导入signal库，用于信号处理
import sys  # 导入sys库，用于执行系统相关的操作

from config import Config  # 导入配置管理类
from github_client import GitHubClient  # 导入GitHub客户端类，处理GitHub API请求
from notifier import Notifier  # 导入通知器类，用于发送通知
from report_generator import ReportGenerator  # 导入报告生成器类
from llm import LLM  # 导入语言模型类，可能用于生成报告内容
from subscription_manager import SubscriptionManager  # 导入订阅管理器类，管理GitHub仓库订阅
from logger import LOG  # 导入日志记录器
from hacker_news_client import HackerNewsClient


def graceful_shutdown(signum, frame):
    # 优雅关闭程序的函数，处理信号时调用
    LOG.info("[优雅退出]守护进程接收到终止信号")
    sys.exit(0)  # 安全退出程序

def github_job(subscription_manager, github_client, report_generator, notifier, days):
    LOG.info("[开始执行定时任务]")
    subscriptions = subscription_manager.list_subscriptions()  # 获取当前所有订阅
    LOG.info(f"订阅列表：{subscriptions}")
    for repo in subscriptions:
        # 遍历每个订阅的仓库，执行以下操作
        markdown_file_path = github_client.export_progress_by_date_range(repo, days)
        # 从Markdown文件自动生成进展简报
        report, report_file_path = report_generator.generate_report_by_date_range(markdown_file_path, days)
        notifier.notify(repo, report)
    LOG.info(f"[定时任务执行完毕]")


def hackernews_job(hackernews_client: HackerNewsClient, llm: LLM, notifier: Notifier=None):
    LOG.info("[Hacker News 开始执行定时任务]")
    top_stories = hackernews_client.fetch_hackernews_top_stories(120)
    report = llm.hackernews_report(top_stories)
    print(report)
    notifier.notify("Hacker News", report)


def main():
    # 设置信号处理器
    signal.signal(signal.SIGTERM, graceful_shutdown)

    config = Config()  # 创建配置实例
    github_client = GitHubClient(config.github_token)  # 创建GitHub客户端实例
    notifier = Notifier(config.email)  # 创建通知器实例
    llm = LLM()  # 创建语言模型实例
    report_generator = ReportGenerator(llm)  # 创建报告生成器实例
    subscription_manager = SubscriptionManager(config.subscriptions_file)  # 创建订阅管理器实例

    hackernews_client = HackerNewsClient()

    # 启动时立即执行（如不需要可注释）
    github_job(subscription_manager, github_client, report_generator, notifier, config.freq_days)

    # 安排每天的定时任务
    schedule.every(config.freq_days).days.at(
        config.exec_time
    ).do(github_job, subscription_manager, github_client, report_generator, notifier, config.freq_days)

    schedule.every(8).hours.do(hackernews_job, hackernews_client, llm)

    try:
        # 在守护进程中持续运行
        while True:
            schedule.run_pending()
            time.sleep(1)  # 短暂休眠以减少 CPU 使用
    except Exception as e:
        LOG.error(f"主进程发生异常: {str(e)}")
        sys.exit(1)



if __name__ == '__main__':
    main()
    # client = HackerNewsClient()
    # llm = LLM() 
    # hackernews_job(client, llm)
    """
    在Hacker News最新的技术洞察中，以下几个主题引起了广泛关注和讨论：

    1. **个人项目与创作**：许多开发者在“Ask HN”中分享了自己的项目，展示了社区在自我表达和创业方面的热情。个人创作的氛围表明，越来越多的开发者选择通过自己的项目来探索和实现想法。

    2. **网络安全思维转变**：关于防守者与攻击者思维的讨论显示出人们对网络安全的关注不断加深。开发者和企业都意识到，理解不同角色的思维方式是加强安全防护的关键。

    3. **神经科技**：随着神经科技的进步，投资者和开发者对这一领域的应用潜力表示了浓厚的兴趣，特别是在医疗和人类增强技术方面。

    4. **开源项目的崛起**：开源项目如Serpent OS和Jules引发了技术社区的瞩目，这表明开源软件在促进技术创新和协作方面的不可替代性日益显著。

    5. **Rust编程语言的应用**：Rust在社区中的讨论热度持续上升，尤其是在内存安全和性能优化方面，开发者对其越来越感兴趣，表明随着技术需求的变化，Rust的应用场景也在不断拓展。

    以上主题反映了技术快速发展的趋势，以及开发者社区在面对新挑战时的创新思维和解决方案。
    """
