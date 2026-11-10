/*
 * Visuel Instagram « OFFRES SPORT BUSINESS » (1080 x 1350), dessiné en canvas.
 * Reproduit ~/ssb-insta/offres/build.py : le modèle vierge porte déjà les 5 cartes beiges,
 * on y pose le logo, le titre, l'entreprise et la pastille du contrat.
 * Typo de la charte SSB : General Sans (500, 600) et Geist Mono (500), chargées par FontFace.
 *
 * API : SSBInsta.ready() -> Promise ; SSBInsta.render(canvas, cartes) -> Promise ;
 *       SSBInsta.loadLogo(url | File) -> Promise<{ img, w, h }> ; SSBInsta.autoHeight(logo).
 * Une carte : { titre, entreprise, contrat, logo: { img, w, h } | null, logoH }.
 */
(function (g) {
  "use strict";
  const W = 1080, H = 1350;
  const CX = 173, CW = 734, CH = 144, CY = [278, 463, 650, 835, 1020];
  const TX = CX + 206, TW = CW - 206 - 20;            // bloc texte : 508 px de large
  const LOGO_CX = CX + 18 + 86, LOGO_W = 160;           // zone logo de 172 px, logo de 160 px au plus
  const INK = "#0b1428", GREY = "#5a5f6b", PILL_BG = "#15213a", PILL_TX = "#dcab55";
  const GS = '"SSB General Sans"', GM = '"SSB Geist Mono"';
  const here = document.currentScript && document.currentScript.src
    ? new URL(".", document.currentScript.src).href : "insta/";

  let loading = null;
  function loadImage(src) {
    return new Promise((res, rej) => {
      const img = new Image();
      img.onload = () => res(img);
      img.onerror = () => rej(new Error("Image illisible : " + src));
      img.src = src;
    });
  }
  function ready() {
    if (!loading) loading = (async () => {
      const faces = [
        new FontFace("SSB General Sans", `url(${here}gs500.woff2)`, { weight: "500" }),
        new FontFace("SSB General Sans", `url(${here}gs600.woff2)`, { weight: "600" }),
        new FontFace("SSB Geist Mono", `url(${here}gm500.woff2)`, { weight: "500" }),
      ];
      faces.forEach(f => document.fonts.add(f));
      await Promise.all(faces.map(f => f.load()));
      return { bg: await loadImage(here + "modele-vierge.webp") };
    })();
    return loading;
  }

  // Ligne de base mesurée par le navigateur, comme dans le rendu HTML de référence
  // (hauteur de ligne CSS, demi-interlignage compris).
  const baseCache = new Map();
  function baseline(font, lineHeight) {
    const key = font + "|" + lineHeight;
    if (!baseCache.has(key)) {
      const d = document.createElement("div");
      d.style.cssText = `position:absolute;left:-9999px;top:0;white-space:nowrap;font:${font};line-height:${lineHeight}`;
      d.innerHTML = 'Xg<span style="display:inline-block;width:0;height:0"></span>';
      document.body.appendChild(d);
      baseCache.set(key, { base: d.lastChild.offsetTop, height: d.offsetHeight });
      d.remove();
    }
    return baseCache.get(key);
  }

  // Interlettrage : ctx.letterSpacing quand le navigateur le connaît, sinon lettre par lettre.
  const hasLS = "letterSpacing" in CanvasRenderingContext2D.prototype;
  function setLS(ctx, px) { if (hasLS) ctx.letterSpacing = px + "px"; }
  function width(ctx, text, ls) {
    return hasLS ? ctx.measureText(text).width : ctx.measureText(text).width + ls * [...text].length;
  }
  function fill(ctx, text, x, y, ls) {
    if (hasLS || !ls) { ctx.fillText(text, x, y); return; }
    for (const ch of text) { ctx.fillText(ch, x, y); x += ctx.measureText(ch).width + ls; }
  }

  // Retour à la ligne aux espaces (et après un trait d'union dans un mot trop long).
  function wrap(ctx, text, max, ls) {
    const words = text.split(/\s+/).filter(Boolean), lines = [];
    let line = "";
    for (const w of words) {
      const test = line ? line + " " + w : w;
      if (!line || width(ctx, test, ls) <= max) { line = test; continue; }
      lines.push(line); line = w;
    }
    if (line) lines.push(line);
    return lines;
  }
  function ellipsis(ctx, text, max, ls) {
    if (width(ctx, text, ls) <= max) return text;
    let t = text;
    while (t && width(ctx, t.replace(/[\s\-–,·:]+$/, "") + "…", ls) > max) t = t.slice(0, -1);
    return t.replace(/[\s\-–,·:]+$/, "") + "…";
  }

  // Titre : 28 px, deux lignes au plus ; la taille descend par demi-pixel jusqu'à 20 px,
  // puis on coupe avec « … ».
  function fitTitle(ctx, text) {
    for (let s = 28; s >= 20; s -= 0.5) {
      ctx.font = `600 ${s}px ${GS}`; setLS(ctx, -0.4);
      const lines = wrap(ctx, text, TW, -0.4);
      if (lines.length <= 2) return { s, lines };
    }
    const lines = wrap(ctx, text, TW, -0.4);
    return { s: 20, lines: [lines[0], ellipsis(ctx, lines.slice(1).join(" "), TW, -0.4)] };
  }

  function rrect(ctx, x, y, w, h, r) {
    ctx.beginPath();
    if (ctx.roundRect) { ctx.roundRect(x, y, w, h, r); return; }
    ctx.moveTo(x + r, y); ctx.arcTo(x + w, y, x + w, y + h, r); ctx.arcTo(x + w, y + h, x, y + h, r);
    ctx.arcTo(x, y + h, x, y, r); ctx.arcTo(x, y, x + w, y, r); ctx.closePath();
  }

  // Hauteur maximale d'un logo sans réglage : surface visuelle à peu près constante
  // (PSG rond : ~98 px ; Canal+ très large : bloqué par les 160 px de largeur).
  function autoHeight(logo) {
    const ratio = logo.w / logo.h;
    return Math.round(Math.min(104, Math.sqrt(9600 / ratio)));
  }

  function drawCard(ctx, c, y) {
    // Logo, centré dans sa zone, contenu dans 160 x logoH.
    if (c.logo) {
      const maxH = c.logoH || autoHeight(c.logo);
      const k = Math.min(LOGO_W / c.logo.w, maxH / c.logo.h);
      const w = c.logo.w * k, h = c.logo.h * k;
      ctx.drawImage(c.logo.img, LOGO_CX - w / 2, y + CH / 2 - h / 2, w, h);
    } else if (c.entreprise) {
      // Pas de logo : le nom de l'employeur à sa place.
      ctx.fillStyle = INK; ctx.textAlign = "center";
      ctx.font = `600 22px ${GS}`; setLS(ctx, 0);
      const lines = wrap(ctx, c.entreprise, LOGO_W, 0).slice(0, 3);
      const lh = 26, top = y + CH / 2 - (lines.length * lh) / 2 + 19;
      lines.forEach((l, i) => fill(ctx, ellipsis(ctx, l, LOGO_W, 0), LOGO_CX, top + i * lh, 0));
      ctx.textAlign = "left";
    }

    // Pastille du contrat, en bas à droite.
    const label = (c.contrat || "").toUpperCase();
    let pillX = CX + CW - 20;
    if (label) {
      ctx.font = `500 17px ${GM}`; setLS(ctx, 1.5);
      const pw = width(ctx, label, 1.5) + 48, ph = 38, py = y + CH - 14 - ph;
      pillX = CX + CW - 20 - pw;
      ctx.fillStyle = PILL_BG; rrect(ctx, pillX, py, pw, ph, 19); ctx.fill();
      const m = baseline(`500 17px ${GM}`, "normal");
      ctx.fillStyle = PILL_TX;
      fill(ctx, label, pillX + 24, py + (ph - m.height) / 2 + m.base, 1.5);
    }

    // Titre.
    const t = fitTitle(ctx, c.titre || "");
    const mt = baseline(`600 ${t.s}px ${GS}`, "1.12");
    const lh = t.s * 1.12;
    ctx.fillStyle = INK; ctx.font = `600 ${t.s}px ${GS}`; setLS(ctx, -0.4);
    t.lines.forEach((l, i) => fill(ctx, l, TX, y + 16 + i * lh + mt.base, -0.4));

    // Entreprise, en bas à gauche, sans toucher la pastille.
    ctx.font = `500 21px ${GS}`; setLS(ctx, 0); ctx.fillStyle = GREY;
    const me = baseline(`500 21px ${GS}`, "normal");
    const name = ellipsis(ctx, c.entreprise || "", pillX - 16 - TX, 0);
    fill(ctx, name, TX, y + CH - 14 - 6 - me.height + me.base, 0);
    if (hasLS) ctx.letterSpacing = "0px";
  }

  async function render(canvas, cards) {
    const { bg } = await ready();
    canvas.width = W; canvas.height = H;
    const ctx = canvas.getContext("2d");
    ctx.textBaseline = "alphabetic"; ctx.textAlign = "left";
    ctx.drawImage(bg, 0, 0, W, H);
    cards.slice(0, 5).forEach((c, i) => { if (c) drawCard(ctx, c, CY[i]); });
  }

  // Logo depuis une URL ou un fichier déposé. Un SVG sans largeur ni hauteur prend celles de
  // son viewBox, sinon le navigateur lui donnerait 300 x 150. Un logo clair (fait pour un fond
  // sombre) est recoloré en encre, et un fond blanc opaque est rendu transparent.
  async function loadLogo(source) {
    let url = typeof source === "string" ? source : URL.createObjectURL(source);
    const isSvg = typeof source === "string" ? /\.svg(\?|$)/i.test(source) : source.type === "image/svg+xml";
    if (isSvg) {
      const text = typeof source === "string" ? await (await fetch(url)).text() : await source.text();
      const doc = new DOMParser().parseFromString(text, "image/svg+xml"), svg = doc.documentElement;
      const vb = (svg.getAttribute("viewBox") || "").split(/[\s,]+/).map(Number);
      const pw = parseFloat(svg.getAttribute("width")), ph = parseFloat(svg.getAttribute("height"));
      let w = pw, h = ph;
      if (!(w > 0 && h > 0) && vb.length === 4) { w = vb[2]; h = vb[3]; }
      if (w > 0 && h > 0) {
        const k = 1200 / Math.max(w, h);       // rendu net une fois réduit
        if (!svg.getAttribute("viewBox")) svg.setAttribute("viewBox", `0 0 ${w} ${h}`);
        svg.setAttribute("width", w * k); svg.setAttribute("height", h * k);
        svg.setAttribute("preserveAspectRatio", "xMidYMid meet");
        url = URL.createObjectURL(new Blob([new XMLSerializer().serializeToString(doc)], { type: "image/svg+xml" }));
      }
    }
    const img = await loadImage(url);
    const logo = { img, w: img.naturalWidth || 300, h: img.naturalHeight || 150 };
    return adapt(logo);
  }

  function lum(r, g2, b) { return (0.2126 * r + 0.7152 * g2 + 0.0722 * b) / 255; }
  function adapt(logo) {
    const k = Math.min(1, 600 / Math.max(logo.w, logo.h));
    const cw = Math.max(1, Math.round(logo.w * k)), ch = Math.max(1, Math.round(logo.h * k));
    const cv = document.createElement("canvas"); cv.width = cw; cv.height = ch;
    const ctx = cv.getContext("2d");
    ctx.drawImage(logo.img, 0, 0, cw, ch);
    let data;
    try { data = ctx.getImageData(0, 0, cw, ch); } catch { return logo; }
    const p = data.data, n = cw * ch;
    let transparent = 0;
    for (let i = 3; i < p.length; i += 4) if (p[i] < 20) transparent++;
    let changed = false;
    if (transparent / n < 0.02) {
      // Fond opaque : un fond blanc ou très clair (mêmes coins) ferait une boîte sur la carte
      // beige, on l'efface. Un cartouche sombre (Canal+) fait partie du logo : on le garde.
      const at = (x, y) => { const i = (y * cw + x) * 4; return [p[i], p[i + 1], p[i + 2]]; };
      const corners = [at(0, 0), at(cw - 1, 0), at(0, ch - 1), at(cw - 1, ch - 1)];
      const [r0, g0, b0] = corners[0];
      const same = corners.every(([r, g2, b]) => Math.abs(r - r0) + Math.abs(g2 - g0) + Math.abs(b - b0) < 30);
      if (!same || lum(r0, g0, b0) < 0.85) return logo;
      for (let i = 0; i < p.length; i += 4) {
        const d = Math.abs(p[i] - r0) + Math.abs(p[i + 1] - g0) + Math.abs(p[i + 2] - b0);
        if (d < 60) p[i + 3] = Math.round(255 * Math.max(0, (d - 30) / 30));
      }
      changed = true;
    }
    // Logo clair : il disparaîtrait sur la carte beige, on le passe en encre.
    let sum = 0, count = 0;
    for (let i = 0; i < p.length; i += 4) if (p[i + 3] > 128) { sum += lum(p[i], p[i + 1], p[i + 2]); count++; }
    if (count && sum / count > 0.78) {
      for (let i = 0; i < p.length; i += 4) { p[i] = 0x0b; p[i + 1] = 0x14; p[i + 2] = 0x28; }
      changed = true;
    }
    if (!changed) return logo;
    ctx.putImageData(data, 0, 0);
    return { img: cv, w: cw, h: ch, adapte: true };
  }

  g.SSBInsta = { ready, render, loadLogo, autoHeight, W, H };
})(window);
