from pathlib import Path
import re, py_compile

root = Path.cwd()
parser_file = root / "intent_parser.py"
main_file = root / "main.py"

for f in (parser_file, main_file):
    if not f.exists():
        raise SystemExit(f"ERROR: {f.name} not found. Open PowerShell in the folder containing main.py.")

p = parser_file.read_text(encoding="utf-8-sig")
m = main_file.read_text(encoding="utf-8-sig")

# Avoid inserting the patch twice.
if "WORD_VOICE_COMMANDS_V1" in p or "WORD_VOICE_COMMANDS_V1" in m:
    raise SystemExit("Word voice commands already appear to be installed. No files changed.")

# Parse custom Word commands before the existing fixed command list.
marker = "    for cmd, phrases in PHRASES.items():"
patterns = r'''
    # WORD_VOICE_COMMANDS_V1
    dynamic_patterns = [
        (r'^(?:change|set) (?:the )?font size(?: to)? (\d{1,3})$', 'set_font_size:'),
        (r'^(?:change|set) (?:the )?font(?: to)? (.+)$', 'set_font:'),
        (r'^(?:type this|type|write|enter text) (.+)$', 'type_text:'),
        (r'^(?:go to|open|switch to) (home|insert|layout|review|view|references|mailings)(?: tab)?$', 'ribbon_tab:'),
        (r'^(?:make it|make text) bold$', 'format:bold'),
        (r'^(?:make it|make text) italic$', 'format:italic'),
        (r'^(?:underline|underline text)$', 'format:underline'),
        (r'^(?:select all|select the whole document)$', 'shortcut:select_all'),
        (r'^(?:save document|save file|save)$', 'shortcut:save'),
        (r'^(?:new line|next line|press enter)$', 'shortcut:enter'),
        (r'^(?:undo that|undo)$', 'shortcut:undo'),
        (r'^(?:center align|align center)$', 'shortcut:align_center'),
        (r'^(?:left align|align left)$', 'shortcut:align_left'),
        (r'^(?:right align|align right)$', 'shortcut:align_right'),
        (r'^(?:justify text|justify alignment)$', 'shortcut:justify'),
        (r'^(?:go to the beginning|start of document)$', 'shortcut:beginning'),
        (r'^(?:go to the end|end of document)$', 'shortcut:end'),
        (r'^(?:increase font size|make font bigger)$', 'shortcut:font_up'),
        (r'^(?:decrease font size|make font smaller)$', 'shortcut:font_down'),
    ]
    for pattern, prefix in dynamic_patterns:
        match = re.match(pattern, t)
        if match:
            value = match.group(1).strip() if match.lastindex else ''
            return prefix + value, 0.90
'''
if marker not in p:
    raise SystemExit("Could not locate command parser. No files changed.")
p = p.replace(marker, patterns + "\n" + marker, 1)

# Add execution for the parsed commands to the existing command handler.
marker = '    print(f"You: {text}")'
if marker not in m:
    raise SystemExit("Could not locate handle_command(). No files changed.")

actions = r'''
    # WORD_VOICE_COMMANDS_V1
    if text.startswith("type_text:"):
        pyautogui.write(text.split(":", 1)[1], interval=0.02)
        speak("Typing text.")
        return
    if text.startswith("set_font:"):
        font = text.split(":", 1)[1].strip()
        pyautogui.hotkey("ctrl", "shift", "f")
        time.sleep(0.3)
        pyautogui.write(font, interval=0.04)
        pyautogui.press("enter")
        speak("Font changed to " + font)
        return
    if text.startswith("set_font_size:"):
        size = text.split(":", 1)[1].strip()
        if size.isdigit() and 1 <= int(size) <= 200:
            pyautogui.hotkey("ctrl", "shift", "p")
            time.sleep(0.3)
            pyautogui.write(size)
            pyautogui.press("enter")
            speak("Font size changed to " + size)
        else:
            speak("Say a font size from 1 to 200.")
        return
    if text.startswith("ribbon_tab:"):
        tab = text.split(":", 1)[1].strip()
        keys = {"home":"h", "insert":"n", "layout":"p", "review":"r",
                "view":"w", "references":"s", "mailings":"m"}
        if tab in keys:
            pyautogui.press("esc")
            pyautogui.hotkey("alt", keys[tab])
            speak("Opening " + tab + " tab.")
        return
    if text.startswith("format:"):
        key = {"bold":"b", "italic":"i", "underline":"u"}.get(text.split(":",1)[1])
        if key:
            pyautogui.hotkey("ctrl", key)
            speak("Formatting toggled.")
        return
    if text.startswith("shortcut:"):
        action = text.split(":", 1)[1]
        keys = {
            "select_all":("ctrl","a"), "save":("ctrl","s"),
            "undo":("ctrl","z"), "beginning":("ctrl","home"),
            "end":("ctrl","end"), "font_up":("ctrl","shift",">"),
            "font_down":("ctrl","shift","<"), "align_center":("ctrl","e"),
            "align_left":("ctrl","l"), "align_right":("ctrl","r"),
            "justify":("ctrl","j")
        }
        if action == "enter":
            pyautogui.press("enter")
        elif action in keys:
            pyautogui.hotkey(*keys[action])
        speak("Done.")
        return
    if text == "help":
        speak("Try type this hello world, go to Home tab, change font to Arial, change font size to 16, make it bold, center align, or save document.")
        return
'''
m = m.replace(marker, marker + "\n" + actions, 1)

# Validate both edited files before saving them.
import ast
ast.parse(p)
ast.parse(m)

parser_file.write_text(p, encoding="utf-8")
main_file.write_text(m, encoding="utf-8")
py_compile.compile(str(parser_file), doraise=True)
py_compile.compile(str(main_file), doraise=True)
print("SUCCESS: Word voice commands installed and Python syntax checks passed.")
print("Restart the assistant before testing.")
