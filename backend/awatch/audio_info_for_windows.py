import ctypes
# 以下をインストールしておく
#  comtypes : WASAPI の COM インターフェイス
#  pycaw : WASAPI の COM インターフェイスを扱う

from comtypes import CoCreateInstance, CLSCTX_ALL, GUID
from comtypes.client import CreateObject
from comtypes import CoCreateInstance
from pycaw.pycaw import (
    AudioUtilities,
    #IMMDeviceEnumerator,
    IMMDeviceEnumerator,
    IAudioMeterInformation,
    EDataFlow,
    ERole,
    #AudioSessionState
)

# IMMDeviceEnumerator の CLSID（CoClass）
CLSID_MMDeviceEnumerator = GUID("{BCDE0395-E52F-467C-8E3D-C4579291692E}")

def get_device(dataflow):
    """
    デバイスを取得（dataflowに出力か入力かが渡される）
    """
    dataflow = int(dataflow.value)
    enum = CoCreateInstance(
        CLSID_MMDeviceEnumerator,
        interface=IMMDeviceEnumerator,
        clsctx=CLSCTX_ALL
    )
    return enum.GetDefaultAudioEndpoint(dataflow, int(ERole.eMultimedia.value))

def get_output_level():
    """
    スピーカーのレベルを取得（共有モード時のみ有効）
    """
    device = get_device(EDataFlow.eRender)  
    meter = device.Activate(IAudioMeterInformation._iid_, CLSCTX_ALL, None)
    meter = ctypes.cast(meter, POINTER(IAudioMeterInformation))
    return meter.GetPeakValue()

    
def is_output_device_active():
    """
    アウトプットデバイス（スピーカー）が他アプリで使用中かどうかを調べる
    """
    sessions = AudioUtilities.GetAllSessions()
    for session in sessions:
        # AudioSessionState: 0=Inactive, 1=Active, 2=Expired
        if session.State == 1:  # Active
            return True
    return False


def get_mic_level():
    """
    マイクのレベルを取得
    """
    device = get_device(EDataFlow.eCapture)
    meter = device.Activate(IAudioMeterInformation._iid_, CLSCTX_ALL, None)
    meter = ctypes.cast(meter, POINTER(IAudioMeterInformation))
    return meter.GetPeakValue()


def is_any_mic_active():
    """
    マイク（録音デバイス）が他アプリで使用中かどうかを調べる
    """
    sessions = AudioUtilities.GetAllSessions()
    for session in sessions:
        ctl = session._ctl
        state = ctl.GetState()

        # Active なセッションがあれば録音アプリが動作中
        #if state == AudioSessionState.AudioSessionStateActive:
        if state == 1:
            # システムサウンドは除外
            if not session.Process or session.Process.name() != "SystemSoundsService.exe":
                return True
    return False


def is_audio_active_for_windows():
        try:
            mic_active = is_any_mic_active()
            #mic_level = get_mic_level()
            speaker_active = is_output_device_active()
            #output_level = get_output_level()
            #print(f"マイク使用中: {mic_active}:{mic_level}, 出力あり: {speaker_active}:{output_level}")

            if mic_active or speaker_active:
                return True
            else:
                return False

        except Exception as e:
            print("Error:", e)