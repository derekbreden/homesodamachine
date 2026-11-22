"""Return the photographed cup to its starting contact and observe it with both motors at rest."""
from position_after_reset import HERE, CONFIG, endpoint, drive, wait_from
from board import Board, Journal
import time

def run():
    tag="return-to-reference"
    path=HERE/(tag+".jsonl")
    if path.exists():raise FileExistsError(path)
    log=Journal(path)
    board=Board("/dev/cu.usbserial-120",log)
    try:
        level,sample=endpoint(tag+"-before",log,independent_ink=True)
        log.append("return_request",target_relative_px=0,pre_px=level,
                   minimum_hold_after_last_motor_s=25)
        last=None
        for i in range(2):
            if abs(level)<CONFIG["correction_deadband_px"]:break
            _,last=drive(board,log,tag,0,"first" if i==0 else "correction",level,sample,"return")
            wait_from(last,4)
            level,sample=endpoint(tag+f"-after{i+1}",log,independent_ink=True)
        if last:wait_from(last,25)
        else:time.sleep(25)
        held,_=endpoint(tag+"-at-rest",log,independent_ink=True)
        log.append("return_observation",immediate_px=level,settled_px=held,
                   hold_motion_px=held-level)
        print("Start reference 0. Latest stop-relative and at-rest rows:",level,held)
    finally:
        board.close()
        log.append("session_end")

if __name__=="__main__":run()
