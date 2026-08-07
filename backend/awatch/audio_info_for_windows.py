import ctypes
from ctypes import POINTER

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
    IAudioSessionManager2,
    IAudioSessionControl2,
    AudioSession,
    EDataFlow,
    ERole,
    #AudioSessionState
)

# IMMDeviceEnumerator の CLSID（CoClass）
CLSID_MMDeviceEnumerator = GUID("{BCDE0395-E52F-467C-8E3D-C4579291692E}")

# 実際にユーザーが録音・再生しているアプリではなく、OS自身がデバイス管理のために
# 保持しているセッション。使用中判定から除外する。
#   SystemSoundsService.exe : Windowsの通知音・システム効果音の再生
#   svchost.exe             : Windows Audio(Audiosrv)/Audio Endpoint Builder等の
#                              サービスがデバイス管理のために保持するプレースホルダー的セッション
_SYSTEM_PROCESS_NAMES = {"SystemSoundsService.exe", "svchost.exe"}

def _is_real_session(session):
    return not session.Process or session.Process.name() not in _SYSTEM_PROCESS_NAMES


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


def get_capture_sessions():
    """
    マイク（キャプチャ）デバイスのセッション一覧を取得する。

    マイクの使用状況を見るには、キャプチャデバイス自体からIAudioSessionManager2を
    取得する必要がある。
    """
    device = get_device(EDataFlow.eCapture)
    mgr = device.Activate(IAudioSessionManager2._iid_, CLSCTX_ALL, None)
    mgr = ctypes.cast(mgr, POINTER(IAudioSessionManager2))

    session_enumerator = mgr.GetSessionEnumerator()
    count = session_enumerator.GetCount()

    sessions = []
    for i in range(count):
        ctl = session_enumerator.GetSession(i)
        if ctl is None:
            continue
        ctl2 = ctl.QueryInterface(IAudioSessionControl2)
        if ctl2 is None:
            continue
        sessions.append(AudioSession(ctl2))
    return sessions


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
        # 通知音の出力は無視する。Windowsの通知音を再生するSystemSoundsService.exeは除外
        if session.State == 1 and _is_real_session(session): 
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
    sessions = get_capture_sessions()
    # AudioSessionState: 0=Inactive, 1=Active, 2=Expired
    return any(session.State == 1 and _is_real_session(session) for session in sessions) 



class AudioStatus_Win:
    """
    オーディオの状態を調べる

    """ 
    def __init__(self, silence_threshold):
        self.threshold = silence_threshold

    def is_active(self):
        """
        デバイスがアクティブ、かつ音声出力レベルがスレッショルドを超えていればTrueを返す
        """             
        device_active = self.is_audio_active()
        print(f"    device: {device_active}")
        try:
            level = get_output_level()  # 0.0 - 1.0
            #print(f"    level_value: {level}")   
            level_active = (level * 100) > self.threshold
        except Exception:
            level_active = device_active
        #print(f"    level: {level_active}")    
        return device_active and level_active


    def is_audio_active(self):
        """
        デバイスの状態を調べる
        マイクとスピーカーのどちらかがアクティブになっていればTrueを返す
        """              
        try:
            mic_active = is_any_mic_active()
            speaker_active = is_output_device_active()
            if mic_active or speaker_active:
                return True
            else:
                return False
        except Exception as e:
            print("Error:", e)