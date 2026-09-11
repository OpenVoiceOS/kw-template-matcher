# API reference

Everything importable from the top-level package:

```python
from kw_template_matcher import TemplateMatcher, expand_template, expand_slots
```

## `expand_template(template: str) -> list[str]`

Expands `[optional]` and `(a|b)` syntax into the full sorted list of concrete
sentences. `{slot}` markers stay verbatim in each sentence. The result is
sorted and de-duplicated.

```python
from kw_template_matcher import expand_template

expand_template("sentence[s] can have (pre|suf)fixes")
# ['sentence can have prefixes',
#  'sentence can have suffixes',
#  'sentences can have prefixes',
#  'sentences can have suffixes']
```

Optionals can nest alternatives, and an entirely-optional group yields the empty
string as one branch:

```python
expand_template("[(this|that) is optional]")
# ['', 'that is optional', 'this is optional']
```

## `expand_slots(template: str, slots: dict[str, list[str]]) -> list[str]`

Runs `expand_template` first, then substitutes each `{slot}` with every value
from `slots`, producing the Cartesian product. A slot with no entry in the
dict stays as its `{name}` literal.

- **template**: the template string.
- **slots**: `{slot_name: [value, ...]}`.

Returns one string per expansion and slot-value combination. The order
follows the sorted expansion order, then `itertools.product` over the slot
values.

```python
from kw_template_matcher import expand_slots

expand_slots("turn {device} {state}",
             {"device": ["lamp"], "state": ["on", "off"]})
# ['turn lamp on', 'turn lamp off']
```

## `class TemplateMatcher`

Holds registered templates grouped by their slot signature and matches an
utterance back to slot values.

### `TemplateMatcher()`

No arguments. Internally keeps `templates: dict[str, list[str]]`, keyed by the
sorted, `|`-joined slot names of each expanded template.

### `add_templates(templates: list[str]) -> None`

Expands each template and registers every expansion that contains at least
one slot. It drops slot-free expansions, because the matcher only routes
utterances that fill named holes.

```python
from kw_template_matcher import TemplateMatcher

matcher = TemplateMatcher()
matcher.add_templates([
    "tell me a [{joke_type}] joke",
    "play {query} [in ({device_name}|{zone_name})]",
])
```

### `match(query: str, threshold: float = 0.4) -> dict[str, str]`

Returns the slot dict of the single highest-scoring template, or `{}` if no
template clears the threshold.

```python
matcher.match("play jazz in kitchen", threshold=0.3)
# {'query': 'jazz', 'device_name': 'kitchen'}
```

The default `threshold=0.4` is stricter than this example's own similarity score, so this
call must lower it. Passing no `threshold` override here returns `{}`.

### `predict(query: str, threshold: float = 0.4) -> list[tuple[float, dict[str, str]]]`

Returns every template that structurally matches (via `simplematch`) and
scores at or above `threshold`, as `(score, slots)` tuples sorted by
descending score. `match` is `predict(...)[0][1]` when the list is not empty.

- **score**: `rapidfuzz` normalized Damerau-Levenshtein similarity between the
  template string and the query, in `[0.0, 1.0]`. Longer literal overlap and
  fewer edits score higher.
- **threshold**: minimum score to keep a candidate. Default `0.4`.

```python
for score, slots in matcher.predict("play jazz in kitchen", threshold=0.3):
    print(round(score, 3), slots)
# 0.379 {'query': 'jazz', 'device_name': 'kitchen'}
# 0.37 {'query': 'jazz', 'zone_name': 'kitchen'}
```

A query that fills no slot structurally returns `[]` from `predict` and `{}`
from `match`.

---
[← Quickstart](quickstart.md) · [Home](../README.md) · [Advanced →](advanced.md)
