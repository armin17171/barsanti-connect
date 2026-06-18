(function () {
  "use strict";

  // ---------- Drawer laterale ----------
  var drawer = document.getElementById("drawer");
  var overlay = document.getElementById("drawerOverlay");
  var menuBtn = document.getElementById("menuBtn");

  function openDrawer() { drawer.classList.add("open"); overlay.classList.add("open"); }
  function closeDrawer() { drawer.classList.remove("open"); overlay.classList.remove("open"); }

  if (menuBtn) menuBtn.addEventListener("click", openDrawer);
  if (overlay) overlay.addEventListener("click", closeDrawer);

  // ---------- Tema (persistente) ----------
  // Presente solo in Home (switch) e Impostazioni (pulsante).
  function currentTheme() {
    return document.documentElement.getAttribute("data-theme") || "light";
  }
  function setTheme(next) {
    document.documentElement.setAttribute("data-theme", next);
    try { localStorage.setItem("bc-theme", next); } catch (e) {}
    document.querySelectorAll(".js-theme-checkbox").forEach(function (cb) {
      cb.checked = next === "dark";
    });
  }
  function toggleTheme() { setTheme(currentTheme() === "light" ? "dark" : "light"); }

  // Pulsante (Impostazioni)
  document.querySelectorAll(".js-theme-toggle").forEach(function (btn) {
    btn.addEventListener("click", toggleTheme);
  });
  // Switch della luce (Home)
  document.querySelectorAll(".js-theme-checkbox").forEach(function (cb) {
    cb.checked = currentTheme() === "dark";
    cb.addEventListener("change", function () {
      setTheme(cb.checked ? "dark" : "light");
    });
  });

  // ---------- Nome file selezionato (composer post + avatar) ----------
  function bindFileName(inputSel, labelId) {
    var input = document.querySelector(inputSel);
    var label = document.getElementById(labelId);
    if (input && label) {
      input.addEventListener("change", function () {
        label.textContent = input.files.length ? input.files[0].name : "";
      });
    }
  }
  bindFileName('.composer input[type="file"]', "fileName");
  bindFileName("#avatarInput", "avatarName");

  // ---------- Like via fetch (con fallback al submit normale) ----------
  document.querySelectorAll(".like-form").forEach(function (form) {
    form.addEventListener("submit", function (ev) {
      ev.preventDefault();
      fetch(form.action, {
        method: "POST",
        headers: { "Accept": "application/json" },
      })
        .then(function (r) { return r.ok ? r.json() : Promise.reject(r); })
        .then(function (data) {
          var btn = form.querySelector(".like-btn");
          var heart = form.querySelector(".heart");
          var count = form.querySelector(".like-count");
          if (count) count.textContent = data.count;
          if (heart) heart.textContent = data.liked ? "❤️" : "🤍";
          if (btn) btn.classList.toggle("liked", data.liked);
        })
        .catch(function () { form.submit(); }); // fallback: invio classico
    });
  });

  // ---------- Mostra/nascondi password ----------
  document.querySelectorAll(".js-pwd-toggle").forEach(function (btn) {
    btn.addEventListener("click", function () {
      var input = btn.parentElement.querySelector("input");
      if (!input) return;
      input.type = input.type === "password" ? "text" : "password";
      btn.classList.toggle("on", input.type === "text");
    });
  });

  // ---------- Textarea che si adatta al contenuto ----------
  function autogrow(el) { el.style.height = "auto"; el.style.height = el.scrollHeight + "px"; }
  document.querySelectorAll("textarea.js-autogrow").forEach(function (t) {
    autogrow(t);
    t.addEventListener("input", function () { autogrow(t); });
  });

  // ---------- Menu a tendina "Media" (foto/video/audio) ----------
  document.querySelectorAll(".media-menu").forEach(function (menu) {
    var btn = menu.querySelector(".js-media-btn");
    var opts = menu.querySelector(".media-options");
    var file = menu.parentElement.querySelector('input[type="file"]');
    if (!btn || !opts) return;
    btn.addEventListener("click", function (e) {
      e.stopPropagation();
      opts.hidden = !opts.hidden;
    });
    opts.querySelectorAll("button[data-accept]").forEach(function (o) {
      o.addEventListener("click", function () {
        if (file) { file.accept = o.dataset.accept; file.click(); }
        opts.hidden = true;
      });
    });
  });
  document.addEventListener("click", function () {
    document.querySelectorAll(".media-options").forEach(function (o) { o.hidden = true; });
  });

  // ---------- Popup eventi imminenti (home), con "non mostrare più" ----------
  (function () {
    var popup = document.querySelector(".js-event-popup");
    if (!popup) return;
    var dismissed;
    try { dismissed = JSON.parse(localStorage.getItem("bc-ev-dismissed") || "[]"); }
    catch (e) { dismissed = []; }
    var items = popup.querySelectorAll("li[data-event-id]");
    var visible = 0;
    items.forEach(function (li) {
      if (dismissed.indexOf(li.dataset.eventId) >= 0) li.style.display = "none";
      else visible++;
    });
    if (visible === 0) { popup.style.display = "none"; return; }
    var close = popup.querySelector(".js-popup-close");
    if (close) close.addEventListener("click", function () {
      items.forEach(function (li) {
        if (dismissed.indexOf(li.dataset.eventId) < 0) dismissed.push(li.dataset.eventId);
      });
      try { localStorage.setItem("bc-ev-dismissed", JSON.stringify(dismissed)); } catch (e) {}
      popup.style.display = "none";
    });
  })();

  // ---------- Confessioni: invio con token segreto + delete dell'autore ----------
  function getConfTokens() {
    try { return JSON.parse(localStorage.getItem("bc-conf-tokens") || "{}"); }
    catch (e) { return {}; }
  }
  function setConfTokens(m) {
    try { localStorage.setItem("bc-conf-tokens", JSON.stringify(m)); } catch (e) {}
  }
  var confForm = document.querySelector(".js-confession-form");
  if (confForm) {
    confForm.addEventListener("submit", function (ev) {
      ev.preventDefault();
      fetch(confForm.action, {
        method: "POST",
        body: new FormData(confForm),
        headers: { "Accept": "application/json" },
      })
        .then(function (r) { return r.ok ? r.json() : Promise.reject(r); })
        .then(function (data) {
          if (data && data.id && data.token) {
            var m = getConfTokens(); m[data.id] = data.token; setConfTokens(m);
          }
          window.location.reload();
        })
        .catch(function () { confForm.submit(); });
    });
  }
  (function () {
    var tokens = getConfTokens();
    document.querySelectorAll(".confession[data-conf-id]").forEach(function (art) {
      var id = art.dataset.confId;
      var form = art.querySelector(".js-conf-author-delete");
      if (form && tokens[id]) {
        form.querySelector('input[name="token"]').value = tokens[id];
        form.hidden = false;
        form.addEventListener("submit", function () {
          var m = getConfTokens(); delete m[id]; setConfTokens(m);
        });
      }
    });
  })();

  // ---------- Player audio con onde ----------
  document.querySelectorAll(".js-audio").forEach(function (player) {
    var src = player.dataset.src;
    var audio = new Audio();
    audio.src = src; audio.preload = "metadata";
    var playBtn = player.querySelector(".ap-play");
    var wave = player.querySelector(".ap-wave");
    var timeEl = player.querySelector(".ap-time");
    var BARS = 48;
    for (var i = 0; i < BARS; i++) {
      var b = document.createElement("span");
      var seed = (i * 9301 + (src.length || 7) * 49297) % 233280;
      b.style.height = (20 + (seed / 233280) * 80).toFixed(0) + "%";
      wave.appendChild(b);
    }
    var bars = wave.querySelectorAll("span");
    function fmt(t) {
      if (isNaN(t) || t === Infinity) return "0:00";
      var m = Math.floor(t / 60), s = Math.floor(t % 60);
      return m + ":" + (s < 10 ? "0" : "") + s;
    }
    playBtn.addEventListener("click", function () {
      if (audio.paused) audio.play(); else audio.pause();
    });
    audio.addEventListener("play", function () { playBtn.textContent = "⏸"; player.classList.add("playing"); });
    audio.addEventListener("pause", function () { playBtn.textContent = "▶"; player.classList.remove("playing"); });
    audio.addEventListener("ended", function () { playBtn.textContent = "▶"; player.classList.remove("playing"); });
    audio.addEventListener("loadedmetadata", function () { timeEl.textContent = fmt(audio.duration); });
    audio.addEventListener("timeupdate", function () {
      var ratio = audio.currentTime / (audio.duration || 1);
      var active = Math.floor(ratio * BARS);
      bars.forEach(function (bar, idx) { bar.classList.toggle("on", idx < active); });
      timeEl.textContent = fmt((audio.duration || 0) - audio.currentTime);
    });
    wave.addEventListener("click", function (e) {
      var rect = wave.getBoundingClientRect();
      if (audio.duration) audio.currentTime = ((e.clientX - rect.left) / rect.width) * audio.duration;
    });
  });

  // ---------- Registrazione service worker (PWA installabile) ----------
  if ("serviceWorker" in navigator) {
    window.addEventListener("load", function () {
      navigator.serviceWorker.register("/static/sw.js").catch(function () {});
    });
  }
})();
