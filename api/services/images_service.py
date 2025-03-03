import os
import time

from PIL import Image
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename

from api.constants import VerificationStatus
from api.helpers.helper import get_random
from api.helpers.images import (
    allowed_file,
    apply_random_modifications,
    compare_images,
    reverse_random_modifications,
)
from api.models import Modification
from config import DefaultConfig


class ImagesService:

    def modify_image(file: FileStorage):
        return modify_image(file)

    def verify_image(modification_id: str):
        return verify_image(modification_id)


def print_elapsed_time(start_time, label):
    print(f"{label}: {(time.time() - start_time) * 1000:.2f} ms")


def modify_image(file: FileStorage):
    start_time = time.time()
    print("start")

    if file.filename == "":
        return {"error": 1, "data": {"message": "No selected file"}}, 400

    if not allowed_file(file.filename):
        return {"error": 1, "data": {"message": "Invalid file type"}}, 400

    try:
        print_elapsed_time(start_time, "file validation")

        # Ensure upload directory exists
        current_dir = os.path.dirname(os.path.abspath(__file__))
        uploads_dir = os.path.join(current_dir, f"../../{DefaultConfig.UPLOAD_FOLDER}/")

        os.makedirs(uploads_dir, exist_ok=True)
        print_elapsed_time(start_time, "ensure upload dir")

        # Secure filename
        filename_base = secure_filename(file.filename).rsplit(".", 1)[0]
        unique_id = get_random(100000)
        original_filename = f"{unique_id}_{filename_base}.bmp"
        modified_filename = f"modified_{original_filename}"

        original_img_path = os.path.join(uploads_dir, original_filename)
        modified_img_path = os.path.join(uploads_dir, modified_filename)

        # Load image in memory & convert immediately
        original_img = Image.open(file.stream).convert("RGB")
        print_elapsed_time(start_time, "open & convert image")

        # Save original image efficiently
        original_img.save(original_img_path, format="BMP", optimize=True)
        print_elapsed_time(start_time, "save original image")

        # Apply modifications using optimized method
        modified_img, modifications = apply_random_modifications(original_img)
        print_elapsed_time(start_time, "apply modifications")

        # Save modified image efficiently
        modified_img.save(modified_img_path, format="BMP", optimize=True)
        print_elapsed_time(start_time, "save modified image")

        # Save modification metadata
        # modification = Modification.create(
        #     original_path=original_filename,
        #     modified_path=modified_filename,
        #     modification_data=modifications,
        #     verification_status=VerificationStatus.Pending,
        # )
        print_elapsed_time(start_time, "save modification record")

        response = {
            "error": 0,
            "data": {
                "original_filename": original_filename,
                "modified_filename": modified_filename,
                # "modification_id": modification.id,
            },
        }
        return response, 200

    except Exception as e:
        print(f"ERROR (modify_image): {e}")

        response = {"error": 1, "data": {"message": "Internal server error"}}
        return response, 500


def verify_image(modification_id: str):
    try:
        modification = Modification.find_one({"id": modification_id})

        if not modification:
            response = {
                "error": 0,
                "data": None,
            }
            return response, 200

        if modification.reversed_path:
            response = {
                "error": 1,
                "data": {
                    "message": f"File is already verified with status: {modification.verification_status}"
                },
            }
            return response, 400

        current_dir = os.path.dirname(os.path.abspath(__file__))
        uploads_dir = os.path.join(current_dir, f"../../{DefaultConfig.UPLOAD_FOLDER}/")
        if not os.path.exists(uploads_dir):
            os.makedirs(uploads_dir)

        modified_image_path = os.path.join(uploads_dir, modification.modified_path)
        original_image_path = os.path.join(uploads_dir, modification.original_path)
        modifications = modification.modification_data

        original_img = Image.open(original_image_path)
        modified_img = Image.open(modified_image_path)

        reversed_img = reverse_random_modifications(modified_img, modifications)

        reversed_filename = f"reversed_{modification.original_path}"
        reversed_image_path = os.path.join(uploads_dir, reversed_filename)
        reversed_img.save(reversed_image_path)

        is_identical, is_modified_identical, ssim_modified, ssim_reversed = (
            compare_images(original_img, reversed_img, modified_img)
        )

        status = (
            VerificationStatus.Success
            if is_identical and not is_modified_identical
            else VerificationStatus.Fail
        )

        Modification.update_one(
            modification.id, reversed_path=reversed_filename, verification_status=status
        )

        response = {
            "error": 0,
            "data": {
                "reversed_filename": reversed_filename,
                "status": status,
                "modified_status": str(is_modified_identical),
                "ssim_modified": ssim_modified,
                "ssim_reversed": ssim_reversed,
            },
        }

        return response, 200
    except Exception as e:
        print(f"ERROR (verify_image): {e}")

        response = {"error": 1, "data": {"message": "Internal server error"}}
        return response, 500
