"""Interpretable confidence thresholds, de-duplication and confirmation handling."""
import time
class FusionEngine:
    def __init__(self, db, notify, executor):
        self.db,self.notify,self.executor=db,notify,executor
        self.last_command=None; self.last_at=0; self.pending=None
    def submit(self, source, command, confidence):
        threshold=0.70 if source=='gesture' else 0.62
        if confidence<threshold:
            self.db.log(source,command,confidence,'rejected: low confidence'); self.notify(f'Low-confidence {source} command ignored ({confidence:.2f}).'); return
        now=time.time()
        if command==self.last_command and now-self.last_at<0.65: return
        if command in ('close_window','shutdown'):
            self.pending=command; self.db.log(source,command,confidence,'confirmation required')
            self.notify('Potentially disruptive action blocked. This prototype does not execute it; say cancel to clear.'); return
        if command=='cancel': self.pending=None; self.notify('Pending action cancelled.'); return
        self.last_command,self.last_at=command,now
        try: result=self.executor(command)
        except Exception as e: result=f'Action failed: {e}'
        self.db.log(source,command,confidence,result)
