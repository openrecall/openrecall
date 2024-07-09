"""Initial configuration of the application. Read the cli parameters, check & set path to 
screenshots and database

Usage:
import openrecall.config

Returns:
    parser: parser object containing the CLI parameters
    appdata_folder: path to appdata folder
    screenshots_path: path to screenshots folder
    db_path: path to sqlite database recall.db
    get_appdata_folder: Function to get appdata folder
    check_python_version: check the python version and exit if wrong version is used
"""
import os, sys
import argparse
import logging
from openrecall.log_config import set_logging_level

# Define a logger for this module
logger = logging.getLogger(__name__)

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

parser.add_argument(
    "--debug",
    help="Debug Level, default=WARNING",
    default="WARNING",
)


# do not exit on unknown parametes to enables pytest.
# unknown parameters are never used.
# Consider invoking these functions from the main application
args, unknown = parser.parse_known_args()


def get_appdata_folder(app_name="openrecall"):
    """
    This function returns the path to the appdata folder dependent on the opersting system.
    Create directory if not exists.

    Args:
        app_name (str, optional): name of the directory for this application. 
        Defaults to "openrecall".
    """

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
    screenshots_path = os.path.join(appdata_folder, "screenshots")
    db_path = os.path.join(appdata_folder, "recall.db")
else:
    appdata_folder = get_appdata_folder()
    db_path = os.path.join(appdata_folder, "recall.db")
    screenshots_path = os.path.join(appdata_folder, "screenshots")

if not os.path.exists(screenshots_path):
    try:
        os.makedirs(screenshots_path)
    except:
        pass

def check_python_version(version=sys.version[:sys.version.find(".",2)]):
    """
    check_python_version: Stop execution if wrong python version is used
    , warning if old version is used.
    """
    def make_version_set(vinfo):
        return tuple(map(int, vinfo.split(".")))
    filepath=os.path.join(os.path.dirname(__file__),"..",".python-version")
    with open (filepath,"r") as f:
        vinfo=f.readline().strip()
    (major,minor) = make_version_set(vinfo)
    (vmajor,vminor) = make_version_set(version)
    if (major,minor) < (vmajor,vminor):
        print ("ERROR: using wrong python version:",version,"please use python ",vinfo)
        sys.exit()
    if (major,minor) > (vmajor,vminor):
        print ("WARNING: using older python version:",version,"please use python ",vinfo)

check_python_version()    

print(args.debug)
set_logging_level(args.debug)
logger.debug("config loaded")

