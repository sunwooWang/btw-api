import subprocess
import sys
import os
import logging
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

logger = logging.getLogger(__name__)

_scheduler = BackgroundScheduler(timezone="Asia/Seoul")


def _run(crawler_dir: str, script: str, label: str):
    script_path = os.path.join(crawler_dir, script)
    logger.info(f"[스케줄러] {label} 시작")
    result = subprocess.run(
        [sys.executable, script],
        cwd=crawler_dir,
        capture_output=True,
        text=True,
        timeout=600,
    )
    if result.returncode == 0:
        logger.info(f"[스케줄러] {label} 완료")
    else:
        logger.error(f"[스케줄러] {label} 오류\n{result.stderr}")


def job_news():
    _run(os.environ.get("NEW_CRAWLER_DIR", ""), "main.py", "뉴스 크롤러")


def job_support():
    _run(os.environ.get("SUPPORT_CRAWLER_DIR", ""), "main.py", "지원사업 크롤러")


def job_ranking():
    _run(os.environ.get("RANKING_CRAWLER_DIR", ""), "main.py", "랭킹 크롤러")


def start_scheduler():
    # 뉴스 크롤러: 평일 오전 8시
    _scheduler.add_job(job_news, CronTrigger(day_of_week="mon-fri", hour=8, minute=0))
    # 지원사업 크롤러: 매일 오전 9시
    _scheduler.add_job(job_support, CronTrigger(hour=9, minute=0))
    # 랭킹 크롤러: 매일 오전 6시
    _scheduler.add_job(job_ranking, CronTrigger(hour=6, minute=0))

    _scheduler.start()
    logger.info("[스케줄러] APScheduler 시작 완료")
