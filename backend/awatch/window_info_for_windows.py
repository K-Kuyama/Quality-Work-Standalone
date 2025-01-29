import os
import time

import win32gui
import win32api
import win32process


def window_info_for_windows():

    window_handle = get_active_window_handle()
    app = get_app_name(window_handle)
    title = get_window_title(window_handle)

    if app is None:
        app = "None"
    if title is None:
        title = "None"

    return {"app": app, "title": title}


def get_app_path(hwnd):
    """Get application path given hwnd."""
    path = None

    _, pid = win32process.GetWindowThreadProcessId(hwnd)
    process = win32api.OpenProcess(0x0400, False, pid) # PROCESS_QUERY_INFORMATION = 0x0400

    try:
        path = win32process.GetModuleFileNameEx(process, 0)
    finally:
        win32api.CloseHandle(process)

    return path

def get_app_name(hwnd):
    """Get application filename given hwnd."""
    path = get_app_path(hwnd)

    if path is None:
        return None
    
    return os.path.basename(path)

def get_window_title(hwnd):
    return win32gui.GetWindowText(hwnd)

def get_active_window_handle():
    hwnd = win32gui.GetForegroundWindow()
    return hwnd

