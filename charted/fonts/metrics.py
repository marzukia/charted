"""Compact font metrics."""

import json
from pathlib import Path

from charted.utils.defaults import BASE_DEFINITIONS_DIR

REFERENCE_SIZE = 16
CHAR_GROUPS = {
    "digit": set("0123456789"),
    "upper": set("ABCDEFGHIJKLMNOPQRSTUVWXYZ"),
    "lower": set("abcdefghijklmnopqrstuvwxyz"),
    "space": set(" "),
    "punct": set(".,;:!?-'\"()[]{}"),
    "symbol": set("@#$%^&*+=/\\|<>~\\`"),
}
FALLBACK_METRICS = {
    "digit_width": 9.6,
    "upper_width": 10.2,
    "lower_width": 8.1,
    "space_width": 5.3,
    "punct_width": 6.0,
    "symbol_width": 8.5,
    "cap_height": 11.5,
    "x_height": 8.0,
    "default_width": 5.0,
    "default_height": 9.0,
}


def classify_char(c):
    for group, chars in CHAR_GROUPS.items():
        if c in chars:
            return group
    return "default"


def compute_text_width(text, metrics, font_size):
    scale = font_size / metrics.get("ref_size", REFERENCE_SIZE)
    counts = {}
    for c in text:
        g = classify_char(c)
        counts[g] = counts.get(g, 0) + 1
    total = 0.0
    for g, n in counts.items():
        total += n * metrics.get(f"{g}_width", FALLBACK_METRICS.get(f"{g}_width", 5.0))
    return total * scale


def compute_text_height(metrics, font_size):
    scale = font_size / metrics.get("ref_size", REFERENCE_SIZE)
    return metrics.get("cap_height", FALLBACK_METRICS["cap_height"]) * scale


def load_metrics(family, definitions_dir=None):
    directory = definitions_dir or BASE_DEFINITIONS_DIR
    path = Path(directory) / f"{family}.json"
    if not path.exists():
        if family != "Arial":
            m = load_metrics("Arial", directory)
            m["family"] = "Arial"
            return m
        m = dict(FALLBACK_METRICS)
        m["family"] = ""
        return m
    try:
        with open(path) as f:
            data = json.load(f)
    except json.JSONDecodeError:
        import warnings

        warnings.warn(
            f"Failed to parse font JSON for '{family}', using fallback metrics"
        )
        m = dict(FALLBACK_METRICS)
        m["family"] = ""
        return m
    except IOError:
        m = dict(FALLBACK_METRICS)
        m["family"] = ""
        return m
    if isinstance(data, dict) and "ref_size" in data:
        data.setdefault("family", family)
        return data
    m = _convert_legacy(data, family)
    m["family"] = family
    return m


def _convert_legacy(data, family):
    sizes = sorted(int(k) for k in data.keys())
    if not sizes:
        return dict(FALLBACK_METRICS)
    ref = str(REFERENCE_SIZE if REFERENCE_SIZE in sizes else sizes[len(sizes) // 2])
    gw = {}
    for cc, cd in data[ref].items():
        g = classify_char(chr(int(cc)))
        gw.setdefault(g, []).append(cd.get("width", 5))
    metrics = {"ref_size": float(ref), "family": family}
    for g in sorted(gw):
        metrics[f"{g}_width"] = round(sum(gw[g]) / len(gw[g]), 1)
    chars_h = [(chr(int(k)), v.get("height", 9)) for k, v in data[ref].items()]
    uh = [h for c, h in chars_h if c.isupper()]
    lh = [h for c, h in chars_h if c.islower()]
    ah = [h for _, h in chars_h]
    metrics["cap_height"] = (
        round(sum(uh) / len(uh), 1) if uh else round(sum(ah) / len(ah), 1)
    )
    metrics["x_height"] = (
        round(sum(lh) / len(lh), 1) if lh else metrics["cap_height"] * 0.7
    )
    for k in FALLBACK_METRICS:
        metrics.setdefault(k, FALLBACK_METRICS[k])
    return metrics
