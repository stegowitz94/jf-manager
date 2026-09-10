(function(){
  function initPicker(select){
    if(select.dataset.enhanced === '1') return;
    select.dataset.enhanced='1';
    select.classList.add('person-picker-native');

    const wrap=document.createElement('div'); wrap.className='person-picker';
    const selected=document.createElement('div'); selected.className='person-picker-selected';
    const input=document.createElement('input'); input.type='search'; input.autocomplete='off'; input.className='person-picker-input'; input.placeholder=select.dataset.placeholder||'Person suchen …';
    const suggestions=document.createElement('div'); suggestions.className='person-picker-suggestions'; suggestions.hidden=true;
    wrap.append(selected,input,suggestions); select.after(wrap);

    const options=()=>Array.from(select.options);
    function renderSelected(){
      selected.innerHTML='';
      options().filter(o=>o.selected).forEach(o=>{
        const chip=document.createElement('span'); chip.className='person-chip'; chip.textContent=o.textContent;
        const remove=document.createElement('button'); remove.type='button'; remove.setAttribute('aria-label',o.textContent+' entfernen'); remove.textContent='×';
        remove.addEventListener('click',()=>{o.selected=false; renderSelected(); renderSuggestions();});
        chip.appendChild(remove); selected.appendChild(chip);
      });
    }
    function renderSuggestions(){
      const q=input.value.trim().toLocaleLowerCase('de'); suggestions.innerHTML='';
      if(q.length<1){suggestions.hidden=true; return;}
      const matches=options().filter(o=>!o.selected && o.textContent.toLocaleLowerCase('de').includes(q)).slice(0,8);
      if(!matches.length){const empty=document.createElement('div'); empty.className='person-picker-empty'; empty.textContent='Keine passenden Personen gefunden.'; suggestions.appendChild(empty); suggestions.hidden=false; return;}
      matches.forEach(o=>{
        const btn=document.createElement('button'); btn.type='button'; btn.className='person-picker-option'; btn.textContent=o.textContent;
        btn.addEventListener('click',()=>{o.selected=true; input.value=''; renderSelected(); renderSuggestions(); input.focus();}); suggestions.appendChild(btn);
      });
      suggestions.hidden=false;
    }
    input.addEventListener('input',renderSuggestions);
    input.addEventListener('focus',renderSuggestions);
    input.addEventListener('keydown',e=>{if(e.key==='Escape'){suggestions.hidden=true; input.blur();}});
    document.addEventListener('click',e=>{if(!wrap.contains(e.target)) suggestions.hidden=true;});
    renderSelected();
  }
  function boot(){document.querySelectorAll('select.multi-person-source').forEach(initPicker);}
  if(document.readyState==='loading') document.addEventListener('DOMContentLoaded',boot); else boot();
})();
