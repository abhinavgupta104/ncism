
(function(){
  "use strict";
  var reduce=matchMedia("(prefers-reduced-motion: reduce)").matches;

  /* split hero headline */
  document.querySelectorAll("[data-split]").forEach(function(el){
    var w=el.textContent.trim().split(/\s+/);
    el.innerHTML=w.map(function(x,i){
      return '<span class="word"><span style="animation-delay:'+(0.06+i*0.06).toFixed(3)+'s">'+
        x.replace(/&/g,"&amp;").replace(/</g,"&lt;")+"</span></span>";
    }).join(" ");
  });

  /* notices */
  var N={
    notices:[["12 Aug 2026","Expression of Interest to conduct UG &amp; PG Electives","new"],
      ["06 Aug 2026","Amendment in Internship Completion for appearing in AIAPGET-2026","new"],
      ["28 Jul 2026","Submission of schemes to establish new colleges for A.Y. 2027-28","pdf"],
      ["19 Jul 2026","Constitution of the Internal Committee under the POSH Act, 2013","pdf"],
      ["04 Jul 2026","Establishment of new Ayurveda UG colleges with 60-seat intake","pdf"],
      ["21 Jun 2026","Revision of honorarium, TA/DA and accommodation for MARBISM experts","pdf"],
      ["09 Jun 2026","Implementation of Right to Practice of ISM practitioners","pdf"]],
    tenders:[["10 Aug 2026","Supply and installation of network infrastructure, Dhanwantari Bhawan","new"],
      ["30 Jul 2026","Annual maintenance contract for office equipment 2026-27","pdf"],
      ["14 Jul 2026","Engagement of agency for digitisation of Commission records","pdf"],
      ["02 Jul 2026","Housekeeping and security services — two-year contract","pdf"],
      ["15 Jun 2026","Corrigendum: extension of bid submission date for IT hardware","pdf"]],
    jobs:[["08 Aug 2026","Walk-in interview: Young Professional / Consultant (IT)","new"],
      ["25 Jul 2026","Vacancies for various posts on deputation basis","pdf"],
      ["11 Jul 2026","Corrigendum to recruitment notice for Junior Technical Officer","pdf"],
      ["27 Jun 2026","Contractual vacancies for JTO and MTS in NCISM","pdf"],
      ["13 Jun 2026","Advertisement for vacancy in CPMU, Ministry of Ayush","pdf"]],
    results:[["05 Aug 2026","Result for the posts of JTO and MTS in NCISM","ok"],
      ["22 Jul 2026","AACCC AIQ UG and PG counselling — final allotment","ok"],
      ["08 Jul 2026","National Ayurveda Dhanwantari Award 2026 — selected awardees","ok"],
      ["24 Jun 2026","Publication grant beneficiaries 2025-26","pdf"],
      ["10 Jun 2026","Affiliation of Ayurveda Gurukulams — approved list","pdf"]]
  };
  var F={"new":"New","pdf":"PDF","ok":"Result"},nl=document.getElementById("nlist");
  function drawN(k){
    nl.innerHTML=(N[k]||[]).map(function(r){
      return '<li><a href="#notices"><span class="d">'+r[0]+'</span><span class="t">'+r[1]+
        '</span><span class="flag '+r[2]+'">'+F[r[2]]+"</span></a></li>";
    }).join("");
  }
  drawN("notices");
  document.querySelectorAll(".tab").forEach(function(t){
    t.addEventListener("click",function(){
      document.querySelectorAll(".tab").forEach(function(x){x.setAttribute("aria-selected","false");});
      t.setAttribute("aria-selected","true");drawN(t.dataset.tab);
    });
  });

  /* college finder */
  var C=[["State Ayurveda Medical College, Pune","Ayurveda","Maharashtra",100,"Permitted"],
    ["Government Ayurveda College, Thrissur","Ayurveda","Kerala",75,"Permitted"],
    ["Rajkiya Ayurvedic Mahavidyalaya, Varanasi","Ayurveda","Uttar Pradesh",60,"Conditional"],
    ["Shri Dhanwantari Ayurveda Sansthan, Jaipur","Ayurveda","Rajasthan",60,"Permitted"],
    ["Sanjivani Institute of Ayurveda, Nagpur","Ayurveda","Maharashtra",60,"Denied"],
    ["Vaidyaratnam Ayurveda College, Kozhikode","Ayurveda","Kerala",50,"Permitted"],
    ["Government Ayurveda College, Bhubaneswar","Ayurveda","Odisha",60,"Permitted"],
    ["Ayurveda Mahavidyalaya, Ahmedabad","Ayurveda","Gujarat",100,"Permitted"],
    ["Rural Ayurveda Institute, Patna","Ayurveda","Bihar",50,"Denied"],
    ["Government Unani Medical College, Hyderabad","Unani","Telangana",60,"Permitted"],
    ["Tibbia Unani Institute, Lucknow","Unani","Uttar Pradesh",50,"Conditional"],
    ["State Unani Medical College, Bengaluru","Unani","Karnataka",60,"Permitted"],
    ["Hakim Ajmal Khan Unani College, Aligarh","Unani","Uttar Pradesh",40,"Denied"],
    ["Government Unani College, Bhopal","Unani","Madhya Pradesh",50,"Permitted"],
    ["Government Siddha Medical College, Palayamkottai","Siddha","Tamil Nadu",75,"Permitted"],
    ["Siddha Medical Institute, Chennai","Siddha","Tamil Nadu",60,"Permitted"],
    ["Agasthiyar Siddha College, Madurai","Siddha","Tamil Nadu",50,"Conditional"],
    ["Himalayan Sowa-Rigpa Institute, Leh","Sowa-Rigpa","Ladakh",30,"Permitted"],
    ["Central Institute of Sowa-Rigpa, Gangtok","Sowa-Rigpa","Sikkim",25,"Permitted"],
    ["Bodhi Sowa-Rigpa College, Dharamshala","Sowa-Rigpa","Himachal Pradesh",25,"Conditional"]];
  var tb=document.getElementById("ftbody"),fq=document.getElementById("fq"),fs=document.getElementById("fsys"),
      fst=document.getElementById("fstate"),fss=document.getElementById("fstatus"),fc=document.getElementById("fcount");
  C.map(function(c){return c[2];}).filter(function(v,i,a){return a.indexOf(v)===i;}).sort()
   .forEach(function(s){var o=document.createElement("option");o.textContent=s;fst.appendChild(o);});
  function esc(s){return String(s).replace(/[&<>]/g,function(c){return {"&":"&amp;","<":"&lt;",">":"&gt;"}[c];});}
  function drawC(){
    var q=fq.value.trim().toLowerCase();
    var rows=C.filter(function(c){
      if(q&&c[0].toLowerCase().indexOf(q)<0&&c[2].toLowerCase().indexOf(q)<0)return false;
      if(fs.value&&c[1]!==fs.value)return false;
      if(fst.value&&c[2]!==fst.value)return false;
      if(fss.value&&c[4]!==fss.value)return false;
      return true;});
    fc.textContent=rows.length+" of "+C.length+" shown";
    tb.innerHTML=rows.length?rows.map(function(c){
      return "<tr><td>"+esc(c[0])+"</td><td>"+esc(c[1])+"</td><td>"+esc(c[2])+
        "</td><td class='mono'>"+c[3]+"</td><td><span class='st "+c[4].toLowerCase()+"'>"+c[4]+"</span></td></tr>";
    }).join(""):'<tr><td colspan="5" class="tempty">No institutions match those filters.</td></tr>';
  }
  [fq,fs,fst,fss].forEach(function(e){e.addEventListener("input",drawC);});
  drawC();

  /* reveal */
  var rvs=document.querySelectorAll(".rv");
  if("IntersectionObserver" in window){
    var io=new IntersectionObserver(function(es){
      es.forEach(function(e){if(e.isIntersecting){e.target.classList.add("in");io.unobserve(e.target);}});
    },{threshold:.12,rootMargin:"0px 0px -40px 0px"});
    rvs.forEach(function(el){io.observe(el);});
  } else { rvs.forEach(function(el){el.classList.add("in");}); }
  addEventListener("load",function(){
    setTimeout(function(){
      document.querySelectorAll(".rv:not(.in)").forEach(function(el){
        var r=el.getBoundingClientRect();
        if(r.top<innerHeight&&r.bottom>0) el.classList.add("in");
      });
    },900);
  });

  /* ---------- horizontal scrollers: drag, buttons, progress, keys ---------- */
  function hookScroller(id,progId){
    var el=document.getElementById(id), prog=document.getElementById(progId);
    if(!el) return;
    function maxScroll(){ return Math.max(el.scrollWidth-el.clientWidth,0); }
    function step(){ var first=el.firstElementChild; return first?first.getBoundingClientRect().width:320; }
    function paint(){
      var m=maxScroll();
      if(prog) prog.style.width=(m>0?(el.scrollLeft/m)*100:0)+"%";
      document.querySelectorAll('.hs-btn[data-scroll="'+id+'"]').forEach(function(b){
        b.disabled = b.dataset.dir==="-1" ? el.scrollLeft<=2 : el.scrollLeft>=m-2;
      });
    }
    el.addEventListener("scroll",paint,{passive:true});
    addEventListener("resize",paint);
    paint();
    document.querySelectorAll('.hs-btn[data-scroll="'+id+'"]').forEach(function(b){
      b.addEventListener("click",function(){
        el.scrollBy({left:step()*(+b.dataset.dir),behavior:reduce?"auto":"smooth"});
      });
    });
    el.addEventListener("keydown",function(e){
      if(e.key==="ArrowRight"){e.preventDefault();el.scrollBy({left:step(),behavior:reduce?"auto":"smooth"});}
      if(e.key==="ArrowLeft"){e.preventDefault();el.scrollBy({left:-step(),behavior:reduce?"auto":"smooth"});}
    });
    /* pointer drag */
    var down=false,sx=0,sl=0,moved=0;
    el.addEventListener("pointerdown",function(e){
      if(e.pointerType==="touch") return;         /* let native touch scrolling work */
      down=true;moved=0;sx=e.clientX;sl=el.scrollLeft;el.setPointerCapture(e.pointerId);
    });
    el.addEventListener("pointermove",function(e){
      if(!down) return;
      var dx=e.clientX-sx; moved=Math.max(moved,Math.abs(dx));
      if(moved>4) el.classList.add("drag");
      el.scrollLeft=sl-dx;
    });
    function up(e){
      if(!down) return;
      down=false;
      try{el.releasePointerCapture(e.pointerId);}catch(_){}
      setTimeout(function(){el.classList.remove("drag");},0);
    }
    el.addEventListener("pointerup",up);
    el.addEventListener("pointercancel",up);
    el.addEventListener("click",function(e){ if(moved>4) e.preventDefault(); },true);
  }
  hookScroller("sysScroll","sysProg");
  hookScroller("archScroll","archProg");

  /* nav — click only (hover handled by pure CSS) */
  var navItems = document.querySelectorAll(".nav-inner ul > li");
  navItems.forEach(function(li){
    var btn = li.querySelector(".nav-btn");
    if(btn){
      btn.addEventListener("click",function(e){
        e.stopPropagation();
        var was = li.classList.contains("open");
        navItems.forEach(function(o){ o.classList.remove("open"); });
        if(!was) li.classList.add("open");
      });
    }
  });
  document.addEventListener("click",function(){ navItems.forEach(function(o){ o.classList.remove("open"); }); });
  document.addEventListener("keydown",function(e){ if(e.key==="Escape") navItems.forEach(function(o){ o.classList.remove("open"); }); });
  var nav=document.getElementById("nav"),ntg=document.getElementById("navtog");
  ntg.addEventListener("click",function(e){
    e.stopPropagation();
    var o=nav.classList.toggle("open"); ntg.setAttribute("aria-expanded",o?"true":"false");
  });

  /* scroll-collapse: pill nav */
  (function(){
    var lastY=0, ticking=false;
    function onScroll(){
      var y=window.scrollY||window.pageYOffset;
      if(y>80){
        nav.classList.add("scrolled");
      } else {
        nav.classList.remove("scrolled");
      }
      lastY=y;
      ticking=false;
    }
    window.addEventListener("scroll",function(){
      if(!ticking){requestAnimationFrame(onScroll);ticking=true;}
    },{passive:true});
    onScroll();
  })();

  /* ticker */
  var tt=document.getElementById("tickT"),tp=document.getElementById("tickP"),paused=false;
  tp.addEventListener("click",function(){
    paused=!paused;tt.style.animationPlayState=paused?"paused":"running";
    tp.textContent=paused?"▶":"❚❚";tp.setAttribute("aria-label",paused?"Play ticker":"Pause ticker");
  });

  /* text size */
  var S={small:"15px",normal:"16.5px",large:"18.5px"};
  document.querySelectorAll(".tool[data-font]").forEach(function(b){
    b.addEventListener("click",function(){
      document.body.style.fontSize=S[b.dataset.font];
      document.querySelectorAll(".tool[data-font]").forEach(function(x){x.setAttribute("aria-pressed","false");});
      b.setAttribute("aria-pressed","true");
    });
  });

  /* theme */
  var root=document.documentElement,tb2=document.getElementById("themeBtn"),
      tx=document.getElementById("themeTxt"),sys=matchMedia("(prefers-color-scheme: dark)");
  function dark(){var t=root.getAttribute("data-theme");return t?t==="dark":sys.matches;}
  function paintT(){var d=dark();tx.textContent=d?"Light":"Dark";
    tb2.setAttribute("aria-label",d?"Switch to light theme":"Switch to dark theme");}
  tb2.addEventListener("click",function(){
    var n=dark()?"light":"dark";root.setAttribute("data-theme",n);
    try{localStorage.setItem("ncism-theme",n);}catch(e){}
    paintT();
  });
  if(sys.addEventListener) sys.addEventListener("change",function(){if(!root.getAttribute("data-theme"))paintT();});
  paintT();

  /* language demo */
  var lb=document.getElementById("langBtn"),hi=false,
      h1=document.querySelector(".hero h1"),ld=document.querySelector(".hero .lede");
  var EN={h1:h1.innerHTML,ld:ld.textContent};
  var HI={h1:"भारतीय चिकित्सा का मानक।",
    ld:"आयोग आयुर्वेद, यूनानी, सिद्ध और सोवा-रिग्पा में शिक्षा और अभ्यास का नियमन करता है।"};
  lb.addEventListener("click",function(){
    hi=!hi;h1.innerHTML=hi?HI.h1:EN.h1;ld.textContent=hi?HI.ld:EN.ld;
    h1.style.fontFamily=hi?"var(--deva)":"";ld.style.fontFamily=hi?"var(--deva)":"";
    root.lang=hi?"hi":"en";
  });
})();
