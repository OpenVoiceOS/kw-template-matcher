# Advanced

## How a match is scored

`predict` does two things for each expanded template.

1. **Structural match.** `simplematch.match(template, query)` must succeed
   (return a dict, possibly empty) for the template to be a candidate. This
   step extracts the slot values. Every candidate is an exact structural
   match: each literal token of the template is present in the query.
2. **Rank.** The score is the number of literal (non-slot) tokens in the
   template, as a float. When several templates match the same query, the one
   that pins down more of the utterance in literal words ranks first.

The score is a count of the template's own literal tokens. The length of a
captured span does not change it: `"set a timer for {duration}"` scores
`4.0` whatever fills `{duration}`. Scores rank competing templates against
each other. They are not a confidence value and not a similarity.

```python
from kw_template_matcher import TemplateMatcher

matcher = TemplateMatcher()
matcher.add_templates(["set a timer for {duration}"])
for score, slots in matcher.predict("set a timer for five minutes"):
    print(score, slots)
# 4.0 {'duration': 'five minutes'}
```

## The threshold argument

`match` and `predict` accept `threshold` for backwards compatibility and
ignore it. Earlier releases compared a similarity score against it and
dropped correct extractions when the slot value was long relative to the
template. A structural match is exact, so there is nothing to filter.

```python
matcher.predict("set a timer for five minutes", threshold=0.7)
# [(4.0, {'duration': 'five minutes'})]  -- same as with no threshold
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
- **Scores are comparative.** A score is a literal token count. Compare it
  between templates that matched one query. Do not read it as a confidence
  value across unrelated templates.

---
[← API reference](api.md) · [Home](../README.md) · [OVOS plugin →](opm-plugin.md)
