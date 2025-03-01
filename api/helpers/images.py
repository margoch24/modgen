import random

import imagehash
import numpy as np
from PIL import Image
from skimage.metrics import structural_similarity as ssim

from config import DefaultConfig


def resize_image(image):
    width, height = image.size
    if width <= DefaultConfig.MAX_WIDTH:
        return image

    new_height = int((DefaultConfig.MAX_WIDTH / width) * height)
    return image.resize((DefaultConfig.MAX_WIDTH, new_height), Image.LANCZOS)


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


def compare_images(
    original_img, reversed_img, modified_img, hash_size=32, mse_threshold=1
):
    mse_modified = mse(original_img, modified_img)
    mse_reversed = mse(original_img, reversed_img)

    original_gray = original_img.convert("L")
    reversed_gray = reversed_img.convert("L")
    modified_gray = modified_img.convert("L")

    ssim_modified = ssim(np.array(original_gray), np.array(modified_gray))
    ssim_reversed = ssim(np.array(original_gray), np.array(reversed_gray))

    is_identical = mse_reversed < mse_threshold and ssim_reversed > 0.9999
    is_modified_identical = mse_modified < mse_threshold and ssim_modified > 0.9999

    return is_identical, is_modified_identical, ssim_modified, ssim_reversed
