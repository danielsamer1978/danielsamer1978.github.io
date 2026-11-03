(() => {
  const body = document.body;
  const header = document.querySelector(".site-header");

  // Header wird beim Scrollen über dem Titelbild deckend
  const hero = document.querySelector(".hero");
  const onScroll = () => {
    const limit = hero ? hero.offsetHeight - header.offsetHeight - 10 : 10;
    header.classList.toggle("solid", window.scrollY > limit);
  };
  window.addEventListener("scroll", onScroll, { passive: true });
  onScroll();

  // Mobiles Menü
  const menuBtn = document.querySelector(".menu-btn");
  menuBtn?.addEventListener("click", () => {
    const open = body.classList.toggle("menu-open");
    menuBtn.setAttribute("aria-expanded", open);
  });
  document.querySelectorAll(".nav a").forEach(a => a.addEventListener("click", () => body.classList.remove("menu-open")));

  // Sanftes Einblenden
  if ("IntersectionObserver" in window) {
    const io = new IntersectionObserver(entries => entries.forEach(e => {
      if (e.isIntersecting) { e.target.classList.add("in"); io.unobserve(e.target); }
    }), { rootMargin: "0px 0px -8% 0px" });
    document.querySelectorAll(".reveal").forEach(el => io.observe(el));
  } else {
    document.querySelectorAll(".reveal").forEach(el => el.classList.add("in"));
  }

  // Videos: YouTube/Vimeo werden erst nach Klick geladen (Datenschutz)
  const embedUrl = (type, id, h) => type === "youtube"
    ? `https://www.youtube-nocookie.com/embed/${id}?autoplay=1&rel=0&modestbranding=1`
    : `https://player.vimeo.com/video/${id}?autoplay=1&dnt=1${h ? "&h=" + h : ""}`;
  const iframe = (type, id, h, title) => {
    const f = document.createElement("iframe");
    f.src = embedUrl(type, id, h);
    f.allow = "autoplay; fullscreen; picture-in-picture";
    f.allowFullscreen = true;
    f.title = title || "Video";
    return f;
  };
  document.querySelectorAll(".video > button").forEach(btn => {
    btn.addEventListener("click", () => {
      const box = btn.parentElement;
      const { type, id, h, title } = box.dataset;
      box.replaceChildren(iframe(type, id, h, title));
    });
  });

  // Lightbox für Bilder und Videos
  const lb = document.createElement("div");
  lb.className = "lightbox";
  lb.setAttribute("role", "dialog");
  lb.setAttribute("aria-modal", "true");
  const icon = d => `<svg viewBox="0 0 24 24" aria-hidden="true"><path d="${d}"/></svg>`;
  lb.innerHTML = `
    <button class="lb lb-close" aria-label="Schließen">${icon("M5 5l14 14M19 5L5 19")}</button>
    <button class="lb lb-prev" aria-label="Vorheriges Bild">${icon("M15 4l-8 8 8 8")}</button>
    <button class="lb lb-next" aria-label="Nächstes Bild">${icon("M9 4l8 8-8 8")}</button>
    <figure></figure><div class="lb-count"></div><div class="lb-caption"></div>`;
  body.appendChild(lb);
  const fig = lb.querySelector("figure");
  const count = lb.querySelector(".lb-count");
  const caption = lb.querySelector(".lb-caption");
  let set = [], idx = 0, lastFocus = null;

  const show = i => {
    idx = (i + set.length) % set.length;
    const it = set[idx];
    fig.replaceChildren();
    caption.textContent = "";
    if (it.video) {
      const box = document.createElement("div");
      box.className = "video";
      box.appendChild(iframe(it.video.type, it.video.id, it.video.h, it.title));
      fig.appendChild(box);
      caption.textContent = it.title || "";
    } else {
      const img = new Image();
      img.src = it.src; img.alt = it.alt || "";
      fig.appendChild(img);
      // Nachbarbild vorladen
      const next = set[(idx + 1) % set.length];
      if (next && next.src) { const p = new Image(); p.src = next.src; }
    }
    const multi = set.length > 1;
    lb.querySelector(".lb-prev").hidden = !multi;
    lb.querySelector(".lb-next").hidden = !multi;
    count.textContent = multi && !it.video ? `${idx + 1} / ${set.length}` : "";
  };
  const open = (items, i) => {
    set = items; lastFocus = document.activeElement;
    lb.classList.add("open"); body.style.overflow = "hidden";
    show(i);
    lb.querySelector(".lb-close").focus();
  };
  const close = () => {
    lb.classList.remove("open"); body.style.overflow = "";
    fig.replaceChildren();
    lastFocus?.focus();
  };
  lb.querySelector(".lb-close").addEventListener("click", close);
  lb.querySelector(".lb-prev").addEventListener("click", () => show(idx - 1));
  lb.querySelector(".lb-next").addEventListener("click", () => show(idx + 1));
  lb.addEventListener("click", e => { if (e.target === lb || e.target === fig) close(); });
  document.addEventListener("keydown", e => {
    if (!lb.classList.contains("open")) return;
    if (e.key === "Escape") close();
    if (e.key === "ArrowLeft" && set.length > 1) show(idx - 1);
    if (e.key === "ArrowRight" && set.length > 1) show(idx + 1);
  });
  let touchX = null;
  lb.addEventListener("touchstart", e => { touchX = e.touches[0].clientX; }, { passive: true });
  lb.addEventListener("touchend", e => {
    if (touchX === null || set.length < 2) return;
    const dx = e.changedTouches[0].clientX - touchX;
    if (Math.abs(dx) > 50) show(idx + (dx < 0 ? 1 : -1));
    touchX = null;
  });

  // Bildergruppen: alle Elemente mit data-full innerhalb eines [data-gallery]
  // (Reihenfolge wird beim Klick gelesen, weil das Foto-Raster Bilder umsortieren kann)
  document.querySelectorAll("[data-gallery]").forEach(g => {
    g.querySelectorAll("[data-full]").forEach(el => el.addEventListener("click", () => {
      const els = [...g.querySelectorAll("[data-full]")];
      const items = els.map(e => ({ src: e.dataset.full, alt: e.querySelector("img")?.alt }));
      open(items, els.indexOf(el));
    }));
  });

  // Foto-Raster: bündige Reihen, ab und zu eine höhere Reihe mit Hochformaten
  document.querySelectorAll("[data-justify]").forEach(wall => {
    const items = [...wall.querySelectorAll("button")].map(el => ({ el, r: parseFloat(el.style.getPropertyValue("--r")) }));
    const layout = () => {
      const W = wall.clientWidth;
      const gap = parseFloat(getComputedStyle(wall).columnGap) || 10;
      const target = parseFloat(getComputedStyle(wall).getPropertyValue("--row-h")) || 300;
      const tallCount = W < 600 ? 2 : 3;
      const rows = [];
      const pool = items.slice();
      let since = 0;
      while (pool.length) {
        // nach einigen normalen Reihen: die nächsten Hochformate als hohe Reihe
        if (since >= 4) {
          const idx = [];
          for (let i = 0; i < Math.min(pool.length, 12) && idx.length < tallCount; i++) if (pool[i].r < 0.9) idx.push(i);
          if (idx.length === tallCount) {
            rows.push(idx.map(i => pool[i]));
            idx.reverse().forEach(i => pool.splice(i, 1));
            since = 0;
            continue;
          }
        }
        const row = [];
        let sum = 0;
        while (pool.length) {
          row.push(pool.shift()); sum += row[row.length - 1].r;
          if (sum * target + gap * (row.length - 1) >= W) {
            // Reihe ohne das letzte Bild wäre näher an der Zielhöhe? Dann zurücklegen.
            const hWith = (W - gap * (row.length - 1)) / sum;
            const sumWithout = sum - row[row.length - 1].r;
            if (row.length > 1) {
              const hWithout = (W - gap * (row.length - 2)) / sumWithout;
              if (Math.abs(Math.log(hWithout / target)) < Math.abs(Math.log(hWith / target))) {
                pool.unshift(row.pop()); sum = sumWithout;
              }
            }
            break;
          }
        }
        rows.push(row); since++;
      }
      // letzte Reihe ebenfalls auf volle Breite: wird sie dadurch zu hoch,
      // lieber mit der vorherigen Reihe zusammenlegen
      const rowH = row => (W - gap * (row.length - 1)) / row.reduce((a, it) => a + it.r, 0);
      const off = h => Math.abs(Math.log(h / target));
      if (rows.length > 1 && since > 1) {
        const last = rows[rows.length - 1], merged = rows[rows.length - 2].concat(last);
        if (off(rowH(merged)) < off(rowH(last))) { rows.pop(); rows[rows.length - 1] = merged; }
      }
      const frag = document.createDocumentFragment();
      rows.forEach((row, n) => {
        const sum = row.reduce((a, it) => a + it.r, 0);
        const free = W - gap * (row.length - 1);
        const h = free / sum;
        const div = document.createElement("div");
        div.className = "row";
        row.forEach(it => {
          it.el.style.width = (h * it.r) + "px";
          it.el.style.height = h + "px";
          div.appendChild(it.el);
        });
        frag.appendChild(div);
      });
      wall.style.setProperty("--gap", gap + "px");
      wall.replaceChildren(frag);
      wall.classList.add("justified");
    };
    layout();
    let lastW = wall.clientWidth, t;
    window.addEventListener("resize", () => {
      clearTimeout(t);
      t = setTimeout(() => { if (wall.clientWidth !== lastW) { lastW = wall.clientWidth; layout(); } }, 150);
    });
  });
  // Weitere Arbeiten: Video im Overlay
  document.querySelectorAll("[data-play]").forEach(el => {
    el.addEventListener("click", () => {
      const { type, id, h, title } = el.dataset;
      open([{ video: { type, id, h }, title }], 0);
    });
  });
})();
