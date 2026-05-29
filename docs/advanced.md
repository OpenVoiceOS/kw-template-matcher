# Advanced

## How a match is scored

`predict` does two things per registered template:

1. **Structural match** — `simplematch.match(template, query)`. This must
   succeed (return a dict, possibly empty) for the template to be a candidate at
   all. It is what extracts the slot values.
2. **Similarity score** — `rapidfuzz` normalized Damerau-Levenshtein similarity
   between the *template string* (slots and all) and the query. The closer the
   query's surface form is to the template, the higher the score.

Because the score compares against the template *including* the literal `{slot}`
markers, long captured spans pull the score down — the literal `{query}` is
shorter than the text that fills it. This is expected: scores are a relative
ranking signal across competing templates, not an absolute confidence.

```python
from kw_template_matcher import TemplateMatcher

matcher = TemplateMatcher()
matcher.add_templates(["set a timer for {duration}"])
for score, slots in matcher.predict("set a timer for five minutes"):
    print(round(score, 3), slots)
# 0.5 {'duration': 'five minutes'}
```

## Tuning the threshold

The default `0.4` is permissive. Raise it when you want only near-literal
phrasings to match; lower it to tolerate longer slot fills and looser wording.

```python
matcher.predict("set a timer for five minutes", threshold=0.6)  # likely []
matcher.predict("set a timer for five minutes", threshold=0.2)  # keeps the match
```

## Slot-signature routing

Templates are bucketed by their sorted slot names (`"device|query"`), and each
bucket is matched in its own thread. Two templates that capture the *same* set of
slot names compete directly; templates with different slot sets are matched
independently and all surviving candidates are merged, then sorted by score.

A practical consequence: register related phrasings together and let `predict`
rank them, rather than trying to hand-order templates.

## Optional groups that wrap slots

`[in ({device_name}|{zone_name})]` expands to one branch with no slot and several
branches with one slot each. The slot-free branch (`play {query}`) is kept by
`add_templates` only because it still has the `{query}` slot; a branch with *no*
slot at all is silently dropped at registration.

```python
from kw_template_matcher import expand_template

expand_template("play {query} [in ({device_name}|{zone_name})]")
# ['play {query}',
#  'play {query} in {device_name}',
#  'play {query} in {zone_name}']
```

## Generating training data with `expand_slots`

`expand_slots` is the inverse of matching: give it a vocabulary per slot and it
emits every concrete utterance. Feed those into an intent classifier or use them
as fuzz inputs for the matcher itself.

```python
from kw_template_matcher import expand_slots

utterances = expand_slots(
    "play {genre} [music]",
    {"genre": ["jazz", "rock", "fado"]},
)
# both with and without "music", for each genre
```

## Gotchas

- **Whitespace in expansions.** A `[the ]` optional leaves a clean single space
  when present and collapses when absent, but constructs like `do( the | )thing`
  can leave the spacing baked into the alternatives — design templates so each
  branch reads naturally.
- **Slot-free templates vanish.** Anything without a `{slot}` is not registered.
  Use `expand_template` directly if you want the slot-free sentences.
- **Empty-string branch.** A fully optional template (`[(this|that) is optional]`)
  includes `''` among its expansions; it is dropped by the matcher but appears
  from `expand_template`.
- **Scores are comparative.** Do not threshold on an absolute notion of
  confidence across unrelated templates; calibrate per template family.

## Where next

- [api.md](api.md) — exact signatures and return shapes
- [quickstart.md](quickstart.md) — the core idea in one page
- [opm-plugin.md](opm-plugin.md) — wiring the matcher into OVOS intent handling
