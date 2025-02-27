import random

import imagehash
import numpy as np
from PIL import Image

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


def compare_images(
    original_img,
    reversed_img,
    modified_img,
    hash_size=32,
    mse_threshold=500,
):
    hash1 = imagehash.whash(original_img, hash_size=hash_size)
    hash2 = imagehash.whash(modified_img, hash_size=hash_size)
    hash3 = imagehash.whash(reversed_img, hash_size=hash_size)

    modified_hamming_distance = hash1 - hash2
    hamming_distance = hash1 - hash3

    is_identical = hamming_distance == 0
    is_modified_identical = modified_hamming_distance == 0

    return is_identical, is_modified_identical
