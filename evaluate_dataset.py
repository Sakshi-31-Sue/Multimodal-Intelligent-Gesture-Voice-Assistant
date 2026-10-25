"""Optional baseline evaluation: install requirements-ml.txt first."""
import csv
from pathlib import Path
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score,classification_report
p=Path(__file__).resolve().parent/'data'/'gesture_dataset.csv'
if not p.exists(): raise SystemExit('Collect samples with capture_dataset.py first.')
r=list(csv.DictReader(p.open(encoding='utf-8'))); labels=[x['label'] for x in r]
if len(r)<10 or len(set(labels))<2: raise SystemExit('Need at least 10 samples across at least 2 labels.')
X=np.array([[float(x[f'v{i}']) for i in range(63)] for x in r]); y=np.array(labels)
X1,X2,y1,y2=train_test_split(X,y,test_size=.25,random_state=42,stratify=y)
m=make_pipeline(StandardScaler(),SVC(probability=True,class_weight='balanced')); m.fit(X1,y1); pred=m.predict(X2)
print('Holdout accuracy:',round(accuracy_score(y2,pred),3)); print(classification_report(y2,pred))
