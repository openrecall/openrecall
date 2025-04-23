import os
import time
from typing import List, Tuple

import mss
import numpy as np
from PIL import Image

from openrecall.config import screenshots_path, args
from openrecall.database import insert_entry
from openrecall.nlp import get_embedding
from openrecall.ocr import extract_text_from_image
from openrecall.utils import (
    get_active_app_name,
    get_active_window_title,
    is_user_active,
)


def mean_structured_similarity_index(
    img1: np.ndarray, img2: np.ndarray, L: int = 255
) -> float:
    """Calculates the Mean Structural Similarity Index (MSSIM) between two images.

    Args:
        img1: The first image as a NumPy array (RGB).
        img2: The second image as a NumPy array (RGB).
        L: The dynamic range of the pixel values (default is 255).

    Returns:
        The MSSIM value between the two images (float between -1 and 1).
    """
    K1, K2 = 0.01, 0.03
    C1, C2 = (K1 * L) ** 2, (K2 * L) ** 2

    def rgb2gray(img: np.ndarray) -> np.ndarray:
        """Converts an RGB image to grayscale."""
        return 0.2989 * img[..., 0] + 0.5870 * img[..., 1] + 0.1140 * img[..., 2]

    img1_gray: np.ndarray = rgb2gray(img1)
    img2_gray: np.ndarray = rgb2gray(img2)
    mu1: float = np.mean(img1_gray)
    mu2: float = np.mean(img2_gray)
    sigma1_sq = np.var(img1_gray)
    sigma2_sq = np.var(img2_gray)
    sigma12 = np.mean((img1_gray - mu1) * (img2_gray - mu2))
    ssim_index = ((2 * mu1 * mu2 + C1) * (2 * sigma12 + C2)) / (
        (mu1**2 + mu2**2 + C1) * (sigma1_sq + sigma2_sq + C2)
    )
    return ssim_index


def is_similar(
    img1: np.ndarray, img2: np.ndarray, similarity_threshold: float = 0.9
) -> bool:
    """Checks if two images are similar based on MSSIM.

    Args:
        img1: The first image as a NumPy array.
        img2: The second image as a NumPy array.
        similarity_threshold: The threshold above which images are considered similar.

    Returns:
        True if the images are similar, False otherwise.
    """
    similarity: float = mean_structured_similarity_index(img1, img2)
    return similarity >= similarity_threshold


def take_screenshots() -> List[np.ndarray]:
    """Takes screenshots of all connected monitors or just the primary one.

    Depending on the `args.primary_monitor_only` flag, captures either
    all monitors or only the primary monitor (index 1 in mss.monitors).

    Returns:
        A list of screenshots, where each screenshot is a NumPy array (RGB).
    """
    screenshots: List[np.ndarray] = []
    with mss.mss() as sct:
        # sct.monitors[0] is the combined view of all monitors
        # sct.monitors[1] is the primary monitor
        # sct.monitors[2:] are other monitors
        monitor_indices = range(1, len(sct.monitors))  # Skip the 'all monitors' entry

        if args.primary_monitor_only:
            monitor_indices = [1]  # Only index 1 corresponds to the primary monitor

        for i in monitor_indices:
            # Ensure the index is valid before attempting to grab
            if i < len(sct.monitors):
                monitor_info = sct.monitors[i]
                # Grab the screen
                sct_img = sct.grab(monitor_info)
                # Convert to numpy array and change BGRA to RGB
                screenshot = np.array(sct_img)[:, :, [2, 1, 0]]
                screenshots.append(screenshot)
            else:
                # Handle case where primary_monitor_only is True but only one monitor exists (all monitors view)
                # This case might need specific handling depending on desired behavior.
                # For now, we just skip if the index is out of bounds.
                print(f"Warning: Monitor index {i} out of bounds. Skipping.")

    return screenshots


def record_screenshots_thread() -> None:
    """
    Continuously records screenshots, processes them, and stores relevant data.

    Checks for user activity and image similarity before processing and saving
    screenshots, associated OCR text, embeddings, and active application info.
    Runs in an infinite loop, intended to be executed in a separate thread.
    """
    # TODO: Move this environment variable setting to the application's entry point.
    # HACK: Prevents a warning/error from the huggingface/tokenizers library
    # when used in environments where multiprocessing fork safety is a concern.
    os.environ["TOKENIZERS_PARALLELISM"] = "false"

    last_screenshots: List[np.ndarray] = take_screenshots()

    while True:
        if not is_user_active():
            time.sleep(3)  # Wait longer if user is inactive
            continue

        current_screenshots: List[np.ndarray] = take_screenshots()

        # Ensure we have a last_screenshot for each current_screenshot
        # This handles cases where monitor setup might change (though unlikely mid-run)
        if len(last_screenshots) != len(current_screenshots):
             # If monitor count changes, reset last_screenshots and continue
             last_screenshots = current_screenshots
             time.sleep(3)
             continue


        for i, current_screenshot in enumerate(current_screenshots):
            last_screenshot = last_screenshots[i]

            if not is_similar(current_screenshot, last_screenshot):
                last_screenshots[i] = current_screenshot  # Update the last screenshot for this monitor
                image = Image.fromarray(current_screenshot)
                timestamp = int(time.time())
                filename = f"{timestamp}_{i}.webp" # Add monitor index to filename for uniqueness
                filepath = os.path.join(screenshots_path, filename)
                image.save(
                    filepath,
                    format="webp",
                    lossless=True,
                )
                text: str = extract_text_from_image(current_screenshot)
                # Only proceed if OCR actually extracts text
                if text.strip():
                    embedding: np.ndarray = get_embedding(text)
                    active_app_name: str = get_active_app_name() or "Unknown App"
                    active_window_title: str = get_active_window_title() or "Unknown Title"
                    insert_entry(
                        text, timestamp, embedding, active_app_name, active_window_title, filename # Pass filename
                    )

        time.sleep(3) # Wait before taking the next screenshot

    return screenshots


def record_screenshots_thread():
    # TODO: fix the error from huggingface tokenizers
    import os

    os.environ["TOKENIZERS_PARALLELISM"] = "false"

    last_screenshots = take_screenshots()

    while True:
        if not is_user_active():
            time.sleep(3)
            continue

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
                text: str = extract_text_from_image(current_screenshot)
                # Only proceed if OCR actually extracts text
                if text.strip():
                    embedding: np.ndarray = get_embedding(text)
                    active_app_name: str = get_active_app_name() or "Unknown App"
                    active_window_title: str = get_active_window_title() or "Unknown Title"
                    insert_entry(
                        text, timestamp, embedding, active_app_name, active_window_title, filename # Pass filename
                    )

        time.sleep(3) # Wait before taking the next screenshot
