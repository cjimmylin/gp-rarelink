(function(){
  const tbody=document.querySelector('#cand tbody'); if(!tbody) return;
  const names={ha20:'HA20',ssadh:'SSADH',tangier:'Tangier',lad1:'LAD-I',axd:'AxD',danon:'Danon'};
  const full={ha20:'A20 haploinsufficiency',ssadh:'SSADH deficiency',tangier:'Tangier disease',lad1:'Leukocyte adhesion deficiency I',axd:'Alexander disease',danon:'Danon disease'};
  let rows=[], sortKey='id', asc=true;
  const esc=s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  function render(){
    const d=document.getElementById('f-disease').value, q=document.getElementById('f-text').value.trim().toLowerCase();
    let out=rows.filter(r=>(!d||r.disease===d)&&(!q||[r.id,r.gene,r.hgvs_c,r.protein,r.written,r.pmids.join(' '),r.author_class].join(' ').toLowerCase().includes(q)));
    out.sort((a,b)=>{const x=a[sortKey],y=b[sortKey];const c=(typeof x==='number')?x-y:String(x).localeCompare(String(y));return asc?c:-c;});
    tbody.innerHTML=out.map(r=>`<tr><td>${esc(r.id)}</td><td title="${esc(full[r.disease]||r.disease)}">${esc(names[r.disease]||r.disease)}</td><td><i>${esc(r.gene)}</i></td><td class="mono">${esc(r.hgvs_c)}</td><td class="mono">${esc(r.protein||'—')}</td><td class="mono wrap">${esc(r.written)}</td><td>${r.n_papers}</td><td>${r.n_identities}</td><td>${esc(r.author_class)}</td><td>${r.pmids.map(p=>`<a href="https://pubmed.ncbi.nlm.nih.gov/${esc(p)}/" target="_blank" rel="noopener">${esc(p)}</a>`).join(' ')}</td></tr>`).join('');
    document.getElementById('f-count').textContent=`${out.length} of ${rows.length} candidates`;
  }
  fetch('data/candidates.json').then(r=>r.json()).then(j=>{rows=j;render();});
  document.getElementById('f-disease').addEventListener('change',render);
  document.getElementById('f-text').addEventListener('input',render);
  document.querySelectorAll('#cand th[data-k]').forEach(th=>th.addEventListener('click',()=>{const k=th.dataset.k; if(sortKey===k) asc=!asc; else {sortKey=k; asc=true;} render();}));
})();
