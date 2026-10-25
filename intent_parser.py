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
def parse_intent(text):
    if not text: return None,0.0
    t=' '.join(unicodedata.normalize('NFKC',text).lower().strip().split())
    for cmd, phrases in PHRASES.items():
        if t in phrases: return cmd,0.94
        if any(p in t for p in phrases): return cmd,0.78
    m=re.search(r'(?:search for|search|google|खोजो|शोधा)\s+(.+)',t)
    if m: return 'search:'+m.group(1).strip(),0.82
    if 'close window' in t: return 'close_window',0.75
    if 'shutdown computer' in t: return 'shutdown',0.75
    return None,0.2
