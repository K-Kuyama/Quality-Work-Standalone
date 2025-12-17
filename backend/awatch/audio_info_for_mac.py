import ctypes
from ctypes import *
from ctypes.util import find_library

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