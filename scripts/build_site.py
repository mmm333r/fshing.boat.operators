#!/usr/bin/env python3
"""boats.json を埋め込んだ単一HTML（site/index.html）を生成する。"""
import json
import os
from datetime import date

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BOATS_JSON = os.path.join(ROOT, "data", "boats.json")
SITE_OUT = os.path.join(ROOT, "site", "index.html")

TEMPLATE = r"""<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>全国遊漁船 釣果ボード</title>
<style>
:root {
  --ai: #1f3a5f;        /* 藍 */
  --ai-deep: #14263f;
  --ice: #eaf4fb;       /* 氷色 */
  --ice-2: #d7e9f5;
  --uki: #f28c28;       /* 浮き玉オレンジ */
  --board: #23312a;     /* 釣果黒板 */
  --chalk: #f3efe4;
  --ok: #2e8b57;
}
* { margin: 0; padding: 0; box-sizing: border-box; }
body { font-family: "Hiragino Sans", "Noto Sans JP", "Yu Gothic", sans-serif;
       background: var(--ice); color: #22303f; }
header { background: linear-gradient(135deg, var(--ai-deep), var(--ai));
         color: #fff; padding: 22px 20px 16px; }
header h1 { font-size: 1.45rem; letter-spacing: .06em; }
header h1 .uki { color: var(--uki); }
header p { font-size: .82rem; opacity: .85; margin-top: 4px; }
.stats { display: flex; gap: 12px; flex-wrap: wrap; padding: 14px 20px;
         background: var(--ai-deep); }
.stat { background: rgba(255,255,255,.08); border-left: 3px solid var(--uki);
        color: #fff; padding: 8px 14px; border-radius: 4px; min-width: 120px; }
.stat b { display: block; font-size: 1.25rem; }
.stat span { font-size: .72rem; opacity: .8; }
.controls { display: flex; gap: 10px; flex-wrap: wrap; padding: 14px 20px;
            background: #fff; border-bottom: 1px solid var(--ice-2);
            position: sticky; top: 0; z-index: 5; }
.controls select, .controls input { padding: 8px 10px; border: 1px solid var(--ice-2);
   border-radius: 6px; font-size: .9rem; background: var(--ice); }
.controls input { flex: 1; min-width: 180px; }
main { padding: 18px 20px 40px; display: grid;
       grid-template-columns: repeat(auto-fill, minmax(330px, 1fr)); gap: 16px; }
.card { background: #fff; border-radius: 10px; overflow: hidden;
        box-shadow: 0 1px 4px rgba(20,38,63,.12); display: flex; flex-direction: column; }
.card-head { background: var(--ai); color: #fff; padding: 10px 14px;
             display: flex; justify-content: space-between; align-items: baseline; gap: 8px; }
.card-head h2 { font-size: 1.05rem; }
.card-head .place { font-size: .74rem; opacity: .85; white-space: nowrap; }
.badge { display: inline-block; font-size: .68rem; padding: 2px 8px;
         border-radius: 999px; margin-left: 6px; vertical-align: middle; }
.badge.type { background: var(--ice-2); color: var(--ai); }
.badge.st-done { background: #d9f2e3; color: var(--ok); }
.badge.st-part { background: #fdeec9; color: #9a6b00; }
.badge.st-ng { background: #fbdbdb; color: #a33; }
.badge.st-todo { background: #eee; color: #888; }
.board { background: var(--board); color: var(--chalk); padding: 12px 14px;
         font-size: .86rem; min-height: 64px; }
.board .bt { color: var(--uki); font-size: .7rem; letter-spacing: .2em;
             border-bottom: 1px dashed rgba(243,239,228,.35);
             padding-bottom: 4px; margin-bottom: 8px; }
.board ul { list-style: none; }
.board li { padding: 3px 0; border-bottom: 1px dotted rgba(243,239,228,.15); }
.board li:last-child { border-bottom: none; }
.board .fish { font-weight: bold; color: #fff; }
.board .dt { color: #9fd0a8; font-size: .76rem; margin-left: 6px; }
.board .note { color: rgba(243,239,228,.7); font-size: .76rem; }
.board .empty { color: rgba(243,239,228,.5); font-size: .8rem; }
.prices { padding: 10px 14px; font-size: .84rem; flex: 1; }
.prices li { list-style: none; display: flex; justify-content: space-between;
             gap: 8px; padding: 3px 0; border-bottom: 1px dotted var(--ice-2); }
.prices .yen { color: var(--ai); font-weight: bold; white-space: nowrap; }
.prices .pnote { font-size: .72rem; color: #789; }
.card-foot { padding: 8px 14px 12px; display: flex; justify-content: space-between;
             align-items: center; font-size: .72rem; color: #8aa; }
.card-foot a { color: var(--uki); font-weight: bold; text-decoration: none; }
.card-foot a:hover { text-decoration: underline; }
footer { text-align: center; padding: 18px; font-size: .72rem; color: #8aa; }
</style>
</head>
<body>
<header>
  <h1>全国遊漁船 <span class="uki">釣果ボード</span></h1>
  <p>いま・どこで・何が・どれぐらい釣れているか ｜ 生成日: __BUILD_DATE__</p>
</header>
<div class="stats" id="stats"></div>
<div class="controls">
  <select id="fPref"><option value="">都道府県: すべて</option></select>
  <select id="fFish"><option value="">魚種: すべて</option></select>
  <input id="fKw" type="search" placeholder="キーワード（船宿名・港・市町村など）">
</div>
<main id="cards"></main>
<footer>釣果・料金は各船宿の公開情報に基づく参考値です。最新情報は必ず公式サイトでご確認ください。</footer>
<script id="boats-data" type="application/json">__BOATS_JSON__</script>
<script>
const BOATS = JSON.parse(document.getElementById('boats-data').textContent);
const stBadge = s => ({'済':'st-done','一部':'st-part','取得不可':'st-ng','未収集':'st-todo'}[s]||'st-todo');
const esc = s => String(s ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));

function fillFilters() {
  const prefs = [...new Set(BOATS.map(b => b.pref))].sort();
  const fish = [...new Set(BOATS.flatMap(b => (b.catches||[]).map(c => c.fish)))].filter(Boolean).sort();
  for (const p of prefs) fPref.insertAdjacentHTML('beforeend', `<option>${esc(p)}</option>`);
  for (const f of fish) fFish.insertAdjacentHTML('beforeend', `<option>${esc(f)}</option>`);
}

function stats(list) {
  const done = list.filter(b => b.status === '済').length;
  const part = list.filter(b => b.status === '一部').length;
  const withCatch = list.filter(b => (b.catches||[]).length).length;
  const rate = list.length ? Math.round((done + part) / list.length * 100) : 0;
  document.getElementById('stats').innerHTML = `
    <div class="stat"><b>${list.length}</b><span>掲載数</span></div>
    <div class="stat"><b>${done} / ${part}</b><span>済 / 一部</span></div>
    <div class="stat"><b>${rate}%</b><span>収集率</span></div>
    <div class="stat"><b>${withCatch}</b><span>釣果あり</span></div>`;
}

function card(b) {
  const catches = (b.catches||[]).map(c => `
    <li><span class="fish">${esc(c.fish)}</span>
        ${esc(c.size||'')} ${esc(c.count||'')}
        ${c.date ? `<span class="dt">${esc(c.date)}</span>` : ''}
        ${c.note ? `<div class="note">※${esc(c.note)}</div>` : ''}</li>`).join('');
  const prices = (b.prices||[]).map(p => `
    <li><span>${esc(p.label)}${p.note ? `<div class="pnote">※${esc(p.note)}</div>` : ''}</span>
        <span class="yen">${p.yen != null ? p.yen.toLocaleString() + '円' : '－'}</span></li>`).join('');
  return `
  <div class="card">
    <div class="card-head">
      <h2>${esc(b.name)}<span class="badge type">${esc(b.type||'不明')}</span>
          <span class="badge ${stBadge(b.status)}">${esc(b.status)}</span></h2>
      <span class="place">${esc(b.pref)} ${esc(b.city)}／${esc(b.port)}</span>
    </div>
    <div class="board"><div class="bt">━ 釣果黒板 ━</div>
      ${catches ? `<ul>${catches}</ul>` : `<div class="empty">釣果情報 未収集</div>`}</div>
    <ul class="prices">${prices || '<li><span class="pnote">料金情報なし</span></li>'}</ul>
    <div class="card-foot">
      <span>収集日: ${esc(b.collected_at||'－')}／${esc(b.source||'－')}</span>
      ${b.url ? `<a href="${esc(b.url)}" target="_blank" rel="noopener">公式サイト ⚓</a>` : ''}
    </div>
  </div>`;
}

function render() {
  const pref = fPref.value, fish = fFish.value, kw = fKw.value.trim().toLowerCase();
  const list = BOATS.filter(b =>
    (!pref || b.pref === pref) &&
    (!fish || (b.catches||[]).some(c => c.fish === fish)) &&
    (!kw || [b.name, b.city, b.port, b.type, ...(b.catches||[]).map(c => c.fish)]
      .join(' ').toLowerCase().includes(kw)));
  stats(list);
  document.getElementById('cards').innerHTML = list.map(card).join('');
}
fillFilters();
[fPref, fFish].forEach(el => el.addEventListener('change', render));
fKw.addEventListener('input', render);
render();
</script>
</body>
</html>
"""


def main():
    with open(BOATS_JSON, encoding="utf-8") as f:
        boats = json.load(f)
    html = TEMPLATE.replace("__BUILD_DATE__", date.today().isoformat())
    html = html.replace(
        "__BOATS_JSON__",
        json.dumps(boats, ensure_ascii=False).replace("</", "<\\/"),
    )
    os.makedirs(os.path.dirname(SITE_OUT), exist_ok=True)
    with open(SITE_OUT, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"wrote {SITE_OUT} ({len(boats)} boats)")


if __name__ == "__main__":
    main()
