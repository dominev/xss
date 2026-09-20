(function () {
  const cao = document.getElementById("cao");
  const shell = document.getElementById("shell");
  const load = document.getElementById("loadscreen");
  const err = document.getElementById("auth-err");
  let bootCache = null;

  function showErr(text) {
    err.hidden = !text;
    err.textContent = text || "";
  }

  function esc(s) {
    return String(s ?? "")
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;");
  }

  function drawNews(news) {
    document.getElementById("news").innerHTML = (news || [])
      .map(([d, t]) => `<div class="news-line"><span class="d">${d}:</span> ${t}</div>`)
      .join("");
  }

  function drawBoard(rows) {
    const body = document.getElementById("board-body");
    if (!rows || !rows.length) {
      body.innerHTML = `<tr><td class="user">—</td><td colspan="10">нет записанных игр. посмотри позже.</td></tr>`;
      return;
    }
    body.innerHTML = rows
      .map(
        (r) => `<tr>
        <td class="user"><a href="#">${esc(r.user)}</a></td>
        <td>${esc(r.game)}</td>
        <td>${r.xl}</td>
        <td>${esc(r.char)}</td>
        <td>${esc(r.place)}</td>
        <td>${r.turn}</td>
        <td>${esc(r.time)}</td>
        <td>${esc(r.god)}</td>
        <td>${esc(r.idle || "")}</td>
        <td>${esc(r.specs || "")}</td>
        <td>${esc(r.milestone)}</td>
      </tr>`
      )
      .join("");
  }

  function drawVersions(pack) {
    const box = document.getElementById("versions");
    const list = (pack && pack.list) || [];
    if (!list.length) {
      box.innerHTML = "";
      return;
    }
    box.innerHTML = `<div class="ver-line">${list
      .map((v) => {
        if (v.playable) {
          return `<a class="play" data-ver="${esc(v.id)}">${esc(v.label)}</a> <span class="note">(${esc(v.note)})</span>`;
        }
        return `<span class="off">${esc(v.label)}</span>`;
      })
      .join(" <span class=\"pipe\">|</span> ")}</div>`;
    box.querySelectorAll("a.play").forEach((a) =>
      a.addEventListener("click", (e) => {
        e.preventDefault();
        startVersion(a.dataset.ver);
      })
    );
  }

  function setLoggedIn(user) {
    document.getElementById("cao").classList.add("in");
    document.getElementById("auth").hidden = true;
    document.getElementById("session").hidden = false;
    document.getElementById("who").textContent = user;
    const hello = document.getElementById("hello");
    hello.hidden = false;
    hello.textContent = `Hello, ${user}!`;
    document.getElementById("play-now").hidden = false;
  }

  function setLoggedOut() {
    document.getElementById("cao").classList.remove("in");
    document.getElementById("auth").hidden = false;
    document.getElementById("session").hidden = true;
    document.getElementById("hello").hidden = true;
    document.getElementById("play-now").hidden = true;
    document.getElementById("user").value = "";
    document.getElementById("pass").value = "";
  }

  function enterGame() {
    load.hidden = true;
    cao.hidden = true;
    shell.hidden = false;
    document.body.classList.add("ingame");
    if (window.TutaGame && TutaGame.start) TutaGame.start();
  }

  function startVersion(id) {
    const shots = (bootCache && bootCache.versions && bootCache.versions.loading) || [];
    const pick = shots.length ? shots[Math.floor(Math.random() * shots.length)] : "";
    const art = document.getElementById("load-art");
    if (pick) {
      art.src = pick;
      art.hidden = false;
    } else art.hidden = true;
    load.hidden = false;
    // let the splash paint, then hold ~2.8s
    setTimeout(enterGame, 2800);
  }

  async function refresh() {
    const boot = await TutaApi.get("/api/boot");
    bootCache = boot;
    drawNews(boot.news);
    drawBoard(boot.board);
    drawVersions(boot.versions);
    return boot;
  }

  document.getElementById("auth").addEventListener("submit", async (e) => {
    e.preventDefault();
    showErr("");
    const out = await TutaApi.post("/api/login", {
      username: document.getElementById("user").value,
      password: document.getElementById("pass").value,
    });
    if (!out.ok) {
      showErr(out.error || "Login incorrect.");
      return;
    }
    TutaApi.save(out);
    setLoggedIn(out.user);
    refresh();
  });

  document.getElementById("register").addEventListener("click", async () => {
    const out = await TutaApi.post("/api/register", {});
    showErr(out.error || "registration closed");
  });

  document.getElementById("logout").addEventListener("click", (e) => {
    e.preventDefault();
    TutaApi.clear();
    setLoggedOut();
  });

  TutaApi.clear();
  setLoggedOut();
  refresh();
})();
