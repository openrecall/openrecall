import os
import sqlite3
import sys
import threading
import time

import mss
import numpy as np
from doctr.models import ocr_predictor
from flask import Flask, render_template_string, request, send_from_directory
from PIL import Image
from sentence_transformers import SentenceTransformer


def get_appdata_folder(app_name="openrecall"):
    """
    Get the path to the application data folder.

    Args:
        app_name (str): The name of the application.

    Returns:
        str: The path to the application data folder.
    """
    if sys.platform == "win32":
        appdata = os.getenv("APPDATA")
        if not appdata:
            raise EnvironmentError("APPDATA environment variable is not set.")
        path = os.path.join(appdata, app_name)
    elif sys.platform == "darwin":
        home = os.path.expanduser("~")
        path = os.path.join(home, "Library", "Application Support", app_name)
    else:  # Linux and other Unix-like systems
        home = os.path.expanduser("~")
        path = os.path.join(home, ".local", "share", app_name)

    if not os.path.exists(path):
        os.makedirs(path)

    return path


appdata_folder = get_appdata_folder()

print(f"All data is stored in: {appdata_folder}")

db_path = os.path.join(appdata_folder, "recall.db")

screenshots_path = os.path.join(appdata_folder, "screenshots")

# ensure the screenshots folder exists
if not os.path.exists(screenshots_path):
    try:
        os.makedirs(screenshots_path)
    except:
        pass


def get_active_app_name_osx():
    """Returns the name of the active application."""
    from AppKit import NSWorkspace

    active_app = NSWorkspace.sharedWorkspace().activeApplication()
    return active_app["NSApplicationName"]


def get_active_window_title_osx():
    """Returns the title of the active window."""
    from Quartz import (
        CGWindowListCopyWindowInfo,
        kCGNullWindowID,
        kCGWindowListOptionOnScreenOnly,
    )

    app_name = get_active_app_name_osx()
    windows = CGWindowListCopyWindowInfo(
        kCGWindowListOptionOnScreenOnly, kCGNullWindowID
    )

    for window in windows:
        if window["kCGWindowOwnerName"] == app_name:
            return window.get("kCGWindowName", "Unknown")

    return None


def get_active_app_name_windows():
    """returns the app's name .exe"""
    import psutil
    import win32gui
    import win32process

    # Get the handle of the foreground window
    hwnd = win32gui.GetForegroundWindow()
    
    # Get the thread process ID of the foreground window
    _, pid = win32process.GetWindowThreadProcessId(hwnd)
    
    # Get the process name using psutil
    exe = psutil.Process(pid).name()
    return exe


def get_active_window_title_windows():
    """Returns the title of the active window."""
    import win32gui

    hwnd = win32gui.GetForegroundWindow()
    window_title = win32gui.GetWindowText(hwnd)
    return window_title


def get_active_app_name():
    if sys.platform == "win32":
        return get_active_app_name_windows()
    elif sys.platform == "darwin":
        return get_active_app_name_osx()
    else:
        raise NotImplementedError("This platform is not supported")


def get_active_window_title():
    if sys.platform == "win32":
        return get_active_window_title_windows()
    elif sys.platform == "darwin":
        return get_active_window_title_osx()
    else:
        raise NotImplementedError("This platform is not supported")


def create_db():
    # create table if not exists for entries, with columns id, text, datetime, and embedding (blob)
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute(
        """CREATE TABLE IF NOT EXISTS entries
                    (id INTEGER PRIMARY KEY AUTOINCREMENT, app TEXT, title TEXT, text TEXT, timestamp INTEGER, embedding BLOB)"""
    )
    conn.commit()
    conn.close()


def get_embedding(text):
    # Initialize the model
    model = SentenceTransformer("all-MiniLM-L6-v2")

    # Split text into sentences
    sentences = text.split("\n")

    # Get sentence embeddings
    sentence_embeddings = model.encode(sentences)

    # Aggregate embeddings (mean pooling in this example)
    mean = np.mean(sentence_embeddings, axis=0)
    # convert to float64
    mean = mean.astype(np.float64)
    return mean


ocr = ocr_predictor(
    pretrained=True,
    det_arch="db_mobilenet_v3_large",
    reco_arch="crnn_mobilenet_v3_large",
)


def take_screenshot(monitor=1):
    """
    Take a screenshot of the specified monitor.

    Args:
        monitor (int): The index of the monitor to capture the screenshot from.

    Returns:
        numpy.ndarray: The screenshot image as a numpy array.
    """
    with mss.mss() as sct:
        monitor_ = sct.monitors[monitor]
        screenshot = np.array(sct.grab(monitor_))
        screenshot = screenshot[:, :, [2, 1, 0]]
        return screenshot

def record_screenshot_thread():
    """
    Thread function to continuously record screenshots and process them.

    This function takes screenshots at regular intervals and compares them with the previous screenshot.
    If the new screenshot is different enough from the previous one, it saves the screenshot, performs OCR on it,
    extracts the text, computes the embedding, and stores the entry in the database.

    Returns:
        None
    """
    last_screenshot = take_screenshot()

    while True:
        screenshot = take_screenshot()

        if not is_similar(screenshot, last_screenshot):
            last_screenshot = screenshot
            image = Image.fromarray(screenshot)
            timestamp = int(time.time())
            image.save(
                os.path.join(screenshots_path, f"{timestamp}.webp"),
                format="webp",
                lossless=True,
            )
            result = ocr([screenshot])
            text = ""

            for page in result.pages:
                for block in page.blocks:
                    for line in block.lines:
                        for word in line.words:
                            text += word.value + " "
                        text += "\n"
                    text += "\n"

            embedding = get_embedding(text)
            active_app_name = get_active_app_name()
            active_window_title = get_active_window_title()

            # connect to db
            conn = sqlite3.connect(db_path)
            c = conn.cursor()

            # Insert the entry into the database
            embedding_bytes = embedding.tobytes()
            c.execute(
                "INSERT INTO entries (text, timestamp, embedding, app, title) VALUES (?, ?, ?, ?, ?)",
                (
                    text,
                    timestamp,
                    embedding_bytes,
                    active_app_name,
                    active_window_title,
                ),
            )

            # Commit the transaction
            conn.commit()
            conn.close()

        time.sleep(3)


def mean_structured_similarity_index(img1, img2, L=255):
    """Compute the mean Structural Similarity Index between two images."""
    K1, K2 = 0.01, 0.03
    C1, C2 = (K1 * L) ** 2, (K2 * L) ** 2

    # Convert images to grayscale
    def rgb2gray(img):
        return 0.2989 * img[..., 0] + 0.5870 * img[..., 1] + 0.1140 * img[..., 2]

    img1_gray = rgb2gray(img1)
    img2_gray = rgb2gray(img2)

    # Means
    mu1 = np.mean(img1_gray)
    mu2 = np.mean(img2_gray)

    # Variances and covariances
    sigma1_sq = np.var(img1_gray)
    sigma2_sq = np.var(img2_gray)
    sigma12 = np.mean((img1_gray - mu1) * (img2_gray - mu2))

    # SSIM computation
    ssim_index = ((2 * mu1 * mu2 + C1) * (2 * sigma12 + C2)) / (
        (mu1**2 + mu2**2 + C1) * (sigma1_sq + sigma2_sq + C2)
    )

    return ssim_index


def is_similar(img1, img2, similarity_threshold=0.9):
    """Check if two images are similar based on a given similarity threshold."""
    similarity = mean_structured_similarity_index(img1, img2)
    return similarity >= similarity_threshold


def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))


app = Flask(__name__)


def human_readable_time(timestamp):
    import datetime

    now = datetime.datetime.now()
    dt_object = datetime.datetime.fromtimestamp(timestamp)

    diff = now - dt_object

    if diff.days > 0:
        return f"{diff.days} days ago"
    elif diff.seconds < 60:
        return f"{diff.seconds} seconds ago"
    elif diff.seconds < 3600:
        return f"{diff.seconds // 60} minutes ago"
    else:
        return f"{diff.seconds // 3600} hours ago"


def timestamp_to_human_readable(timestamp):
    import datetime
    try:
        dt_object = datetime.datetime.fromtimestamp(timestamp)
        return dt_object.strftime("%Y-%m-%d %H:%M:%S")
    except:
        return ""


app.jinja_env.filters["human_readable_time"] = human_readable_time
app.jinja_env.filters["timestamp_to_human_readable"] = timestamp_to_human_readable


@app.route("/")
def timeline():
    # connect to db
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    results = c.execute(
        "SELECT timestamp FROM entries ORDER BY timestamp DESC LIMIT 1000"
    ).fetchall()
    timestamps = [result[0] for result in results]
    conn.close()
    return render_template_string(
        """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>OpenRecall - Timeline</title>
  <!-- Bootstrap CSS -->
  <link href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css" rel="stylesheet">
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.3.0/font/bootstrap-icons.css">
  <style>
    .slider-container {
      display: flex;
      flex-direction: column;
      align-items: center;
      padding: 20px;
    }
    .slider {
      width: 80%;
    }
    .slider-value {
      margin-top: 10px;
      font-size: 1.2em;
    }
    .image-container {
      margin-top: 20px;
      text-align: center;
    }
    .image-container img {
      max-width: 100%;
      height: auto;
    }
  </style>
</head>
<body>
<nav class="navbar navbar-light bg-light">
  <div class="container">
    <form class="form-inline my-2 my-lg-0 w-100 d-flex" action="/search" method="get">
      <input class="form-control flex-grow-1 mr-sm-2" type="search" name="q" placeholder="Search" aria-label="Search">
      <button class="btn btn-outline-secondary my-2 my-sm-0" type="submit">
        <i class="bi bi-search"></i>
      </button>
    </form>
  </div>
</nav>
{% if timestamps|length > 0 %}
  <div class="container">
    <div class="slider-container">
      <input type="range" class="slider custom-range" id="discreteSlider" min="0" max="{{timestamps|length - 1}}" step="1" value="{{timestamps|length - 1}}">
      <div class="slider-value" id="sliderValue">{{timestamps[0] | timestamp_to_human_readable }}</div>
    </div>
    <div class="image-container">
      <img id="timestampImage" src="/static/{{timestamps[0]}}.webp" alt="Image for timestamp">
    </div>
  </div>
{% else %}
    <div class="container">
        <div class="alert alert-info" role="alert">
            Nothing recorded yet, wait a few seconds.
        </div>
    </div>

{% endif %}
  <!-- Bootstrap and jQuery JS -->
  <script src="https://code.jquery.com/jquery-3.5.1.slim.min.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/@popperjs/core@2.5.3/dist/umd/popper.min.js"></script>
  <script src="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/js/bootstrap.min.js"></script>
  <script>
    const timestamps = {{ timestamps|tojson }};
    const slider = document.getElementById('discreteSlider');
    const sliderValue = document.getElementById('sliderValue');
    const timestampImage = document.getElementById('timestampImage');

    slider.addEventListener('input', function() {
      const reversedIndex = timestamps.length - 1 - slider.value;
      const timestamp = timestamps[reversedIndex];
      sliderValue.textContent = new Date(timestamp * 1000).toLocaleString();  // Convert to human-readable format
      timestampImage.src = `/static/${timestamp}.webp`;
    });

    // Initialize the slider with a default value
    slider.value = timestamps.length - 1;
    sliderValue.textContent = new Date(timestamps[0] * 1000).toLocaleString();  // Convert to human-readable format
    timestampImage.src = `/static/${timestamps[0]}.webp`;
  </script>
</body>
</html>
    """,
        timestamps=timestamps,
    )


@app.route("/search")
def search():
    q = request.args.get("q")

    # load embeddings from db to numpy array
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    # Get all entries
    results = c.execute("SELECT * FROM entries").fetchall()
    embeddings = []

    for result in results:
        embeddings.append(np.frombuffer(result[5], dtype=np.float64))

    embeddings = np.array(embeddings)

    # Get the embedding of the query
    query_embedding = get_embedding(q)

    # Compute the cosine similarity between the query and all entries
    similarities = []

    for embedding in embeddings:
        similarities.append(cosine_similarity(query_embedding, embedding))

    # Sort the entries by similarity
    indices = np.argsort(similarities)[::-1]

    entries = []

    for i in indices:
        result = results[i]
        entries.append(
            {
                "text": result[3],
                "timestamp": result[4],
                "image_path": f"/static/{result[4]}.webp",
            }
        )

    return render_template_string(
        """
<html>
<head>
    <title>Search Results</title>
    <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css">
</head>
<body>
    <nav class="navbar navbar-light bg-light">
        <a class="navbar-brand" href="/">Back to Home</a>
    </nav>
    <div class="container">
        <h1 class="display-4">Search Results</h1>
        <div class="row">
            {% for entry in entries %}
                <div class="col-md-3 mb-4">
                    <div class="card">
                        <a href="#" data-toggle="modal" data-target="#modal-{{ loop.index0 }}">
                            <img src="{{ entry.image_path }}" alt="Image" class="card-img-top">
                        </a>
                    </div>
                </div>
                <!-- Modal -->
                <div class="modal fade" id="modal-{{ loop.index0 }}" tabindex="-1" role="dialog" aria-labelledby="exampleModalLabel" aria-hidden="true">
                    <div class="modal-dialog modal-xl" role="document" style="max-width: none; width: 100vw; height: 100vh; padding: 20px;">
                        <div class="modal-content" style="height: calc(100vh - 40px); width: calc(100vw - 40px); padding: 0;">
                            <div class="modal-body" style="padding: 0;">
                                <img src="{{ entry.image_path }}" alt="Image" style="width: 100%; height: 100%; object-fit: contain; margin: 0 auto;">
                            </div>
                        </div>
                    </div>
                </div>
            {% endfor %}
        </div>
    </div>

    <!-- Bootstrap and jQuery JS -->
    <script src="https://code.jquery.com/jquery-3.5.1.slim.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/@popperjs/core@2.5.3/dist/umd/popper.min.js"></script>
    <script src="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/js/bootstrap.min.js"></script>
</body>
</html>
    """,
        entries=entries,
    )


@app.route("/static/<filename>")
def serve_image(filename):
    return send_from_directory(screenshots_path, filename)


if __name__ == "__main__":
    create_db()

    # Start the thread to record screenshots
    t = threading.Thread(target=record_screenshot_thread)
    t.start()

    app.run(port=8082)
