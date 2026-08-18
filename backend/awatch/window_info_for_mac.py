import objc
from Foundation import NSAppleScript, NSMutableDictionary
from ctypes import cdll, c_void_p, c_bool
from ctypes.util import find_library

# アクセシビリティ権限が必要になるため、
#アプリ起動時に一度ApplicationServiceを呼び出して
# 前倒しでダイアログを出す(request_accessibility_permission)

_app_services_path = find_library("ApplicationServices")
if _app_services_path:
    _app_services = cdll.LoadLibrary(_app_services_path)
    _app_services.AXIsProcessTrustedWithOptions.restype = c_bool
    _app_services.AXIsProcessTrustedWithOptions.argtypes = [c_void_p]
else:
    _app_services = None


def request_accessibility_permission():
    """
    アクセシビリティ権限の状態を確認し、未許可であればOSの許可ダイアログを表示する。
    戻り値: 現在アクセシビリティが許可されているかどうか
    """
    if _app_services is None:
        return False
    options = NSMutableDictionary.dictionary()
    options["AXTrustedCheckOptionPrompt"] = True
    options_ptr = c_void_p(objc.pyobjc_id(options))
    return bool(_app_services.AXIsProcessTrustedWithOptions(options_ptr))


source = """
global frontApp, frontAppName, windowTitle

set windowTitle to ""
tell application "System Events"
    set frontApp to first application process whose frontmost is true
    set frontAppName to name of frontApp
    tell process frontAppName
        try
            tell (1st window whose value of attribute "AXMain" is true)
                set windowTitle to value of attribute "AXTitle"
            end tell
        end try
    end tell
end tell

return frontAppName & "
" & windowTitle
"""

script = None



def window_info_for_mac():
    global script
    if script is None:
        script = NSAppleScript.alloc().initWithSource_(source)

    result, errorinfo = script.executeAndReturnError_(None)
    if errorinfo:
        raise Exception(errorinfo)
    output = result.stringValue()

    app = output.split('\n')[0]
    title = output.split('\n')[1]

    return {"app": app, "title": title}

