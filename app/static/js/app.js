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

  // ---------- Registrazione service worker (PWA installabile) ----------
  if ("serviceWorker" in navigator) {
    window.addEventListener("load", function () {
      navigator.serviceWorker.register("/static/sw.js").catch(function () {});
    });
  }
})();
