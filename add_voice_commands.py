from pathlib import Path
import shutil

parser = Path("intent_parser.py")
main = Path("main.py")

if not parser.exists() or not main.exists():
    raise SystemExit("ERROR: Run this script from the folder containing main.py and intent_parser.py.")

p = parser.read_text(encoding="utf-8")
m = main.read_text(encoding="utf-8")

if "EXTRA_VOICE_COMMANDS_V1" in p or "EXTRA_VOICE_COMMANDS_V1" in m:
    raise SystemExit("Extra voice commands already patched. No changes made.")

# Add new voice phrases to the existing intent parser.
anchor = "'open_youtube':['open youtube','youtube kholo','यूट्यूब खोलो','यूट्यूब उघडा'],"
if p.count(anchor) != 1:
    raise SystemExit("Could not find the expected YouTube phrase in intent_parser.py. No changes made.")

new_phrases = anchor + """
# EXTRA_VOICE_COMMANDS_V1
'open_word':['open word','open microsoft word','start word'],
'open_excel':['open excel','open microsoft excel','start excel'],
'open_powerpoint':['open powerpoint','open power point','start powerpoint'],
'open_paint':['open paint','start paint'],
'open_file_explorer':['open file explorer','open explorer'],
'open_task_manager':['open task manager','start task manager'],
'open_settings':['open settings','open windows settings'],
'open_chatgpt':['open chatgpt','open chat gpt'],
'open_wikipedia':['open wikipedia'],
'open_maps':['open google maps','open maps'],
'scroll_up':['scroll up','page up'],
'scroll_down':['scroll down','page down'],
"""
p = p.replace(anchor, new_phrases, 1)

# Add Windows application launch commands.
app_anchor = '        "explorer": ["explorer.exe"],'
if m.count(app_anchor) != 1:
    raise SystemExit("Could not find the expected application list in main.py. No changes made.")

new_apps = app_anchor + """
        # EXTRA_VOICE_COMMANDS_V1
        "word": ["cmd.exe", "/c", "start", "", "winword"],
        "excel": ["cmd.exe", "/c", "start", "", "excel"],
        "powerpoint": ["cmd.exe", "/c", "start", "", "powerpnt"],
        "task manager": ["taskmgr.exe"],
"""
m = m.replace(app_anchor, new_apps, 1)

# Open Windows Settings through its system URI.
settings_anchor = '    try:\n        if system == "windows":\n            subprocess.Popen(commands[name], shell=False)'
settings_replacement = '''    try:
        if system == "windows" and name == "settings":
            os.startfile("ms-settings:")
            return True
        if system == "windows":
            subprocess.Popen(commands[name], shell=False)'''
if m.count(settings_anchor) != 1:
    raise SystemExit("Could not safely find the application launch block. No changes made.")
m = m.replace(settings_anchor, settings_replacement, 1)

# Add browser destinations and help examples.
web_anchor = '    elif "open youtube" in text or "youtube" == text:'
web_replacement = '''    # EXTRA_VOICE_COMMANDS_V1
    elif text in ("open chatgpt", "chatgpt", "open chat gpt"):
        webbrowser.open("https://chatgpt.com")
        speak("Opening ChatGPT.")
    elif text in ("open wikipedia", "wikipedia"):
        webbrowser.open("https://www.wikipedia.org")
        speak("Opening Wikipedia.")
    elif text in ("open google maps", "open maps", "maps"):
        webbrowser.open("https://maps.google.com")
        speak("Opening Google Maps.")
    elif "open youtube" in text or "youtube" == text:'''
if m.count(web_anchor) != 1:
    raise SystemExit("Could not safely find the website command block. No changes made.")
m = m.replace(web_anchor, web_replacement, 1)

# Map parsed intents to the existing action handler.
map_anchor = '        "open_calculator": "open calculator", "open_notepad": "open notepad",'
if m.count(map_anchor) != 1:
    raise SystemExit("Could not safely find the fused-command mapping. No changes made.")

new_mapping = map_anchor + '''
        # EXTRA_VOICE_COMMANDS_V1
        "open_word": "open word",
        "open_excel": "open excel",
        "open_powerpoint": "open powerpoint",
        "open_paint": "open paint",
        "open_file_explorer": "open file explorer",
        "open_task_manager": "open task manager",
        "open_settings": "open settings",
        "open_chatgpt": "open chatgpt",
        "open_wikipedia": "open wikipedia",
        "open_maps": "open google maps",
        "scroll_up": "scroll up",
        "scroll_down": "scroll down",'''
m = m.replace(map_anchor, new_mapping, 1)

# Save backups first; then write both patched files.
for f in (parser, main):
    backup = f.with_name(f.name + ".before_voice_commands.bak")
    if not backup.exists():
        shutil.copy2(f, backup)

parser.write_text(p, encoding="utf-8")
main.write_text(m, encoding="utf-8")

print("SUCCESS: Extra voice commands added.")
print("Backups: intent_parser.py.before_voice_commands.bak")
print("         main.py.before_voice_commands.bak")
