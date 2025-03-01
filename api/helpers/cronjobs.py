import os
import shutil

from api.app_scheduler import AppScheduler
from api.constants import Environment
from config import DefaultConfig


def list_directory_structure(start_path, indent_level=0):
    try:
        # List all entries in the given directory
        entries = os.listdir(start_path)
        # Indent for better readability
        indent = " " * (indent_level * 4)

        for entry in entries:
            # Skip directories that start with '__'
            if (
                entry.startswith("_")
                or entry.startswith("tests")
                or entry.startswith("xsf")
                or entry.startswith("flask")
            ):
                continue

            full_path = os.path.join(start_path, entry)
            print(f"{indent}- {entry}")  # Print the entry name
            if os.path.isdir(full_path):  # Check if it's a directory
                # Recursively list the directory contents
                list_directory_structure(full_path, indent_level + 1)
    except Exception as e:
        print(f"Error accessing {start_path}: {e}")


def delete_files():
    print("started cronjob")
    current_dir = os.path.dirname(os.path.abspath(__file__))
    uploads_dir = os.path.join(current_dir, "../../uploads/")
    print(current_dir, uploads_dir)

    print(os.path.exists(uploads_dir))
    list_directory_structure(os.path.join(current_dir, "../../"))

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
