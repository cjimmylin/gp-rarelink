"""Small ramped load test with automatic abort. Steps of fixed concurrency; stops if errors exceed the guard."""
import json,sys,time,random,threading,collections,statistics
import requests
B="https://raresharedev30.wpenginepowered.com"
inv=json.load(open(sys.argv[1])); OUT=sys.argv[2]
STEPS=[int(x) for x in sys.argv[3].split(",")] if len(sys.argv)>3 else [5,10,20,30]
STEP_SECONDS=int(sys.argv[4]) if len(sys.argv)>4 else 45
posts=[p["link"] for p in inv["posts"]]; groups=[g["link"] for g in inv["groups"]]
words=["rare","gene","trial","syndrome","deletion","therapy","kidney","newsletter","podcast","diagnosis"]
def pick():
    r=random.random()
    if r<0.20: return B+"/"
    if r<0.35: return B+"/groups/"
    if r<0.45: return random.choice(groups[:200])
    if r<0.50: return B+"/members/"
    if r<0.80: return random.choice(posts)
    if r<0.90: return B+"/?s="+random.choice(words)+"+"+str(random.randint(1,999))
    return B+"/news-links/"
UA="Mozilla/5.0 (RGI RareShare prelaunch load test; run by Claude at the owner's request)"
samples=[]; lock=threading.Lock(); stop=threading.Event(); abort_reason=None
def worker(step):
    s=requests.Session(); s.headers["User-Agent"]=UA
    while not stop.is_set():
        u=pick(); t=time.time()
        try:
            r=s.get(u,timeout=30); el=time.time()-t
            ch = r.status_code in (403,503) and "__CF$cv$params" in r.text[:4000]
            rec=(step,r.status_code,el,len(r.content),(r.headers.get("x-cache") or "").split(":")[0],ch)
        except requests.exceptions.Timeout: rec=(step,"timeout",time.time()-t,0,"",False)
        except Exception as e: rec=(step,"error",time.time()-t,0,"",False)
        with lock: samples.append(rec)
def guard():
    global abort_reason
    while not stop.is_set():
        time.sleep(5)
        with lock: recent=[x for x in samples if x[2]>=0 and time.time()-t_start>0][-max(10,int(len(samples)*0.1)):]
        if len(recent)>=10:
            bad=sum(1 for x in recent if x[1] in ("timeout","error") or (isinstance(x[1],int) and (x[1]>=500 or x[1] in (403,429))))
            if bad/len(recent)>0.15: abort_reason=f"abort: {bad}/{len(recent)} recent requests failed"; stop.set()
t_start=time.time(); results={}
threading.Thread(target=guard,daemon=True).start()
for c in STEPS:
    if stop.is_set(): break
    print(f"step concurrency={c} for {STEP_SECONDS}s",flush=True)
    ths=[threading.Thread(target=worker,args=(c,),daemon=True) for _ in range(c)]
    for t in ths: t.start()
    t0=time.time()
    while time.time()-t0<STEP_SECONDS and not stop.is_set(): time.sleep(1)
    stop.set()
    for t in ths: t.join(timeout=35)
    with lock: S=[x for x in samples if x[0]==c]
    lat=[x[2] for x in S if isinstance(x[1],int)]
    st=collections.Counter(str(x[1]) for x in S)
    res={"concurrency":c,"seconds":round(time.time()-t0,1),"requests":len(S),"rps":round(len(S)/max(1,time.time()-t0),2),"status":dict(st),"challenged":sum(1 for x in S if x[5]),"cache_hit_share":round(sum(1 for x in S if x[4]=="HIT")/max(1,len(S)),2),
         "p50_s":round(statistics.median(lat),2) if lat else None,"p95_s":round(sorted(lat)[int(len(lat)*0.95)-1],2) if len(lat)>=20 else None,"p99_s":round(sorted(lat)[int(len(lat)*0.99)-1],2) if len(lat)>=100 else None,"max_s":round(max(lat),2) if lat else None,
         "errors":sum(1 for x in S if x[1] in ("timeout","error") or (isinstance(x[1],int) and x[1]>=500))}
    results[c]=res; print(json.dumps(res),flush=True)
    if abort_reason: print(abort_reason,flush=True); break
    stop.clear(); time.sleep(8)
json.dump({"steps":results,"abort":abort_reason,"started":t_start,"url_mix":"20% home, 15% groups dir, 10% group page, 5% members, 30% random post, 10% search, 10% news-links"},open(OUT,"w"),indent=1)
print("LOAD DONE",abort_reason or "completed all steps",flush=True)
