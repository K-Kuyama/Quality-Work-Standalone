import ctypes
import logging
from ctypes import *
from ctypes.util import find_library

logger = logging.getLogger(f"QualityWork.{__name__}")

#from audio_tap_for_mac import get_peak_level_percent as _get_tap_peak_level_percent

# Core Audio Process Tap（macOS 14.2+）で実際の出力音声レベルを取得するモジュール。
# 古いmacOSや権限が無い環境ではimport自体が失敗しうるので、その場合は粗い判定にフォールバックする。

try:
    from .audio_tap_for_mac import ProcessTapMonitor as _ProcessTapMonitor
except Exception:
    _ProcessTapMonitor = None


# ctypes は Python のための外部関数ライブラリです。このライブラリは C と互換性のあるデータ型を提供し、
# 動的リンク/共有ライブラリ内の関数呼び出しを可能にします。動的リンク/共有ライブラリを純粋な
# Python でラップするために使うことができます。

# PythonのコードでCoreAudioを使うためには、以下をインストールしておく
# 	pyobjc-core：Objective-C ←→ Pythonブリッジ
# 	pyobjc-framework-CoreAudio : CoreAudio APIのPythonバインディング

# pyobjc から CoreAudio の「正しい」整数定数を取得
from CoreAudio import (
    kAudioHardwarePropertyDefaultInputDevice,
    kAudioHardwarePropertyDefaultOutputDevice,
    kAudioDevicePropertyDeviceIsRunningSomewhere,
    kAudioObjectPropertyScopeGlobal,
    kAudioObjectPropertyElementMaster,
    kAudioObjectPropertyScopeInput,
    kAudioObjectPropertyScopeOutput,
    kAudioObjectSystemObject
)

# CoreAudioフレームワークロード
# C の動的ライブラリを直接ロードする
path = find_library("CoreAudio")
if not path:
    raise RuntimeError("CoreAudio framework not found")

coreaudio = cdll.LoadLibrary(path)
#coreaudio = cdll.LoadLibrary("/System/Library/Frameworks/CoreAudio.framework/CoreAudio")


#CoreAudio の関数に「どのプロパティを要求するか」を伝えるための構造体のctypes表現
class AudioObjectPropertyAddress(Structure):
    _fields_ = [
        ("mSelector", c_uint32),
        ("mScope", c_uint32),
        ("mElement", c_uint32)
    ]

# AudioObjectGetPropertyDataの関数プロトタイプ
# CoreAudio の関数に「どのプロパティを要求するか」を伝えるための構造体
coreaudio.AudioObjectGetPropertyData.argtypes = [
    c_uint32,
    POINTER(AudioObjectPropertyAddress),
    c_uint32,
    c_void_p,
    POINTER(c_uint32),
    c_void_p
]
coreaudio.AudioObjectGetPropertyData.restype = c_uint32


# CoreAudioのオブジェクトのプロパティーを取得し返す
def _get_property_int32(object_id, selector, scope, element):
	# 何のプロパティーを取り出すかを伝える構造体をセット
    addr = AudioObjectPropertyAddress(
        selector,
        scope,
        element
    )
	# プロパティーを取得してvalueにセット
    value = c_uint32(0)
    size = c_uint32(sizeof(value))
    status = coreaudio.AudioObjectGetPropertyData(
        c_uint32(object_id),
        byref(addr),
        0, None,
        byref(size),
        byref(value)
    )
    if status != 0:
        raise RuntimeError(f"CoreAudio error (status={status})")
	# 取得した値を返す
    return value.value

# デフォルトインプットデバイスのidを取得
def get_default_input_device():
    return _get_property_int32(
        kAudioObjectSystemObject,
        kAudioHardwarePropertyDefaultInputDevice,
        kAudioObjectPropertyScopeGlobal,
        kAudioObjectPropertyElementMaster
    )

# デフォルトアウトプットデバイスのidを取得
def get_default_output_device():
    return _get_property_int32(
        kAudioObjectSystemObject,
        kAudioHardwarePropertyDefaultOutputDevice,
        kAudioObjectPropertyScopeGlobal,
        kAudioObjectPropertyElementMaster
    )

# device_idで示すデバイスが使用中かどうかを調べる
def is_device_running(device_id, scope):
    addr = AudioObjectPropertyAddress(
        kAudioDevicePropertyDeviceIsRunningSomewhere,
        scope,
        kAudioObjectPropertyElementMaster
    )
    value = c_uint32(0)
    size = c_uint32(sizeof(value))
    status = coreaudio.AudioObjectGetPropertyData(
        c_uint32(device_id),
        byref(addr),
        0, None,
        byref(size),
        byref(value)
    )
    if status != 0:
        return False
    return bool(value.value)

'''
def is_audio_active_for_mac():
    try:
        indev = get_default_input_device()
        outdev = get_default_output_device()

        mic = is_device_running(indev, kAudioObjectPropertyScopeInput)
        spk = is_device_running(outdev, kAudioObjectPropertyScopeOutput)
        #print(f"mic_active={mic}, speaker_active={spk}")
        if mic or spk:
            return True
        else:
            return False
    except Exception as e:
        print("Error:", e)
'''


class AudioStatus_Mac:
    def __init__(self, silence_threshold, max_silent_polls):
        self.threshold = silence_threshold
        self.max_silent_polls = max_silent_polls
        self._tap_monitor = None
        self._silent_streak = 0
        self._warmup_process_tap_permission()

    def _warmup_process_tap_permission(self):
        # 初回のキャプチャの許可(NSAudioCaptureUsageDescription)ダイアログを
        # 起動時に表示するため、一度仮に_ProcessTapMonitorを生成し即時破棄。
        if _ProcessTapMonitor is None:
            return
        try:
            _ProcessTapMonitor().close()
        except Exception as e:
            print("Error:", e)

    # 音声デバイスの状態と音声出力の状態の両方をチェックする。両方Trueの場合にTrueを返す
    def is_active(self):
        device_active = self.is_device_active()
        if not device_active or _ProcessTapMonitor is None:
            # デバイスが不使用、またはProcess Tapが使えない環境では従来通りの粗い判定にフォールバック
            level_active = device_active
        else:
            try:
                level_active = self.get_peak_level() > self.threshold
            except Exception:
                level_active = device_active

        # 一定回数静音が続いたらProcessTapMonitorを初期化
        if level_active:
            self._silent_streak = 0
        else:
            self._silent_streak += 1
            if self._silent_streak >= self.max_silent_polls:
                self._close_tap_monitor()
                self._silent_streak = 0

        # デバイスがアクティブでかつ音声レベルが一定以上の場合にTrueを返す
        return device_active and level_active

    # 音声デバイスの状態をチェック。デバイスが使用されていたらTrueを返す
    def is_device_active(self):
        try:
            indev = get_default_input_device()
            outdev = get_default_output_device()

            mic = is_device_running(indev, kAudioObjectPropertyScopeInput)
            spk = is_device_running(outdev, kAudioObjectPropertyScopeOutput)
            if mic or spk:
                return True
            else:
                return False
        except Exception as e:
            logger.warning("Error:", e)


    # ProcessTapMonitorの初期化
    def _close_tap_monitor(self):
        if self._tap_monitor is not None:
            try:
                self._tap_monitor.close()
            except Exception:
                pass
            self._tap_monitor = None

    #ProcessTapMonitorのインスタンスを生成して、音声レベルを取得し値を返す
    def get_peak_level(self):
        level = 0
        if self._tap_monitor is None:
            try:
                self._tap_monitor = _ProcessTapMonitor()
            except Exception:
                self._tap_monitor = None
        try:
            level = self._tap_monitor.get_peak_level_percent()
        except Exception:
            self._close_tap_monitor()
        return level

    def close(self):
        self._close_tap_monitor()