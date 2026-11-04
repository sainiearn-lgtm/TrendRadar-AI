<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>TrendRadar AI</title>
<style>
body{margin:0;background:#0b1020;color:#fff;font-family:Arial;padding:20px}
header{max-width:1000px;margin:auto}
h1{color:#8daaff}
main{max-width:1000px;margin:25px auto}
.card{background:#141c31;padding:18px;border-radius:14px;margin:12px 0;border:1px solid #263451}
button,select{padding:12px;border:0;border-radius:8px;margin:5px;background:#829cff;color:#081126;font-weight:bold}
button{cursor:pointer}
.meta{color:#aab8d0;font-size:13px}
input,textarea{width:95%;padding:12px;background:#0b1020;color:white;border:1px solid #444;border-radius:8px}
a{color:#9bb7ff}
</style>
</head>
<body>
<header>
<h1>🛰️ TrendRadar AI</h1>
<p>Daily Trending Content Finder</p>
</header>
<main>
<div class="card">
<h3>Today's Trending Topics</h3>
<select id="region">
<option value="IN">India</option>
<option value="US">Worldwide (US)</option>
<option value="GB">UK</option>
<option value="DE">Germany</option>
</select>
<button onclick="loadTrends()">Refresh Trends</button>
<p id="status">Loading...</p>
</div>
<div id="trends"></div>
<div class="card" id="scriptBox" style="display:none">
<h2>AI Script Generator</h2>
<p id="topic"></p>
<select id="language">
<option>Hinglish</option>
<option>Hindi</option>
<option>English</option>
</select>
<select id="format">
<option>Shorts (60 seconds)</option>
<option>Long video (5–10 minutes)</option>
</select>
<button onclick="generateScript()">Generate Script</button>
<p id="scriptStatus"></p>
<textarea id="output" rows="15"></textarea>
</div>
</main>
<script>
let selectedTopic="";
async function loadTrends(){
const status=document.getElementById("status");
const box=document.getElementById("trends");
status.textContent="Loading trends...";
box.innerHTML="";
try{
const region=document.getElementById("region").value;
const r=await fetch("/api/trends?region="+region);
const data=await r.json();
if(!data.trends.length){status.textContent="No trends found. Try again.";return;}
status.textContent=data.count+" topics found";
data.trends.forEach(t=>{
const card=document.createElement("div");
card.className="card";
const h=document.createElement("h3");
h.textContent=t.title+" | "+t.score+"/100";
const p=document.createElement("p");
p.textContent=t.summary||"Open source for details.";
const m=document.createElement("p");
m.className="meta";
m.textContent="Source: "+t.source;
const a=document.createElement("a");
a.href=t.url;a.target="_blank";a.textContent="Read Source ↗";
const b=document.createElement("button");
b.textContent="Create Video";
b.onclick=()=>openScript(t.title);
card.append(h,m,p,a,b);
box.appendChild(card);
});
}catch(e){status.textContent="Error: "+e.message;}
}
function openScript(t){
selectedTopic=t;
document.getElementById("topic").textContent="Topic: "+t;
document.getElementById("scriptBox").style.display="block";
document.getElementById("scriptBox").scrollIntoView();
}
async function generateScript(){
const status=document.getElementById("scriptStatus");
status.textContent="Generating...";
try{
const r=await fetch("/api/script",{
method:"POST",
headers:{"Content-Type":"application/json"},
body:JSON.stringify({
topic:selectedTopic,
language:document.getElementById("language").value,
format:document.getElementById("format").value
})
});
const d=await r.json();
document.getElementById("output").value=d.script||d.message||d.error||d.prompt||"Error";
status.textContent="Completed";
}catch(e){status.textContent="Error: "+e.message;}
}
loadTrends();
</script>
</body>
</html>
