
const $ = (s, r = document) => r.querySelector(s);

const G = {
  boot: null,
  screen: "lobby",
  loreI: 0,
  draft: { species: "zhar", temper: "snark", name: "admin", relic: "" },
  run: null,
  keys: {},
};

async function boot() {
  if (G._started) return;
  G._started = true;
  G.boot = await TutaApi.get("/api/boot");
  if (!G.boot.meta.seen_lore) G.screen = "lore";
  render();
  requestAnimationFrame(loop);
}

function fmtTime(s) {
  s = Math.max(0, s | 0);
  const m = Math.floor(s / 60);
  return `${m}м ${String(s % 60).padStart(2, "0")}с`;
}

function render() {
  const view = $("#view");
  const right = $("#top-right");
  const meta = G.boot.meta;
  right.textContent = `забеги ${meta.runs || 0} · осколки ${meta.shards || 0} · реликвии ${(meta.relics || []).length}`;
  if (G.screen === "lore") view.innerHTML = viewLore();
  else if (G.screen === "create") view.innerHTML = viewCreate();
  else if (G.screen === "crawl") view.innerHTML = viewCrawl();
  else view.innerHTML = viewLobby();
  bind();
  if (G.screen === "crawl") paint();
}

function viewLobby() {
  const rows = (G.boot.morgue || [])
    .map((r) => `<tr class="${r.result}">
      <td>${r.id}</td><td>${r.name}</td><td>${r.title} ${r.temper}</td>
      <td>${r.xl}</td><td>${r.place}</td><td>${fmtTime(r.time_s)}</td>
      <td>${r.kills}</td><td>${r.milestone}</td><td>${r.result === "win" ? "вышел" : "погиб"}</td>
    </tr>`)
    .join("") || `<tr><td colspan="9" class="tag">могильник пуст. первый забег ещё не сдох.</td></tr>`;
  return `<div class="lobby">
    <h1>КАРМАН</h1>
    <div class="tag">онлайн-могильник локального яйца · вертикалка D:1 · учись умирать быстро</div>
    <div class="stats"><span>runs ${G.boot.meta.runs || 0}</span><span>best XL ${G.boot.meta.best_level || 1}</span><span>shards ${G.boot.meta.shards || 0}</span></div>
    <div class="actions">
      <button class="gold" id="go-create">Новый забег</button>
      <button id="go-lore">Лор</button>
    </div>
    <table class="morgue">
      <tr><th>#</th><th>имя</th><th>вид</th><th>XL</th><th>место</th><th>время</th><th>убийства</th><th>веха</th><th>итог</th></tr>
      ${rows}
    </table>
  </div>`;
}

function viewLore() {
  const s = G.boot.lore[G.loreI];
  const last = G.loreI === G.boot.lore.length - 1;
  return `<div class="lore">
    <img src="${s.img}" alt="">
    <div class="copy">
      <div class="tag">${G.loreI + 1} / ${G.boot.lore.length}</div>
      <h2>${s.title}</h2>
      <p>${s.text}</p>
      <div class="dots">${"●".repeat(G.loreI + 1)}${"○".repeat(G.boot.lore.length - G.loreI - 1)}</div>
      <div class="actions">
        ${G.loreI ? `<button id="lore-back">назад</button>` : ""}
        <button class="gold" id="lore-next">${last ? "проклюнуться" : "дальше"}</button>
        <button id="lore-skip">пропустить</button>
      </div>
    </div>
  </div>`;
}

function viewCreate() {
  const cat = G.boot.catalog;
  const cards = Object.entries(cat.species).map(([id, s]) => `
    <div class="card ${G.draft.species === id ? "on" : ""}" data-sp="${id}">
      <h3>${s.title}</h3>
      <p>${s.type}</p>
      <p>${s.blurb}</p>
    </div>`).join("");
  const tempers = Object.entries(cat.tempers).map(([k, l]) =>
    `<option value="${k}" ${G.draft.temper === k ? "selected" : ""}>${l}</option>`).join("");
  const relics = (G.boot.meta.relics || []).filter((r) => cat.relics[r]);
  const relOpts = [`<option value="">без реликвии прошлого тела</option>`]
    .concat(relics.map((r) => `<option value="${r}">${cat.relics[r].icon} ${cat.relics[r].name}</option>`)).join("");
  return `<div class="lobby">
    <h1>ЯЙЦО</h1>
    <div class="tag">вид — тело на весь забег. характер — как ты бьёшь.</div>
    <div class="grid3">${cards}</div>
    <div class="form">
      <div><div class="tag">имя</div><input id="nm" maxlength="18" value="${G.draft.name}"></div>
      <div><div class="tag">характер</div><select id="tm">${tempers}</select></div>
      <div><div class="tag">реликвия</div><select id="rl">${relOpts}</select></div>
    </div>
    <div class="actions">
      <button id="back-lobby">← могильник</button>
      <button class="gold" id="start-run">Проклюнуться на D:1</button>
    </div>
  </div>`;
}

function viewCrawl() {
  const p = G.run.player;
  const spec = G.boot.catalog.species[p.species];
  const nodes = [0, 1, 2].map((i) => `<b class="${p.tree > i ? "on" : ""}" style="background:${['#3dba7a','#3dba7a','#3dba7a'][i]}"></b>`).join("");
  const inv = Array.from({ length: 8 }, (_, i) => `<i>${p.inv[i] ? p.inv[i].icon : ""}</i>`).join("");
  const end = G.run.over
    ? `<div class="end"><h2>${G.run.over === "win" ? "лестница взята" : "забег сгорел"}</h2>
        <p>${G.run.overText}</p>
        <button class="gold" id="to-lobby">в могильник</button></div>`
    : "";
  return `<div class="crawl">
    <canvas id="stage" width="704" height="512"></canvas>
    <div class="side">
      <h2>${p.name}</h2>
      <div>${spec.title} · ${G.boot.catalog.tempers[p.temper]} · XL ${p.xl}</div>
      <div class="kv"><span>здоровье</span><b>${p.hp}/${p.maxhp}</b></div>
      <div class="bar"><i style="width:${(p.hp / p.maxhp) * 100}%;background:#3dba7a"></i></div>
      <div class="kv"><span>голод</span><b>${p.hunger | 0}</b></div>
      <div class="bar"><i style="width:${p.hunger}%;background:#d4893a"></i></div>
      <div class="kv"><span>опыт</span><b>${p.xp}/${p.need}</b></div>
      <div class="bar"><i style="width:${(p.xp / p.need) * 100}%;background:#c4a35a"></i></div>
      <div class="kv"><span>золото</span><b>${p.gold}</b></div>
      <div class="kv"><span>место</span><b>D:1</b></div>
      <div class="kv"><span>убийства</span><b>${p.kills}</b></div>
      <div class="tag" style="margin-top:8px">ветка Роста</div>
      <div class="tree">${nodes}</div>
      <div class="inv">${inv}</div>
      <div class="help">WASD ход · пробел удар · E подобрать/съесть · лестница &gt;</div>
    </div>
    <div class="log" id="log">${G.run.log.slice(-7).map((l) => `<div>${l}</div>`).join("")}</div>
    ${end}
  </div>`;
}

function bind() {
  $("#go-create")?.addEventListener("click", () => { G.screen = "create"; render(); });
  $("#go-lore")?.addEventListener("click", () => { G.loreI = 0; G.screen = "lore"; render(); });
  $("#lore-back")?.addEventListener("click", () => { G.loreI = Math.max(0, G.loreI - 1); render(); });
  $("#lore-next")?.addEventListener("click", async () => {
    if (G.loreI < G.boot.lore.length - 1) { G.loreI += 1; render(); return; }
    await TutaApi.post("/api/seen-lore", {});
    G.boot.meta.seen_lore = true;
    G.screen = "create";
    render();
  });
  $("#lore-skip")?.addEventListener("click", async () => {
    await TutaApi.post("/api/seen-lore", {});
    G.boot.meta.seen_lore = true;
    G.screen = "lobby";
    render();
  });
  document.querySelectorAll("[data-sp]").forEach((el) => el.addEventListener("click", () => {
    G.draft.species = el.dataset.sp;
    render();
  }));
  $("#back-lobby")?.addEventListener("click", () => { G.screen = "lobby"; render(); });
  $("#start-run")?.addEventListener("click", () => {
    G.draft.name = $("#nm").value.trim() || "Тута";
    G.draft.temper = $("#tm").value;
    G.draft.relic = $("#rl").value;
    startRun();
  });
  $("#to-lobby")?.addEventListener("click", async () => {
    G.boot = await TutaApi.get("/api/boot");
    G.screen = "lobby";
    G.run = null;
    render();
  });
}

function log(msg) {
  if (!G.run) return;
  G.run.log.push(msg);
  if (G.run.log.length > 40) G.run.log = G.run.log.slice(-40);
  const box = $("#log");
  if (box) box.innerHTML = G.run.log.slice(-7).map((l) => `<div>${l}</div>`).join("");
}

function startRun() {
  const spec = G.draft.species;
  const bonus = spec === "zhar" ? { hp: 22, atk: 4, hung: 1.3 } :
    spec === "morok" ? { hp: 18, atk: 3, hung: 0.9 } : { hp: 26, atk: 3, hung: 0.8 };
  const player = {
    name: G.draft.name, species: spec, temper: G.draft.temper, relic: G.draft.relic,
    x: 2, y: 2, fx: 1, fy: 0,
    hp: bonus.hp, maxhp: bonus.hp, hunger: 80,
    xl: 1, xp: 0, need: 12, tree: 0, gold: 0, kills: 0,
    atk: bonus.atk + (G.draft.temper === "venom" ? 1 : 0),
    hungRate: bonus.hung * (G.draft.relic === "warm_core" ? 0.65 : 1),
    inv: [],
    moveCd: 0, atkCd: 0,
  };
  if (G.draft.relic === "fat_wallet") player.gold = 40;
  const dungeon = genDungeon();
  player.x = dungeon.start[0];
  player.y = dungeon.start[1];
  G.run = {
    player, dungeon, t0: performance.now(), last: performance.now(),
    log: ["Скорлупа треснула. Карман:1.", "Черновики шевелятся."],
    over: null, overText: "", sent: false,
  };
  if (player.relic) log(`с собой реликвия прошлого тела.`);
  G.screen = "crawl";
  render();
}

const W = 44, H = 32, TS = 16;
const TILE = { wall: 0, floor: 1, water: 2, stair: 3 };

function genDungeon() {
  const g = Array.from({ length: H }, () => Array(W).fill(TILE.wall));
  const rooms = [];
  for (let i = 0; i < 8; i++) {
    const w = 5 + (Math.random() * 5 | 0);
    const h = 4 + (Math.random() * 4 | 0);
    const x = 1 + (Math.random() * (W - w - 2) | 0);
    const y = 1 + (Math.random() * (H - h - 2) | 0);
    let ok = true;
    for (const r of rooms) {
      if (x < r.x + r.w + 1 && x + w + 1 > r.x && y < r.y + r.h + 1 && y + h + 1 > r.y) ok = false;
    }
    if (!ok) continue;
    for (let yy = y; yy < y + h; yy++)
      for (let xx = x; xx < x + w; xx++) g[yy][xx] = TILE.floor;
    rooms.push({ x, y, w, h, cx: x + (w >> 1), cy: y + (h >> 1) });
  }
  if (rooms.length < 3) return genDungeon();
  rooms.sort((a, b) => a.cx - b.cx);
  for (let i = 1; i < rooms.length; i++) {
    let x = rooms[i - 1].cx, y = rooms[i - 1].cy;
    const tx = rooms[i].cx, ty = rooms[i].cy;
    while (x !== tx) { x += Math.sign(tx - x); g[y][x] = TILE.floor; }
    while (y !== ty) { y += Math.sign(ty - y); g[y][x] = TILE.floor; }
  }
  for (let y = 1; y < H - 1; y++)
    for (let x = 1; x < W - 1; x++) {
      if (g[y][x] === TILE.floor && Math.random() < 0.06) g[y][x] = TILE.water;
    }
  const last = rooms[rooms.length - 1];
  const first = rooms[0];
  g[last.cy][last.cx] = TILE.stair;
  const items = [];
  const enemies = [];
  const kinds = [
    { id: "draft", name: "черновик", hp: 8, atk: 2, spd: 420, col: "#c9b7a0" },
    { id: "crumb", name: "крошка голода", hp: 12, atk: 3, spd: 560, col: "#8a5a2a" },
    { id: "echo", name: "эхо", hp: 7, atk: 3, spd: 300, col: "#5a6a88" },
  ];
  rooms.slice(1).forEach((r, i) => {
    const n = 1 + (Math.random() * 2 | 0);
    for (let k = 0; k < n; k++) {
      const kd = kinds[(Math.random() * kinds.length) | 0];
      enemies.push({
        ...kd, hp: kd.hp, max: kd.hp,
        x: r.x + 1 + (Math.random() * (r.w - 2) | 0),
        y: r.y + 1 + (Math.random() * (r.h - 2) | 0),
        cd: kd.spd,
      });
    }
    if (Math.random() < 0.8) items.push({ x: r.x + 1, y: r.y + 1, kind: "food", icon: "🍖", name: "паёк" });
    if (Math.random() < 0.6) items.push({ x: r.x + r.w - 2, y: r.y + 1, kind: "gold", icon: "₮", name: "монета", n: 3 + (Math.random() * 8 | 0) });
  });
  items.push({ x: first.cx + 1, y: first.cy, kind: "ring", icon: "○", name: "непонятное кольцо" });
  return { g, start: [first.cx, first.cy], items, enemies };
}

function walkable(x, y) {
  const t = G.run.dungeon.g[y] && G.run.dungeon.g[y][x];
  return t === TILE.floor || t === TILE.water || t === TILE.stair;
}

function enemyAt(x, y) {
  return G.run.dungeon.enemies.find((e) => e.hp > 0 && e.x === x && e.y === y);
}

function tick(dt) {
  const run = G.run;
  if (!run || run.over) return;
  const p = run.player;
  p.moveCd -= dt;
  p.atkCd -= dt;
  p.hunger -= dt * 0.0045 * p.hungRate;
  if (p.hunger <= 0) {
    p.hunger = 0;
    p.hp -= dt * 0.008;
    if (Math.random() < 0.01) log("Голод ест тебя. Карман сыт.");
  }
  const t = G.run.dungeon.g[p.y][p.x];
  if (t === TILE.water) p.moveCd = Math.max(p.moveCd, 40);

  let dx = 0, dy = 0;
  if (G.keys["KeyW"] || G.keys["ArrowUp"]) dy = -1;
  if (G.keys["KeyS"] || G.keys["ArrowDown"]) dy = 1;
  if (G.keys["KeyA"] || G.keys["ArrowLeft"]) dx = -1;
  if (G.keys["KeyD"] || G.keys["ArrowRight"]) dx = 1;
  if (dx || dy) {
    p.fx = dx || p.fx; p.fy = dy || p.fy;
    if (dx && dy) dy = 0;
    if (p.moveCd <= 0) {
      const nx = p.x + dx, ny = p.y + dy;
      const foe = enemyAt(nx, ny);
      if (foe) tryHit(foe);
      else if (walkable(nx, ny)) { p.x = nx; p.y = ny; }
      p.moveCd = 105;
    }
  }
  if (G.keys["Space"] && p.atkCd <= 0) {
    const foe = enemyAt(p.x + p.fx, p.y + p.fy);
    if (foe) tryHit(foe);
    p.atkCd = 260;
  }
  if (G.keys["KeyE"]) {
    G.keys["KeyE"] = false;
    pickup();
  }

  for (const e of run.dungeon.enemies) {
    if (e.hp <= 0) continue;
    e.cd -= dt;
    const dist = Math.abs(e.x - p.x) + Math.abs(e.y - p.y);
    if (dist === 1 && e.cd <= 0) {
      let dmg = e.atk;
      if (p.species === "zhar" && e.id === "crumb") dmg = Math.max(1, dmg - 1);
      p.hp -= dmg;
      log(`${e.name} бьёт. −${dmg}`);
      e.cd = e.spd;
    } else if (dist < 8 && e.cd <= 0) {
      const sx = Math.sign(p.x - e.x), sy = Math.sign(p.y - e.y);
      const opts = Math.random() < 0.5 ? [[sx, 0], [0, sy]] : [[0, sy], [sx, 0]];
      for (const [ox, oy] of opts) {
        const nx = e.x + ox, ny = e.y + oy;
        if (walkable(nx, ny) && !enemyAt(nx, ny) && !(nx === p.x && ny === p.y)) {
          e.x = nx; e.y = ny; break;
        }
      }
      e.cd = e.spd;
    }
  }

  if (p.hp <= 0) {
    p.hp = 0;
    finish("dead", `Тебя сложил ${run.lastHit || "голод"}. Тело станет вещью.`);
  }
  const side = $("#stage") ? null : null;
  hudSoft();
}

function hudSoft() {
  if (G.screen !== "crawl") return;
  const p = G.run.player;
  const side = document.querySelector(".side");
  if (!side) return;
  const bars = side.querySelectorAll(".bar i");
  if (bars[0]) bars[0].style.width = `${(p.hp / p.maxhp) * 100}%`;
  if (bars[1]) bars[1].style.width = `${p.hunger}%`;
  if (bars[2]) bars[2].style.width = `${(p.xp / p.need) * 100}%`;
  const kvs = side.querySelectorAll(".kv b");
  if (kvs[0]) kvs[0].textContent = `${Math.max(0, p.hp | 0)}/${p.maxhp}`;
  if (kvs[1]) kvs[1].textContent = `${p.hunger | 0}`;
  if (kvs[2]) kvs[2].textContent = `${p.xp}/${p.need}`;
  if (kvs[3]) kvs[3].textContent = `${p.gold}`;
  if (kvs[5]) kvs[5].textContent = `${p.kills}`;
}

function tryHit(foe) {
  const p = G.run.player;
  if (p.atkCd > 0 && !G.keys["Space"]) return;
  let dmg = p.atk + (p.tree > 0 ? 1 : 0);
  if (p.temper === "snark" && p.hp < p.maxhp * 0.4) dmg += 2;
  if (p.temper === "venom") dmg += 1;
  foe.hp -= dmg;
  G.run.lastHit = foe.name;
  log(`ты бьёшь ${foe.name}. −${dmg}`);
  p.atkCd = 240;
  if (foe.hp <= 0) {
    foe.hp = 0;
    p.kills += 1;
    p.xp += 4;
    log(`${foe.name} опадает в пыль.`);
    if (p.xp >= p.need) {
      p.xp -= p.need;
      p.xl += 1;
      p.need = 10 + p.xl * 6;
      p.maxhp += 4;
      p.hp = Math.min(p.maxhp, p.hp + 6);
      if (p.tree < 3) p.tree += 1;
      log(`XL ${p.xl}. Ветка Роста +1.`);
      render();
    }
  }
}

function pickup() {
  const p = G.run.player;
  const items = G.run.dungeon.items;
  const i = items.findIndex((it) => it.x === p.x && it.y === p.y);
  if (i < 0) {
    if (G.run.dungeon.g[p.y][p.x] === TILE.stair) {
      finish("win", "Лестница вниз есть. Дальше Карман ещё не собран. Осколок записан.");
    }
    return;
  }
  const it = items.splice(i, 1)[0];
  if (it.kind === "food") {
    p.hunger = Math.min(100, p.hunger + 28);
    p.hp = Math.min(p.maxhp, p.hp + 3);
    log("паёк. Карман на минуту отступил.");
  } else if (it.kind === "gold") {
    p.gold += it.n;
    log(`+${it.n}₮`);
  } else {
    p.inv.push(it);
    log(`подобрано: ${it.name}. неясно, стоит ли надевать.`);
    render();
  }
}

async function finish(result, text) {
  if (G.run.over) return;
  G.run.over = result;
  G.run.overText = text;
  const p = G.run.player;
  const time_s = Math.floor((performance.now() - G.run.t0) / 1000);
  if (!G.run.sent) {
    G.run.sent = true;
    await TutaApi.post("/api/run-end", {
      name: p.name, species: p.species, temper: p.temper, xl: p.xl,
      place: result === "win" ? "D:1>" : "D:1",
      time_s, kills: p.kills, result,
      killed_by: G.run.lastHit || "голод",
      milestone: result === "win" ? "found the D:1 stair" : `killed by ${G.run.lastHit || "hunger"}`,
      relic_id: result === "dead" ? null : p.relic,
    });
  }
  render();
}

function paint() {
  const cv = $("#stage");
  if (!cv || !G.run) return;
  const ctx = cv.getContext("2d");
  const p = G.run.player;
  const camx = Math.max(0, Math.min(W - 44, p.x - 22));
  const camy = Math.max(0, Math.min(H - 32, p.y - 16));
  ctx.fillStyle = "#050505";
  ctx.fillRect(0, 0, cv.width, cv.height);
  for (let y = 0; y < 32; y++) {
    for (let x = 0; x < 44; x++) {
      const mx = x + camx, my = y + camy;
      const t = G.run.dungeon.g[my] ? G.run.dungeon.g[my][mx] : TILE.wall;
      if (t === TILE.wall) ctx.fillStyle = "#1b1612";
      else if (t === TILE.floor) ctx.fillStyle = (mx + my) % 2 ? "#2a2a28" : "#32322e";
      else if (t === TILE.water) ctx.fillStyle = "#1a3a48";
      else ctx.fillStyle = "#c4a35a";
      ctx.fillRect(x * TS, y * TS, TS, TS);
      if (t === TILE.wall) {
        ctx.fillStyle = "#3a3128";
        ctx.fillRect(x * TS, y * TS, TS, 3);
      }
      if (t === TILE.stair) {
        ctx.fillStyle = "#7a5a18";
        ctx.fillRect(x * TS + 3, y * TS + 3, 10, 10);
      }
    }
  }
  for (const it of G.run.dungeon.items) {
    ctx.fillStyle = "#efe3b0";
    ctx.font = "12px monospace";
    ctx.fillText(it.icon, (it.x - camx) * TS + 2, (it.y - camy) * TS + 13);
  }
  for (const e of G.run.dungeon.enemies) {
    if (e.hp <= 0) continue;
    ctx.fillStyle = e.col;
    ctx.fillRect((e.x - camx) * TS + 3, (e.y - camy) * TS + 3, 10, 10);
  }
  const spec = G.boot.catalog.species[p.species];
  const col = spec.palette["1"] || "#f08a2a";
  ctx.fillStyle = col;
  ctx.fillRect((p.x - camx) * TS + 2, (p.y - camy) * TS + 2, 12, 12);
  ctx.fillStyle = "#111";
  ctx.fillRect((p.x - camx) * TS + 4 + p.fx * 3, (p.y - camy) * TS + 5 + p.fy * 3, 3, 3);
}

let acc = 0;
function loop(t) {
  if (G.run && G.screen === "crawl") {
    const dt = Math.min(40, t - G.run.last);
    G.run.last = t;
    tick(dt);
    paint();
  }
  requestAnimationFrame(loop);
}

window.addEventListener("keydown", (e) => {
  G.keys[e.code] = true;
  if (["Space", "ArrowUp", "ArrowDown", "ArrowLeft", "ArrowRight"].includes(e.code)) e.preventDefault();
});
window.addEventListener("keyup", (e) => { G.keys[e.code] = false; });

window.TutaGame = { start: boot };
