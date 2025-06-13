#!/usr/bin/env python3
import os
import time
import uuid
import requests
import csv
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

# === CONFIGURATION ===
API_BASE = "https://dashscope-intl.aliyuncs.com"
SECRET_KEY = os.getenv("ALIYUN_VIDEO_API") 
# If you need a cookie header, set COOKIE_HEADER too, otherwise comment out:
#COOKIE_HEADER = os.getenv("COOKIE_HEADER", None)

HEADERS = {
    "Authorization": f"Bearer {SECRET_KEY}",
    "Content-Type": "application/json",
    "X-DashScope-Async": "enable",
}
# if COOKIE_HEADER:
#     HEADERS["Cookie"] = COOKIE_HEADER

MODELS = ["wan2.1-t2v-turbo", "wan2.1-t2v-plus"]
SIZE = "720*1280"
DURATION = "5"

BASE_DIR = Path(__file__).resolve().parent
MAPPING_CSV = BASE_DIR / "prompt_video_mapping.csv"
PROMPTS_FILE = BASE_DIR / "prompts.txt"
VIDEOS_DIR = BASE_DIR / "videos"
# === HELPER FUNCTIONS ===

def submit_task(model: str, prompt: str) -> str:
    """Submit a video-synthesis task; return the task_id."""
    payload = {
        "model": model,
        "input": {"prompt": prompt},
        "parameters": {
            "size": SIZE
        }
    }
    resp = requests.post(
        f"{API_BASE}/api/v1/services/aigc/video-generation/video-synthesis",
        headers=HEADERS,
        json=payload,
    )
    resp.raise_for_status()
    data = resp.json()
    task_id = data["output"]["task_id"]
    print(f"[{model}] submitted, task_id={task_id}")
    return task_id

def wait_for_completion(task_id: str, poll_interval: int = 20, timeout: int = 600) -> dict:
    """
    Poll the GET /tasks/{task_id} endpoint until status is SUCCEEDED (or fail/timeout).
    Returns the full JSON response when done.
    """
    url = f"{API_BASE}/api/v1/tasks/{task_id}"
    elapsed = 0
    while elapsed < timeout:
        resp = requests.get(url, headers={"Authorization": f"Bearer {SECRET_KEY}"})
        resp.raise_for_status()
        data = resp.json()
        status = data["output"]["task_status"]
        print(f"  → status={status} (elapsed {elapsed}s)")
        if status == "SUCCEEDED":
            return data
        elif status in ("FAILED", "CANCELLED"):
            raise RuntimeError(f"Task {task_id} ended with status {status}")
        time.sleep(poll_interval)
        elapsed += poll_interval
    raise TimeoutError(f"Task {task_id} did not complete within {timeout}s")

def download_video(model: str, task_id: str, video_url: str) -> str:
    """Download the MP4 and save it under videos/{uuid4}.mp4."""
    os.makedirs(VIDEOS_DIR, exist_ok=True)
    filename = f"{model}_{task_id}.mp4"
    local_filename = os.path.join(VIDEOS_DIR, filename)
    with requests.get(video_url, stream=True) as r:
        r.raise_for_status()
        with open(local_filename, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
    print(f"  → downloaded to {local_filename}")
    return local_filename

def record_mapping(model: str, task_id: str, prompt: str, filepath: str):
    """
    Append a row to MAPPING_CSV mapping this prompt to the downloaded file.
    """
    header = ["model", "task_id", "prompt", "filename"]
    write_header = not os.path.exists(MAPPING_CSV)
    with open(MAPPING_CSV, mode="a", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        if write_header:
            writer.writerow(header)
        writer.writerow([model, task_id, prompt, filepath])

# === MAIN LOOP ===

def main():
    # Load prompts
    with open(PROMPTS_FILE, "r", encoding="utf-8") as f:
        prompts = [line.strip() for line in f if line.strip()]

    for idx, prompt in enumerate(prompts, start=1):
        print(f"\n=== Prompt #{idx} ===")
        print(prompt)
        for model in MODELS:
            # 1) Submit
            task_id = submit_task(model, prompt)

            # 2) Wait ~2 minutes before polling (as you requested)
            if model == "wan2.1-t2v-plus":
                print("Waiting 2 minutes before polling...")
                time.sleep(120)

            # 3) Poll until done
            result = wait_for_completion(task_id)

            # 4) Download
            video_url = result["output"]["video_url"]
            local_filename = download_video(model, task_id, video_url)

            # 5) Record prompt ↔ filename mapping
            record_mapping(model, task_id, prompt, local_filename)

if __name__ == "__main__":
    main()
