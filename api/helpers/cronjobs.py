import os
import shutil

from api.app_scheduler import AppScheduler
from api.constants import Environment
from config import DefaultConfig


def delete_files():
    print("started cronjob")
    current_dir = os.path.dirname(os.path.abspath(__file__))
    uploads_dir = os.path.join(current_dir, "../../uploads/")
    print(current_dir, uploads_dir)

    if not os.path.exists(uploads_dir):
        return

    files = os.listdir(uploads_dir)

    if not files:
        print("no files found")
        return

    for filename in files:
        file_path = os.path.join(uploads_dir, filename)
        try:
            os.unlink(file_path)
            print(f"Success to delete {file_path}")
        except Exception as e:
            print(f"Failed to delete {file_path}: {e}")


def set_cronjobs(app_context):
    if DefaultConfig.ENV == Environment.TEST:
        return

    scheduler = AppScheduler(app_context)

    scheduler.add_job(
        delete_files,
        trigger="interval",
        minutes=10,
        job_id="delete_files",
    )

    scheduler.initiate()
