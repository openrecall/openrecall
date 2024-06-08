import os
import time

import mss
import numpy as np
from PIL import Image

from openrecall.config import db_path, screenshots_path
from openrecall.ocr import extract_text_from_image
from openrecall.utils import (
    get_active_app_name,
    get_active_window_title
)
from openrecall.nlp import get_embedding
from openrecall.database import insert_entry

def mean_structured_similarity_index(img1, img2, L=255):
    K1, K2 = 0.01, 0.03
    C1, C2 = (K1 * L) ** 2, (K2 * L) ** 2

    def rgb2gray(img):
        return 0.2989 * img[..., 0] + 0.5870 * img[..., 1] + 0.1140 * img[..., 2]

    img1_gray = rgb2gray(img1)
    img2_gray = rgb2gray(img2)
    mu1 = np.mean(img1_gray)
    mu2 = np.mean(img2_gray)
    sigma1_sq = np.var(img1_gray)
    sigma2_sq = np.var(img2_gray)
    sigma12 = np.mean((img1_gray - mu1) * (img2_gray - mu2))
    ssim_index = ((2 * mu1 * mu2 + C1) * (2 * sigma12 + C2)) / (
        (mu1**2 + mu2**2 + C1) * (sigma1_sq + sigma2_sq + C2)
    )
    return ssim_index


def is_similar(img1, img2, similarity_threshold=0.9):
    similarity = mean_structured_similarity_index(img1, img2)
    return similarity >= similarity_threshold


def take_screenshots(monitor=1):
    screenshots = []
    with mss.mss() as sct:
        for monitor in range(len(sct.monitors)):
            monitor_ = sct.monitors[monitor]
            screenshot = np.array(sct.grab(monitor_))
            screenshot = screenshot[:, :, [2, 1, 0]]
            screenshots.append(screenshot)
    return screenshots


def record_screenshots_thread():
    last_screenshots = take_screenshots()
    while True:
        screenshots = take_screenshots()
        for i, screenshot in enumerate(screenshots):
            last_screenshot = last_screenshots[i]
            if not is_similar(screenshot, last_screenshot):
                last_screenshots[i] = screenshot
                image = Image.fromarray(screenshot)
                timestamp = int(time.time())
                image.save(
                    os.path.join(screenshots_path, f"{timestamp}.webp"),
                    format="webp",
                    lossless=True,
                )
                text = extract_text_from_image(screenshot)
                embedding = get_embedding(text)
                active_app_name = get_active_app_name()
                active_window_title = get_active_window_title()
                insert_entry(text, timestamp, embedding, active_app_name, active_window_title)
        time.sleep(3)
