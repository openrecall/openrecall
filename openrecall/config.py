import os
import sys
import argparse

parser = argparse.ArgumentParser(
    description="OpenRecall"
)

parser.add_argument(
    "--storage-path",
    default=None,
    help="Path to store the screenshots and database",
)

parser.add_argument(
    "--primary-monitor-only",
    action="store_true",
    help="Only record the primary monitor",
    default=False,
)

args = parser.parse_args()


def get_appdata_folder(app_name="openrecall"):
    if sys.platform == "win32":
        appdata = os.getenv("APPDATA")
        if not appdata:
            raise EnvironmentError("APPDATA environment variable is not set.")
        path = os.path.join(appdata, app_name)
    elif sys.platform == "darwin":
        home = os.path.expanduser("~")
        path = os.path.join(home, "Library", "Application Support", app_name)
    else:
        home = os.path.expanduser("~")
        path = os.path.join(home, ".local", "share", app_name)
    if not os.path.exists(path):
        os.makedirs(path)
    return path

if args.storage_path:
    appdata_folder = args.storage_path
else:
    appdata_folder = get_appdata_folder()

screenshots_path = os.path.join(appdata_folder, "screenshots")
db_path = os.path.join(appdata_folder, "recall.db")
model_cache_path = os.path.join(appdata_folder, "sentence_transformers")

for d in [screenshots_path, model_cache_path]:
    if not os.path.exists(d):
        try:
            os.makedirs(d)
        except:
            pass
