from pathlib import Path
import ast
import py_compile

f = Path("intent_parser.py")
if not f.exists():
    raise SystemExit("ERROR: Run this in the folder containing intent_parser.py.")

s = f.read_text(encoding="utf-8-sig")
marker = "FUZZY_MULTILINGUAL_WRAPPER_V1"

if marker in s:
    print("Fuzzy matching is already installed.")
    raise SystemExit(0)

if "def parse_intent(text):" not in s:
    raise SystemExit("Could not find parse_intent(). No changes made.")

# Preserve the existing parser, including previously added commands.
s = s.replace(
    "def parse_intent(text):",
    "def _parse_intent_original(text):",
    1
)

s += r"""

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
"""

ast.parse(s)
f.write_text(s, encoding="utf-8")
py_compile.compile(str(f), doraise=True)

print("SUCCESS: fuzzy matching and command aliases installed.")
