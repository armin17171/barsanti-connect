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

  // ---------- Toggle tema (persistente) ----------
  function toggleTheme() {
    var cur = document.documentElement.getAttribute("data-theme") || "light";
    var next = cur === "light" ? "dark" : "light";
    document.documentElement.setAttribute("data-theme", next);
    try { localStorage.setItem("bc-theme", next); } catch (e) {}
  }
  ["themeToggle", "themeToggle2"].forEach(function (id) {
    var el = document.getElementById(id);
    if (el) el.addEventListener("click", toggleTheme);
  });

  // ---------- Nome file selezionato nel composer ----------
  var fileInput = document.querySelector('.composer input[type="file"]');
  var fileName = document.getElementById("fileName");
  if (fileInput && fileName) {
    fileInput.addEventListener("change", function () {
      fileName.textContent = fileInput.files.length ? fileInput.files[0].name : "";
    });
  }

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
