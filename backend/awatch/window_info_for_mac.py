from Foundation import NSAppleScript



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

