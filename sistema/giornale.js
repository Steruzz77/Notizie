
(function(){
  var sheets=[].slice.call(document.querySelectorAll('.sheet')), N=sheets.length, cur=0, busy=false;
  var book=document.getElementById('book'), flap=document.getElementById('flap'), fsh=document.getElementById('fshadow');
  var edgeL=document.getElementById('edgeL'), edgeR=document.getElementById('edgeR');
  
  var prev=document.getElementById('prev'), next=document.getElementById('next'), pname=document.getElementById('pname'), pnum=document.getElementById('pnum');
  var bar=document.getElementById('bar'), pop=document.getElementById('pop'), openTerm=null;
  var calm=window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  function setBar(){document.documentElement.style.setProperty('--barh',bar.offsetHeight+'px')}
  setBar();window.addEventListener('resize',setBar);

  function paint(){
    pname.textContent=sheets[cur].dataset.name; pnum.textContent='Pagina '+(cur+1)+' di '+N;
    prev.disabled=cur===0; next.disabled=cur===N-1;
    
    edgeL.style.width=Math.min(8,cur*2.5)+'px'; document.getElementById('crL').hidden=cur===N-1; document.getElementById('crR').hidden=cur!==N-1; edgeR.style.width=Math.min(8,(N-1-cur)*2.5)+'px';
  }
  function closePop(){pop.hidden=true;if(openTerm)openTerm.setAttribute('aria-expanded','false');openTerm=null}

  // Disegna la piega: "top" è il foglio che si piega, "under" quello che appare sotto. x = posizione della piega.
  var T=null;
  function begin(dir){
    var to=cur+dir; if(to<0||to>=N)return false;
    closePop();
    var a=sheets[cur], b=sheets[to];
    b.scrollTop=0; b.hidden=false;
    var top=dir>0?a:b, under=dir>0?b:a;
    top.classList.add('top'); under.classList.add('under');
    flap.hidden=false; fsh.hidden=false;
    T={dir:dir,to:to,top:top,under:under,W:book.clientWidth,x:dir>0?book.clientWidth:0};
    render(T.x); return true;
  }
  function render(x){
    var W=T.W; x=Math.max(0,Math.min(W,x)); T.x=x;
    var v=Math.max(0,2*x-W);
    T.top.style.clipPath='inset(0 '+(W-v)+'px 0 0)';
    var fl=2*x-W, fw=W-x;
    flap.style.left=fl+'px'; flap.style.width=fw+'px';
    var k=Math.sin(Math.PI*x/W);
    flap.style.opacity=fw<1?0:1;
    fsh.style.left=x+'px'; fsh.style.opacity=(0.25+0.75*k).toFixed(2);
  }
  function finish(ok){
    var t=T; T=null;
    flap.hidden=true; fsh.hidden=true;
    t.top.style.clipPath=''; t.top.classList.remove('top'); t.under.classList.remove('top','under'); t.top.classList.remove('under');
    if(ok){sheets[cur].hidden=true; cur=t.to;} else {sheets[t.to].hidden=true;}
    sheets.forEach(function(s,i){s.hidden=i!==cur}); if(ok)sheets[cur].scrollTop=0;
    busy=false; paint();
  }
  function animateTo(target,ms,cb){
    var from=T.x, t0=null;
    function step(ts){ if(!t0)t0=ts; var p=Math.min(1,(ts-t0)/ms); var e=1-Math.pow(1-p,3);
      render(from+(target-from)*e); if(p<1)requestAnimationFrame(step); else cb(); }
    requestAnimationFrame(step);
  }
  function go(to,after){
    if(busy||to===cur||to<0||to>=N)return;
    if(calm){closePop();sheets[cur].hidden=true;cur=to;sheets[cur].hidden=false;sheets[cur].scrollTop=0;paint();if(after)after();return}
    // salta più pagine: gira una alla volta, veloce
    var dir=to>cur?1:-1; busy=true;
    (function one(){
      if(!begin(dir)){busy=false;return}
      var fast=Math.abs(to-cur)>1;
      animateTo(dir>0?0:T.W, fast?380:620, function(){ finish(true); busy=cur!==to; if(cur!==to){one()} else if(after)after(); });
    })();
  }
  prev.addEventListener('click',function(){go(cur-1)});
  next.addEventListener('click',function(){go(cur+1)});
  document.addEventListener('keydown',function(e){if(e.key==='ArrowRight')go(cur+1);if(e.key==='ArrowLeft')go(cur-1);if(e.key==='Escape')closePop(); if((e.key==='Enter'||e.key===' ')&&document.activeElement&&document.activeElement.classList.contains('term')){e.preventDefault();document.activeElement.click();}});

  // Trascinamento col dito: la pagina si piega seguendo il dito
  var sx=0,sy=0,dragging=false,decided=false,lastX=0,lastT=0,vel=0,pid=null;
  book.addEventListener('pointerdown',function(e){
    if(busy||e.button>0)return; if(e.target.closest('.term,a,.goto'))return;
    sx=e.clientX;sy=e.clientY;decided=false;dragging=false;pid=e.pointerId;lastX=e.clientX;lastT=performance.now();vel=0;
  });
  book.addEventListener('pointermove',function(e){
    if(pid!==e.pointerId||busy&&!dragging)return;
    var dx=e.clientX-sx, dy=e.clientY-sy;
    if(!decided){
      if(Math.abs(dx)<10&&Math.abs(dy)<10)return;
      decided=true;
      if(Math.abs(dx)>Math.abs(dy)*1.2){
        var dir=dx<0?1:-1;
        if(begin(dir)){dragging=true;busy=true;try{book.setPointerCapture(e.pointerId)}catch(_){}}
      }
      if(!dragging){pid=null;return}
    }
    if(!dragging)return;
    var now=performance.now(); vel=(e.clientX-lastX)/Math.max(1,now-lastT); lastX=e.clientX; lastT=now;
    var W=T.W;
    render(T.dir>0 ? W+dx*1.0 : dx*1.0);
  });
  function up(e){
    if(pid!==e.pointerId)return; pid=null;
    if(!dragging)return; dragging=false;
    var W=T.W, done = T.dir>0 ? (T.x<W*0.72||vel<-0.5) : (T.x>W*0.28||vel>0.5);
    if(T.dir>0&&vel>0.3)done=false; if(T.dir<0&&vel<-0.3)done=false;
    var target = done ? (T.dir>0?0:W) : (T.dir>0?W:0);
    animateTo(target,320,function(){finish(done)});
  }
  book.addEventListener('pointerup',up); book.addEventListener('pointercancel',up);

  // Sommario
  document.querySelectorAll('.goto').forEach(function(b){b.addEventListener('click',function(){go(+b.dataset.page)})});

  // Termini
  var pw=document.getElementById('pw'),pd=document.getElementById('pd');
  document.addEventListener('click',function(e){
    var t=e.target.closest('.term');
    if(t){ if(openTerm===t){closePop();return}
      if(openTerm)openTerm.setAttribute('aria-expanded','false');
      openTerm=t;t.setAttribute('aria-expanded','true');
      var w=t.textContent.trim();pw.textContent=w.charAt(0).toUpperCase()+w.slice(1);pd.textContent=t.dataset.d;pop.hidden=false;return; }
    if(e.target.closest('#px')||!e.target.closest('.pop .box'))closePop();
  });
  paint();
})();

// Se il giornale resta aperto in background (es. icona nella schermata Home), quando lo riapri
// dopo un po' si ricarica da solo, così mostra sempre l'ultima edizione.
(function(){
  var aperto=Date.now();
  document.addEventListener('visibilitychange',function(){
    if(document.visibilityState==='visible' && Date.now()-aperto>10*60*1000){ location.reload(); }
  });
})();
