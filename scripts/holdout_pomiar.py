"""Score Local Scout's local detector on the frozen holdout.

Per target category and language: labelled values fully / partly masked, trap texts with a false mask of the
target type, and visible false masks (detected spans overlapping no labelled value). Names are also counted per
form (full, single, titled, reversed) and as seen / unseen in earlier sets. Detection is the whole local mask
pipeline (privacy.local_spans with names enabled), not a Hermes request.

Usage: python -B holdout_pomiar.py PARENT_DIR part.jsonl [part.jsonl ...] [--seen imiona_widziane_wczesniej.json]
PARENT_DIR contains the plugin checkout as plugin/. Prints one JSON object: {setting: {"category|LANG": counters}}.
Field names in the data are Polish: kategoria_celu = target category, pulapka = trap, formy = name forms."""
import sys, json, re, collections
args = sys.argv[1:]; seen = set()
if '--seen' in args:
    i = args.index('--seen'); seen = set(json.load(open(args[i + 1]))); del args[i:i + 2]
sys.path.insert(0, args[0]); files = args[1:]
import inspect, contextlib
from plugin.scout import privacy, pii_model
try:
    from plugin.scout import language
except ImportError:
    language = None
V175 = not hasattr(privacy, 'local_spans')
if V175:   # 1.7.5: the same pipeline as its mask_local_details (spans + credentials + name_model.spans)
    from plugin.scout import credentials, name_model
    privacy.local_spans = lambda t, names=True: privacy.spans(t) + credentials.spans(t) + (name_model.spans(t) if names else [])

SETTINGS = {'default': dict(name_masking='basic', address_masking='on', other_languages='off'),
            'deep': dict(name_masking='deep', address_masking='on', other_languages='off'),
            'other_on': dict(name_masking='basic', address_masking='on', other_languages='on'),
            'deep_other_on': dict(name_masking='deep', address_masking='on', other_languages='on')}
ALNUM = re.compile(r'[^\W_]', re.U)


if V175:
    SETTINGS = {'v175': {}}


def detect(text, setting):
    with contextlib.ExitStack() as stack:
        if hasattr(pii_model, '_CANDIDATE_BUDGET'):
            t = pii_model._CANDIDATE_BUDGET.set(pii_model.MASK_CANDIDATE_LIMIT); stack.callback(pii_model._CANDIDATE_BUDGET.reset, t)
        if language is not None and hasattr(language, 'CACHE'):
            t2 = language.CACHE.set({}); stack.callback(language.CACHE.reset, t2)
        clean, index = privacy._normalise_for_detection(text) if hasattr(privacy, '_normalise_for_detection') else (text, None)
        found = privacy.local_spans(clean, names=True, **SETTINGS[setting])
        if index is not None:
            ends = getattr(index, 'ends', None)   # 1.9+: an entity like &amp; maps back to its full source span
            found = [(index[s], ends[e - 1] if ends is not None else index[e - 1] + 1, c) for s, e, c in found if e > s]
        return found


def coverage(text, s, e, found):
    need = [i for i in range(s, e) if ALNUM.match(text[i])]
    hit = [i for i in need if any(a <= i < b for a, b, _ in found)]
    return len(hit) == len(need), bool(hit)


out = {}
for setting in SETTINGS:
    c = collections.defaultdict(collections.Counter)
    for f in files:
        for r in map(json.loads, open(f)):
            t, k, lang = r['text'], r['kategoria_celu'], r['lang']
            found = detect(t, setting)
            forms = {(s, e): fm for s, e, fm in r.get('formy', [])}
            key = (k, lang)
            c[key]['texts'] += 1
            gold = r['gold']
            for a, b, cat in found:   # visible false mask: a detected span overlapping no labelled value
                if not any(a < e and s < b for s, e, _ in gold):
                    c[key]['fp_visible'] += 1; c[key][f'fp_visible:{cat}'] += 1
                    if r['pulapka'] and cat == k: c[key]['fp_trap_target'] += 1
            if r['pulapka']:
                c[key]['traps'] += 1
                c[key]['traps_with_false_target'] += any(cat == k and not any(a < e and s < b for s, e, _ in gold) for a, b, cat in found)
            for s, e, cat in gold:
                full, part = coverage(t, s, e, found)
                tags = [cat if cat == k else f'side:{cat}']
                if cat == 'name':
                    fm = forms.get((s, e), 'full' if len(t[s:e].split()) > 1 else 'single')
                    tags.append(f'forma:{fm}')
                    if seen: tags.append('imie:' + ('seen' if t[s:e] in seen else 'unseen'))
                for tag in tags:
                    c[key][tag] += 1; c[key][tag + ':full'] += full; c[key][tag + ':part'] += part
    out[setting] = {f'{k}|{l}': dict(v) for (k, l), v in sorted(c.items())}
print(json.dumps(out, ensure_ascii=False))
