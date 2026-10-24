import swisseph as swe, datetime as dt
S=['Aries','Taurus','Gemini','Cancer','Leo','Virgo','Libra','Scorpio','Sagittarius','Capricorn','Aquarius','Pisces']
def fmt(l):
    l%=360;s=int(l//30);d=l-30*s;return f"{int(d)}°{int((d-int(d))*60):02d}' {S[s]}"
LAT,LON=4.711,-74.072
jdn=swe.julday(1991,1,10,16+33/60)
B=[('Sun',swe.SUN),('Moon',swe.MOON),('Mercury',swe.MERCURY),('Venus',swe.VENUS),('Mars',swe.MARS),('Jupiter',swe.JUPITER),('Saturn',swe.SATURN),('Uranus',swe.URANUS),('Neptune',swe.NEPTUNE),('Pluto',swe.PLUTO)]
nat={n:swe.calc_ut(jdn,p,swe.FLG_SWIEPH)[0][0] for n,p in B}
cusps,ascmc=swe.houses(jdn,LAT,LON,b'P'); nat['ASC']=ascmc[0]; nat['MC']=ascmc[1]
def house(l):
    for i in range(12):
        a,b=cusps[i],cusps[(i+1)%12]
        if (l-a)%360<(b-a)%360: return i+1
print("Natal cusps:",[fmt(c) for c in cusps])
ASP=[('conj',0),('sextile',60),('square',90),('trine',120),('opp',180)]
def sep(a,b): d=abs(a-b)%360; return min(d,360-d)
# slow transits on Nov 1, 15, 30
for day in (1,15,30):
    jd=swe.julday(2026,11,day,17)
    print(f"\n--- 2026-11-{day:02d} transits ---")
    for n,p in B:
        x=swe.calc_ut(jd,p,swe.FLG_SWIEPH|swe.FLG_SPEED)[0]
        print(f"  {n:8s} {fmt(x[0]):18s} {'R' if x[3]<0 else ' '} house {house(x[0])}")
# exact aspects of transiting planets to natal points during November (daily scan)
print("\n--- exact transit aspects in Nov 2026 (orb crossing) ---")
prev={}
for i in range(0,32):
    d=dt.date(2026,10,31)+dt.timedelta(days=i); jd=swe.julday(d.year,d.month,d.day,17)
    cur={n:swe.calc_ut(jd,p,swe.FLG_SWIEPH)[0][0] for n,p in B}
    for tn,tl in cur.items():
        if tn=='Moon': continue
        for nn,nl in nat.items():
            for an,ang in ASP:
                for sg in ((1,) if ang in (0,180) else (1,-1)):
                    f=lambda L:((L-nl-sg*ang+180)%360)-180
                    if tn in prev and f(prev[tn])*f(tl)<0 and abs(f(prev[tn]))<2:
                        print(f"  {d} transiting {tn} {an} natal {nn} ({fmt(tl)})")
    prev=cur
# slow planets within orb (<=3°) to natal during Nov
print("\n--- slow transits within 3° on Nov 15 ---")
jd=swe.julday(2026,11,15,17)
for tn,p in B[5:]:
    tl=swe.calc_ut(jd,p,swe.FLG_SWIEPH)[0][0]
    for nn,nl in nat.items():
        for an,ang in ASP:
            o=abs(sep(tl,nl)-ang)
            if o<=3: print(f"  {tn} {fmt(tl)} {an} natal {nn} {fmt(nl)} orb {o:.2f}")
# lunations
print("\n--- lunations ---")
for i in range(0,32):
    d=dt.date(2026,10,31)+dt.timedelta(days=i); jd=swe.julday(d.year,d.month,d.day,17)
    s=swe.calc_ut(jd,swe.SUN,swe.FLG_SWIEPH)[0][0]; m=swe.calc_ut(jd,swe.MOON,swe.FLG_SWIEPH)[0][0]
    ph=(m-s)%360
    if i>0 and (prevph>350 and ph<10): print(f"  New Moon ~{d} at {fmt(s)} (natal house {house(s)})")
    if i>0 and prevph<180<=ph: print(f"  Full Moon ~{d} Moon at {fmt(m)} (house {house(m)}), Sun {fmt(s)}")
    prevph=ph
# profection
age=35; print("\nprofection house (age 35):", age%12+1, "sign", S[(int(nat['ASC']//30)+age%12)%12])
# solar return 2026 approx: Sun returns to 19°55' Cap
for h in range(0,24*12):
    jd=swe.julday(2026,1,9,h/12); s=swe.calc_ut(jd,swe.SUN,swe.FLG_SWIEPH)[0][0]
    if abs(s-nat['Sun'])<0.005: print("solar return 2026 ~ JD",jd, swe.revjul(jd)); break
