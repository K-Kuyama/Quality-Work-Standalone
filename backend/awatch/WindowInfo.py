import sys

def get_window_info():
    if sys.platform == "darwin":
        from .window_info_for_mac import window_info_for_mac
        return window_info_for_mac()
    elif sys.platform == "win32":
        from .window_info_for_windows import window_info_for_windows
        return window_info_for_windows()
    else:
        raise FatalError(f"Unsupported OS: {sys.platform}")
