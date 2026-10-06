#!/usr/bin/env python3
"""Check the released UF2, source receipt and mechanical binding."""
from pathlib import Path
import hashlib,json,struct,subprocess,sys
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def decode(path):
    data=path.read_bytes()
    if not data or len(data)%512:raise ValueError('Invalid UF2 block length')
    count=len(data)//512;binary=bytearray()
    for i in range(count):
        block=data[512*i:512*(i+1)];h=struct.unpack('<8I',block[:32])
        if h!=(0x0A324655,0x9E5D5157,0x2000,0x10000000+256*i,256,i,count,0xE48BFF56)or struct.unpack('<I',block[-4:])[0]!=0x0AB16F30:
            raise ValueError(f'Invalid UF2 header at block {i}')
        binary.extend(block[32:288])
    return bytes(binary)
def main():
    subprocess.run([sys.executable,str(HERE/'make_geometry.py'),'--check'],check=True)
    receipt=json.loads((HERE/'assets/build-receipt.json').read_text())
    for rel,h in receipt['sources'].items():
        if sha(ROOT/rel)!=h:raise ValueError('Source changed: '+rel)
    uf2=HERE/'assets/pgfun-positioner-r1.uf2'
    if sha(uf2)!=receipt['uf2_sha256']:raise ValueError('UF2 digest mismatch')
    binary=decode(uf2);n=receipt['binary_bytes']
    if hashlib.sha256(binary[:n]).hexdigest()!=receipt['binary_sha256']or any(binary[n:]):raise ValueError('UF2 payload mismatch')
    if receipt['geometry_sha256']!=json.loads((ROOT/'hardware/printed-parts/fixtures/pgfun-positioner/motion-geometry.json').read_text())['sha256']:raise ValueError('Geometry mismatch')
    print('Released UF2, linked binary, source hashes and geometry binding match')
if __name__=='__main__':main()
