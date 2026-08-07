"""
macOS 14.2以降で追加された Core Audio Process Tap API を使い、
仮想ループバックデバイス(BlackHole等)のインストールなしにシステム出力音声の
実際のピークレベルを取得するためのモジュール。

参考: WWDC 2023 "Enhance your app’s audio experience" セッション、
及びこのAPIの代表的なOSS実装である insidegui/AudioCap の手順に準拠。
  1. CATapDescription でタップの内容(ここではシステム全体のミックス出力)を定義
  2. AudioHardwareCreateProcessTap でタップを作成
  3. タップを含むprivateなaggregate deviceを AudioHardwareCreateAggregateDevice で作成
  4. aggregate deviceにIOProcを登録してバッファを受け取り、ピーク振幅を計算する

macOS 14.2未満の環境や、CATapDescriptionクラスが見つからない環境、権限が
得られない環境では初期化時に例外を送出する。呼び出し側 (audio_info_for_mac.py) は
これを捕捉し、既存の粗い判定(kAudioDevicePropertyDeviceIsRunningSomewhere)に
フォールバックすること。
"""

import ctypes
import threading
import uuid
from ctypes import POINTER, Structure, byref, c_int32, c_uint32, c_void_p, cdll, sizeof
from ctypes.util import find_library

import objc
from Foundation import NSMutableDictionary, NSUUID

# CATapDescription はObjective-Cクラスなので、CoreAudioバンドルからロードする
objc.loadBundle(
    "CoreAudio", globals(), bundle_path="/System/Library/Frameworks/CoreAudio.framework"
)
CATapDescription = objc.lookUpClass("CATapDescription")

_lib_path = find_library("CoreAudio")
if not _lib_path:
    raise RuntimeError("CoreAudio framework not found")
_coreaudio = cdll.LoadLibrary(_lib_path)

_cf_path = find_library("CoreFoundation")
if not _cf_path:
    raise RuntimeError("CoreFoundation framework not found")
_cf = cdll.LoadLibrary(_cf_path)

OSStatus = c_int32
AudioObjectID = c_uint32
kCFStringEncodingUTF8 = 0x08000100

try:
    from CoreAudio import (
        kAudioAggregateDeviceIsPrivateKey,
        kAudioAggregateDeviceIsStackedKey,
        kAudioAggregateDeviceMainSubDeviceKey,
        kAudioAggregateDeviceNameKey,
        kAudioAggregateDeviceSubDeviceListKey,
        kAudioAggregateDeviceTapAutoStartKey,
        kAudioAggregateDeviceTapListKey,
        kAudioAggregateDeviceUIDKey,
        kAudioDevicePropertyDeviceUID,
        kAudioHardwarePropertyDefaultOutputDevice,
        kAudioObjectPropertyElementMaster,
        kAudioObjectPropertyScopeGlobal,
        kAudioObjectSystemObject,
        kAudioSubDeviceUIDKey,
        kAudioSubTapDriftCompensationKey,
        kAudioSubTapUIDKey,
    )
except ImportError:
    # 古いpyobjc-framework-coreaudioでは未定義の可能性があるため、
    # Apple公開ヘッダー上の実際の文字列値をフォールバックとして直接使う
    kAudioObjectSystemObject = 1
    kAudioObjectPropertyScopeGlobal = 0x676C6F62  # 'glob'
    kAudioObjectPropertyElementMaster = 0
    kAudioHardwarePropertyDefaultOutputDevice = 0x644F7574  # 'dOut'
    kAudioDevicePropertyDeviceUID = 0x75696420  # 'uid '
    kAudioAggregateDeviceUIDKey = "uid"
    kAudioAggregateDeviceNameKey = "name"
    kAudioAggregateDeviceMainSubDeviceKey = "master"
    kAudioAggregateDeviceIsPrivateKey = "private"
    kAudioAggregateDeviceIsStackedKey = "stacked"
    kAudioAggregateDeviceTapAutoStartKey = "autostart"
    kAudioAggregateDeviceSubDeviceListKey = "subdevices"
    kAudioAggregateDeviceTapListKey = "taps"
    kAudioSubDeviceUIDKey = "uid"
    kAudioSubTapUIDKey = "uid"
    kAudioSubTapDriftCompensationKey = "drift"


def _to_str(value):
    # pyobjc-framework-coreaudioのバージョンによっては、CFString系の定数を
    # Python文字列ではなくbytesとして公開している場合がある。bytesのままNSDictionaryの
    # キー/値に使うとNSData扱いになりCoreAudio側のCFString比較と一致せず、
    # 必須キーが見つからないままC実装側で不正な参照が発生しうる(実機で確認したセグフォルトの原因)。
    # そのため必ずPython strに正規化してからNSMutableDictionaryに渡す。
    return value.decode("utf-8") if isinstance(value, bytes) else value


kAudioAggregateDeviceIsPrivateKey = _to_str(kAudioAggregateDeviceIsPrivateKey)
kAudioAggregateDeviceIsStackedKey = _to_str(kAudioAggregateDeviceIsStackedKey)
kAudioAggregateDeviceMainSubDeviceKey = _to_str(kAudioAggregateDeviceMainSubDeviceKey)
kAudioAggregateDeviceNameKey = _to_str(kAudioAggregateDeviceNameKey)
kAudioAggregateDeviceSubDeviceListKey = _to_str(kAudioAggregateDeviceSubDeviceListKey)
kAudioAggregateDeviceTapAutoStartKey = _to_str(kAudioAggregateDeviceTapAutoStartKey)
kAudioAggregateDeviceTapListKey = _to_str(kAudioAggregateDeviceTapListKey)
kAudioAggregateDeviceUIDKey = _to_str(kAudioAggregateDeviceUIDKey)
kAudioSubDeviceUIDKey = _to_str(kAudioSubDeviceUIDKey)
kAudioSubTapDriftCompensationKey = _to_str(kAudioSubTapDriftCompensationKey)
kAudioSubTapUIDKey = _to_str(kAudioSubTapUIDKey)


class AudioObjectPropertyAddress(Structure):
    _fields_ = [
        ("mSelector", c_uint32),
        ("mScope", c_uint32),
        ("mElement", c_uint32),
    ]


class AudioBuffer(Structure):
    _fields_ = [
        ("mNumberChannels", c_uint32),
        ("mDataByteSize", c_uint32),
        ("mData", c_void_p),
    ]


class AudioBufferList(Structure):
    _fields_ = [
        ("mNumberBuffers", c_uint32),
        ("mBuffers", AudioBuffer * 1),
    ]


AudioDeviceIOProc = ctypes.CFUNCTYPE(
    OSStatus,
    AudioObjectID,      # inDevice
    c_void_p,           # inNow
    POINTER(AudioBufferList),  # inInputData
    c_void_p,           # inInputTime
    c_void_p,           # outOutputData
    c_void_p,           # inOutputTime
    c_void_p,           # inClientData
)

_coreaudio.AudioObjectGetPropertyData.argtypes = [
    c_uint32, POINTER(AudioObjectPropertyAddress), c_uint32, c_void_p, POINTER(c_uint32), c_void_p
]
_coreaudio.AudioObjectGetPropertyData.restype = OSStatus

_coreaudio.AudioHardwareCreateProcessTap.argtypes = [c_void_p, POINTER(AudioObjectID)]
_coreaudio.AudioHardwareCreateProcessTap.restype = OSStatus
_coreaudio.AudioHardwareDestroyProcessTap.argtypes = [AudioObjectID]
_coreaudio.AudioHardwareDestroyProcessTap.restype = OSStatus
_coreaudio.AudioHardwareCreateAggregateDevice.argtypes = [c_void_p, POINTER(AudioObjectID)]
_coreaudio.AudioHardwareCreateAggregateDevice.restype = OSStatus
_coreaudio.AudioHardwareDestroyAggregateDevice.argtypes = [AudioObjectID]
_coreaudio.AudioHardwareDestroyAggregateDevice.restype = OSStatus
_coreaudio.AudioDeviceCreateIOProcID.argtypes = [AudioObjectID, AudioDeviceIOProc, c_void_p, POINTER(c_void_p)]
_coreaudio.AudioDeviceCreateIOProcID.restype = OSStatus
_coreaudio.AudioDeviceStart.argtypes = [AudioObjectID, c_void_p]
_coreaudio.AudioDeviceStart.restype = OSStatus
_coreaudio.AudioDeviceStop.argtypes = [AudioObjectID, c_void_p]
_coreaudio.AudioDeviceStop.restype = OSStatus
_coreaudio.AudioDeviceDestroyIOProcID.argtypes = [AudioObjectID, c_void_p]
_coreaudio.AudioDeviceDestroyIOProcID.restype = OSStatus

_cf.CFStringGetCStringPtr.argtypes = [c_void_p, c_uint32]
_cf.CFStringGetCStringPtr.restype = ctypes.c_char_p
_cf.CFStringGetLength.argtypes = [c_void_p]
_cf.CFStringGetLength.restype = ctypes.c_long
_cf.CFStringGetCString.argtypes = [c_void_p, ctypes.c_char_p, ctypes.c_long, c_uint32]
_cf.CFStringGetCString.restype = ctypes.c_bool
_cf.CFRelease.argtypes = [c_void_p]
_cf.CFRelease.restype = None


def _cfstring_to_str(cfstr_ptr):
    if not cfstr_ptr:
        return None
    ptr = _cf.CFStringGetCStringPtr(cfstr_ptr, kCFStringEncodingUTF8)
    if ptr:
        return ptr.decode("utf-8")
    length = _cf.CFStringGetLength(cfstr_ptr)
    buf_size = (length * 4) + 1
    buf = ctypes.create_string_buffer(buf_size)
    if _cf.CFStringGetCString(cfstr_ptr, buf, buf_size, kCFStringEncodingUTF8):
        return buf.value.decode("utf-8")
    return None


def _get_default_output_device_uid():
    addr = AudioObjectPropertyAddress(
        kAudioHardwarePropertyDefaultOutputDevice,
        kAudioObjectPropertyScopeGlobal,
        kAudioObjectPropertyElementMaster,
    )
    device_id = c_uint32(0)
    size = c_uint32(sizeof(device_id))
    status = _coreaudio.AudioObjectGetPropertyData(
        c_uint32(kAudioObjectSystemObject), byref(addr), 0, None, byref(size), byref(device_id)
    )
    if status != 0:
        raise RuntimeError(f"failed to get default output device: {status}")

    uid_addr = AudioObjectPropertyAddress(
        kAudioDevicePropertyDeviceUID,
        kAudioObjectPropertyScopeGlobal,
        kAudioObjectPropertyElementMaster,
    )
    cfstr_ref = c_void_p()
    size2 = c_uint32(sizeof(cfstr_ref))
    status2 = _coreaudio.AudioObjectGetPropertyData(
        device_id, byref(uid_addr), 0, None, byref(size2), byref(cfstr_ref)
    )
    if status2 != 0:
        raise RuntimeError(f"failed to get default output device UID: {status2}")
    uid = _cfstring_to_str(cfstr_ref)
    _cf.CFRelease(cfstr_ref)
    if not uid:
        raise RuntimeError("failed to decode default output device UID")
    return uid


def _build_aggregate_description(tap_uid_str, output_device_uid, agg_uid_str, agg_name):
    tap_entry = NSMutableDictionary.dictionary()
    tap_entry[kAudioSubTapUIDKey] = tap_uid_str
    tap_entry[kAudioSubTapDriftCompensationKey] = True

    sub_device_entry = NSMutableDictionary.dictionary()
    sub_device_entry[kAudioSubDeviceUIDKey] = output_device_uid

    description = NSMutableDictionary.dictionary()
    description[kAudioAggregateDeviceNameKey] = agg_name
    description[kAudioAggregateDeviceUIDKey] = agg_uid_str
    description[kAudioAggregateDeviceMainSubDeviceKey] = output_device_uid
    description[kAudioAggregateDeviceIsPrivateKey] = True
    description[kAudioAggregateDeviceIsStackedKey] = False
    description[kAudioAggregateDeviceTapAutoStartKey] = True
    description[kAudioAggregateDeviceSubDeviceListKey] = [sub_device_entry]
    description[kAudioAggregateDeviceTapListKey] = [tap_entry]
    return description


class ProcessTapMonitor:
    """
    Core Audio Process Tap を使い、システム出力の実際のピークレベル(0-100)を保持する。
    コンストラクタで初期化に失敗した場合は例外を送出するので、呼び出し側でフォールバックすること。
    """

    def __init__(self):
        print(f"ProcessTapMonitor initializing")
        self._lock = threading.Lock()
        self._peak = 0.0
        self._tap_id = AudioObjectID(0)
        self._agg_id = AudioObjectID(0)
        self._ioproc_id = c_void_p()
        self._ioproc_cfunc = None  # GCされないよう参照を保持し続ける
        self._started = False
        self._setup()

    def _setup(self):
        print(f"Setting up ProcessTapMonitor")
        tap_uuid = NSUUID.UUID()
        tap_description = CATapDescription.alloc().initStereoGlobalTapButExcludeProcesses_([])
        tap_description.setName_("QualityWork-AudioLevelTap")
        tap_description.setUUID_(tap_uuid)
        tap_description.setPrivate_(True)
        tap_description.setMuteBehavior_(0)  # CATapUnmuted: ミュートされていない実際のサンプルを取得

        print(f"   Setting up Hardware")
        tap_ptr = c_void_p(objc.pyobjc_id(tap_description))
        tap_id = AudioObjectID(0)
        status = _coreaudio.AudioHardwareCreateProcessTap(tap_ptr, byref(tap_id))
        if status != 0:
            raise RuntimeError(f"AudioHardwareCreateProcessTap failed: {status}")
        self._tap_id = tap_id

        print(f"   Getting device")
        try:
            output_uid = _get_default_output_device_uid()
            agg_uuid_str = str(uuid.uuid4())
            description = _build_aggregate_description(
                str(tap_uuid), output_uid, agg_uuid_str, "QualityWork-TapAggregate"
            )
            agg_ptr = c_void_p(objc.pyobjc_id(description))
            agg_id = AudioObjectID(0)
            status = _coreaudio.AudioHardwareCreateAggregateDevice(agg_ptr, byref(agg_id))
            if status != 0:
                raise RuntimeError(f"AudioHardwareCreateAggregateDevice failed: {status}")
            self._agg_id = agg_id
            self._ioproc_cfunc = AudioDeviceIOProc(self._io_callback)
            ioproc_id = c_void_p()
            status = _coreaudio.AudioDeviceCreateIOProcID(
                self._agg_id, self._ioproc_cfunc, None, byref(ioproc_id)
            )
            if status != 0:
                raise RuntimeError(f"AudioDeviceCreateIOProcID failed: {status}")
            self._ioproc_id = ioproc_id
            status = _coreaudio.AudioDeviceStart(self._agg_id, self._ioproc_id)
            if status != 0:
                raise RuntimeError(f"AudioDeviceStart failed: {status}")
            self._started = True
        except Exception:
            self.close()
            raise

    def _io_callback(self, in_device, in_now, in_input_data, in_input_time,
                      out_output_data, in_output_time, in_client_data):
        try:
            buf_list = in_input_data.contents
            n = buf_list.mNumberBuffers
            if n > 0:
                buffers = (AudioBuffer * n).from_address(ctypes.addressof(buf_list.mBuffers))
                peak = 0.0
                for i in range(n):
                    buf = buffers[i]
                    if buf.mData and buf.mDataByteSize >= 4:
                        sample_count = buf.mDataByteSize // 4
                        samples = (ctypes.c_float * sample_count).from_address(buf.mData)
                        for j in range(sample_count):
                            v = samples[j]
                            if v < 0:
                                v = -v
                            if v > peak:
                                peak = v
                with self._lock:
                    self._peak = peak
        except Exception:
            pass
        return 0

    def get_peak_level_percent(self):
        with self._lock:
            return self._peak * 100

    def close(self):
        if self._started:
            try:
                _coreaudio.AudioDeviceStop(self._agg_id, self._ioproc_id)
            except Exception:
                pass
            self._started = False
        if self._ioproc_id:
            try:
                _coreaudio.AudioDeviceDestroyIOProcID(self._agg_id, self._ioproc_id)
            except Exception:
                pass
        if self._agg_id.value:
            try:
                _coreaudio.AudioHardwareDestroyAggregateDevice(self._agg_id)
            except Exception:
                pass
        if self._tap_id.value:
            try:
                _coreaudio.AudioHardwareDestroyProcessTap(self._tap_id)
            except Exception:
                pass


_monitor = None
_monitor_lock = threading.Lock()
_init_failed = False


def get_peak_level_percent():
    """
    システム出力のピークレベル(0-100)を返す。
    初期化に失敗している場合は例外を送出する(呼び出し側でフォールバックすること)。
    """
    global _monitor, _init_failed
    with _monitor_lock:
        if _init_failed:
            raise RuntimeError("process tap unavailable")
        if _monitor is None:
            try:
                _monitor = ProcessTapMonitor()
            except Exception:
                _init_failed = True
                raise
    return _monitor.get_peak_level_percent()
    

