import random
import time
from concurrent.futures import ThreadPoolExecutor

import imagehash
import numpy as np
from PIL import Image
from skimage.metrics import structural_similarity as ssim

from config import DefaultConfig


def allowed_file(filename: str):
    if "." not in filename:
        return False

    [_, file_extension] = filename.split(".")
    return file_extension.lower() in DefaultConfig.ALLOWED_EXTENSIONS


def apply_random_modifications(img, num_mods=100):
    img_array = np.array(img)
    height, width, _ = img_array.shape
    modifications = []

    for _ in range(num_mods):
        mod_type = random.choice(["invert", "swap"])

        if mod_type == "swap":
            y1, x1 = random.randint(0, height - 1), random.randint(0, width - 1)
            y2, x2 = random.randint(0, height - 1), random.randint(0, width - 1)

            original_pixel1 = img_array[y1, x1].copy()
            original_pixel2 = img_array[y2, x2].copy()

            img_array[y1, x1], img_array[y2, x2] = original_pixel2, original_pixel1
            modifications.append(
                (
                    "swap",
                    (
                        y1,
                        x1,
                        y2,
                        x2,
                        original_pixel1.tolist(),
                        original_pixel2.tolist(),
                    ),
                )
            )

        elif mod_type == "invert":
            y, x = random.randint(0, height - 1), random.randint(0, width - 1)
            img_array[y, x] = 255 - img_array[y, x]
            modifications.append(("invert", (y, x)))

    modified_img = Image.fromarray(img_array)
    return modified_img, modifications


def reverse_random_modifications(img, modifications):
    img_array = np.array(img)

    for mod in reversed(modifications):
        mod_type, params = mod

        if mod_type == "swap":
            y1, x1, y2, x2, original_pixel1, original_pixel2 = params
            img_array[y1, x1], img_array[y2, x2] = np.array(
                original_pixel1, dtype=np.uint8
            ), np.array(original_pixel2, dtype=np.uint8)

        elif mod_type == "invert":
            y, x = params
            img_array[y, x] = 255 - img_array[y, x]

    return Image.fromarray(img_array)


def mse(imageA, imageB):
    err = np.sum(
        (np.array(imageA, dtype="float") - np.array(imageB, dtype="float")) ** 2
    )
    err /= float(imageA.size[0] * imageA.size[1])
    return err


def resize_image(img, size=(256, 256)):
    """Resize image to a smaller size to speed up SSIM calculation."""
    return img.resize(size, Image.LANCZOS)


def print_elapsed_time(start_time, label):
    elapsed_time = (time.time() - start_time) * 1000  # Convert to milliseconds
    print(f"{label}: {elapsed_time:.2f} ms")


def compare_images(
    original_img, reversed_img, modified_img, hash_size=32, mse_threshold=1
):
    start_time = time.time()
    print("start")

    # Resize images before processing
    original_gray = resize_image(original_img.convert("L"))
    reversed_gray = resize_image(reversed_img.convert("L"))
    modified_gray = resize_image(modified_img.convert("L"))
    print_elapsed_time(start_time, "Gray conversion & resize")

    # Convert to NumPy arrays efficiently
    original_gray_np = np.asarray(original_gray, dtype=np.uint8)
    reversed_gray_np = np.asarray(reversed_gray, dtype=np.uint8)
    modified_gray_np = np.asarray(modified_gray, dtype=np.uint8)
    print_elapsed_time(start_time, "NumPy conversion")

    # Compute SSIM in parallel to speed up processing
    with ThreadPoolExecutor() as executor:
        ssim_modified_future = executor.submit(
            ssim, original_gray_np, modified_gray_np, data_range=255
        )
        ssim_reversed_future = executor.submit(
            ssim, original_gray_np, reversed_gray_np, data_range=255
        )

        ssim_modified = ssim_modified_future.result()
        ssim_reversed = ssim_reversed_future.result()

    print_elapsed_time(start_time, "SSIM calculations")

    # Determine if images are identical based on SSIM
    is_identical = ssim_reversed > 0.9999
    is_modified_identical = ssim_modified > 0.9999
    print_elapsed_time(start_time, "Final comparison")

    return is_identical, is_modified_identical, ssim_modified, ssim_reversed
