"""Reduce space used by older native camera archives while preserving every array member."""
import argparse
import os
import time
import zipfile
from pathlib import Path

def compress_old(path):
    stat=path.stat();tmp=path.with_suffix('.recoding')
    with zipfile.ZipFile(path) as src:
        members=src.infolist()
        if all(m.compress_type==zipfile.ZIP_BZIP2 for m in members):return 0
        expected={m.filename:(m.file_size,m.CRC) for m in members}
        with zipfile.ZipFile(tmp,'w',compression=zipfile.ZIP_BZIP2,compresslevel=5) as dst:
            for m in members:dst.writestr(m.filename,src.read(m))
    with zipfile.ZipFile(tmp) as check:
        actual={m.filename:(m.file_size,m.CRC) for m in check.infolist()}
        if expected!=actual or check.testzip() is not None:raise ValueError(f'Native archive verification failed for {path}')
    current=path.stat()
    if (stat.st_ino,stat.st_mtime_ns,stat.st_size)!=(current.st_ino,current.st_mtime_ns,current.st_size) or tmp.stat().st_size>=stat.st_size:
        tmp.unlink();return 0
    saving=stat.st_size-tmp.stat().st_size;tmp.replace(path);return saving
if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('directory',type=Path);a=ap.parse_args()
    saving=0;count=0
    for path in sorted(a.directory.glob('*.npz')):
        if time.time()-path.stat().st_mtime<60:continue
        n=compress_old(path)
        if n:saving+=n;count+=1
    print('Losslessly recompressed',count,'files, saved',saving,'bytes')
