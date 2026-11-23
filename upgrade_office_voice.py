from pathlib import Path
import shutil
import re

ROOT = Path(__file__).resolve().parent
MAIN = ROOT / "main.py"
PARSER = ROOT / "intent_parser.py"
if not MAIN.exists() or not PARSER.exists():
    raise SystemExit("ERROR: Run this script from the project folder containing main.py and intent_parser.py.")

m = MAIN.read_text(encoding="utf-8")
p = PARSER.read_text(encoding="utf-8-sig")
if "OFFICE_FOLLOWUP_COMMANDS_V1" in m and "OFFICE_FOLLOWUP_INTENTS_V1" in p:
    print("Office follow-up command support is already installed. No changes made.")
    raise SystemExit(0)

if "import re\n" not in m:
    m = m.replace("import queue\n", "import queue\nimport re\n", 1)

anchor = '    elif text.startswith("open "):'
if m.count(anchor) != 1:
    raise SystemExit("Could not locate the expected open-command branch in main.py; no files changed.")

block = r'''    # OFFICE_FOLLOWUP_COMMANDS_V1
    elif text.startswith(("type:", "type ", "write:", "write ", "dictate:", "dictate ")):
        content = re.sub(r"^(type|write|dictate)[: ]+", "", text, count=1, flags=re.I).strip()
        if content:
            pyautogui.write(content, interval=0.015)
            speak("Typing.")
        else:
            speak("Please say the text after type.")
    elif text.startswith("tab:"):
        tab = text.split(":", 1)[1].strip().lower()
        tab_keys = {"home": "h", "insert": "n", "page layout": "p", "layout": "p",
                    "references": "s", "mailings": "m", "review": "r", "view": "w",
                    "design": "g", "formulas": "m", "formula": "m", "data": "a",
                    "draw": "j", "help": "y"}
        if tab in tab_keys:
            pyautogui.press("esc")
            pyautogui.hotkey("alt", tab_keys[tab])
            speak("Opening " + tab + " tab.")
        else:
            speak("Unknown tab. Try Home, Insert, Layout, Review, View, Data or Formulas.")
    elif text in ("save", "save file", "save document", "save workbook"):
        pyautogui.hotkey("ctrl", "s")
        speak("Save command sent.")
    elif text in ("select all", "select everything"):
        pyautogui.hotkey("ctrl", "a")
        speak("Selected all.")
    elif text in ("copy", "copy that"):
        pyautogui.hotkey("ctrl", "c")
        speak("Copied.")
    elif text in ("paste", "paste that"):
        pyautogui.hotkey("ctrl", "v")
        speak("Pasted.")
    elif text in ("cut", "cut that"):
        pyautogui.hotkey("ctrl", "x")
        speak("Cut.")
    elif text in ("undo", "undo that"):
        pyautogui.hotkey("ctrl", "z")
        speak("Undo.")
    elif text in ("redo", "redo that"):
        pyautogui.hotkey("ctrl", "y")
        speak("Redo.")
    elif text in ("bold", "make bold", "bold this"):
        pyautogui.hotkey("ctrl", "b")
        speak("Bold toggled.")
    elif text in ("italic", "make italic", "italic this"):
        pyautogui.hotkey("ctrl", "i")
        speak("Italic toggled.")
    elif text in ("underline", "underline this"):
        pyautogui.hotkey("ctrl", "u")
        speak("Underline toggled.")
    elif text in ("increase font size", "make font bigger", "font size up"):
        pyautogui.hotkey("ctrl", "shift", ">")
        speak("Font size increased.")
    elif text in ("decrease font size", "make font smaller", "font size down"):
        pyautogui.hotkey("ctrl", "shift", "<")
        speak("Font size decreased.")
    elif text in ("new line", "next line", "press enter", "enter"):
        pyautogui.press("enter")
    elif text in ("press tab", "tab key"):
        pyautogui.press("tab")
    elif text in ("press escape", "escape"):
        pyautogui.press("esc")
    elif text in ("press backspace", "backspace"):
        pyautogui.press("backspace")
    elif text in ("press delete", "delete"):
        pyautogui.press("delete")
    elif text in ("press space", "space"):
        pyautogui.press("space")
    elif text.startswith("find:"):
        query = text.split(":", 1)[1].strip()
        if query:
            pyautogui.hotkey("ctrl", "f")
            pyautogui.write(query, interval=0.02)
            speak("Searching in the current application.")
    elif text.startswith("open website:"):
        site = text.split(":", 1)[1].strip()
        if site:
            if "." not in site:
                site += ".com"
            webbrowser.open("https://" + site)
            speak("Opening " + site)
'''
m = m.replace(anchor, block + "\n" + anchor, 1)

parse_anchor = "def parse_intent(text):"
if p.count(parse_anchor) != 1:
    raise SystemExit("Could not locate parse_intent() in intent_parser.py; no files changed.")

new_parser = r'''# OFFICE_FOLLOWUP_INTENTS_V1
def _office_followup_intent(t):
    for prefix in ("type ", "write ", "dictate "):
        if t.startswith(prefix):
            value = t[len(prefix):].strip()
            return ("type:" + value, 0.91) if value else (None, 0.2)
    match = re.fullmatch(r"(?:go to|open|switch to|select) (?:the )?(home|insert|page layout|layout|references|mailings|review|view|design|formulas|formula|data|draw|help)(?: tab)?", t)
    if match:
        return ("tab:" + match.group(1), 0.90)
    exact = {
        "save": "save", "save document": "save document", "save workbook": "save workbook",
        "save file": "save file", "select all": "select all", "copy": "copy", "paste": "paste",
        "cut": "cut", "undo": "undo", "undo that": "undo", "redo": "redo", "bold": "bold",
        "bold this": "bold this", "make bold": "make bold", "italic": "italic",
        "italic this": "italic this", "underline": "underline", "underline this": "underline this",
        "increase font size": "increase font size", "make font bigger": "make font bigger",
        "font size up": "font size up", "decrease font size": "decrease font size",
        "make font smaller": "make font smaller", "font size down": "font size down",
        "new line": "new line", "next line": "next line", "press enter": "press enter",
        "enter": "enter", "press tab": "press tab", "tab key": "tab key",
        "press escape": "press escape", "escape": "escape", "press backspace": "press backspace",
        "backspace": "backspace", "press delete": "press delete", "delete": "delete",
        "press space": "press space", "space": "space",
    }
    if t in exact:
        return exact[t], 0.92
    if t.startswith("open "):
        target = t[5:].strip()
        known_sites = {"youtube", "google", "gmail", "github", "wikipedia", "chatgpt", "maps"}
        if target in known_sites:
            return target, 0.90
        if target and "." in target:
            return "open website:" + target, 0.88
    if t.startswith(("search in document ", "find in document ", "find ")):
        query = re.sub(r"^(search in document|find in document|find)\s+", "", t).strip()
        if query:
            return "find:" + query, 0.85
    return None

'''
p = p.replace(parse_anchor, new_parser + "\n" + parse_anchor, 1)
old = "def parse_intent(text):\n    if not text: return None,0.0\n    t=' '.join(unicodedata.normalize('NFKC',text).lower().strip().split())"
new = old + "\n    followup = _office_followup_intent(t)\n    if followup is not None:\n        return followup"
if old not in p:
    raise SystemExit("Could not locate the expected parse_intent setup; no files changed.")
p = p.replace(old, new, 1)

for f in (MAIN, PARSER):
    backup = f.with_name(f.name + ".before_office_followup.bak")
    if not backup.exists():
        shutil.copy2(f, backup)
MAIN.write_text(m, encoding="utf-8")
PARSER.write_text(p, encoding="utf-8")
print("SUCCESS: Office follow-up commands installed.")
print("Backups: main.py.before_office_followup.bak and intent_parser.py.before_office_followup.bak")
print("Try: type hello world; go to Home tab; go to Insert tab; save; bold; increase font size; open wikipedia; find machine learning.")
