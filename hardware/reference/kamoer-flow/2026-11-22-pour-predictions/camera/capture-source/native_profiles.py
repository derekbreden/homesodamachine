"""Encode and recover integer native camera luma exactly using consecutive-frame differences."""
import numpy as np
import zipfile

def compress(surface):
    if surface.dtype!=np.uint16:raise ValueError('Expected native uint16 optical samples')
    d=np.diff(surface.astype(np.int16),axis=0)
    zigzag=((d<<1)^(d>>15)).astype(np.uint16)
    return {'first_x4':surface[0],'delta_low':(zigzag&255).astype('u1'),'delta_high':(zigzag>>8).astype('u1')}

def recover(recording):
    first=recording['first_x4']
    zigzag=recording['delta_low'].astype(np.int32)|(recording['delta_high'].astype(np.int32)<<8)
    diff=(zigzag>>1)^-(zigzag&1)
    restored=np.concatenate([first[None],first[None].astype(np.int32)+np.cumsum(diff,axis=0,dtype=np.int32)])
    return restored.astype('u2')

def write(container,**fields):
    with zipfile.ZipFile(container,'w',compression=zipfile.ZIP_BZIP2,compresslevel=5) as output:
        for key,value in fields.items():
            with output.open(key+'.npy','w',force_zip64=True) as member:
                np.lib.format.write_array(member,np.asarray(value),allow_pickle=False)
