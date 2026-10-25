"""Capture landmark samples: python capture_dataset.py --label click --count 100"""
import argparse,csv
from pathlib import Path
import cv2, mediapipe as mp
DATA=Path(__file__).resolve().parent/'data'; DATA.mkdir(exist_ok=True)
def main():
 p=argparse.ArgumentParser(); p.add_argument('--label',required=True); p.add_argument('--count',type=int,default=100); a=p.parse_args()
 out=DATA/'gesture_dataset.csv'; fresh=not out.exists(); cap=cv2.VideoCapture(0)
 if not cap.isOpened(): raise SystemExit('Webcam unavailable')
 with out.open('a',newline='',encoding='utf-8') as f, mp.solutions.hands.Hands(max_num_hands=1) as model:
  w=csv.writer(f)
  if fresh: w.writerow(['label']+[f'v{i}' for i in range(63)])
  n=0
  while n<a.count:
   ok,frame=cap.read()
   if not ok: continue
   frame=cv2.flip(frame,1); r=model.process(cv2.cvtColor(frame,cv2.COLOR_BGR2RGB))
   if r.multi_hand_landmarks:
    lm=r.multi_hand_landmarks[0].landmark; root=lm[0]; scale=max(max(abs(x.x-root.x) for x in lm),max(abs(x.y-root.y) for x in lm),1e-6); row=[]
    for x in lm: row += [(x.x-root.x)/scale,(x.y-root.y)/scale,(x.z-root.z)/scale]
    w.writerow([a.label]+row); n+=1
   cv2.putText(frame,f'{a.label}: {n}/{a.count} (q to stop)',(10,30),cv2.FONT_HERSHEY_SIMPLEX,.7,(0,255,0),2); cv2.imshow('Dataset capture',frame)
   if cv2.waitKey(1)&255==ord('q'): break
 cap.release(); cv2.destroyAllWindows(); print('Saved samples to',out)
if __name__=='__main__': main()
