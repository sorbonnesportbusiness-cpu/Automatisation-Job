# -*- coding: utf-8 -*-
"""
Détection de langue sans dépendance, pour la règle de la veille : une offre dont
l'intitulé ou le contenu n'est ni en français ni en anglais n'entre pas au tableau
(les étudiants de SSB ne pourraient pas y postuler).

- `titre_ok(titre)` : faux si l'intitulé contient des marqueurs d'une autre langue
  (« Praktikant (m/w/d) », « Beca », « Stagiair », « Tirocinio »...).
- `langue(texte)` : langue dominante d'un texte d'au moins quelques phrases, par
  comptage de mots outils ; None si le texte est trop court pour trancher.
"""

import re
import unicodedata


def _norm(text):
    text = unicodedata.normalize("NFD", text or "").encode("ascii", "ignore").decode().lower()
    return re.sub(r"\s+", " ", text)


# Mots d'intitulés propres à une langue (comparés sans accents, en mots entiers).
TITLE_MARKERS = {
    "de": r"m/w/d|m\|w\|d|w/m/d|\(gn\)|praktik\w*|werkstudent\w*|pflicht\w*|duale[rs]?|mitarbeiter\w*|"
          r"sachbearbeit\w*|kaufm\w*|ausbildung|azubi|bereich|und|fur|mit|der|die|das|im|zur|zum|"
          r"\w{4,}ung|\w+ierung|\w+schaft|\w+management\w*in|manager\*in|\w+\*in|\w+:in",
    "es": r"practicas|beca|becario\w*|deportiv\w*|ventas|analista|comunicacion|programa|y|del|para|con",
    "nl": r"stagiair(?![a-z])|medewerker\w*|zoekt|vacature|stage veiligheid|allround|communicatie|van|voor|bij|het|een",
    "it": r"tirocin\w*|stagista|addetto|responsabile|di|della|per",
    "pt": r"estagi\w*|estagiario|gestao|comunicacao|desportiv\w*",
}
TITLE_RE = {k: re.compile(rf"(?<![\w-])(?:{v})(?![\w-])") for k, v in TITLE_MARKERS.items()}
# Mots qui ressemblent à un marqueur mais sont aussi français ou anglais.
SAFE = re.compile(r"(?<![\w-])(management|communication|programme|program|stage|marketing|e-commerce|ecommerce)(?![\w-])")

STOPWORDS = {
    "fr": "le la les des du un une et est pour avec dans sur nous vous votre vos au aux ce cette qui que sont "
          "être plus par ou en de",
    "en": "the and to of in for with you your we our is are will on as be this that an at or from have",
    "de": "der die das und ist mit für wir sie ihr ihre bei auf ein eine einen dem den zu von im sich als oder "
          "werden nicht auch",
    "es": "el los las y es con para por una un del se su sus nuestro como más en de que al lo",
    "nl": "de het en een van voor met je jij wij ons onze bij op is zijn als dat die niet ook wordt",
    "it": "il lo gli le e è con per una un del della dei che di da al nel sono",
    "pt": "o os as e é com para uma um do da dos das que em no na ao nos",
}
STOP = {k: set(_norm(v).split()) for k, v in STOPWORDS.items()}


def titre_ok(titre):
    """Vrai si rien dans l'intitulé ne trahit une langue autre que le français ou l'anglais."""
    t = SAFE.sub(" ", _norm(titre))
    t = re.sub(r"\b(fc|cf|ac|as|sc|sv|rb|vfb|bvb|tsg|psv|nac)\b", " ", t)  # sigles de clubs
    return not any(r.search(t) for r in TITLE_RE.values())


def langue(texte, minimum=25):
    """Langue dominante (fr, en, de, es, nl, it, pt) ou None si moins de `minimum` mots outils."""
    words = re.findall(r"[a-z]+", _norm(texte))
    scores = {k: sum(w in s for w in words) for k, s in STOP.items()}
    best = max(scores, key=scores.get)
    if scores[best] < minimum:
        return None
    # « de », « en », « que »... sont partagés : le français ou l'anglais gagne en cas de quasi-égalité.
    for ok in ("fr", "en"):
        if best not in ("fr", "en") and scores[ok] >= 0.8 * scores[best]:
            return ok
    return best


def offre_ok(titre, texte=""):
    """Règle de la veille : intitulé et contenu en français ou en anglais."""
    if not titre_ok(titre):
        return False, "intitulé ni en français ni en anglais"
    lang = langue(texte) if texte else None
    if lang and lang not in ("fr", "en"):
        return False, f"contenu en {lang}"
    return True, ""


def page_text(url, timeout=20):
    """Texte visible d'une page d'offre (scripts et styles retirés), ou "" si illisible."""
    import html as _html
    import urllib.request
    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/129.0 Safari/537.36", "Accept-Language": "en-GB,en;q=0.9,fr;q=0.8"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            if "html" not in (r.headers.get("Content-Type") or "html"):
                return ""  # PDF ou autre binaire : on ne tranche pas
            body = r.read(800_000).decode("utf-8", "replace")
    except Exception:  # noqa: BLE001 - page illisible : on ne tranche pas sur le contenu
        return ""
    # LinkedIn : seule la description compte, l'habillage de la page est en anglais.
    m = re.search(r'(?s)class="show-more-less-html__markup[^"]*"[^>]*>(.*?)</div>', body)
    if m:
        body = m.group(1)
    body = re.sub(r"(?is)<(script|style|noscript|template|nav|header|footer)\b.*?</\1>", " ", body)
    return re.sub(r"\s+", " ", _html.unescape(re.sub(r"(?s)<[^>]+>", " ", body)))[:8000]
