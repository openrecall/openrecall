import sys
import datetime
import time
from typing import Any  # Using Any for platform-specific imports

# Platform-specific imports with error handling
try:
    import psutil
    import win32gui
    import win32process
    import win32api
except ImportError:
    psutil = None
    win32gui = None
    win32process = None
    win32api = None

try:
    from AppKit import NSWorkspace
except ImportError:
    NSWorkspace = None

try:
    from Quartz import (
        CGWindowListCopyWindowInfo,
        kCGNullWindowID,
        kCGWindowListOptionOnScreenOnly,
    )
except ImportError:
    CGWindowListCopyWindowInfo = None
    kCGNullWindowID = None
    kCGWindowListOptionOnScreenOnly = None

try:
    import subprocess
except ImportError:
    subprocess = None  # Should always be available in standard lib


def human_readable_time(timestamp: int) -> str:
    """Converts a Unix timestamp into a human-readable relative time string.

    Args:
        timestamp: The Unix timestamp (seconds since epoch).

    Returns:
        A string representing the relative time (e.g., "5 minutes ago").
    """
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


def timestamp_to_human_readable(timestamp: int) -> str:
    """Converts a Unix timestamp into a human-readable absolute date/time string.

    Args:
        timestamp: The Unix timestamp (seconds since epoch).

    Returns:
        A string representing the absolute date and time (YYYY-MM-DD HH:MM:SS),
        or an empty string if conversion fails.
    """
    try:
        dt_object = datetime.datetime.fromtimestamp(timestamp)
        return dt_object.strftime("%Y-%m-%d %H:%M:%S")
    except:
        return ""


def get_active_app_name_osx() -> str:
    """Gets the name of the active application on macOS.

    Requires the pyobjc package.

    Returns:
        The name of the active application, or an empty string if unavailable.
    """
    if NSWorkspace is None:
        return ""  # Indicate unavailability if import failed
    try:
        active_app = NSWorkspace.sharedWorkspace().activeApplication()
        return active_app.get("NSApplicationName", "")
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
    return ""  # Default if no specific window is found


def get_active_app_name_windows() -> str:
    """Gets the name of the executable for the active window on Windows.

    Requires pywin32 and psutil packages.

    Returns:
        The executable name (e.g., "chrome.exe"), or an empty string if unavailable.
    """
    if not all([psutil, win32gui, win32process]):
        return ""  # Indicate unavailability if imports failed
    try:
        hwnd = win32gui.GetForegroundWindow()
        if not hwnd:
            return ""
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        if not pid:
            return ""
        exe = psutil.Process(pid).name()
        return exe
    except:
        return ""


def get_active_window_title_windows() -> str:
    """Gets the title of the active window on Windows.

    Requires the pywin32 package.

    Returns:
        The title of the foreground window, or an empty string if unavailable.
    """
    if win32gui is None:
        return ""  # Indicate unavailability if import failed
    try:
        hwnd = win32gui.GetForegroundWindow()
        if not hwnd:
            return ""
        return win32gui.GetWindowText(hwnd)
    except Exception as e:
        print(f"Error getting Windows window title: {e}")
        return ""


def get_active_app_name_linux() -> str:
    """Gets the name of the active application on Linux.

    Placeholder implementation. Requires additional logic (e.g., using xprop
    or similar tools/libraries).

    Returns:
        An empty string (currently not implemented).
    """
    # TODO: Implement Linux active app name retrieval
    # Example using subprocess and xprop (requires xprop to be installed):
    # try:
    #     root = subprocess.Popen(['xprop', '-root', '_NET_ACTIVE_WINDOW'], stdout=subprocess.PIPE)
    #     stdout, _ = root.communicate()
    #     active_window_id = re.search(b'window id # (0x[0-9a-f]+)', stdout)
    #     if active_window_id:
    #         window_id = active_window_id.group(1).decode('utf-8')
    #         prop = subprocess.Popen(['xprop', '-id', window_id, 'WM_CLASS'], stdout=subprocess.PIPE)
    #         stdout, _ = prop.communicate()
    #         wm_class = re.search(b'WM_CLASS\(STRING\) = (?P<class>.*)\n', stdout)
    #         if wm_class:
    #              class_string = wm_class.group("class").decode('utf-8')
    #              # WM_CLASS usually gives "instance", "class" - return the instance
    #              return class_string.split(', ')[0].strip('"')
    # except Exception as e:
    #      print(f"Error getting Linux app name: {e}")
    return ""


def get_active_window_title_linux() -> str:
    """Gets the title of the active window on Linux.

    Placeholder implementation. Requires additional logic (e.g., using xprop
    or similar tools/libraries).

    Returns:
        An empty string (currently not implemented).
    """
    # TODO: Implement Linux active window title retrieval
    # Example using subprocess and xprop:
    # try:
    #     root = subprocess.Popen(['xprop', '-root', '_NET_ACTIVE_WINDOW'], stdout=subprocess.PIPE)
    #     stdout, _ = root.communicate()
    #     active_window_id = re.search(b'window id # (0x[0-9a-f]+)', stdout)
    #     if active_window_id:
    #         window_id = active_window_id.group(1).decode('utf-8')
    #         prop = subprocess.Popen(['xprop', '-id', window_id, '_NET_WM_NAME'], stdout=subprocess.PIPE)
    #         stdout, _ = prop.communicate()
    #         wm_name = re.search(b'_NET_WM_NAME\(UTF8_STRING\) = "(?P<name>.*)"\n', stdout)
    #         if wm_name:
    #             return wm_name.group("name").decode('utf-8')
    # except Exception as e:
    #     print(f"Error getting Linux window title: {e}")
    return ""


def get_active_app_name() -> str:
    """Gets the active application name for the current platform.

    Returns:
        The name of the active application, or an empty string if unavailable
        or the platform is unsupported (or not implemented).
    """
    if sys.platform == "win32":
        return get_active_app_name_windows()
    elif sys.platform == "darwin":
        return get_active_app_name_osx()
    elif sys.platform.startswith("linux"):
        return get_active_app_name_linux()
    else:
        print("Warning: Active app name retrieval not implemented for this platform.")
        return ""
        # raise NotImplementedError(f"Platform '{sys.platform}' not supported yet for get_active_app_name")


def get_active_window_title() -> str:
    """Gets the active window title for the current platform.

    Returns:
        The title of the active window, or an empty string if unavailable
        or the platform is unsupported (or not implemented).
    """
    if sys.platform == "win32":
        return get_active_window_title_windows()
    elif sys.platform == "darwin":
        return get_active_window_title_osx()
    elif sys.platform.startswith("linux"):
        return get_active_window_title_linux()
    else:
        print("Warning: Active window title retrieval not implemented for this platform.")
        return ""
        # raise NotImplementedError(f"Platform '{sys.platform}' not supported yet for get_active_window_title")


def is_user_active_osx() -> bool:
    """Checks if the user is active on macOS based on HID idle time.

    Requires the pyobjc package and uses the 'ioreg' command. Considers the user
    active if the idle time is less than 5 seconds.

    Returns:
        True if the user is considered active, False otherwise. Returns True
        if the check fails for any reason.
    """
    if subprocess is None:
        print("Warning: 'subprocess' module not available, assuming user is active.")
        return True
    try:
        # Run the 'ioreg' command to get idle time information
        # Filtering directly with -k is more efficient
        output = subprocess.check_output(
            ["ioreg", "-c", "IOHIDSystem", "-r", "-k", "HIDIdleTime"], timeout=1
        ).decode()

        # Find the line containing "HIDIdleTime"
        for line in output.splitlines():
            if "HIDIdleTime" in line:
                # Extract the idle time value
                idle_time = int(line.split("=")[-1].strip())

                # Convert idle time from nanoseconds to seconds
                idle_seconds = idle_time / 1_000_000_000  # Use underscore for clarity

                # If idle time is less than 5 seconds, consider the user active
                return idle_seconds < 5.0

        # If "HIDIdleTime" is not found (e.g., screen locked), assume inactive?
        # Or assume active as a fallback? Let's assume active for now.
        print("Warning: Could not find HIDIdleTime in ioreg output.")
        return True

    except subprocess.TimeoutExpired:
        print("Warning: 'ioreg' command timed out, assuming user is active.")
        return True
    except subprocess.CalledProcessError as e:
        # This might happen if the class IOHIDSystem is not found, etc.
        print(f"Warning: 'ioreg' command failed ({e}), assuming user is active.")
        return True
    except Exception as e:
        print(f"An error occurred during macOS idle check: {e}")
        # Fallback: assume the user is active
        return True


def is_user_active_windows() -> bool:
    """Checks if the user is active on Windows based on last input time.

    Requires the pywin32 package. Considers the user active if the last input
    was less than 5 seconds ago.

    Returns:
        True if the user is considered active, False otherwise. Returns True
        if the check fails.
    """
    if win32api is None:
        print("Warning: 'win32api' module not available, assuming user is active.")
        return True
    try:
        last_input_info = win32api.GetLastInputInfo()
        # GetTickCount returns milliseconds since system start
        current_time = win32api.GetTickCount()
        idle_milliseconds = current_time - last_input_info
        idle_seconds = idle_milliseconds / 1000.0
        return idle_seconds < 5.0
    except Exception as e:
        print(f"An error occurred during Windows idle check: {e}")
        # Fallback: assume the user is active
        return True


def is_user_active_linux() -> bool:
    """Checks if the user is active on Linux.

    Placeholder implementation. Requires interaction with the display server
    (X11 or Wayland) to get idle time.

    Returns:
        True (currently always assumes active).
    """
    # TODO: Implement Linux user active check
    # Example using xprintidle (requires xprintidle to be installed):
    # try:
    #     output = subprocess.check_output(['xprintidle'], timeout=1).decode()
    #     idle_milliseconds = int(output.strip())
    #     idle_seconds = idle_milliseconds / 1000.0
    #     return idle_seconds < 5.0
    # except (FileNotFoundError, subprocess.CalledProcessError, subprocess.TimeoutExpired, ValueError) as e:
    #     print(f"Warning: Could not check Linux idle time ({e}), assuming user is active.")
    #     return True
    # except Exception as e:
    #     print(f"An error occurred during Linux idle check: {e}")
    #     return True
    print("Warning: Linux user active check not implemented, assuming active.")
    return True


def is_user_active() -> bool:
    """Checks if the user is active on the current platform.

    Considers the user active if their last input was recent (e.g., < 5 seconds ago).
    Implementation varies by platform.

    Returns:
        True if the user is considered active, False otherwise. Returns True
        if the check is not implemented or fails.
    """
    if sys.platform == "win32":
        return is_user_active_windows()
    elif sys.platform == "darwin":
        return is_user_active_osx()
    elif sys.platform.startswith("linux"):
        return is_user_active_linux()
    else:
        print(f"Warning: User active check not supported for platform '{sys.platform}', assuming active.")
        return True
        # raise NotImplementedError(f"Platform '{sys.platform}' not supported yet for is_user_active")
