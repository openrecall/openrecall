import sys

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


def get_active_app_name_osx():
    from AppKit import NSWorkspace

    try:
        active_app = NSWorkspace.sharedWorkspace().activeApplication()
        return active_app["NSApplicationName"]
    except:
        return ""

def get_active_window_title_osx():
    from Quartz import (
        CGWindowListCopyWindowInfo,
        kCGNullWindowID,
        kCGWindowListOptionOnScreenOnly,
    )

    try:
        app_name = get_active_app_name_osx()
        windows = CGWindowListCopyWindowInfo(
            kCGWindowListOptionOnScreenOnly, kCGNullWindowID
        )
        for window in windows:
            if window["kCGWindowOwnerName"] == app_name:
                return window.get("kCGWindowName", "Unknown")
    except:
        return ""
    return ""


def get_active_app_name_windows():
    import psutil
    import win32gui
    import win32process

    try:
        hwnd = win32gui.GetForegroundWindow()
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        exe = psutil.Process(pid).name()
        return exe
    except:
        return ""


def get_active_window_title_windows():
    import win32gui

    try:
        hwnd = win32gui.GetForegroundWindow()
        return win32gui.GetWindowText(hwnd)
    except:
        return ""


def get_active_app_name_linux():
    return ''


def get_active_window_title_linux():
    return ''

def get_active_app_name():
    if sys.platform == "win32":
        return get_active_app_name_windows()
    elif sys.platform == "darwin":
        return get_active_app_name_osx()
    elif sys.platform.startswith("linux"):
        return get_active_app_name_linux()
    else:
        raise NotImplementedError("This platform is not supported")


def get_active_window_title():
    if sys.platform == "win32":
        return get_active_window_title_windows()
    elif sys.platform == "darwin":
        return get_active_window_title_osx()
    elif sys.platform.startswith("linux"):
        return get_active_window_title_linux()
    else:
        raise NotImplementedError("This platform is not supported")

def is_user_active_osx():
    import subprocess

    try:
        # Run the 'ioreg' command to get idle time information
        output = subprocess.check_output(["ioreg", "-c", "IOHIDSystem"]).decode()
        
        # Find the line containing "HIDIdleTime"
        for line in output.split('\n'):
            if "HIDIdleTime" in line:
                # Extract the idle time value
                idle_time = int(line.split('=')[-1].strip())
                
                # Convert idle time from nanoseconds to seconds
                idle_seconds = idle_time / 1000000000
                
                # If idle time is less than 5 seconds, consider the user not idle
                return idle_seconds < 5
        
        # If "HIDIdleTime" is not found, assume the user is not idle
        return True
    
    except subprocess.CalledProcessError:
        # If there's an error running the command, assume the user is not idle
        return True
    except Exception as e:
        print(f"An error occurred: {e}")
        # If there's any other error, assume the user is not idle
        return True

def is_user_active():
    if sys.platform == "win32":
        return True
    elif sys.platform == "darwin":
        return is_user_active_osx()
    elif sys.platform.startswith("linux"):
        return True
    else:
        raise NotImplementedError("This platform is not supported")
    