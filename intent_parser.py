import re, unicodedata
PHRASES={
'open_calculator':['open calculator','calculator kholo','कैलकुलेटर खोलो','कॅल्क्युलेटर उघडा'],
'open_notepad':['open notepad','notepad kholo','नोटपैड खोलो','नोटपॅड उघडा'],
'open_browser':['open browser','open google','browser kholo','ब्राउज़र खोलो','ब्राउजर उघडा'],
'open_youtube':['open youtube','youtube kholo','यूट्यूब खोलो','यूट्यूब उघडा'],
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

'volume_up':['volume up','increase volume','आवाज बढ़ाओ','आवाज वाढवा'],
'volume_down':['volume down','decrease volume','आवाज कम करो','आवाज कमी करा'],
'mute':['mute','आवाज बंद करो','आवाज बंद करा'],
'take_screenshot':['take screenshot','screenshot','स्क्रीनशॉट लो','स्क्रीनशॉट घ्या'],
'undo':['undo that','undo','पूर्ववत करा'], 'repeat':['do it again','repeat that','repeat','पुन्हा करा'],
'what_time':['what time is it','tell me the time','time now','समय क्या है','वेळ किती झाली'],
'stop_assistant':['stop assistant','stop listening','assistant stop','बंद करो','थांबा'],
'help':['help','what can you do','commands'], 'confirm':['confirm','yes','हां','हाँ','हो'], 'cancel':['cancel','no','नहीं','नाही']}
# OFFICE_FOLLOWUP_INTENTS_V1
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


def _parse_intent_original(text):
    if not text: return None,0.0
    t=' '.join(unicodedata.normalize('NFKC',text).lower().strip().split())
    followup = _office_followup_intent(t)
    if followup is not None:
        return followup

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

    for cmd, phrases in PHRASES.items():
        if t in phrases: return cmd,0.94
        if any(p in t for p in phrases): return cmd,0.78
    m=re.search(r'(?:search for|search|google|खोजो|शोधा)\s+(.+)',t)
    if m: return 'search:'+m.group(1).strip(),0.82
    if 'close window' in t: return 'close_window',0.75
    if 'shutdown computer' in t: return 'shutdown',0.75
    return None,0.2


# FUZZY_MULTILINGUAL_WRAPPER_V1
import difflib as _difflib
import re as _fuzzy_re
import unicodedata as _fuzzy_unicode

PHRASES.update({
    "open_youtube": [
        "open youtube", "open you tube", "open u tube",
        "open youtub", "youtube kholo", "you tube kholo",
        "यूट्यूब खोलो", "यूट्यूब उघडा", "युट्युब उघडा",
        "यूट्यूब चालू करा", "यूट्यूब सुरू करा", "यूट्यूब शुरू करो"
    ],
    "open_browser": [
        "open browser", "open the browser", "browser kholo",
        "ब्राउज़र खोलो", "ब्राउजर उघडा", "इंटरनेट खोलो",
        "इंटरनेट उघडा"
    ],
    "open_calculator": [
        "open calculator", "open the calculator", "calculator kholo",
        "कैलकुलेटर खोलो", "कॅल्क्युलेटर उघडा"
    ],
    "open_notepad": [
        "open notepad", "open the notepad", "notepad kholo",
        "नोटपैड खोलो", "नोटपॅड उघडा"
    ],
    "open_word": [
        "open word", "open microsoft word", "start word",
        "word kholo", "वर्ड खोलो", "वर्ड उघडा"
    ],
    "open_excel": [
        "open excel", "open microsoft excel", "start excel",
        "excel kholo", "एक्सेल खोलो", "एक्सेल उघडा"
    ],
    "open_paint": [
        "open paint", "start paint", "paint kholo",
        "पेंट खोलो", "पेंट उघडा"
    ],
    "scroll_up": [
        "scroll up", "page up", "upar scroll karo",
        "ऊपर स्क्रॉल करो", "वर स्क्रोल करा"
    ],
    "scroll_down": [
        "scroll down", "page down", "neeche scroll karo",
        "नीचे स्क्रॉल करो", "खाली स्क्रोल करा"
    ],
    "volume_up": [
        "volume up", "increase volume",
        "आवाज बढ़ाओ", "आवाज वाढवा"
    ],
    "volume_down": [
        "volume down", "decrease volume",
        "आवाज कम करो", "आवाज कमी करा"
    ],
    "mute": [
        "mute", "आवाज बंद करो", "आवाज बंद करा", "म्यूट करा"
    ],
    "take_screenshot": [
        "take screenshot", "screenshot",
        "स्क्रीनशॉट लो", "स्क्रीनशॉट घ्या"
    ],
    "stop_assistant": [
        "stop assistant", "stop listening", "assistant stop",
        "बंद करो", "थांबा", "असिस्टंट बंद करा"
    ],
    "help": [
        "help", "what can you do", "commands",
        "मदत", "मदत करा", "मदत चाहिए"
    ]
})

def _normalize_voice_text(value):
    value = _fuzzy_unicode.normalize(
        "NFKC", str(value or "")
    ).lower().strip()

    value = value.replace("-", " ")

    replacements = [
        (r"\byou\s+tube\b", "youtube"),
        (r"\bu\s+tube\b", "youtube"),
        (r"\byoo\s+tube\b", "youtube"),
        (r"\byou\s+toob\b", "youtube"),
        (r"\byoutub\b", "youtube"),
        (r"\byou\s+to\s+be\b", "youtube"),
        (r"\bchat\s*gpt\b", "chatgpt"),
        (r"\bpower\s+point\b", "powerpoint"),
        (r"\bplease\b", " "),
        (r"\bthe\b", " "),
        (r"\bhey assistant\b", " ")
    ]

    for pattern, replacement in replacements:
        value = _fuzzy_re.sub(pattern, replacement, value)

    return " ".join(value.split())



# KEYWORD_MATCHING_V1
# Allow important command keywords to trigger commands even when
# the speech recognizer does not capture the complete phrase.

def _keyword_command_match(text):
    t = " ".join(str(text or "").lower().strip().split())

    keyword_commands = [
        (("youtube",), "open_youtube", 0.84),
        (("google",), "open_browser", 0.84),

        (("scroll down", "down"), "scroll_down", 0.82),
        (("scroll up", "up"), "scroll_up", 0.82),

        (("back",), "go_back", 0.82),
        (("forward",), "go_forward", 0.82),

        (("refresh", "reload"), "refresh_page", 0.82),

        (("volume up", "increase volume"), "volume_up", 0.82),
        (("volume down", "decrease volume"), "volume_down", 0.82),

        (("mute",), "mute", 0.82),
        (("screenshot",), "screenshot", 0.82),
    ]

    for keywords, command, confidence in keyword_commands:
        for keyword in keywords:
            if keyword in t:
                return command, confidence

    return None, 0.0


def parse_intent(text):
    normalized = _normalize_voice_text(text)

    if not normalized:
        return None, 0.0

    # Try the original parser first, retaining dynamic commands.
    command, confidence = _parse_intent_original(normalized)

    if command is not None and confidence >= 0.70:
        return command, confidence

    # Compare against all known command phrases.
    candidates = []

    for intent, phrases in PHRASES.items():
        for phrase in phrases:
            phrase_norm = _normalize_voice_text(phrase)

            if not phrase_norm:
                continue

            score = _difflib.SequenceMatcher(
                None, normalized, phrase_norm
            ).ratio()

            if phrase_norm in normalized:
                score = max(score, 0.88)

            candidates.append((score, intent, phrase_norm))

    candidates.sort(reverse=True)

    if candidates:
        best_score, best_intent, best_phrase = candidates[0]
        second_score = candidates[1][0] if len(candidates) > 1 else 0.0

        # Avoid acting on very uncertain or ambiguous speech.
        if best_score >= 0.76 and (
            best_score - second_score >= 0.025
            or best_score >= 0.92
        ):
            return best_intent, min(0.90, best_score)

    return command, confidence
import difflib as _difflib
import re as _re
import unicodedata as _ud

# Recursion fix: preserve the original parser; do not overwrite it with its wrapper.

def parse_intent(text):
    if not text:
        return None, 0.0

    # First check important keywords so partial voice commands work.
    keyword_command, keyword_confidence = _keyword_command_match(text)

    if keyword_command is not None:
        return keyword_command, keyword_confidence

    t = " ".join(_ud.normalize("NFKC", text).lower().strip().split())
    words = set(_re.findall(r"[a-z0-9]+", t))

    # Commands that should still work when the wake/action words are missed.
    aliases = {
        "open_browser": {"google", "browser", "chrome"},
        "open_youtube": {"youtube"},
        "open_chatgpt": {"chatgpt"},
        "open_wikipedia": {"wikipedia"},
        "open_maps": {"maps"},
        "open_word": {"word"},
        "open_excel": {"excel"},
        "open_powerpoint": {"powerpoint"},
        "open_notepad": {"notepad"},
        "open_calculator": {"calculator"},
        "open_paint": {"paint"},
        "open_file_explorer": {"explorer"},
        "scroll_up": {"up"},
        "scroll_down": {"down"},
    }

    # Prefer the longest explicit search phrase so the query is preserved.
    search_patterns = [
        r"\bsearch\s+for\s+(.+)",
        r"\bsearch\s+(.+)",
        r"\bgoogle\s+(.+)",
    ]
    for pattern in search_patterns:
        m = _re.search(pattern, t)
        if m:
            query = m.group(1).strip()
            if query and query not in {"google", "youtube", "browser"}:
                return "search:" + query, 0.88

    # Exact command aliases or meaningful fragments.
    for command, names in aliases.items():
        if t in names or any(name in words for name in names):
            return command, 0.84

    # Keep all existing project commands working.
    command, confidence = _parse_intent_original(t)
    if command:
        return command, confidence

    # Recover near-matches such as "open googel" or "you tube".
    compact = t.replace(" ", "")
    for command, names in aliases.items():
        for name in names:
            if _difflib.SequenceMatcher(None, compact, name.replace(" ", "")).ratio() >= 0.78:
                return command, 0.70

    return None, 0.0
