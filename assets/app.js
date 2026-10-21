(()=>{"use strict";
const B=document.body.dataset,$=s=>document.querySelector(s),$$=s=>[...document.querySelectorAll(s)];
let MAN=null;

/* ---------- manifest (version, size, sha) ---------- */
async function loadManifest(){
  try{const r=await fetch("latest.json",{cache:"no-cache"});if(r.ok)MAN=await r.json();}catch(e){}
  if(!MAN)return;
  $$("[data-ver]").forEach(e=>e.textContent=MAN.version||"");
  const w=MAN.windows||{};
  $$("[data-size]").forEach(e=>e.textContent=w.size?(w.size/1048576).toFixed(1)+" MB":"");
  $$("[data-sha]").forEach(e=>e.textContent=w.sha256||"n/a");
  $$("[data-rel]").forEach(e=>e.textContent=MAN.released?"· "+MAN.released:"");
  const n=$("#notes");if(n&&MAN.notes)n.innerHTML=MAN.notes.map(x=>"<li>"+x.replace(/[<>&]/g,c=>({"<":"&lt;",">":"&gt;","&":"&amp;"}[c]))+"</li>").join("");
  const url=winUrl();if($("#dl-btn")){$("#dl-btn").href=url;$("#dl-direct").href=url;}
  const a=MAN.android;if(a&&a.url&&$("#android-row")){$("#android-row").hidden=false;$("#dl-android").href=a.url;}
}
function winUrl(){
  const w=(MAN&&MAN.windows)||{};
  if(w.url)return w.url;
  if(MAN&&MAN.version)return B.releaseBase+"v"+MAN.version+"/"+B.installer;
  return B.fallback;
}

/* ---------- in-page download with progress ---------- */
function setStatus(t){const s=$("#dl-status");if(s)s.textContent=t}
function bar(p){const b=$("#dl-bar");if(!b)return;b.hidden=false;b.firstElementChild.style.width=Math.round(p*100)+"%"}
function save(blob,name){const u=URL.createObjectURL(blob),a=document.createElement("a");a.href=u;a.download=name;document.body.appendChild(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(u),30000)}
function direct(url){const a=document.createElement("a");a.href=url;a.rel="noopener";document.body.appendChild(a);a.click();a.remove()}
let busy=false;
async function startDownload(){
  if(busy)return;busy=true;
  const url=winUrl(),w=(MAN&&MAN.windows)||{};
  setStatus("Starting download…");bar(0);
  try{
    const r=await fetch(url,{mode:"cors"});if(!r.ok||!r.body)throw 0;
    const total=+r.headers.get("content-length")||w.size||0,rd=r.body.getReader(),parts=[];let got=0;
    for(;;){const {done,value}=await rd.read();if(done)break;parts.push(value);got+=value.length;
      if(total){bar(got/total);setStatus("Downloading… "+Math.round(got/total*100)+"%  ("+(got/1048576).toFixed(1)+" MB)")}
      else setStatus("Downloading… "+(got/1048576).toFixed(1)+" MB")}
    const blob=new Blob(parts,{type:"application/octet-stream"});bar(1);
    let msg="Downloaded. Open the file to install.";
    if(w.sha256&&crypto.subtle&&blob.size<400e6){
      const h=[...new Uint8Array(await crypto.subtle.digest("SHA-256",await blob.arrayBuffer()))].map(b=>b.toString(16).padStart(2,"0")).join("");
      if(h!==w.sha256.toLowerCase()){setStatus("Checksum mismatch - file discarded. Please retry.");busy=false;return}
      msg="Downloaded and checksum verified ✓ Open the file to install.";
    }
    save(blob,B.installer);setStatus(msg);
  }catch(e){
    bar(1);setStatus("Download started by your browser - watch its download bar.");direct(url);
  }
  busy=false;
}
function initDownload(){
  const b=$("#dl-btn");if(!b)return;
  b.addEventListener("click",e=>{e.preventDefault();startDownload()});
  if(/[?&]auto=1/.test(location.search)&&location.pathname.endsWith("download.html"))setTimeout(startDownload,900);
}

/* ---------- announcement strip ---------- */
async function announce(){
  try{
    const r=await fetch("announcement.json",{cache:"no-cache"});if(!r.ok)return;const a=await r.json();
    if(!a.active||!(a.message||a.title))return;
    const id=a.id||"x";if(sessionStorage.getItem("ann-"+id))return;
    const el=$("#ann");el.textContent=[a.title,a.message].filter(Boolean).join(" - ");
    if(a.url&&/^https?:/.test(a.url)){const l=document.createElement("a");l.href=a.url;l.textContent=" "+(a.button||"Learn more");el.append(l)}
    const x=document.createElement("button");x.textContent="✕";x.setAttribute("aria-label","Dismiss");x.onclick=()=>{el.hidden=true;try{sessionStorage.setItem("ann-"+id,1)}catch(e){}};
    el.append(x);el.hidden=false;
  }catch(e){}
}

/* ---------- instant search (typo tolerant) ---------- */
let IDX=[];
const lev1=(a,b)=>{if(Math.abs(a.length-b.length)>1)return false;let i=0,j=0,d=0;while(i<a.length&&j<b.length){if(a[i]===b[j]){i++;j++;continue}if(++d>1)return false;
  if(a.length>b.length)i++;else if(a.length<b.length)j++;else{i++;j++}}return d+(a.length-i)+(b.length-j)<=1};
function score(it,q){const t=it.t.toLowerCase(),k=it.k.toLowerCase(),all=t+" "+k+" "+it.d.toLowerCase(),words=all.split(/[^a-z0-9.]+/);let s=0;
  for(const w of q){if(t.includes(w))s+=5;else if(k.includes(w))s+=3;else if(all.includes(w))s+=1;else if(w.length>=4&&words.some(x=>x.length>=3&&lev1(x,w)))s+=1;else return 0}return s}
async function initSearch(){
  const q=$("#q"),ul=$("#results");if(!q)return;let cur=-1,list=[];
  try{IDX=await (await fetch("search-index.json",{cache:"no-cache"})).json()}catch(e){}
  const esc=s=>s.replace(/[<>&"]/g,c=>({"<":"&lt;",">":"&gt;","&":"&amp;",'"':"&quot;"}[c]));
  function render(){
    const terms=q.value.toLowerCase().split(/\s+/).filter(Boolean);
    if(!terms.length){ul.hidden=true;return}
    list=IDX.map(i=>[score(i,terms),i]).filter(x=>x[0]).sort((a,b)=>b[0]-a[0]).slice(0,8).map(x=>x[1]);cur=-1;
    ul.innerHTML=list.length?list.map((i,n)=>`<li data-n="${n}"><a href="${i.u}">${esc(i.t)}<small>${esc(i.d)}</small></a></li>`).join(""):"<li><a>No match - try “download” or “compress”</a></li>";
    ul.hidden=false}
  q.addEventListener("input",render);q.addEventListener("focus",render);
  q.addEventListener("keydown",e=>{const li=[...ul.children];
    if(e.key==="ArrowDown"||e.key==="ArrowUp"){e.preventDefault();cur=(cur+(e.key==="ArrowDown"?1:-1)+li.length)%li.length;li.forEach((x,n)=>x.classList.toggle("on",n===cur))}
    else if(e.key==="Enter"){const t=list[Math.max(cur,0)];if(t)location.href=t.u}
    else if(e.key==="Escape"){ul.hidden=true;q.blur()}});
  document.addEventListener("click",e=>{if(!e.target.closest(".search"))ul.hidden=true});
  document.addEventListener("keydown",e=>{if(e.key==="/"&&!/INPUT|TEXTAREA/.test(document.activeElement.tagName)){e.preventDefault();q.focus()}});
}
loadManifest().then(initDownload);announce();initSearch();
})();
