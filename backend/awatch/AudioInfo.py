import sys

def is_audio_active():
    if sys.platform == "darwin":
        from .audio_info_for_mac import is_audio_active_for_mac
        return is_audio_active_for_mac()
    elif sys.platform == "win32":
        from .audio_info_for_windows import is_audio_active_for_windows
        return is_audio_active_for_windows()
    else:
        raise FatalError(f"Unsupported OS: {sys.platform}")
