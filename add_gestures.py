from pathlib import Path
import shutil

p = Path("main.py")
if not p.exists():
    raise SystemExit("ERROR: main.py not found. Open the correct project folder first.")

src = p.read_text(encoding="utf-8")

if "GESTURE_EXTENSIONS_V1" in src:
    raise SystemExit("Gesture extensions already appear to be installed. No changes made.")

anchor = '    last_click = 0.0\n'
if src.count(anchor) != 1:
    raise SystemExit("Could not safely locate the gesture variables. No changes made.")

src = src.replace(
    anchor,
    anchor + '    was_pose = None\n    last_gesture_at = 0.0\n',
    1
)

start = '                    thumb = lm[4]\n'
end = '                    was_pinching = pinching\n'

if src.count(start) != 1 or src.count(end) != 1:
    raise SystemExit("Could not safely locate the existing pinch code. No changes made.")

a = src.index(start)
b = src.index(end, a) + len(end)

replacement = '''                    # GESTURE_EXTENSIONS_V1
                    thumb = lm[4]
                    index = lm[8]
                    middle = lm[12]
                    ring = lm[16]

                    def distance(a, b):
                        return ((a.x - b.x) ** 2 + (a.y - b.y) ** 2) ** 0.5

                    threshold = float(os.getenv("PINCH_THRESHOLD", "0.045"))
                    pinching = distance(thumb, index) < threshold
                    middle_pinch = distance(thumb, middle) < threshold
                    ring_pinch = distance(thumb, ring) < threshold
                    now = time.time()

                    # Pinch actions only fire on the transition into a pinch.
                    if now - last_gesture_at > 0.55:
                        if pinching and not was_pinching:
                            if FUSION is not None:
                                FUSION.submit("gesture", "left_click", 0.92)
                            else:
                                pyautogui.click()
                            status = "LEFT CLICK"
                            last_gesture_at = now
                        elif middle_pinch and not was_pinching:
                            pyautogui.rightClick()
                            status = "RIGHT CLICK"
                            last_gesture_at = now
                        elif ring_pinch and not was_pinching:
                            pyautogui.doubleClick(interval=0.12)
                            status = "DOUBLE CLICK"
                            last_gesture_at = now

                    # Detect poses using the existing MediaPipe finger landmarks.
                    _, idx_up, mid_up, ring_up, pinky_up = fingers_up(hand)
                    pose = (idx_up, mid_up, ring_up, pinky_up)

                    if not (pinching or middle_pinch or ring_pinch):
                        action_pose = None
                        if pose == (True, True, True, True):
                            action_pose = "open_palm"
                        elif pose == (False, False, False, False):
                            action_pose = "fist"
                        elif pose == (True, True, False, False):
                            action_pose = "peace"
                        elif pose == (True, True, True, False):
                            action_pose = "three_fingers"

                        # Trigger once per pose, then require a different pose
                        # before that gesture can trigger again.
                        if action_pose is None:
                            was_pose = None
                        elif action_pose != was_pose and now - last_gesture_at > 0.55:
                            if action_pose == "open_palm":
                                pyautogui.scroll(3)
                                status = "SCROLL UP"
                            elif action_pose == "fist":
                                pyautogui.scroll(-3)
                                status = "SCROLL DOWN"
                            elif action_pose == "peace":
                                pyautogui.press("space")
                                status = "SPACE / PLAY-PAUSE"
                            elif action_pose == "three_fingers":
                                folder = Path.home() / "Pictures" / "AssistantScreenshots"
                                folder.mkdir(parents=True, exist_ok=True)
                                filename = folder / (
                                    "gesture_" + datetime.datetime.now().strftime("%Y%m%d_%H%M%S") + ".png"
                                )
                                pyautogui.screenshot().save(filename)
                                status = "SCREENSHOT SAVED"
                            last_gesture_at = now
                            was_pose = action_pose

                    was_pinching = pinching or middle_pinch or ring_pinch
'''

src = src[:a] + replacement + src[b:]

backup = p.with_name("main.py.before_extra_gestures.bak")
if not backup.exists():
    shutil.copy2(p, backup)

p.write_text(src, encoding="utf-8")
print("SUCCESS: Added extra gesture controls to main.py")
print("Backup saved as:", backup)
