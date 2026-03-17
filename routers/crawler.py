import subprocess
import sys
import os
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

router = APIRouter()


def _run_crawler(crawler_dir: str, script: str) -> dict:
    """주어진 디렉토리에서 Python 스크립트를 실행하고 결과를 반환한다."""
    if not os.path.isdir(crawler_dir):
        raise HTTPException(status_code=500, detail=f"크롤러 디렉토리를 찾을 수 없음: {crawler_dir}")

    script_path = os.path.join(crawler_dir, script)
    if not os.path.isfile(script_path):
        raise HTTPException(status_code=500, detail=f"스크립트를 찾을 수 없음: {script_path}")

    # 크롤러 디렉토리의 venv python 우선 사용, 없으면 현재 인터프리터 사용
    venv_python = os.path.join(crawler_dir, "venv", "bin", "python3")
    python_exe = venv_python if os.path.isfile(venv_python) else sys.executable

    result = subprocess.run(
        [python_exe, script],
        cwd=crawler_dir,
        capture_output=True,
        text=True,
        timeout=600,
    )
    return {
        "returncode": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr,
    }


@router.post("/news/run")
def run_news_crawler():
    """뉴스 크롤러(new_crawler) 수동 실행"""
    crawler_dir = os.environ.get("NEW_CRAWLER_DIR", "")
    output = _run_crawler(crawler_dir, "main.py")
    if output["returncode"] != 0:
        return JSONResponse(status_code=500, content={"status": "error", **output})
    return {"status": "ok", **output}


@router.post("/support/run")
def run_support_crawler():
    """지원사업 크롤러(support_bussiness_crawler) 수동 실행"""
    crawler_dir = os.environ.get("SUPPORT_CRAWLER_DIR", "")
    output = _run_crawler(crawler_dir, "main.py")
    if output["returncode"] != 0:
        return JSONResponse(status_code=500, content={"status": "error", **output})
    return {"status": "ok", **output}


@router.post("/ranking/run")
def run_ranking_crawler():
    """랭킹 크롤러(ranking_crawler) 수동 실행"""
    crawler_dir = os.environ.get("RANKING_CRAWLER_DIR", "")
    output = _run_crawler(crawler_dir, "main.py")
    if output["returncode"] != 0:
        return JSONResponse(status_code=500, content={"status": "error", **output})
    return {"status": "ok", **output}
