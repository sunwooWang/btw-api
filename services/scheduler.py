import subprocess
import sys
import os
import logging
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

_scheduler = BackgroundScheduler(timezone="Asia/Seoul")


def _run(crawler_dir: str, script: str, label: str):
    print(f"[스케줄러] {label} 시작", flush=True)
    logger.info(f"[스케줄러] {label} 시작")
    venv_python = os.path.join(crawler_dir, "venv", "bin", "python3")
    python_exe = venv_python if os.path.isfile(venv_python) else sys.executable
    result = subprocess.run(
        [python_exe, script],
        cwd=crawler_dir,
        capture_output=True,
        text=True,
        timeout=600,
    )
    if result.returncode == 0:
        print(f"[스케줄러] {label} 완료", flush=True)
        logger.info(f"[스케줄러] {label} 완료")
    else:
        print(f"[스케줄러] {label} 오류\n{result.stderr}", flush=True)
        logger.error(f"[스케줄러] {label} 오류\n{result.stderr}")


def job_news():
    _run(os.environ.get("NEW_CRAWLER_DIR", ""), "main.py", "뉴스 크롤러")


def job_support():
    _run(os.environ.get("SUPPORT_CRAWLER_DIR", ""), "main.py", "지원사업 크롤러")


def start_scheduler():
    # [테스트] 2분마다 실행 — 확인 후 아래 CronTrigger로 교체
    _scheduler.add_job(job_news, IntervalTrigger(minutes=2), id="job_news")
    _scheduler.add_job(job_support, IntervalTrigger(minutes=2), id="job_support")
    # [운영] 아래 주석 해제 후 위 2줄 삭제
    # _scheduler.add_job(job_news, CronTrigger(day_of_week="mon-fri", hour=8, minute=0))
    # _scheduler.add_job(job_support, CronTrigger(hour=9, minute=0))
    _scheduler.start()
    print("[스케줄러] APScheduler 시작 완료", flush=True)
    logger.info("[스케줄러] APScheduler 시작 완료")
