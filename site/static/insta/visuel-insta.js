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

  // Sous-titre libre sous « OFFRES SPORT BUSINESS » (« Droit du sport », « Spécial clubs »...) :
  // Geist Mono doré en capitales espacées, comme les pastilles.
  function subtitle(ctx, text, cx, y, size, ls, maxW) {
    const t = (text || "").trim().toUpperCase();
    if (!t) return;
    ctx.font = `500 ${size}px ${GM}`; setLS(ctx, ls); ctx.fillStyle = PILL_TX;
    const line = ellipsis(ctx, t, maxW, ls), w = width(ctx, line, ls);
    fill(ctx, line, cx - w / 2 + (hasLS ? ls / 2 : 0), y, ls);
    if (hasLS) ctx.letterSpacing = "0px";
  }

  async function render(canvas, cards, opts = {}) {
    const { bg } = await ready();
    canvas.width = W; canvas.height = H;
    const ctx = canvas.getContext("2d");
    ctx.textBaseline = "alphabetic"; ctx.textAlign = "left";
    ctx.drawImage(bg, 0, 0, W, H);
    subtitle(ctx, opts.sousTitre, W / 2, 238, 25, 5, 760);
    cards.slice(0, 5).forEach((c, i) => { if (c) drawCard(ctx, c, CY[i]); });
  }

  // Logo depuis une URL ou un fichier déposé. Un SVG sans largeur ni hauteur prend celles de
  // son viewBox, sinon le navigateur lui donnerait 300 x 150. Un logo clair (fait pour un fond
  // sombre) est recoloré en encre, et un fond blanc opaque est rendu transparent.
  async function loadLogo(source) {
    let url = typeof source === "string" ? source : URL.createObjectURL(source);
    const isSvg = typeof source === "string" ? /\.svg(\?|$)/i.test(source) || source.startsWith("data:image/svg")
      : source.type === "image/svg+xml";
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

  // --- Story 1080 x 1920 : une offre par story -------------------------------------------
  // Le fond est redessiné (le modèle du post porte ses 5 cartes) ; le titre, l'icône, le logo
  // SSB et le bandeau « Adhère » sont repris du modèle, détourés par leur luminosité.
  // Zones de l'interface Instagram : rien d'important dans les 250 px du haut et du bas.
  const SW = 1080, SH = 1920;
  const PIECES = {                      // x, y, largeur, hauteur dans modele-vierge.webp
    titre: [180, 130, 721, 58], icone: [944, 52, 68, 67], ssb: [80, 1194, 134, 79], cta: [298, 1198, 484, 49],
  };
  const cut = new Map();
  function piece(bg, name) {
    if (cut.has(name)) return cut.get(name);
    const [x, y, w, h] = PIECES[name];
    const cv = document.createElement("canvas"); cv.width = w; cv.height = h;
    const ctx = cv.getContext("2d");
    ctx.drawImage(bg, x, y, w, h, 0, 0, w, h);
    const d = ctx.getImageData(0, 0, w, h), p = d.data;
    // Le fond navy devient transparent, le texte clair ou doré reste.
    for (let i = 0; i < p.length; i += 4) {
      const L = lum(p[i], p[i + 1], p[i + 2]);
      p[i + 3] = Math.round(255 * Math.min(1, Math.max(0, (L - 0.16) / 0.3)));
    }
    ctx.putImageData(d, 0, 0);
    cut.set(name, cv);
    return cv;
  }

  let storyBg = null;
  function grain(ctx, w, h, x0, y0, r, colors) {
    // Halo doré granuleux, comme les coins du modèle.
    const cv = document.createElement("canvas"); cv.width = w; cv.height = h;
    const c = cv.getContext("2d");
    const gr = c.createRadialGradient(x0, y0, 0, x0, y0, r);
    colors.forEach(([at, col]) => gr.addColorStop(at, col));
    c.fillStyle = gr; c.fillRect(0, 0, w, h);
    const d = c.getImageData(0, 0, w, h), p = d.data;
    let seed = 7;
    const rnd = () => (seed = (seed * 16807) % 2147483647) / 2147483647;
    for (let i = 3; i < p.length; i += 4) {
      const a = p[i] / 255;
      // Chaque pixel s'allume ou non selon la force du halo : un nuage de grains qui se
      // resserre vers le coin, sans bord net.
      p[i] = Math.round(255 * (rnd() < Math.pow(a, 0.8) ? Math.min(1, 0.35 + a * 0.75) : a * 0.12));
    }
    c.putImageData(d, 0, 0);
    ctx.drawImage(cv, 0, 0);
  }
  function backgroundStory() {
    if (storyBg) return storyBg;
    const cv = document.createElement("canvas"); cv.width = SW; cv.height = SH;
    const ctx = cv.getContext("2d");
    const base = ctx.createLinearGradient(0, 0, 0, SH);
    base.addColorStop(0, "#0a1b31"); base.addColorStop(0.5, "#0a1a2e"); base.addColorStop(1, "#0d2036");
    ctx.fillStyle = base; ctx.fillRect(0, 0, SW, SH);
    // Halo bleu à gauche et grands anneaux discrets, comme le fond du post.
    const blue = ctx.createRadialGradient(0, 760, 0, 0, 760, 700);
    blue.addColorStop(0, "rgba(40, 92, 160, 0.42)"); blue.addColorStop(1, "rgba(40, 92, 160, 0)");
    ctx.fillStyle = blue; ctx.fillRect(0, 0, SW, SH);
    ctx.strokeStyle = "rgba(90, 120, 160, 0.10)"; ctx.lineWidth = 120;
    ctx.beginPath(); ctx.arc(560, 980, 600, 0, Math.PI * 2); ctx.stroke();
    ctx.strokeStyle = "rgba(90, 120, 160, 0.06)"; ctx.lineWidth = 70;
    ctx.beginPath(); ctx.arc(560, 980, 330, 0, Math.PI * 2); ctx.stroke();
    // Quadrillage fin.
    ctx.strokeStyle = "rgba(140, 170, 210, 0.055)"; ctx.lineWidth = 1;
    ctx.beginPath();
    for (let x = 0.5; x < SW; x += 22) { ctx.moveTo(x, 0); ctx.lineTo(x, SH); }
    for (let y = 0.5; y < SH; y += 22) { ctx.moveTo(0, y); ctx.lineTo(SW, y); }
    ctx.stroke();
    grain(ctx, SW, SH, 0, 0, 820, [[0, "rgba(238,182,84,0.9)"], [0.3, "rgba(226,160,50,0.5)"], [0.7, "rgba(226,160,50,0.12)"], [1, "rgba(226,160,50,0)"]]);
    grain(ctx, SW, SH, SW, SH, 900, [[0, "rgba(255,244,222,0.95)"], [0.18, "rgba(244,196,96,0.85)"], [0.5, "rgba(218,147,21,0.35)"], [0.8, "rgba(218,147,21,0.08)"], [1, "rgba(218,147,21,0)"]]);
    // Cadre arrondi, doré en haut à gauche et en bas à droite.
    const fr = ctx.createLinearGradient(0, 0, SW, SH);
    fr.addColorStop(0, "rgba(242,196,90,0.95)"); fr.addColorStop(0.3, "rgba(120,150,190,0.25)");
    fr.addColorStop(0.7, "rgba(120,150,190,0.25)"); fr.addColorStop(1, "rgba(255,236,200,0.95)");
    ctx.strokeStyle = fr; ctx.lineWidth = 3;
    rrect(ctx, 58, 58, SW - 116, SH - 116, 40); ctx.stroke();
    storyBg = cv;
    return cv;
  }

  // Texte centré sur plusieurs lignes, taille réduite jusqu'à ce qu'il tienne.
  function fitCentered(ctx, text, maxW, maxLines, from, to, weight, ls) {
    for (let s = from; s >= to; s -= 1) {
      ctx.font = `${weight} ${s}px ${GS}`; setLS(ctx, ls);
      const lines = wrap(ctx, text, maxW, ls);
      if (lines.length <= maxLines) return { s, lines };
    }
    ctx.font = `${weight} ${to}px ${GS}`; setLS(ctx, ls);
    const lines = wrap(ctx, text, maxW, ls);
    return { s: to, lines: [...lines.slice(0, maxLines - 1), ellipsis(ctx, lines.slice(maxLines - 1).join(" "), maxW, ls)] };
  }
  function centered(ctx, text, cx, y, ls) {
    const w = width(ctx, text, ls);
    fill(ctx, text, cx - w / 2 + (hasLS ? ls / 2 : 0), y, ls);
  }

  async function renderStory(canvas, c, index, total, opts = {}) {
    const { bg } = await ready();
    canvas.width = SW; canvas.height = SH;
    const ctx = canvas.getContext("2d");
    ctx.textBaseline = "alphabetic"; ctx.textAlign = "left";
    ctx.drawImage(backgroundStory(), 0, 0);
    const cx = SW / 2;

    // En-tête : icône SSB et titre du modèle, un peu agrandi.
    ctx.drawImage(piece(bg, "icone"), SW - 58 - 34 - 68 * 1.25, 92, 68 * 1.25, 67 * 1.25);
    const tk = 1.18, tw = PIECES.titre[2] * tk, th = PIECES.titre[3] * tk;
    ctx.drawImage(piece(bg, "titre"), cx - tw / 2, 262, tw, th);
    const sous = (opts.sousTitre || "").trim();
    if (sous) subtitle(ctx, sous, cx, 390, 30, 5, 860);
    else if (total > 1) {
      ctx.font = `500 26px ${GM}`; setLS(ctx, 4); ctx.fillStyle = PILL_TX;
      centered(ctx, `OFFRE ${index + 1} / ${total}`, cx, 388, 4);
    }

    // Carte de l'offre.
    const X = 90, Y = 430, CWs = SW - 180, CHs = 1060, inner = CWs - 120;
    ctx.save();
    ctx.shadowColor = "rgba(0, 0, 0, 0.35)"; ctx.shadowBlur = 40; ctx.shadowOffsetY = 14;
    ctx.fillStyle = "#e4e1d8"; rrect(ctx, X, Y, CWs, CHs, 44); ctx.fill();
    ctx.restore();
    ctx.save(); rrect(ctx, X, Y, CWs, CHs, 44); ctx.clip();
    ctx.strokeStyle = "rgba(11, 20, 40, 0.035)"; ctx.lineWidth = 1; ctx.beginPath();
    for (let x = X + 0.5; x < X + CWs; x += 22) { ctx.moveTo(x, Y); ctx.lineTo(x, Y + CHs); }
    for (let y = Y + 0.5; y < Y + CHs; y += 22) { ctx.moveTo(X, y); ctx.lineTo(X + CWs, y); }
    ctx.stroke(); ctx.restore();
    if (sous && total > 1) {
      // Avec un sous-titre, le numéro de l'offre passe dans le coin de la carte.
      ctx.font = `500 24px ${GM}`; setLS(ctx, 3); ctx.fillStyle = "rgba(11, 20, 40, 0.45)";
      const lab = `${index + 1} / ${total}`;
      fill(ctx, lab, X + CWs - 44 - width(ctx, lab, 3), Y + 62, 3);
    }

    // Contenu de la carte, centré verticalement : logo (ou nom), trait, titre, entreprise et
    // lieu, pastille du contrat.
    let logoH = 0, nameFit = null;
    if (c.logo) {
      const maxH = Math.min(260, (c.logoH || autoHeight(c.logo)) * 2.5), maxW = 560;
      const k = Math.min(maxW / c.logo.w, maxH / c.logo.h);
      logoH = c.logo.h * k;
    } else {
      nameFit = fitCentered(ctx, c.entreprise || "", inner, 2, 66, 46, 600, -0.5);
      logoH = nameFit.lines.length * nameFit.s * 1.12;
    }
    const t = fitCentered(ctx, c.titre || "", inner, 4, 78, 48, 600, -0.8);
    const lh = t.s * 1.12;
    ctx.font = `500 36px ${GS}`; setLS(ctx, 0);
    const sub = [c.logo ? c.entreprise : "", c.lieu].filter(Boolean).map(x => ellipsis(ctx, x, inner, 0));
    const label = (c.contrat || "").toUpperCase(), ph = 72;
    const blockH = logoH + 56 + 3 + 56 + t.lines.length * lh + (sub.length ? 30 + sub.length * 50 : 0) + (label ? 64 + ph : 0);
    let y = Y + Math.max(70, (CHs - blockH) / 2);

    if (c.logo) {
      const k = logoH / c.logo.h;
      ctx.drawImage(c.logo.img, cx - c.logo.w * k / 2, y, c.logo.w * k, logoH);
    } else {
      ctx.fillStyle = INK; ctx.font = `600 ${nameFit.s}px ${GS}`; setLS(ctx, -0.5);
      const mn = baseline(`600 ${nameFit.s}px ${GS}`, "1.12");
      nameFit.lines.forEach((l, i) => centered(ctx, l, cx, y + i * nameFit.s * 1.12 + mn.base, -0.5));
    }
    y += logoH + 56;
    ctx.fillStyle = "rgba(11, 20, 40, 0.14)"; ctx.fillRect(cx - 60, y, 120, 3);
    y += 3 + 56;

    ctx.fillStyle = INK; ctx.font = `600 ${t.s}px ${GS}`; setLS(ctx, -0.8);
    const mt = baseline(`600 ${t.s}px ${GS}`, "1.12");
    t.lines.forEach((l, i) => centered(ctx, l, cx, y + i * lh + mt.base, -0.8));
    y += t.lines.length * lh;
    if (sub.length) {
      y += 30;
      ctx.fillStyle = GREY; ctx.font = `500 36px ${GS}`; setLS(ctx, 0);
      const ms = baseline(`500 36px ${GS}`, "50px");
      sub.forEach((l, i) => centered(ctx, l, cx, y + i * 50 + ms.base, 0));
      y += sub.length * 50;
    }
    if (label) {
      y += 64;
      ctx.font = `500 32px ${GM}`; setLS(ctx, 2.5);
      const pw = width(ctx, label, 2.5) + 84;
      ctx.fillStyle = PILL_BG; rrect(ctx, cx - pw / 2, y, pw, ph, ph / 2); ctx.fill();
      const m = baseline(`500 32px ${GM}`, "normal");
      ctx.fillStyle = PILL_TX; fill(ctx, label, cx - pw / 2 + 42, y + (ph - m.height) / 2 + m.base, 2.5);
    }

    // Pied : logo SSB, bandeau « Adhère » du modèle et renvoi vers le lien.
    const ck = 1.3, cw = PIECES.cta[2] * ck, ch = PIECES.cta[3] * ck;
    ctx.drawImage(piece(bg, "cta"), cx - cw / 2, 1528, cw, ch);
    ctx.font = `500 26px ${GS}`; setLS(ctx, 1.5); ctx.fillStyle = "rgba(255, 255, 255, 0.82)";
    centered(ctx, ellipsis(ctx, (opts.phraseBas ?? "TOUTES LES OFFRES : LIEN EN BIO").toUpperCase(), 820, 1.5), cx, 1640, 1.5);
    const sk = 1.15;
    ctx.drawImage(piece(bg, "ssb"), 96, 1742, PIECES.ssb[2] * sk, PIECES.ssb[3] * sk);
    if (hasLS) ctx.letterSpacing = "0px";
  }

  // Logo en PNG (600 px au plus) pour le garder dans le navigateur d'une fois sur l'autre.
  function logoDataURL(logo) {
    const k = Math.min(1, 600 / Math.max(logo.w, logo.h));
    const cv = document.createElement("canvas");
    cv.width = Math.max(1, Math.round(logo.w * k)); cv.height = Math.max(1, Math.round(logo.h * k));
    cv.getContext("2d").drawImage(logo.img, 0, 0, cv.width, cv.height);
    return cv.toDataURL("image/png");
  }

  g.SSBInsta = { ready, render, renderStory, loadLogo, logoDataURL, autoHeight, W, H, SW, SH };
})(window);
