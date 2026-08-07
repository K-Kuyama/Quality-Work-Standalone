import sys


def create_audio_status(silence_threshold, end_frame_threshold=None):
    """
    プラットフォームに応じたAudioStatusクラスをインスタンス化するFactory。

    silence_threshold   : 実音声レベルとみなすしきい値(%)。両OS共通。
    end_frame_threshold  : macOSのみで使用。Process Tapを閉じる/開いたままにするかの
                           判定に使う連続無音回数(audio_watcher_start.py側の
                           終了確定デバウンスと同じ値を渡すことを想定)。

    生成されるAudioStatusは is_active() -> bool と close() を持つ。
    """
    if sys.platform == "darwin":
        from .audio_info_for_mac import AudioStatus_Mac
        return AudioStatus_Mac(silence_threshold, end_frame_threshold)
    elif sys.platform == "win32":
        from .audio_info_for_windows import AudioStatus_Win
        return AudioStatus_Win(silence_threshold)
    else:
        raise RuntimeError(f"Unsupported OS: {sys.platform}")

'''
def is_audio_active():
    if sys.platform == "darwin":
        from .audio_info_for_mac import is_audio_active_for_mac
        return is_audio_active_for_mac()
    elif sys.platform == "win32":
        from .audio_info_for_windows import is_audio_active_for_windows
        return is_audio_active_for_windows()
    else:
        raise FatalError(f"Unsupported OS: {sys.platform}")

'''
