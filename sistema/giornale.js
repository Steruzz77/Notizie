(function(){
  var root=document.documentElement, book=document.getElementById('book');
  var pages=[].slice.call(book.querySelectorAll('.page')), N=pages.length, cur=0;
  var prev=document.getElementById('prev'), next=document.getElementById('next'), where=document.getElementById('where'), pname=document.getElementById('pname'), pnum=document.getElementById('pnum');
  var idx=[].slice.call(document.querySelectorAll('.idx button'));
  var flapw=document.getElementById('flapw'), flap=document.getElementById('flap'), ush=document.getElementById('ush');
  var calm=window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  function get(k){try{return localStorage.getItem(k)}catch(e){return null}}
  function put(k,v){try{if(v===null)localStorage.removeItem(k);else localStorage.setItem(k,v)}catch(e){}}

  // Aggiorna barra, indice e pallini dopo un cambio di pagina
  function segna(){
    var p=pages[cur];
    where.className='where '+p.className.replace(/\b(page|top|under)\b/g,'').trim();
    pname.textContent=p.dataset.name; pnum.textContent='Pagina '+(cur+1)+' di '+N;
    prev.disabled=cur===0; next.disabled=cur===N-1;
    idx.forEach(function(b,k){b.setAttribute('aria-current',k===cur?'page':'false')});
    dots(); salva();
  }
  function show(i,y){
    if(i<0||i>=N)return;
    pages.forEach(function(p,k){p.hidden=k!==i});
    cur=i; pages[i].scrollTop=y||0; segna();
  }

  /* Pagina che si gira, come un foglio vero.
     Il dito tiene il bordo del foglio: la piega sta a metà strada tra il bordo di partenza e il dito.
     Il foglio sopra viene tagliato lungo la piega; il pezzo tagliato si ribalta e diventa il lembo,
     che mostra il retro della carta con la luce della curva; sotto si vede la pagina nuova con l'ombra. */
  var R=null;
  function el(cls,parent){var d=document.createElement('div');d.className=cls;if(parent)parent.appendChild(d);return d}
  function begin(to,oy){
    if(R||to===cur||to<0||to>=N)return false;
    closePop();
    var dir=to>cur?1:-1, a=pages[cur], b=pages[to];
    b.scrollTop=0; b.hidden=false;
    var top=dir>0?a:b, under=dir>0?b:a;
    top.classList.add('top'); under.classList.add('under'); book.classList.add('turning');
    var W=book.clientWidth, H=book.clientHeight, sc=top.scrollTop, BIG=Math.ceil(Math.hypot(W,H))*2;
    R={dir:dir,to:to,top:top,under:under,W:W,H:H,oy:oy,low:oy>H*.5,fx:dir>0?W:-W,fy:oy,BIG:BIG};
    // Il foglio che si gira è fatto di copie ferme della pagina: a ogni passo cambiano solo le posizioni,
    // così il telefono non deve ridisegnare niente e la girata resta fluida.
    flapw.textContent='';
    var src=top.querySelector('.in'), br=book.getBoundingClientRect(), sr=src.getBoundingClientRect();
    // la copia deve avere la stessa larghezza e la stessa posizione del testo vero, così va a capo uguale
    var cw=sr.width.toFixed(2), cx=(sr.left-br.left).toFixed(2), cy=(sr.top-br.top).toFixed(2);
    function copia(){var w=document.createElement('div');w.className='t-copia';w.style.width=cw+'px';w.style.transform='translate('+cx+'px,'+cy+'px)';var n=src.cloneNode(true);[].forEach.call(n.querySelectorAll('img'),function(i){i.removeAttribute('loading');i.decoding='sync'});w.appendChild(n);return w}
    R.sh=el('t-ush',flapw);
    R.clip=el('t-clip',flapw); R.clip.style.width=BIG+'px'; R.clip.style.height=2*BIG+'px';
    R.wrl=el('t-wrl',R.clip); R.wrl.style.width=W+'px'; R.wrl.style.height=H+'px';
    var kp=el('t-keep '+top.className.replace(/\b(page|top|under)\b/g,''),R.wrl), kin=copia(); kp.appendChild(kin); kp.style.backgroundPosition='0 0,0 '+(-sc)+'px,0 0';
    R.fl=el('t-flap',R.wrl);
    if(root.getAttribute('data-retro')!=='liscio'){
      var gp=el('gpaper',R.fl); gp.style.backgroundPosition='0 0,0 '+(-sc)+'px';
      var gi=el('gink',R.fl), gin=copia(); gi.appendChild(gin);
    }
    R.cv=el('t-curva',R.fl); R.cv.style.height=2*BIG+'px'; R.sh.style.height=2*BIG+'px';
    // la pagina vera resta visibile finché le foto della copia non sono pronte: niente lampo di foto vuote
    R.kp=kp; if(dir<0){top.style.visibility='hidden'}else kp.style.opacity='0';
    var pronti=[].map.call(kp.querySelectorAll('img'),function(i){return i.decode?i.decode().catch(function(){}):0});
    var via=function(){if(R&&R.kp===kp&&kp.style.opacity==='0'){kp.style.opacity='';top.style.visibility='hidden'}};
    Promise.all(pronti).then(function(){requestAnimationFrame(via)}); setTimeout(via,250);
    flapw.hidden=false; draw(R.fx,R.fy);
    return true;
  }
  function draw(fx,fy){
    var W=R.W,H=R.H, ox=W, oy=R.oy, BIG=R.BIG;
    var lim=.3*Math.abs(W-fx); fy=oy+Math.max(-lim,Math.min(lim,fy-oy));
    // un foglio vero non si piega dritto: il bordo si alza un po' in diagonale, più a metà giro
    var tilt=.13*(W-fx)*(fx+W)/W*(R.low?-1:1);
    fy=fy+tilt; R.fx=fx; R.fy=fy-tilt;
    var dx=ox-fx, dy=oy-fy, L=Math.hypot(dx,dy);
    if(L<1){dx=1;dy=0;L=1;fx=ox-1}
    var nx=dx/L, ny=dy/L, mx=(ox+fx)/2, my=(oy+fy)/2, th=Math.atan2(ny,nx)*180/Math.PI;
    var w=Math.max(8,Math.min(L/2,W)), k=Math.sin(Math.PI*Math.min(1,Math.max(0,(W-fx)/(2*W))));
    var at='translate('+mx.toFixed(1)+'px,'+my.toFixed(1)+'px) rotate('+th.toFixed(3)+'deg)';
    // ritaglio: tiene solo la parte del foglio che resta giù (prima della piega)
    R.clip.style.transform=at+' translate('+(-BIG)+'px,'+(-BIG)+'px)';
    R.wrl.style.transform='translate('+BIG+'px,'+BIG+'px) rotate('+(-th).toFixed(3)+'deg) translate('+(-mx).toFixed(1)+'px,'+(-my).toFixed(1)+'px)';
    // lembo: il foglio ribaltato lungo la piega
    var c=2*(mx*nx+my*ny);
    R.fl.style.transform='matrix('+[1-2*nx*nx,-2*nx*ny,-2*nx*ny,1-2*ny*ny,c*nx,c*ny].map(function(v){return v.toFixed(4)}).join(',')+')';
    R.cv.style.transform=at+' translate(0,'+(-BIG)+'px) scaleX('+(w/50).toFixed(3)+')';
    // ombra sulla pagina nuova, appena oltre la piega
    var sw=Math.min(70,w*.5);
    R.sh.style.transform=at+' translate(0,'+(-BIG)+'px) scaleX('+(sw/100).toFixed(3)+')';
    R.sh.style.opacity=((.45*k+.1)/.55).toFixed(2);
  }
  function finish(ok){
    var r=R; R=null;
    flapw.hidden=true; flapw.textContent='';
    r.top.style.visibility=''; r.top.classList.remove('top'); r.under.classList.remove('under'); book.classList.remove('turning');
    if(ok){pages[cur].hidden=true; pages[r.to].hidden=false; cur=r.to; segna()}
    else pages[r.to].hidden=true;
  }
  function animateTo(tx,ty,ms,done){
    if(calm){done();return}
    var sx=R.fx, sy=R.fy, t0=performance.now(), r=R, fatto=false;
    R.anim=true;
    function fine(){if(fatto)return;fatto=true;if(R===r){draw(tx,ty);done()}}
    (function step(now){
      if(fatto||R!==r)return;
      var t=Math.max(0,Math.min(1,(now-t0)/ms)), e=1-Math.pow(1-t,3);
      draw(sx+(tx-sx)*e, sy+(ty-sy)*e);
      if(t<1)requestAnimationFrame(step);else fine();
    })(t0);
    // se Safari smette di disegnare (app in secondo piano, risparmio energetico) la girata si chiude lo stesso
    setTimeout(fine,ms+400);
  }
  // fine del gesto: il foglio va avanti se è oltre metà o se il dito ha dato uno strappo
  function lascia(v){
    var ok=R.dir>0?(R.fx<R.W*.25||v<-.45):(R.fx>-R.W*.25||v>.45);
    var avanti=R.dir>0?ok:!ok;   // "avanti" = il foglio sopra finisce girato a sinistra
    animateTo(avanti?-R.W-4:R.W,R.oy,ok?380:300,function(){finish(ok)});
  }
  // girata con i tasti o dall'indice: parte dall'angolo in basso
  function go(i){
    if(i===cur||i<0||i>=N||R)return;
    if(calm){show(i);return}
    begin(i,book.clientHeight*.86);
    if(R.dir>0)animateTo(-R.W-4,R.oy,620,function(){finish(true)});
    else{R.fx=-R.W;animateTo(R.W,R.oy,620,function(){finish(true)})}
  }
  document.addEventListener('click',function(e){var g=e.target.closest('[data-go]');if(g){apri(false);go(+g.dataset.go)}});
  prev.addEventListener('click',function(){go(cur-1)}); next.addEventListener('click',function(){go(cur+1)});

  // Col dito: si decide dopo i primi millimetri. In verticale scorre la pagina, in orizzontale si gira il foglio.
  // I caroselli e le parole spiegate restano per conto loro.
  var P=null, noClick=false;
  function giu(id,x,y,t){
    // un gesto rimasto a metà (dito perso da Safari) non deve bloccare i successivi
    if(P&&performance.now()-P.lt>1500)P=null;
    if(R&&!R.anim&&!P)finish(false);
    if(R||P)return;
    // si può girare partendo anche da una parola spiegata o da un link: il tocco semplice li apre comunque
    if(t.closest('.track,input'))return;
    var b=book.getBoundingClientRect();
    P={id:id,sx:x,sy:y,oy:y-b.top,lock:null,lx:x,lt:performance.now(),v:0};
  }
  function muovi(id,x,y){
    if(!P||id!==P.id)return false;
    var dx=x-P.sx, dy=y-P.sy;
    if(P.lock===null){
      if(Math.abs(dx)<10&&Math.abs(dy)<10)return false;
      if(Math.abs(dx)>Math.abs(dy)*1.5){
        var to=cur+(dx<0?1:-1);
        if(begin(to,P.oy))P.lock='x';
        // oltre la prima o l'ultima pagina il foglio non si gira: lo diciamo, e il gesto non passa al browser
        else if(to<0||to>=N){P.lock='fine';
          if(to>=N)avvisa("Fine dell'edizione.",'Archivio',function(){apri(true);faccia(2)});else avvisa('Sei alla prima pagina.');}
        else{P=null;return false}
      }else{P=null;return false}
    }
    if(P.lock==='fine'||!R||R.anim)return true;
    var now=performance.now(); P.v=P.v*.6+.4*(x-P.lx)/Math.max(1,now-P.lt); P.lx=x; P.lt=now;
    var base=R.dir>0?R.W:-R.W;
    voglio(Math.max(-R.W,Math.min(R.W,base+dx*1.7)), P.oy+Math.max(-80,Math.min(80,dy*.5)));
    return true;
  }
  var raf=0, vx=0, vy=0;
  function voglio(x,y){vx=x;vy=y;if(!raf)raf=requestAnimationFrame(function(){raf=0;if(R&&!R.anim)draw(vx,vy)})}
  function su(id,annulla){
    if(!P||id!==P.id)return;
    var p=P; P=null;
    if(p.lock==='x'&&R&&!R.anim){if(raf){cancelAnimationFrame(raf);raf=0;draw(vx,vy)}noClick=true;setTimeout(function(){noClick=false},350);lascia(annulla?0:p.v)}
  }
  book.addEventListener('touchstart',function(e){if(e.touches.length===1){var t=e.touches[0];giu(t.identifier,t.clientX,t.clientY,e.target)}else P=null},{passive:true});
  book.addEventListener('touchmove',function(e){var t=e.changedTouches[0];if(P&&muovi(t.identifier,t.clientX,t.clientY)&&P&&P.lock)e.preventDefault()},{passive:false});
  book.addEventListener('touchend',function(e){su(e.changedTouches[0].identifier,false);if(P&&!e.touches.length)su(P.id,false)});
  book.addEventListener('touchcancel',function(e){su(e.changedTouches[0].identifier,true);if(P&&!e.touches.length)su(P.id,true)});
  book.addEventListener('pointerdown',function(e){if(e.pointerType==='mouse'&&e.button===0)giu('m',e.clientX,e.clientY,e.target)});
  window.addEventListener('pointermove',function(e){if(e.pointerType==='mouse')muovi('m',e.clientX,e.clientY)});
  window.addEventListener('pointerup',function(e){if(e.pointerType==='mouse')su('m',false)});
  book.addEventListener('click',function(e){if(noClick){e.stopPropagation();e.preventDefault()}},true);
  window.addEventListener('resize',function(){if(R&&!R.anim){finish(false)}});

  // Caroselli con i pallini
  function dots(){[].forEach.call(pages[cur].querySelectorAll('.car'),function(c){
    var tr=c.querySelector('.track'), d=c.querySelector('.dots'), n=tr.children.length;
    if(!d.children.length){for(var i=0;i<n;i++){var b=document.createElement('span');d.appendChild(b)}
      tr.addEventListener('scroll',function(){pallino(c)},{passive:true})}
    pallino(c)})}
  function pallino(c){var tr=c.querySelector('.track'), k=Math.round(tr.scrollLeft/Math.max(1,tr.clientWidth));
    [].forEach.call(c.querySelectorAll('.dots span'),function(s,i){s.classList.toggle('on',i===k)})}
  window.addEventListener('resize',dots);

  // Parole spiegate: la nota si appoggia vicino alla parola (sotto, o sopra se la parola è in basso) e segue la pagina
  var pop=document.getElementById('pop'),pbox=pop.querySelector('.box'),pw=document.getElementById('pw'),pd=document.getElementById('pd'),pm=document.getElementById('pmore'),pl=document.getElementById('pl'),open=null;
  document.querySelectorAll('.term').forEach(function(t){t.setAttribute('aria-expanded','false')});
  function closePop(){pop.hidden=true;if(open)open.setAttribute('aria-expanded','false');open=null}
  // la nota sta ferma in basso: si chiude solo se la parola esce dal foglio
  function piazza(){
    if(!open)return;
    var r=open.getBoundingClientRect(), b=book.getBoundingClientRect();
    if(r.bottom<b.top||r.top>b.bottom)closePop();
  }
  document.addEventListener('click',function(e){
    var t=e.target.closest('.term');
    if(t){if(open===t){closePop();return}if(open)open.setAttribute('aria-expanded','false');open=t;t.setAttribute('aria-expanded','true');
      var w=t.textContent.trim();pw.textContent=w.charAt(0).toUpperCase()+w.slice(1);pd.textContent=t.dataset.d;
      pl.hidden=true;pm.textContent='Approfondisci ▾';if(t.dataset.x){pm.hidden=false;pl.textContent=t.dataset.x}else pm.hidden=true;pop.hidden=false;piazza();return}
    if(e.target.closest('#pmore')){pl.hidden=!pl.hidden;pm.textContent=pl.hidden?'Approfondisci ▾':'Chiudi ▴';piazza();return}
    if(e.target.closest('#px')||!e.target.closest('.pop .box'))closePop();
  });
  book.addEventListener('scroll',piazza,true); window.addEventListener('resize',piazza);
  document.addEventListener('keydown',function(e){var t=e.target.closest&&e.target.closest('.term');if(t&&(e.key==='Enter'||e.key===' ')){e.preventDefault();t.click()}});

  // Indice in basso: tutte le pagine, tema e grandezza del testo
  var menu=document.getElementById('menu');
  // Sommario, Impostazioni e Archivio: tre facce della stessa scheda, che scorre di lato
  var views=document.getElementById('views'), facce=[].slice.call(views.children);
  function faccia(k){views.style.transform='translateX('+(-100*k/facce.length)+'%)';facce.forEach(function(f,i){f.inert=i!==k})}
  document.getElementById('toSet').addEventListener('click',function(){faccia(1)});
  document.getElementById('toArc').addEventListener('click',function(){faccia(2)});
  [].forEach.call(views.querySelectorAll('[data-som]'),function(b){b.addEventListener('click',function(){faccia(0)})});
  function apri(o){menu.hidden=!o;where.setAttribute('aria-expanded',String(o));if(o){closePop();faccia(0);menu.querySelector('.box').scrollTop=0}}
  where.addEventListener('click',function(){apri(menu.hidden)});
  document.getElementById('mx').addEventListener('click',function(){apri(false)});
  menu.addEventListener('click',function(e){if(!e.target.closest('.box'))apri(false)});
  function tema(v){if(v==='auto')root.removeAttribute('data-theme');else root.setAttribute('data-theme',v);put('corriere-tema',v==='auto'?null:v);segni()}
  function testo(v){root.setAttribute('data-testo',v);put('corriere-testo',v==='0'?null:v);segni()}
  function segni(){var t=root.getAttribute('data-theme')||'auto', s=root.getAttribute('data-testo')||'0';
    [].forEach.call(document.querySelectorAll('#segTema button'),function(b){b.setAttribute('aria-pressed',String(b.dataset.v===t))});
    [].forEach.call(document.querySelectorAll('#segTesto button'),function(b){b.setAttribute('aria-pressed',String(b.dataset.v===s))})}
  document.getElementById('segTema').addEventListener('click',function(e){var b=e.target.closest('button');if(b)tema(b.dataset.v)});
  document.getElementById('segTesto').addEventListener('click',function(e){var b=e.target.closest('button');if(b)testo(b.dataset.v)});
  testo(get('corriere-testo')||'0'); segni();
  // effetto carta: 0 liscia, 50 come di base, 100 il doppio
  var cr=document.getElementById('cartaR');
  function carta(v){v=+v;root.style.setProperty('--ca',(1-v/100).toFixed(2));cr.value=v;put('corriere-carta',v===50?null:String(v))}
  cr.addEventListener('input',function(){carta(cr.value)});
  carta(get('corriere-carta')||50);
  // foto: un involucro per la trama della carta; un tocco la ingrandisce, un altro la chiude
  [].forEach.call(document.querySelectorAll('img.ph'),function(i){var w=document.createElement('span');w.className='phw';i.parentNode.insertBefore(w,i);w.appendChild(i)});
  book.addEventListener('click',function(e){var i=e.target.closest('.phw');if(!i||noClick||R)return;var im=i.querySelector('img');
    var z=document.createElement('div');z.className='zoom';z.setAttribute('role','dialog');z.setAttribute('aria-label','Foto ingrandita');
    var c=im.cloneNode();c.removeAttribute('class');c.removeAttribute('onerror');z.appendChild(c);var t=document.createElement('small');t.textContent='Tocca per chiudere';z.appendChild(t);
    z.addEventListener('click',function(){z.remove()});document.body.appendChild(z)});
  // notizie stampate sul foglio (di base) o in schede, più separate tra loro
  function schede(v){if(v==='schede')root.removeAttribute('data-schede');else root.setAttribute('data-schede','stampa');put('corriere-schede',v==='schede'?'schede':null);
    [].forEach.call(document.querySelectorAll('#segSchede button'),function(b){b.setAttribute('aria-pressed',String(b.dataset.v===v))})}
  document.getElementById('segSchede').addEventListener('click',function(e){var b=e.target.closest('button');if(b)schede(b.dataset.v)});
  schede(get('corriere-schede')||'stampa');

  // Istruzioni per la schermata Home: si apre già sul telefono giusto
  var guide=document.getElementById('guide'), ua=navigator.userAgent, inst=document.getElementById('inst'), richiesta=null;
  var giaHome=window.navigator.standalone===true||window.matchMedia('(display-mode: standalone)').matches;
  function os(v){[].forEach.call(document.querySelectorAll('#segOs button'),function(b){b.setAttribute('aria-pressed',String(b.dataset.v===v))});
    [].forEach.call(guide.querySelectorAll('.steps'),function(o){o.hidden=o.dataset.os!==v});
    inst.hidden=!(v==='and'&&richiesta)}
  document.getElementById('segOs').addEventListener('click',function(e){var b=e.target.closest('button');if(b)os(b.dataset.v)});
  document.getElementById('homebtn').addEventListener('click',function(){apri(false);guide.hidden=false;document.getElementById('gok').hidden=!giaHome;os(/Android/i.test(ua)?'and':'ios')});
  document.getElementById('gx').addEventListener('click',function(){guide.hidden=true});
  guide.addEventListener('click',function(e){if(!e.target.closest('.box'))guide.hidden=true});
  window.addEventListener('beforeinstallprompt',function(e){e.preventDefault();richiesta=e});
  inst.addEventListener('click',function(){if(richiesta){richiesta.prompt();richiesta=null;inst.hidden=true}});

  // Avviso breve in basso
  var toast=document.getElementById('toast'), tt=document.getElementById('toastt'), tb=document.getElementById('toastb'), tTimer;
  function avvisa(msg,btn,fn){tt.textContent=msg;tb.hidden=!btn;if(btn){tb.textContent=btn;tb.onclick=function(){toast.hidden=true;fn()}}
    toast.hidden=false;clearTimeout(tTimer);tTimer=setTimeout(function(){toast.hidden=true},5000)}

  // Dove eri arrivato: vale solo per la stessa edizione; con un'edizione nuova si riparte dalla prima pagina
  var ED=book.dataset.ed, sTimer;
  function salva(){clearTimeout(sTimer);sTimer=setTimeout(function(){put('corriere-punto',JSON.stringify({ed:ED,p:cur,y:Math.round(pages[cur].scrollTop)}))},300)}
  book.addEventListener('scroll',function(e){if(e.target===pages[cur])salva()},true);

  var h=(location.hash.match(/^#p(\d+)$/)||[])[1], punto=null;
  try{punto=JSON.parse(get('corriere-punto')||'null')}catch(e){}
  if(book.dataset.arch){show(h?Math.min(N,Math.max(1,+h))-1:0);avvisa("Stai leggendo un'edizione passata.","Vai all'ultima",function(){location.href='../index.html'});salva=function(){};return}
  if(h){show(Math.min(N,Math.max(1,+h))-1)}
  else if(punto&&punto.ed===ED&&(punto.p>0||punto.y>300)){
    show(Math.min(N-1,punto.p),punto.y);
    avvisa('Sei tornato dove eri arrivato.','Vai alla prima',function(){go(0)});
  }else{
    show(0);
    if(punto&&punto.ed!==ED)avvisa('Nuova edizione: '+book.dataset.edl+'.');
  }
})();
;if(/schede=liscia/.test(location.search))document.documentElement.setAttribute("data-schede","liscia");
;(function(){
  // Meteo: le previsioni arrivano dal vivo da Open-Meteo, per i capoluoghi di regione e per Lumezzane e Brescia
  var box=document.querySelector('.wxmap'), t=box&&box.querySelector('.wxtab'); if(!box)return;
  var D=JSON.parse(document.getElementById('wxdati').textContent), V=null, g='oggi';
  function tipo(c){return c===0?'sole':c<=2?'parz':c===3?'nuvole':c<=48?'nebbia':c<=67||(c>=80&&c<=82)?'pioggia':c<=77||c===85||c===86?'neve':'temporale'}
  var DESC={0:'Sereno',1:'Poco nuvoloso',2:'Nuvole e schiarite',3:'Coperto',45:'Nebbia',48:'Nebbia con brina',51:'Pioviggine debole',53:'Pioviggine',55:'Pioviggine fitta',56:'Pioviggine gelata',57:'Pioviggine gelata',61:'Pioggia debole',63:'Pioggia',65:'Pioggia forte',66:'Pioggia gelata',67:'Pioggia gelata forte',71:'Neve debole',73:'Neve',75:'Neve forte',77:'Nevischio',80:'Rovesci deboli',81:'Rovesci',82:'Rovesci forti',85:'Rovesci di neve',86:'Forti rovesci di neve',95:'Temporale',96:'Temporale con grandine',99:'Temporale con grandine'};
  function ico(k){return D.ico[k]||D.ico.nuvole}
  function gr(v){return Math.round(v)+'°'}
  function disegna(){
    if(!V)return; var d=g==='oggi'?0:1;
    [].forEach.call(box.querySelectorAll('.cap'),function(el){var c=V[+el.dataset.i];var k=tipo(c.weather_code[d]);
      el.innerHTML='<circle class="bg" r="12"/><svg x="-10.5" y="-10.5" width="21" height="21" viewBox="0 0 32 32">'+ico(k).replace(/^<svg[^>]*>|<\/svg>$/g,'')+'</svg>'});
    ['n','c','s'].forEach(function(z){var mi=0,ma=0,n=0,cnt={};
      D.cap.forEach(function(c,i){if(c.z!==z)return;n++;mi+=V[i].temperature_2m_min[d];ma+=V[i].temperature_2m_max[d];var k=tipo(V[i].weather_code[d]);cnt[k]=(cnt[k]||0)+1});
      var best=Object.keys(cnt).sort(function(a,b){return cnt[b]-cnt[a]})[0], ch=box.querySelector('.zch[data-z="'+z+'"]');
      ch.querySelector('.zi').innerHTML=ico(best); ch.querySelector('b').textContent=gr(mi/n)+'–'+gr(ma/n)});
    var casa='';D.cap.forEach(function(c,i){if(c.z!=='l')return;var w=V[i].weather_code[d];
      casa+='<li><span class="ic">'+ico(tipo(w))+'</span><span class="lu">'+c.n+'<small>'+(DESC[w]||'')+'</small></span><b>'+gr(V[i].temperature_2m_min[d])+'–'+gr(V[i].temperature_2m_max[d])+'</b></li>'});
    [].forEach.call(box.querySelectorAll('.casa-l'),function(u){u.innerHTML=casa});
  }
  // i tasti prendono il giorno vero delle previsioni: se apri il giornale il giorno dopo, "Oggi" è davvero oggi
  function etichette(tt){var gg=['domenica','lunedì','martedì','mercoledì','giovedì','venerdì','sabato'];
    [].forEach.call(t.querySelectorAll('button'),function(b,i){var p=tt[i].split('-'),d=new Date(+p[0],p[1]-1,+p[2]);b.textContent=(i?'Domani':'Oggi')+' · '+gg[d.getDay()]+' '+d.getDate()})}
  var u='https://api.open-meteo.com/v1/forecast?latitude='+D.cap.map(function(c){return c.lat}).join(',')+'&longitude='+D.cap.map(function(c){return c.lon}).join(',')+'&daily=weather_code,temperature_2m_max,temperature_2m_min&timezone=Europe%2FRome&forecast_days=2';
  fetch(u).then(function(r){if(!r.ok)throw 0;return r.json()}).then(function(j){V=(Array.isArray(j)?j:[j]).map(function(x){return x.daily});box.removeAttribute('data-attesa');box.setAttribute('data-vivo','1');etichette(V[0].time);disegna()})
    .catch(function(){box.removeAttribute('data-attesa');box.setAttribute('data-vivo','0')});
  t.addEventListener('click',function(e){var b=e.target.closest('button');if(!b)return;g=b.dataset.g;
    [].forEach.call(t.querySelectorAll('button'),function(x){x.setAttribute('aria-pressed',String(x===b))});
    [].forEach.call(box.querySelectorAll('.gday'),function(x){x.hidden=x.dataset.g!==g});tip.hidden=true;disegna()});
  // tocco su un'icona: nome della città con minima e massima
  var tip=box.querySelector('.ctip'), mb=box.querySelector('.mapbox');
  box.querySelector('.itmap').addEventListener('click',function(e){
    // il dito è grosso: si prende l'icona più vicina al punto toccato
    var el=null,best=34*34;[].forEach.call(box.querySelectorAll('.cap'),function(c){var r=c.getBoundingClientRect(),dx=r.left+r.width/2-e.clientX,dy=r.top+r.height/2-e.clientY,q=dx*dx+dy*dy;if(q<best){best=q;el=c}});
    if(!el||!V){tip.hidden=true;return}
    var i=+el.dataset.i,c=D.cap[i],d=g==='oggi'?0:1,w=V[i].weather_code[d];
    tip.innerHTML='<b>'+c.n+'</b> '+gr(V[i].temperature_2m_min[d])+'–'+gr(V[i].temperature_2m_max[d])+'<small>'+(DESC[w]||'')+'</small>';
    var r=el.getBoundingClientRect(),b=mb.getBoundingClientRect();tip.hidden=false;
    var x=Math.max(0,Math.min(b.width-tip.offsetWidth,r.left-b.left+r.width/2-tip.offsetWidth/2));tip.style.left=x+'px';tip.style.top=(r.top-b.top-tip.offsetHeight-6)+'px'});
})();
