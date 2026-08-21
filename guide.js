/* OwnerOS room guide. One shared script, like midnight.css is one shared
   stylesheet: any element with data-guide="<key>" becomes Brock's orb. Press it
   and he talks you through that part of the room. Clips are shipped in
   assets/guide/ and fetched as blobs (send_file has no Range support, so never
   <audio src>). No Fish key is needed on the owner's Mac. Fallback: the
   shipped transcript spoken by the browser voice, text shown either way. */
(function () {
  "use strict";
  var CSS =
    ".gd-orb{width:26px;height:26px;border-radius:50%;border:1px solid var(--line);" +
    "background:var(--g2);position:relative;flex-shrink:0;cursor:pointer;padding:0;" +
    "display:inline-grid;place-items:center;vertical-align:middle;transition:border-color .3s}" +
    ".gd-orb img{width:100%;height:100%;object-fit:cover;border-radius:50%;display:block}" +
    ".gd-orb::after{content:'';position:absolute;inset:-1px;border-radius:50%;opacity:0;" +
    "pointer-events:none;transition:opacity .3s}" +
    ".gd-orb.on{border-color:var(--ember)}" +
    ".gd-orb.on::after{opacity:1;box-shadow:0 0 0 5px rgba(255,107,53,.14),0 0 18px 3px rgba(255,107,53,.22);" +
    "animation:gd-glow 1.6s ease-in-out infinite}" +
    ".gd-orb.lg{width:36px;height:36px}" +
    "@keyframes gd-glow{0%,100%{transform:scale(1)}50%{transform:scale(1.06)}}" +
    ".gd-strip{position:fixed;left:50%;bottom:22px;transform:translateX(-50%) translateY(12px);" +
    "width:min(680px,calc(100% - 32px));background:var(--g1);border:1px solid var(--line);" +
    "border-radius:14px;padding:16px 18px 16px 18px;display:flex;gap:14px;align-items:flex-start;" +
    "z-index:90;opacity:0;pointer-events:none;transition:opacity .25s,transform .25s;" +
    "box-shadow:0 20px 60px rgba(0,0,0,.45)}" +
    ".gd-strip.on{opacity:1;pointer-events:auto;transform:translateX(-50%) translateY(0)}" +
    ".gd-strip .gd-face{width:44px;height:44px;border-radius:50%;border:1px solid var(--line);" +
    "overflow:hidden;flex-shrink:0}.gd-strip .gd-face img{width:100%;height:100%;object-fit:cover;display:block}" +
    ".gd-strip .gd-body{flex:1;min-width:0}" +
    ".gd-strip .gd-eyebrow{font-family:var(--f-mono);font-size:10px;letter-spacing:.14em;" +
    "text-transform:uppercase;color:var(--mid);margin-bottom:6px}" +
    ".gd-strip .gd-text{font-family:var(--f-body);font-size:14px;line-height:1.55;color:#cbc8c3}" +
    ".gd-strip .gd-acts{display:flex;gap:8px;flex-shrink:0}" +
    ".gd-strip .gd-btn{font:inherit;font-family:var(--f-statement);font-size:12px;font-weight:500;" +
    "color:var(--ink);background:transparent;border:1px solid var(--line);border-radius:980px;" +
    "padding:6px 12px;cursor:pointer}.gd-strip .gd-btn:hover{background:var(--g2)}" +
    "@media (prefers-reduced-motion:reduce){.gd-orb.on::after{animation:none}.gd-strip{transition:none}}" +
    "@media (max-width:720px){.gd-strip{flex-wrap:wrap}.gd-strip .gd-acts{width:100%;justify-content:flex-end}}";

  var data = null, audio = null, strip = null, current = null, currentBtn = null;

  function style() {
    var s = document.createElement("style"); s.textContent = CSS;
    document.head.appendChild(s);
  }

  function load() {
    if (data) return Promise.resolve(data);
    return fetch("/assets/guide/guide.json").then(function (r) { return r.json(); })
      .then(function (d) { data = d; return d; });
  }

  function ensureStrip() {
    if (strip) return strip;
    strip = document.createElement("div");
    strip.className = "gd-strip";
    strip.setAttribute("role", "status");
    strip.innerHTML =
      '<div class="gd-face"><img src="/assets/hermes/brock.jpg" alt=""></div>' +
      '<div class="gd-body"><div class="gd-eyebrow"></div><div class="gd-text"></div></div>' +
      '<div class="gd-acts"><button class="gd-btn" type="button" data-gd="stop">Stop</button>' +
      '<button class="gd-btn" type="button" data-gd="close" aria-label="Close">Close</button></div>';
    document.body.appendChild(strip);
    strip.addEventListener("click", function (e) {
      var b = e.target.closest("[data-gd]"); if (!b) return;
      stopAll(); if (b.dataset.gd === "close") strip.classList.remove("on");
    });
    return strip;
  }

  function setOn(btn, on) {
    document.querySelectorAll(".gd-orb.on").forEach(function (b) { b.classList.remove("on"); });
    if (on && btn) btn.classList.add("on");
  }

  function stopAll() {
    if (audio) { try { audio.pause(); } catch (e) {} audio = null; }
    if (window.speechSynthesis) { try { speechSynthesis.cancel(); } catch (e) {} }
    setOn(null, false); current = null; currentBtn = null;
  }

  function pickVoice() {
    return new Promise(function (resolve) {
      var done = false;
      function choose() {
        if (done) return;
        var vs = speechSynthesis.getVoices(); if (!vs.length) return;
        done = true;
        resolve(vs.find(function (v) { return v.name === "Lee"; }) ||
                vs.find(function (v) { return v.name === "Karen"; }) ||
                vs.find(function (v) { return /en[-_]AU/i.test(v.lang); }) || vs[0]);
      }
      choose();
      if (!done) {
        speechSynthesis.addEventListener("voiceschanged", choose, { once: true });
        setTimeout(function () { if (!done) { done = true; resolve(null); } }, 1000);
      }
    });
  }

  function speakFallback(text, btn) {
    if (!("speechSynthesis" in window)) return;
    pickVoice().then(function (v) {
      if (current === null) return;
      var u = new SpeechSynthesisUtterance(text);
      if (v) u.voice = v;
      u.rate = 1; u.pitch = 1;
      u.onend = function () { setOn(btn, false); current = null; };
      speechSynthesis.cancel(); speechSynthesis.speak(u);
    });
  }

  function play(key, btn) {
    if (current === key && audio && !audio.paused) { stopAll(); return; }
    stopAll();
    load().then(function (d) {
      var room = d.rooms[key]; if (!room) return;
      current = key; currentBtn = btn;
      var s = ensureStrip();
      s.querySelector(".gd-eyebrow").textContent = "Brock · " + room.title;
      s.querySelector(".gd-text").textContent = room.text;
      s.classList.add("on");
      setOn(btn, true);
      return fetch("/assets/guide/" + key + ".mp3").then(function (r) {
        if (!r.ok) throw new Error("no clip"); return r.blob();
      }).then(function (blob) {
        if (current !== key) return;
        audio = new Audio(URL.createObjectURL(blob));
        audio.onended = function () { setOn(btn, false); current = null; };
        return audio.play();
      }).catch(function () { speakFallback(room.text, btn); });
    }).catch(function () {});
  }

  function decorate() {
    document.querySelectorAll("[data-guide]").forEach(function (b) {
      if (b.dataset.gdReady) return;
      b.dataset.gdReady = "1";
      b.classList.add("gd-orb");
      b.setAttribute("type", "button");
      b.setAttribute("aria-label", "Brock, talk me through this");
      b.title = "Talk me through this";
      b.innerHTML = '<img src="/assets/hermes/brock.jpg" alt="">';
    });
  }

  style(); decorate();
  new MutationObserver(decorate).observe(document.documentElement, { childList: true, subtree: true });
  document.addEventListener("click", function (e) {
    var b = e.target.closest("[data-guide]"); if (!b) return;
    e.preventDefault(); play(b.dataset.guide, b);
  });
  document.addEventListener("keydown", function (e) { if (e.key === "Escape" && current) stopAll(); });
  window.osGuide = { play: play, stop: stopAll };
})();
