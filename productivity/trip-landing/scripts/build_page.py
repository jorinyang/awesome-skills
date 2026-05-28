#!/usr/bin/env python3
"""Build trip landing page v2 - 5 Tabs: Overview/Itinerary/Map/Pre-trip/Safety"""
import json, sys, os, argparse

CSS = """/* 贵州之客 Brand */
:root{--f:#1A4A3A;--fd:#0E3125;--fl:#2A6B52;--w:#4A7C96;--s:#8B6F5C;--t:#D4914A;--tc:#F5ECE0;--bg:#FBFAF7;--ca:#FFF;--bo:#E8E4DD;--tx:#2C3228;--t2:#6B7365;--tm:#9CA395;--dg:#C9403B;--db:#FDF0EE;--su:#3A8C5C;--r:14px;--rs:8px;--sh:0 2px 16px rgba(0,0,0,0.05);--mw:780px}
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:-apple-system,BlinkMacSystemFont,"PingFang SC","Noto Sans SC",sans-serif;background:var(--bg);color:var(--tx);line-height:1.7;-webkit-font-smoothing:antialiased}
.hero{background:linear-gradient(165deg,var(--fd)0%,var(--f)40%,#226045 100%);color:#fff;padding:48px 20px 40px;text-align:center;position:relative;overflow:hidden}
.hero::before{content:'';position:absolute;inset:0;background:url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M30 5 L55 55 L5 55 Z' fill='none' stroke='rgba(255,255,255,0.03)' stroke-width='1'/%3E%3C/svg%3E") repeat;pointer-events:none}
.hero h1{font-family:"Noto Serif SC",serif;font-size:clamp(24px,5vw,34px);font-weight:700;letter-spacing:.02em;margin-bottom:10px;position:relative}
.hero .sub{font-size:14px;opacity:.8;letter-spacing:.05em;position:relative}
.hero .sts{display:flex;justify-content:center;gap:24px;margin-top:24px;flex-wrap:wrap;position:relative}
.hero .st{text-align:center;min-width:60px}.hero .sv{font-size:22px;font-weight:700;font-family:"Noto Serif SC",serif}.hero .sl{font-size:11px;opacity:.65;text-transform:uppercase;letter-spacing:.08em;margin-top:2px}
.tn{display:flex;background:var(--ca);border-bottom:1px solid var(--bo);position:sticky;top:0;z-index:100;overflow-x:auto;scrollbar-width:none}
.tn::-webkit-scrollbar{display:none}
.tb{flex:0 0 auto;padding:14px 16px;border:none;background:none;font-size:13px;color:var(--t2);cursor:pointer;border-bottom:2px solid transparent;transition:all .2s;font-family:inherit;white-space:nowrap}
.tb.ac{color:var(--f);border-bottom-color:var(--f);font-weight:600}
.tb .ti{display:block;font-size:18px;margin-bottom:2px}
.tc{display:none}.tc.ac{display:block;animation:fsi .35s ease}
@keyframes fsi{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:translateY(0)}}
.ti2{padding:20px 16px 32px;max-width:var(--mw);margin:0 auto}
.sc{background:var(--ca);border-radius:var(--r);box-shadow:var(--sh);padding:24px;margin-bottom:20px}
.st2{font-family:"Noto Serif SC",serif;font-size:19px;font-weight:700;color:var(--f);margin-bottom:16px;padding-bottom:12px;border-bottom:1px solid var(--bo)}
.si{font-size:15px;color:var(--t2);line-height:1.8}
.hl{list-style:none;display:flex;flex-wrap:wrap;gap:10px}
.hi{background:var(--tc);color:var(--s);padding:8px 16px;border-radius:20px;font-size:13px;font-weight:500}
.tl{position:relative;padding-left:40px}
.tl::before{content:'';position:absolute;left:17px;top:8px;bottom:8px;width:2px;background:linear-gradient(to bottom,var(--fl),var(--t));border-radius:1px}
.dc{position:relative;background:var(--ca);border-radius:var(--r);box-shadow:var(--sh);padding:20px;margin-bottom:24px}
.dc::before{content:'';position:absolute;left:-29px;top:24px;width:12px;height:12px;background:var(--f);border-radius:50%;border:3px solid var(--bg);box-shadow:0 0 0 2px var(--fl)}
.dh{display:flex;align-items:center;gap:12px;margin-bottom:12px}
.dn{background:var(--f);color:#fff;min-width:34px;height:34px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-weight:700;font-size:16px;flex-shrink:0;font-family:"Noto Serif SC",serif}
.dt{font-family:"Noto Serif SC",serif;font-size:17px;font-weight:600;color:var(--f)}
.wb{display:flex;align-items:center;gap:8px;padding:10px 14px;border-radius:var(--rs);margin-bottom:14px;font-size:12px;font-weight:500;flex-wrap:wrap}
.ws{background:linear-gradient(135deg,#FFF8E1,#FFECB3);color:#6D4C00}
.wc{background:linear-gradient(135deg,#ECEFF1,#CFD8DC);color:#37474F}
.wr{background:linear-gradient(135deg,#E3F2FD,#BBDEFB);color:#0D47A1}
.wi{font-size:20px}
.stc{background:var(--bg);border-radius:var(--rs);padding:14px 16px;margin-bottom:10px;border-left:3px solid var(--fl)}
.sn{font-size:15px;font-weight:600;margin-bottom:2px}
.sm{font-size:12px;color:var(--t2);margin-bottom:6px}
.sa{display:flex;gap:8px;margin-top:10px;flex-wrap:wrap}
.b{display:inline-flex;align-items:center;gap:5px;padding:8px 18px;border-radius:20px;font-size:13px;font-weight:500;text-decoration:none;cursor:pointer;border:none;font-family:inherit;transition:all .2s}
.bp{background:var(--f);color:#fff}
.bo2{background:transparent;color:var(--f);border:1.5px solid var(--f)}
.ba{background:var(--t);color:#fff}
.bl{padding:12px 28px;font-size:15px;border-radius:24px}
.tp{text-align:center;padding:4px 0 8px;position:relative;z-index:1}
.tb2{display:inline-flex;align-items:center;gap:6px;background:var(--tc);padding:6px 14px;border-radius:14px;font-size:12px;color:var(--s);font-weight:500}
.hc{background:linear-gradient(135deg,var(--tc),#E8D9C0);border-radius:var(--rs);padding:14px 16px;margin-top:10px;display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:10px}
.hn{font-size:14px;font-weight:600;color:var(--s)}
.mrc{background:linear-gradient(135deg,#EDF4F8,#E8F0F5);border:1.5px solid #6A9CB5;border-radius:var(--r);padding:20px;margin-bottom:20px;display:none;animation:fsi .4s ease}
.mrc.sh{display:block}
.mrc h3{font-family:"Noto Serif SC",serif;font-size:17px;color:var(--f);margin-bottom:8px}
.mrc .rd{font-size:16px;font-weight:600;color:var(--w);margin-bottom:12px}
.mrc .ra{display:flex;gap:10px;flex-wrap:wrap}
.mpl{display:grid;gap:10px;margin-top:16px}
.mpi{background:var(--ca);border-radius:var(--rs);padding:14px 16px;box-shadow:var(--sh);display:flex;justify-content:space-between;align-items:center;gap:10px;flex-wrap:wrap}
.mpi .pn{font-size:14px;font-weight:600}
.mpi .pd{font-size:11px;color:var(--tm);background:var(--bg);padding:2px 10px;border-radius:10px}
.mfw{border-radius:var(--r);overflow:hidden;box-shadow:var(--sh);margin-bottom:20px}
.mfw iframe{width:100%;height:50vh;min-height:350px;border:none}
.ck{list-style:none;display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:10px}
.ck li{display:flex;align-items:flex-start;gap:10px;padding:10px 14px;background:var(--bg);border-radius:var(--rs);font-size:14px;border-left:3px solid var(--su)}
.ci{color:var(--su);font-weight:700;flex-shrink:0}
.pc{list-style:none}
.pc li{padding:12px 16px;margin-bottom:8px;background:#FFF8EC;border-radius:var(--rs);font-size:14px;border-left:3px solid var(--t);display:flex;align-items:flex-start;gap:10px}
.wi2{color:var(--t);font-size:18px;flex-shrink:0}
.ac2{margin-bottom:8px}
.ah{width:100%;background:var(--ca);border:1px solid var(--bo);border-radius:var(--rs);padding:16px 20px;font-size:15px;font-weight:600;cursor:pointer;text-align:left;display:flex;justify-content:space-between;align-items:center;font-family:inherit;color:var(--tx);transition:all .2s}
.ah:hover{border-color:var(--fl)}
.ah .ar{transition:transform .3s;font-size:12px;color:var(--tm)}
.ah.op .ar{transform:rotate(180deg)}
.ab{max-height:0;overflow:hidden;transition:max-height .4s,padding .3s;background:var(--bg);border-radius:0 0 var(--rs) var(--rs);font-size:14px;color:var(--t2);line-height:1.9}
.ab.op{max-height:2000px;padding:16px 20px}
.ab ul{padding-left:20px;margin:8px 0}.ab li{margin-bottom:6px}
.eg{display:grid;grid-template-columns:repeat(auto-fill,minmax(180px,1fr));gap:12px;margin-top:16px}
.ec2{background:var(--db);border:1px solid #F5D0CC;border-radius:var(--rs);padding:16px;text-align:center}
.ec2 .ei2{font-size:28px;margin-bottom:6px}.ec2 .en2{font-size:13px;font-weight:600;margin-bottom:4px}
.ec2 .ep{font-size:20px;font-weight:700;color:var(--dg);font-family:"Noto Serif SC",serif;letter-spacing:.03em}
.ec2 .ep a{color:var(--dg);text-decoration:none}
.ft{text-align:center;padding:32px 20px 28px;background:var(--fd);color:rgba(255,255,255,.85);font-size:13px}
.ft .br{font-family:"Noto Serif SC",serif;font-size:16px;font-weight:600;margin-bottom:4px}
.ft .tg{opacity:.65;margin-bottom:18px;font-size:12px;letter-spacing:.04em}
.ft .cb2{display:inline-block;padding:10px 28px;background:#fff;color:var(--f);border-radius:24px;text-decoration:none;font-weight:600;font-size:14px;transition:all .2s}
@media(max-width:767px){.ti2{padding:16px 12px 24px}.sc{padding:18px 16px}.ck{grid-template-columns:1fr}.eg{grid-template-columns:1fr 1fr}.hero .sts{gap:14px}.hero .sv{font-size:18px}}
@media(min-width:768px){.tb{padding:15px 24px;font-size:14px}.ck{grid-template-columns:repeat(2,1fr)}}
"""

JS = """function switchTab(n,b){document.querySelectorAll('.tb').forEach(function(x){x.classList.remove('ac')});document.querySelectorAll('.tc').forEach(function(x){x.classList.remove('ac')});if(b)b.classList.add('ac');else{var x=document.querySelector('.tb[data-tab=\"'+n+'\"]');if(x)x.classList.add('ac')}var c=document.getElementById(n);if(c)c.classList.add('ac');if(n==='map'&&window._pr){showRouteCard(window._pr.lng,window._pr.lat,window._pr.name,window._pr.info)}}
document.addEventListener('DOMContentLoaded',function(){document.querySelectorAll('.tb').forEach(function(b){b.addEventListener('click',function(){switchTab(this.getAttribute('data-tab'),this)})})})
var _pr=null,_ml=null
function navigateToMap(lng,lat,name,info){_pr={lng:lng,lat:lat,name:name,info:info};switchTab('map')}
function showRouteCard(lng,lat,name,info){var c=document.getElementById('routeCard'),d=document.getElementById('routeDest'),n=document.getElementById('routeNavBtn'),f=document.getElementById('routeFrom');if(!c||!d||!n)return;c.classList.add('show');d.textContent='目的地：'+name+(info?' ('+info+')':'');var u='https://uri.amap.com/navigation?to='+lng+','+lat+','+encodeURIComponent(name)+'&mode=car&callnative=1';if(_ml){u+='&from='+_ml.lng+','+_ml.lat+','+encodeURIComponent('我的位置');f.textContent='起点：我的位置'}else{f.textContent='默认起点：兴义市区 · 点击「使用我的位置」获取实时定位'}n.href=u}
function useMyLocation(){var f=document.getElementById('routeFrom');if(!navigator.geolocation){f.textContent='浏览器不支持定位';return}f.textContent='正在获取位置...';navigator.geolocation.getCurrentPosition(function(p){_ml={lng:p.coords.longitude,lat:p.coords.latitude};f.textContent='起点：我的位置（已获取）';if(_pr)showRouteCard(_pr.lng,_pr.lat,_pr.name,_pr.info)},function(){f.textContent='无法获取位置，使用默认起点'},{enableHighAccuracy:true,timeout:10000,maximumAge:300000})}
function toggleAccordion(h){var b=h.nextElementSibling,o=b.classList.contains('op');document.querySelectorAll('.ab').forEach(function(x){x.classList.remove('op')});document.querySelectorAll('.ah').forEach(function(x){x.classList.remove('op')});if(!o){b.classList.add('op');h.classList.add('op')}}
"""

def nl(lng,lat,name,m="car"):
    if not lng or not lat: return "javascript:void(0)"
    return f"https://uri.amap.com/navigation?to={lng},{lat},{name}&mode={m}&callnative=1"

def aml(lng,lat,name):
    if not lng or not lat: return "javascript:void(0)"
    return f"https://uri.amap.com/marker?position={lng},{lat}&name={name}&zoom=14&callnative=0"

def wc(d):
    if not d: return 'ws'
    s=str(d).lower()
    for w in ['雨','rain','雪','snow']:
        if w in s: return 'wr'
    for w in ['云','阴','cloud','overcast']:
        if w in s: return 'wc'
    return 'ws'

def we(d):
    if not d: return '☀️'
    s=str(d)
    if '雨' in s or 'rain' in s.lower(): return '🌧️'
    if '雪' in s or 'snow' in s.lower(): return '❄️'
    if '云' in s or 'cloud' in s.lower(): return '⛅'
    if '阴' in s or 'overcast' in s.lower(): return '☁️'
    return '☀️'

def esc(s):
    return str(s).replace('&','&amp;').replace('<','&lt;').replace('>','&gt;').replace('"','&quot;')

def tab_overview(trip):
    p=[]
    ov=trip.get('overview','')
    if ov:
        p.append(f'<div class="sc"><div class="st2">行程简介</div><div class="si">{ov.replace(chr(10),"<br>")}</div></div>')
    else:
        days=trip.get('days',[]);stops=[]
        for d in days:
            for s in d.get('stops',[]): stops.append(s['name'])
        sp='、'.join(stops[:8])
        if len(stops)>8: sp+=f'等{len(stops)}个景点'
        p.append(f'<div class="sc"><div class="st2">行程简介</div><div class="si">{trip.get("total_days",0)}天{trip.get("stops_count",0)}站深度体验，串联{sp}，全程专车品质出行。</div></div>')
    hl=trip.get('highlights',[])
    if hl:
        items=''.join(f'<li class="hi">{esc(h)}</li>' for h in hl)
        p.append(f'<div class="sc"><div class="st2">行程亮点</div><ul class="hl">{items}</ul></div>')
    bg=trip.get('background','')
    if bg: p.append(f'<div class="sc"><div class="st2">目的地背景</div><div class="si">{bg.replace(chr(10),"<br>")}</div></div>')
    return '\n'.join(p) if p else '<div class="sc"><div class="si">暂无概览信息</div></div>'

def tab_itinerary(trip):
    days=trip.get('days',[]);tr=trip.get('transport',[])
    if not days: return '<div class="sc"><div class="si">暂无行程数据</div></div>'
    dp=[]
    for day in days:
        w=day.get('weather',{});wb=''
        if w:
            wb=f'<div class="wb {wc(w.get("day_weather",w.get("day","")))}"><span class="wi">{we(w.get("day_weather",w.get("day","")))}</span><span>{esc(w.get("day_weather",w.get("day","")))} {esc(w.get("high",""))}°/{esc(w.get("low",""))}°</span><span>· AQI {esc(w.get("aqi","-"))} {esc(w.get("air_level",""))}</span></div>'
        sh=''
        sl=day.get('stops',[])
        for si,s in enumerate(sl):
            dur=f' · 建议游玩 {s["duration"]}小时' if s.get('duration') else ''
            sh+=f'<div class="stc"><div class="sn">📍 {esc(s["name"])}</div><div class="sm">{dur}</div><div class="sa"><a href="javascript:void(0)" class="b bp" onclick="navigateToMap({s.get("lng","null")},{s.get("lat","null")},\'{esc(s["name"])}\',\'{dur.strip()}\')">🗺️ 导航前往</a></div></div>'
            if si<len(sl)-1:
                a,b=sl[si],sl[si+1];tf=None
                for t in tr:
                    if t.get('from')==a['name'] and t.get('to')==b['name']: tf=t;break
                if tf: sh+=f'<div class="tp"><span class="tb2">🚗 {tf.get("distance_km","")}km · {tf.get("duration_min","")}分钟</span></div>'
                else: sh+='<div class="tp"><span class="tb2">↓ 前往下一站</span></div>'
        hh=''
        if day.get('hotel'):
            hh=f'<div class="hc"><div class="hn">🏨 {esc(day["hotel"])}</div><a href="{nl(day.get("hotel_lng"),day.get("hotel_lat"),day["hotel"])}" class="b bo2">🗺️ 导航前往</a></div>'
        dp.append(f'<div class="dc"><div class="dh"><div class="dn">{day["day"]}</div><div class="dt">{esc(day["title"])}</div></div>{wb}{sh}{hh}</div>')
    return f'<div class="tl">{"".join(dp)}</div>'

def tab_map(trip):
    days=trip.get('days',[]);pois=[]
    for day in days:
        for s in day.get('stops',[]):
            if s.get('lng'): pois.append({**s,'day':day['day'],'tp':'stop'})
        if day.get('hotel') and day.get('hotel_lng'):
            pois.append({'name':day['hotel'],'lng':day.get('hotel_lng'),'lat':day.get('hotel_lat'),'day':day['day'],'tp':'hotel'})
    if not pois: return '<div class="sc"><div class="si">暂无地图数据</div></div>'
    p=[f'''<div class="mrc" id="routeCard">
<h3>📍 路线规划</h3>
<div class="rd" id="routeDest">选择一个目的地</div>
<div class="ra">
<a href="#" id="routeNavBtn" class="b ba bl" target="_blank">🗺️ 打开高德地图导航</a>
<button class="b bo2" onclick="useMyLocation()">📍 使用我的位置</button>
</div>
<div style="margin-top:10px;font-size:12px;color:var(--tm)" id="routeFrom">默认起点：兴义市区 · 点击「使用我的位置」获取实时定位</div>
</div>''']
    c=pois[0]
    p.append(f'<div class="mfw"><iframe src="{aml(c["lng"],c["lat"],"行程总览")}" title="行程地图" loading="lazy"></iframe></div>')
    pi=''
    for x in pois:
        icon='🏨' if x.get('tp')=='hotel' else '📍'
        pi+=f'<div class="mpi"><div><div class="pn">{icon} {esc(x["name"])}</div><div class="pd" style="margin-top:2px">Day {x["day"]}</div></div><div style="display:flex;gap:8px"><a href="{nl(x["lng"],x["lat"],x["name"])}" class="b bp" style="font-size:12px;padding:6px 14px">导航</a><button class="b bo2" style="font-size:12px;padding:6px 14px" onclick="navigateToMap({x["lng"]},{x["lat"]},\'{esc(x["name"])}\',\'\')">规划</button></div></div>'
    p.append(f'<div class="mpl">{pi}</div>')
    return '\n'.join(p)

def tab_pretrip(trip):
    p=[]
    ess=trip.get('essentials',[])
    if ess:
        items=''.join(f'<li><span class="ci">✓</span> {esc(e)}</li>' for e in ess)
        p.append(f'<div class="sc"><div class="st2">必备物品</div><ul class="ck">{items}</ul></div>')
    prc=trip.get('precautions',[])
    if prc:
        items=''.join(f'<li><span class="wi2">⚠️</span> {esc(x)}</li>' for x in prc)
        p.append(f'<div class="sc"><div class="st2">注意事项</div><ul class="pc">{items}</ul></div>')
    inc=trip.get('inclusions',[]);exc=trip.get('exclusions',[])
    if inc or exc:
        fp=[]
        if inc:
            items=''.join(f'<li><span class="ci">✓</span> {esc(x)}</li>' for x in inc)
            fp.append(f'<div style="margin-bottom:12px"><strong>费用包含</strong><ul class="ck" style="margin-top:8px">{items}</ul></div>')
        if exc:
            items=''.join(f'<li><span class="wi2">✗</span> {esc(x)}</li>' for x in exc)
            fp.append(f'<div><strong>费用不含</strong><ul class="pc" style="margin-top:8px">{items}</ul></div>')
        pn=trip.get('pricing_note','')
        ph=f'<div style="margin-top:12px;font-size:13px;color:var(--t2)">{esc(pn)}</div>' if pn else ''
        p.append(f'<div class="sc"><div class="st2">费用说明</div>{"".join(fp)}{ph}</div>')
    if not p: p.append('<div class="sc"><div class="si">暂无行前须知，请联系客服获取详细信息。</div></div>')
    return '\n'.join(p)

def tab_safety(trip):
    p=[]
    sf=trip.get('safety',{})
    sdef=[('protection','🛡️','户外防护措施'),('self_rescue','🩹','基础自救知识'),('disaster','🌪️','灾害天气提醒'),('emergency_procedures','🚨','意外事故处置流程')]
    hs=False
    for key,icon,title in sdef:
        ct=sf.get(key,'')
        if not ct: continue
        hs=True
        ch=ct.replace('\n','<br>')
        if '- ' in ct or '• ' in ct:
            lines=ct.split('\n');up=[]
            for line in lines:
                st=line.strip()
                if st.startswith('- ') or st.startswith('• '): up.append(f'<li>{esc(st[2:])}</li>')
                elif st: up.append(f'<br>{esc(st)}')
            if up: ch=f'<ul>{"".join(up)}</ul>'
        p.append(f'<div class="ac2"><button class="ah" onclick="toggleAccordion(this)"><span>{icon} {title}</span><span class="ar">▼</span></button><div class="ab">{ch}</div></div>')
    if not hs: p.append('<div class="sc"><div class="si" style="color:var(--tm);text-align:center;padding:20px">暂无详细安全指南。户外活动请注意安全，听从领队安排。</div></div>')
    ct2=trip.get('emergency_contacts',[])
    if not ct2: ct2=[{"name":"贵州之客客服","phone":"待补充","icon":"service"},{"name":"紧急救援","phone":"110 / 120","icon":"emergency"}]
    im={'service':'📞','emergency':'🚑','local':'🏔️','police':'👮','fire':'🚒','hospital':'🏥'}
    ec=''
    for c in ct2:
        ico=im.get(c.get('icon',''),'📞')
        ec+=f'<div class="ec2"><div class="ei2">{ico}</div><div class="en2">{esc(c["name"])}</div><div class="ep"><a href="tel:{c["phone"].replace(" ","")}">{esc(c["phone"])}</a></div></div>'
    p.append(f'<div class="sc"><div class="st2">📞 紧急联系方式</div><div class="eg">{ec}</div></div>')
    return '\n'.join(p)

def build(trip):
    title=esc(trip.get('title','行程方案'))
    td=trip.get('total_days',len(trip.get('days',[])))
    sc=trip.get('stops_count',0)
    df=trip.get('difficulty','适中')
    bs=trip.get('best_season','全年')
    return f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0,maximum-scale=1.0,user-scalable=no">
<meta name="description" content="{title} - 贵州之客黔西南深度游">
<title>{title} - 贵州之客</title>
<style>{CSS}</style>
</head>
<body>
<header class="hero">
<h1>{title}</h1>
<p class="sub">贵州之客 · 黔西南深度游专家</p>
<div class="sts"><div class="st"><div class="sv">{td}天</div><div class="sl">行程天数</div></div><div class="st"><div class="sv">{sc}站</div><div class="sl">景点体验</div></div><div class="st"><div class="sv">{esc(df)}</div><div class="sl">难度等级</div></div><div class="st"><div class="sv">{esc(bs)}</div><div class="sl">最佳季节</div></div></div>
</header>
<nav class="tn">
<button class="tb ac" data-tab="overview"><span class="ti">📋</span>行程概览</button>
<button class="tb" data-tab="itinerary"><span class="ti">🗓️</span>每日行程</button>
<button class="tb" data-tab="map"><span class="ti">🗺️</span>地图导航</button>
<button class="tb" data-tab="pretrip"><span class="ti">📝</span>行前须知</button>
<button class="tb" data-tab="safety"><span class="ti">🛡️</span>安全保障</button>
</nav>
<section id="overview" class="tc ac"><div class="ti2">{tab_overview(trip)}</div></section>
<section id="itinerary" class="tc"><div class="ti2">{tab_itinerary(trip)}</div></section>
<section id="map" class="tc"><div class="ti2">{tab_map(trip)}</div></section>
<section id="pretrip" class="tc"><div class="ti2">{tab_pretrip(trip)}</div></section>
<section id="safety" class="tc"><div class="ti2">{tab_safety(trip)}</div></section>
<footer class="ft">
<div class="br">贵州之客</div>
<div class="tg">让黔西南的美好触手可及</div>
<a href="weixin://contacts/profile/gzzhike2026" class="cb2">💬 咨询客服</a>
</footer>
<script>{JS}</script>
</body>
</html>'''

def main():
    p=argparse.ArgumentParser(description="Build trip landing page v2")
    p.add_argument("--trip",required=True);p.add_argument("--output",default="output/")
    args=p.parse_args()
    with open(args.trip) as f: trip=json.load(f)
    print(f"Building: {trip.get('title','N/A')}",file=sys.stderr)
    html=build(trip)
    os.makedirs(args.output,exist_ok=True)
    out=os.path.join(args.output,'index.html')
    with open(out,'w',encoding='utf-8') as f: f.write(html)
    print(f"OK {out} ({os.path.getsize(out)//1024}KB)",file=sys.stderr)
    print(out)

if __name__=='__main__': main()
