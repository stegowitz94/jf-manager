(function () {
  'use strict';

  function initPicker(select) {
    if (!select || select.dataset.enhanced === '2') return;
    select.dataset.enhanced = '2';

    // Native Mehrfachauswahl nur nach erfolgreicher JS-Initialisierung ausblenden.
    // Damit bleibt ohne JavaScript ein funktionierender Fallback erhalten.
    select.hidden = true;
    select.setAttribute('aria-hidden', 'true');
    select.tabIndex = -1;

    const wrap = document.createElement('div');
    wrap.className = 'person-picker person-picker-v2';

    const selected = document.createElement('div');
    selected.className = 'person-picker-selected';
    selected.setAttribute('aria-live', 'polite');

    const inputWrap = document.createElement('div');
    inputWrap.className = 'person-picker-input-wrap';

    const input = document.createElement('input');
    input.type = 'search';
    input.autocomplete = 'off';
    input.className = 'person-picker-input';
    input.placeholder = select.dataset.placeholder || 'Person suchen …';
    input.setAttribute('role', 'combobox');
    input.setAttribute('aria-autocomplete', 'list');
    input.setAttribute('aria-expanded', 'false');

    const count = document.createElement('span');
    count.className = 'person-picker-count';

    inputWrap.append(input, count);

    const suggestions = document.createElement('div');
    suggestions.className = 'person-picker-suggestions';
    suggestions.hidden = true;
    suggestions.setAttribute('role', 'listbox');

    wrap.append(selected, inputWrap, suggestions);
    select.after(wrap);

    let activeIndex = -1;
    const options = () => Array.from(select.options).filter(o => o.value !== '');

    function dispatchChange() {
      select.dispatchEvent(new Event('change', { bubbles: true }));
    }

    function updateCount() {
      const n = options().filter(o => o.selected).length;
      count.textContent = n ? `${n} ausgewählt` : '';
    }

    function renderSelected() {
      selected.innerHTML = '';
      const chosen = options().filter(o => o.selected);
      chosen.forEach(o => {
        const chip = document.createElement('span');
        chip.className = 'person-chip';

        const text = document.createElement('span');
        text.textContent = o.textContent;

        const remove = document.createElement('button');
        remove.type = 'button';
        remove.setAttribute('aria-label', `${o.textContent} entfernen`);
        remove.title = 'Auswahl entfernen';
        remove.textContent = '×';
        remove.addEventListener('click', () => {
          o.selected = false;
          dispatchChange();
          renderSelected();
          renderSuggestions();
          input.focus();
        });

        chip.append(text, remove);
        selected.appendChild(chip);
      });
      updateCount();
    }

    function closeSuggestions() {
      suggestions.hidden = true;
      input.setAttribute('aria-expanded', 'false');
      activeIndex = -1;
    }

    function getMatches() {
      const q = input.value.trim().toLocaleLowerCase('de');
      return options()
        .filter(o => !o.selected && (!q || o.textContent.toLocaleLowerCase('de').includes(q)))
        .slice(0, 10);
    }

    function setActive(index) {
      const buttons = Array.from(suggestions.querySelectorAll('.person-picker-option'));
      if (!buttons.length) {
        activeIndex = -1;
        return;
      }
      activeIndex = Math.max(0, Math.min(index, buttons.length - 1));
      buttons.forEach((b, i) => b.classList.toggle('is-active', i === activeIndex));
      buttons[activeIndex].scrollIntoView({ block: 'nearest' });
    }

    function choose(option) {
      option.selected = true;
      dispatchChange();
      input.value = '';
      renderSelected();
      renderSuggestions();
      input.focus();
    }

    function renderSuggestions() {
      suggestions.innerHTML = '';
      activeIndex = -1;
      const matches = getMatches();

      if (!matches.length) {
        if (!input.value.trim()) {
          closeSuggestions();
          return;
        }
        const empty = document.createElement('div');
        empty.className = 'person-picker-empty';
        empty.textContent = 'Keine passenden Personen gefunden.';
        suggestions.appendChild(empty);
        suggestions.hidden = false;
        input.setAttribute('aria-expanded', 'true');
        return;
      }

      matches.forEach(o => {
        const btn = document.createElement('button');
        btn.type = 'button';
        btn.className = 'person-picker-option';
        btn.setAttribute('role', 'option');
        btn.textContent = o.textContent;
        btn.addEventListener('mousedown', e => e.preventDefault());
        btn.addEventListener('click', () => choose(o));
        suggestions.appendChild(btn);
      });

      suggestions.hidden = false;
      input.setAttribute('aria-expanded', 'true');
    }

    input.addEventListener('input', renderSuggestions);
    input.addEventListener('focus', renderSuggestions);
    input.addEventListener('keydown', e => {
      const buttons = Array.from(suggestions.querySelectorAll('.person-picker-option'));
      if (e.key === 'Escape') {
        closeSuggestions();
        return;
      }
      if (e.key === 'ArrowDown') {
        e.preventDefault();
        if (suggestions.hidden) renderSuggestions();
        setActive(activeIndex + 1);
        return;
      }
      if (e.key === 'ArrowUp') {
        e.preventDefault();
        if (suggestions.hidden) renderSuggestions();
        setActive(activeIndex <= 0 ? 0 : activeIndex - 1);
        return;
      }
      if (e.key === 'Enter' && !suggestions.hidden && buttons.length) {
        e.preventDefault();
        const idx = activeIndex >= 0 ? activeIndex : 0;
        buttons[idx].click();
      }
    });

    document.addEventListener('click', e => {
      if (!wrap.contains(e.target)) closeSuggestions();
    });

    renderSelected();
  }

  function boot() {
    document.querySelectorAll('select.multi-person-source').forEach(initPicker);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', boot);
  } else {
    boot();
  }
})();
