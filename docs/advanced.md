# Advanced

## How a match is scored

`predict` does two things for each registered template.

1. **Structural match.** `simplematch.match(template, query)` must succeed
   (return a dict, possibly empty) for the template to be a candidate. This
   step extracts the slot values.
2. **Similarity score.** `rapidfuzz` computes the normalized
   Damerau-Levenshtein similarity between the template string (slots and all)
   and the query. The closer the query's surface form is to the template, the
   higher the score.

The score compares against the template, including the literal `{slot}`
markers. A long captured span pulls the score down, because the literal
`{query}` is shorter than the text that fills it. This is expected. Scores
rank competing templates against each other. They are not an absolute
confidence value.

```python
from kw_template_matcher import TemplateMatcher

matcher = TemplateMatcher()
matcher.add_templates(["set a timer for {duration}"])
for score, slots in matcher.predict("set a timer for five minutes"):
    print(round(score, 3), slots)
# 0.5 {'duration': 'five minutes'}
```

## Tuning the threshold

The default `0.4` is permissive. Raise it to match only near-literal
phrasings. Lower it to allow longer slot fills and looser wording.

```python
matcher.predict("set a timer for five minutes", threshold=0.6)  # likely []
matcher.predict("set a timer for five minutes", threshold=0.2)  # keeps the match
```

## Slot-signature routing

The matcher buckets templates by their sorted slot names (`"device|query"`).
It matches each bucket in its own thread. Two templates that capture the same
set of slot names compete directly. Templates with different slot sets are
matched independently, then all surviving candidates are merged and sorted by
score.

As a result, register related phrasings together and let `predict` rank them.
Do not hand-order templates.

## Optional groups that wrap slots

`[in ({device_name}|{zone_name})]` expands to one branch with no slot and
several branches with one slot each. `add_templates` keeps the slot-free
branch (`play {query}`) only because it still has the `{query}` slot. A
branch with no slot at all is dropped at registration.

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

- **Whitespace in expansions.** A `[the ]` optional leaves a clean single
  space when present and collapses when absent. A construct like
  `do( the | )thing` can bake uneven spacing into the alternatives. Design
  each branch so it reads naturally.
- **Slot-free templates vanish.** The matcher does not register anything
  without a `{slot}`. Call `expand_template` directly to get the slot-free
  sentences.
- **Empty-string branch.** A fully optional template
  (`[(this|that) is optional]`) includes `''` among its expansions. The
  matcher drops this branch, but `expand_template` still returns it.
- **Scores are comparative.** Do not set a threshold as an absolute
  confidence value across unrelated templates. Calibrate the threshold per
  template family.

---
[← API reference](api.md) · [Home](../README.md) · [OVOS plugin →](opm-plugin.md)
