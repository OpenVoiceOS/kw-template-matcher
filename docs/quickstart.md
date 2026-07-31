# Quickstart

`keyword-template-matcher` turns a compact natural-language template into
every sentence it describes, and matches an utterance back to the slots it
filled. One template, such as `play {query} [in ({device}|{zone})]`, stands in
for dozens of phrasings that you do not have to write out.

## Install

```bash
pip install keyword-template-matcher
```

Two runtime dependencies pull in: [`rapidfuzz`](https://github.com/maxbachmann/RapidFuzz)
for the similarity score and [`simplematch`](https://github.com/OpenVoiceOS/simplematch)
for slot extraction. Both are pure leaf installs.

## The one idea

A template is a string with three pieces of syntax:

| Syntax       | Meaning                                    |
|--------------|--------------------------------------------|
| `{slot}`     | a named hole to capture text into          |
| `[optional]` | a word or phrase that may be absent         |
| `(a\|b\|c)`  | alternatives, exactly one is chosen        |

`expand_template` walks the optionals and alternatives and returns the full
set of concrete sentences. It leaves slots in place as `{name}` markers.

```python
from kw_template_matcher import expand_template

for sentence in expand_template("[hello,] (call me|my name is) {name}"):
    print(sentence)
# call me {name}
# hello, call me {name}
# hello, my name is {name}
# my name is {name}
```

## First real call

`TemplateMatcher` registers templates, then matches an utterance to the slots
it captured. `match` returns the single best slot dict. `predict` returns
every candidate with its score.

```python
from kw_template_matcher import TemplateMatcher

matcher = TemplateMatcher()
matcher.add_templates([
    "[hello, ](call me|my name is) {name} [and] [I am from {location}]",
])

print(matcher.match("my name is Alice and I am from The United Kingdom"))
# {'name': 'Alice', 'location': 'The United Kingdom'}
```

Want the scores too?

```python
for score, slots in matcher.predict("my name is Alice and I am from The United Kingdom"):
    print(round(score, 3), slots)
# 0.592 {'name': 'Alice', 'location': 'The United Kingdom'}
```

## Filling slots with values

When you have a fixed vocabulary per slot, `expand_slots` substitutes every
combination. Use it to generate training utterances.

```python
from kw_template_matcher import expand_slots

template = "change [the ]brightness to {level} and color to {color}"
slots = {"level": ["low", "high"], "color": ["red", "blue"]}

for sentence in expand_slots(template, slots):
    print(sentence)
# change the brightness to low and color to red
# change the brightness to low and color to blue
# ... every level x color x optional combination
```

---
[Home](../README.md) · [API reference →](api.md)
