(()=>{"use strict";
const $=(s,r=document)=>r.querySelector(s),$$=(s,r=document)=>[...r.querySelectorAll(s)];
const REPO="Havenova-x/stegzpc",REL="https://github.com/"+REPO+"/releases/";
const reduce=matchMedia("(prefers-reduced-motion: reduce)").matches;
const ua=navigator.userAgent||"";
const platform=/Android/i.test(ua)?"android":/Windows/i.test(ua)?"pc":"other";
const root=document.documentElement;
const wait=ms=>new Promise(r=>setTimeout(r,reduce?Math.min(ms,120):ms));
const fmtMB=n=>n?(n/1048576).toFixed(1)+" MB":"";
const fmtN=n=>new Intl.NumberFormat().format(n);

/* ---------- theme ---------- */
function setTheme(t,save){
  root.dataset.theme=t;
  const m=$('meta[name="theme-color"]');if(m)m.content=t==="dark"?"#070b12":"#f6f8fb";
  const b=$("#theme");if(b)b.setAttribute("aria-label",t==="dark"?"Switch to light mode":"Switch to dark mode");
  if(save)try{localStorage.setItem("theme",t)}catch(e){}
}
setTheme(root.dataset.theme||"light");
$("#theme")?.addEventListener("click",()=>setTheme(root.dataset.theme==="dark"?"light":"dark",true));
matchMedia("(prefers-color-scheme: dark)").addEventListener?.("change",e=>{let s=null;try{s=localStorage.getItem("theme")}catch(x){}if(!s)setTheme(e.matches?"dark":"light")});

/* ---------- menu ---------- */
const menu=$("#menu"),nav=$("#nav");
menu?.addEventListener("click",()=>{const o=nav.classList.toggle("open");menu.setAttribute("aria-expanded",o)});
nav?.addEventListener("click",e=>{if(e.target.closest("a")){nav.classList.remove("open");menu?.setAttribute("aria-expanded","false")}});

/* ---------- scroll reveal ---------- */
if("IntersectionObserver"in window){
  const io=new IntersectionObserver(es=>es.forEach(e=>{if(e.isIntersecting){e.target.classList.add("in");io.unobserve(e.target)}}),{rootMargin:"0px 0px -8% 0px"});
  $$("[data-r]").forEach(el=>io.observe(el));
}else $$("[data-r]").forEach(el=>el.classList.add("in"));

/* ---------- smart button label ---------- */
$$("[data-smart]").forEach(el=>{
  if(platform==="pc")el.firstChild.textContent="Download for Windows";
  else if(platform==="android")el.firstChild.textContent="Download for Android";
});

/* ---------- release data ---------- */
const T={
  windows:{name:"StegZ-Setup.exe",url:REL+"latest/download/StegZ-Setup.exe",size:0,sha:"",ver:"",notes:[]},
  android:{name:"StegZ.apk",url:"",size:0,sha:"",ver:""}
};
const getJSON=async u=>{try{const r=await fetch(u,{cache:"no-cache"});return r.ok?await r.json():null}catch(e){return null}};
const ready=Promise.all([getJSON("latest.json"),getJSON("android.json")]).then(([m,a])=>{
  if(m){
    const w=m.windows||{};
    T.windows.ver=m.version||"";T.windows.size=w.size||0;T.windows.sha=w.sha256||"";T.windows.notes=m.notes||[];
    T.windows.url=w.url||(m.version?REL+"download/v"+m.version+"/StegZ-Setup.exe":T.windows.url);
  }
  if(a&&a.url){T.android.url=a.url;T.android.ver=a.version||"";T.android.size=a.size||0;T.android.sha=a.sha256||""}
});

/* ---------- download counts (GitHub public API, cached) ---------- */
async function counts(){
  const K="stegz-dl",now=Date.now();let c=null;
  try{c=JSON.parse(localStorage.getItem(K))}catch(e){}
  if(c&&now-c.t<18e5)return c;
  try{
    const r=await fetch("https://api.github.com/repos/"+REPO+"/releases?per_page=100",{headers:{Accept:"application/vnd.github+json"}});
    if(!r.ok)throw 0;
    let w=0,a=0;
    for(const rel of await r.json())for(const s of rel.assets||[]){
      const n=(s.name||"").toLowerCase();
      if(n.endsWith(".exe"))w+=s.download_count|0;else if(n.endsWith(".apk"))a+=s.download_count|0;
    }
    c={t:now,w,a};try{localStorage.setItem(K,JSON.stringify(c))}catch(e){}
    return c;
  }catch(e){return c}
}
function countUp(el,to){
  const box=el.closest(".count");box&&box.classList.add("on");
  if(reduce||to<2){el.textContent=fmtN(to);return}
  const t0=performance.now(),d=1100;
  (function f(t){const p=Math.min(1,(t-t0)/d),e=1-Math.pow(1-p,3);el.textContent=fmtN(Math.round(to*e));if(p<1)requestAnimationFrame(f)})(t0);
}
if($("[data-count]"))counts().then(c=>{
  if(!c)return;
  const v={total:c.w+c.a,win:c.w,android:c.a};
  $$("[data-count]").forEach(el=>{const n=v[el.dataset.count];if(n!=null)countUp(el,n)});
});

/* ---------- download page ---------- */
const grid=$(".platforms");
if(grid){
  grid.dataset.platform=platform;
  const cw=$("#card-windows"),ca=$("#card-android");
  const hint=$("#hint");
  if(platform==="pc"||platform==="android"){
    const first=platform==="pc"?cw:ca,second=platform==="pc"?ca:cw;
    first.classList.add("is-primary");second.classList.add("is-secondary");
    hint.textContent=platform==="pc"?"You're on a Windows PC, so the Windows installer is first.":"You're on an Android device, so the Android app is first.";
  }else hint.textContent="StegZ is available for Windows and Android. Choose the one that matches your device.";
  hint.classList.add("on");

  const put=(id,v)=>{const e=$("#"+id);if(e)e.textContent=v};
  ready.then(()=>{
    const w=T.windows,a=T.android;
    put("win-sub",["Windows 10 and 11",w.ver&&"Version "+w.ver,fmtMB(w.size)].filter(Boolean).join("  ·  "));
    if(w.sha){$("#win-sha").hidden=false;put("win-sha-v",w.sha)}
    if(w.notes.length){const d=$("#notes-box");d.hidden=false;put("notes-ver",w.ver);const ul=$("#notes");w.notes.forEach(n=>{const li=document.createElement("li");li.textContent=n;ul.append(li)})}
    if(a.url){
      put("an-sub",["Android phones and tablets (APK)",a.ver&&"Version "+a.ver,fmtMB(a.size)].filter(Boolean).join("  ·  "));
      if(a.sha){$("#an-sha").hidden=false;put("an-sha-v",a.sha)}
    }else{
      put("an-sub","Android app · coming soon");
      const b=$("#btn-android");b.setAttribute("aria-disabled","true");b.lastChild.textContent="Coming soon";
    }
  });

  $$("[data-copy]").forEach(b=>b.addEventListener("click",async()=>{
    const t=$("#"+b.dataset.copy).textContent;
    try{await navigator.clipboard.writeText(t);b.textContent="Copied";setTimeout(()=>b.textContent="Copy",1600)}catch(e){}
  }));

  /* mismatch popup */
  const dlg=$("#warn");
  const mismatch=t=>t==="android"?platform!=="android":platform!=="pc";
  function ask(t){
    const other=t==="android"?"windows":"android";
    const copy={
      "android-pc":["You're on a computer, but this is the Android version of StegZ (an APK). It installs only on Android phones and tablets and will not run on Windows. To use StegZ on this PC, download the Windows installer instead.","Get the Windows version"],
      "windows-android":["You're on an Android device, but this is the Windows installer (.exe). It will not run on a phone or tablet. To use StegZ here, download the Android app instead.","Get the Android version"],
      "android-other":["This is the Android version of StegZ (an APK). It installs only on Android phones and tablets, and your device doesn't look like one.",""],
      "windows-other":["This is the Windows installer (.exe). It runs only on Windows 10 and 11, and your device doesn't look like a Windows PC.",""]
    }[t+"-"+(platform==="pc"?"pc":platform==="android"?"android":"other")];
    $("#warn-text").textContent=copy[0];
    const sw=$("#warn-switch");sw.hidden=!copy[1];sw.textContent=copy[1];sw.value=other;
    dlg.returnValue="";
    return new Promise(res=>{
      dlg.addEventListener("close",()=>res(dlg.returnValue),{once:true});
      dlg.showModal();
    });
  }
  dlg.addEventListener("click",e=>{if(e.target===dlg)dlg.close("cancel")});

  /* preparing + download */
  let busy=false;
  async function request(t,auto){
    if(busy)return;
    if(mismatch(t)){
      if(auto)return;
      const r=await ask(t);
      if(r==="windows"||r==="android")return request(r,false);
      if(r!=="ok")return;
    }
    run(t);
  }
  async function run(t){
    busy=true;
    const card=t==="android"?ca:cw,btn=$(".btn",card),p=$(".prep",card),lis=$$("ol li",p),bar=$(".pbar i",p),res=$(".res",p);
    btn.setAttribute("aria-disabled","true");
    res.hidden=true;res.className="res";p.hidden=false;
    const mark=i=>{lis.forEach((l,n)=>l.className=n<i?"done":n===i?"active":"");bar.style.width=Math.min(100,(i+.6)/lis.length*100)+"%"};
    p.scrollIntoView({behavior:reduce?"auto":"smooth",block:"nearest"});
    mark(0);await ready;await wait(650);
    const g=T[t];
    mark(1);await wait(750);
    const ok=g.url.startsWith(REL)&&/^https:\/\/github\.com\//.test(g.url);
    if(!ok){
      lis.forEach(l=>l.className="");bar.style.width="0";
      res.className="res err";res.hidden=false;res.innerHTML="";
      const b=document.createElement("b");b.textContent="We couldn't confirm the download link.";
      const a=document.createElement("a");a.href=REL;a.textContent="Open the releases page";a.rel="noopener";
      res.append(b,"Please try again, or ",a,".");
      btn.removeAttribute("aria-disabled");busy=false;return;
    }
    mark(2);await wait(600);
    const a=document.createElement("a");a.href=g.url;a.rel="noopener";a.download=g.name;document.body.append(a);a.click();a.remove();
    mark(3);
    res.hidden=false;res.innerHTML="";
    const b=document.createElement("b");b.textContent="Your download has started.";
    const again=document.createElement("a");again.href=g.url;again.rel="noopener";again.textContent="Download again";
    res.append(b,g.name+(g.size?" ("+fmtMB(g.size)+"). ":". ")+"Check your browser's downloads. Nothing happening? ",again,".");
    btn.removeAttribute("aria-disabled");busy=false;
  }
  $("#btn-windows").addEventListener("click",e=>{e.preventDefault();request("windows")});
  $("#btn-android").addEventListener("click",e=>{e.preventDefault();if($("#btn-android").getAttribute("aria-disabled")!=="true")request("android")});

  if(/[?&]auto=1/.test(location.search)){
    history.replaceState(null,"",location.pathname);
    if(platform==="pc")setTimeout(()=>request("windows",true),500);
    else if(platform==="android")setTimeout(()=>request("android",true),500);
  }
}
})();
