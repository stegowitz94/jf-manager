(() => {
  const csrf=()=>document.cookie.split('; ').find(x=>x.startsWith('csrftoken='))?.split('=')[1]||'';

  // Command palette
  const palette=document.querySelector('[data-command-palette]'), input=document.querySelector('[data-command-input]'), results=document.querySelector('[data-command-results]');
  const openPalette=()=>{if(!palette)return;palette.hidden=false;setTimeout(()=>input?.focus(),0)};
  const closePalette=()=>{if(palette)palette.hidden=true};
  document.addEventListener('keydown',e=>{if((e.ctrlKey||e.metaKey)&&e.key.toLowerCase()==='k'){e.preventDefault();openPalette()} if(e.key==='Escape')closePalette()});
  document.querySelectorAll('[data-command-close]').forEach(x=>x.addEventListener('click',closePalette));
  let timer;
  input?.addEventListener('input',()=>{clearTimeout(timer);const q=input.value.trim();if(q.length<2){results.innerHTML='<p class="muted">Mindestens zwei Zeichen eingeben.</p>';return}timer=setTimeout(async()=>{results.innerHTML='<div class="loading-row"><i></i> Suche …</div>';try{const r=await fetch(`${window.JF_SEARCH_API}?q=${encodeURIComponent(q)}`,{headers:{'X-Requested-With':'fetch'}});const data=await r.json();results.innerHTML=data.results.length?data.results.map(x=>`<a class="command-result" href="${x.url}"><span><strong>${escapeHtml(x.title)}</strong><small>${escapeHtml(x.type)}${x.detail?' · '+escapeHtml(x.detail):''}</small></span><b>›</b></a>`).join(''):'<p class="muted">Keine Treffer.</p>'}catch{results.innerHTML='<p class="error">Suche konnte nicht geladen werden.</p>'}},180)});
  function escapeHtml(v){return String(v??'').replace(/[&<>'"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;'}[c]))}

  // Dashboard drag/drop
  const grid=document.querySelector('[data-dashboard-grid]');
  if(grid){let dragged=null;const widgets=[...grid.querySelectorAll('[data-dashboard-widget]')];widgets.forEach(w=>{w.addEventListener('dragstart',()=>{dragged=w;w.classList.add('is-dragging')});w.addEventListener('dragend',()=>{w.classList.remove('is-dragging');dragged=null;saveLayout()});w.addEventListener('dragover',e=>{e.preventDefault();if(!dragged||dragged===w)return;const rect=w.getBoundingClientRect();const before=e.clientY<rect.top+rect.height/2;grid.insertBefore(dragged,before?w:w.nextSibling);[...grid.querySelectorAll('[data-dashboard-widget]')].forEach((x,i)=>x.style.order=i+1)})});async function saveLayout(){const order=[...grid.querySelectorAll('[data-dashboard-widget]')].map(x=>x.dataset.widgetKey);try{await fetch(grid.dataset.layoutSaveUrl,{method:'POST',headers:{'Content-Type':'application/json','X-CSRFToken':csrf()},body:JSON.stringify({order})})}catch{}}}

  // configurable tables
  document.querySelectorAll('[data-configurable-table]').forEach(async wrap=>{
    const table=wrap.querySelector('table'), key=wrap.dataset.tableKey, api=wrap.dataset.prefUrl;if(!table||!key||!api)return;
    const columns=[...table.querySelectorAll('thead th[data-column]')].map(th=>({key:th.dataset.column,label:th.dataset.label||th.textContent.trim()}));
    let pref={};try{pref=await (await fetch(api)).json()}catch{}
    apply(pref);
    const scope=wrap.parentElement||wrap; const menu=wrap.querySelector('[data-column-menu]')||scope.querySelector('[data-column-menu]');if(menu){menu.innerHTML=columns.map(c=>`<label><input type="checkbox" value="${c.key}"> ${escapeHtml(c.label)}</label>`).join('');const visible=new Set(pref.visible_columns?.length?pref.visible_columns:columns.map(c=>c.key));menu.querySelectorAll('input').forEach(i=>{i.checked=visible.has(i.value);i.addEventListener('change',()=>{const vals=[...menu.querySelectorAll('input:checked')].map(x=>x.value);setColumns(vals,pref.column_order||[]);save({visible_columns:vals})})})}
    (wrap.querySelector('[data-page-size]')||scope.querySelector('[data-page-size]'))?.addEventListener('change',e=>{save({page_size:Number(e.target.value)}).then(()=>{const u=new URL(location.href);u.searchParams.set('page_size',e.target.value);u.searchParams.delete('page');location.href=u})});
    function apply(p){setColumns(p.visible_columns||[],p.column_order||[]);const ps=wrap.querySelector('[data-page-size]')||scope.querySelector('[data-page-size]');if(ps&&p.page_size)ps.value=String(p.page_size)}
    function setColumns(visible,order){const all=columns.map(c=>c.key);const vis=new Set(visible.length?visible:all);const ord=[...(order||[]).filter(x=>all.includes(x)),...all.filter(x=>!(order||[]).includes(x))];const rows=[...table.rows];ord.forEach((colKey,targetIndex)=>{rows.forEach(row=>{const cell=[...row.cells].find(c=>c.dataset.column===colKey);if(cell)row.appendChild(cell)})});rows.forEach(row=>[...row.cells].forEach(c=>{if(c.dataset.column)c.hidden=!vis.has(c.dataset.column)}))}
    async function save(part){pref={...pref,...part};try{await fetch(api,{method:'POST',headers:{'Content-Type':'application/json','X-CSRFToken':csrf()},body:JSON.stringify(part)})}catch{}}
  });

  // loading feedback for normal forms
  document.querySelectorAll('form').forEach(f=>f.addEventListener('submit',()=>{const b=f.querySelector('button[type="submit"],input[type="submit"]');if(b&&!b.dataset.noLoading){b.classList.add('is-loading');b.setAttribute('aria-busy','true')}}));
})();
