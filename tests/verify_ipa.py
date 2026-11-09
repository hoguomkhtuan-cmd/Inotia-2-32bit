#!/usr/bin/env python3
"""Static-only F2 ARM32 IPA regression gate. Never claims device/runtime PASS."""
import hashlib, json, struct, sys, zipfile
from collections import deque
from pathlib import Path

EXPECTED = "44ad660b7604be51e6231044cfb4faebbf0cfa5209b6945a310187c4059ef71c"
APP = "Payload/Inotia2.app/"
FOREST_GATES = [(37,8,39,11),(11,33,12,37),(10,21,12,24),(11,8,13,11),
                (24,7,25,10),(37,21,39,24),(37,35,39,38)]

def record(inf, data, i):
    start, size=struct.unpack_from(">II",inf,8*i)
    if start+size>len(data): raise ValueError(f"map {i} out of bounds")
    return data[start:start+size]

def full_map(raw):
    if len(raw)<8: raise ValueError("map too short")
    tile_set,w,h,n=raw[:4]
    if not 0<=tile_set<=5 or not w or not h: raise ValueError("bad map header")
    p=4+2*n
    terrain=raw[p:p+w*h]
    if len(terrain)!=w*h or max(terrain)>=n: raise ValueError("bad tile indices")
    p+=w*h
    coll=raw[p:p+(w*h+1)//2]
    if len(coll)!=(w*h+1)//2: raise ValueError("bad collisions")
    p+=len(coll)
    gen=[]
    for _ in range(2):
        if p+2>len(raw): raise ValueError("missing generator count")
        amount=int.from_bytes(raw[p:p+2],"big");p+=2
        if p+amount*3>len(raw): raise ValueError("truncated generators")
        gen.append([int.from_bytes(raw[p+j*3:p+j*3+3],"big") for j in range(amount)])
        p+=amount*3
    if p+1!=len(raw) or raw[p]!=0: raise ValueError("map trailing bytes")
    return w,h,coll,gen

def mobs(generators):
    return [((v>>16)&255,(v>>6)&63,v&63) for v in generators]

def connected(m,source):
    w,h,coll,_=m
    def free(x,y):
        if not 0<=x<w or not 0<=y<h: return False
        q=y*w+x
        return ((coll[q//2]>>(4 if q%2==0 else 0))&8)==0
    if not free(*source): raise ValueError("blocked landing")
    seen={source};queue=deque([source])
    while queue:
        x,y=queue.popleft()
        for pt in ((x-1,y),(x+1,y),(x,y-1),(x,y+1)):
            if pt not in seen and free(*pt):
                seen.add(pt);queue.append(pt)
    return seen

def validate(path):
    p=Path(path)
    if not p.exists(): raise FileNotFoundError(
        f"IPA NOT UPLOADED: {path}. Static CI cannot run on metadata alone.")
    sha=hashlib.sha256(p.read_bytes()).hexdigest()
    if sha!=EXPECTED: raise ValueError("Wrong IPA SHA-256: "+sha)
    with zipfile.ZipFile(p) as z:
        broken=z.testzip()
        if broken: raise ValueError("CRC mismatch: "+broken)
        inf=z.read(APP+"MapData.inf");dat=z.read(APP+"MapData.dat")
        if len(inf)!=286*8: raise ValueError("Not 286 map entries")
        forest=full_map(record(inf,dat,260))
        forest_mobs=mobs(forest[3][1])
        if sorted(x[0] for x in forest_mobs)!=list(range(117,125)):
            raise ValueError("Forest lost DP14/15 mob set")
        if any(t==176 for t,_,_ in forest_mobs):
            raise ValueError("Duplicate room boss remains in Forest")
        walk=connected(forest,(11,42))
        for j,(x,y,rx,ry) in enumerate(FOREST_GATES):
            room=full_map(record(inf,dat,279+j))
            if mobs(room[3][1])!=[(176,12,10)]:
                raise ValueError(f"Room {279+j} missing its boss")
            if (x,y) not in walk or (rx,ry) not in walk:
                raise ValueError(f"Forest gate {279+j} blocked")
            pathset=connected(room,(12,18))
            if not {(12,10),(12,21),(12,22),(12,23)}.issubset(pathset):
                raise ValueError(f"Room {279+j} passage blocked")
    return {"status":"STATIC PASS / NATIVE NOT TESTED", "sha256":sha,
            "boss_rooms":7, "forest_dp14_15_mob_generators":8,
            "map_count":286, "zip_crc":"PASS",
            "arm32_gameplay_combat_skills_loot":"NOT EXECUTED",
            "save_storage_continue":"NOT EXECUTED",
            "iphone4s_ipad4_cpu_ram":"NOT MEASURED"}

if __name__=="__main__":
    try:
        result=validate(sys.argv[1] if len(sys.argv)>1 else "test-input/current.ipa")
        print(json.dumps(result,indent=2))
    except Exception as exc:
        print(f"::error::{exc}",file=sys.stderr)
        sys.exit(1)
