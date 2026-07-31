[![Ask DeepWiki](https://deepwiki.com/badge.svg)](https://deepwiki.com/TigreGotico/kw-template-matcher)

# KeywordTemplateMatcher

KeywordTemplateMatcher is a Python library for natural language templates. A
template can hold slots, optional phrases, and alternatives. The library
expands a template into every sentence it describes, and matches an utterance
back to the slot values it filled. Use it to prototype NLU systems, voice
assistants, or rule-based query matching.

## Features

- Template expansion with:
    - Optional phrases (`[optional]`)
    - Alternatives (`(choice1|choice2)`)
    - Slots (`{slot_name}`)
- Slot substitution from a supplied dictionary
- Fuzzy matching and confidence scoring with `rapidfuzz`
- A simple template structure that extends to any language or grammar rule
- Built-in integration with `simplematch` for fuzzy slot matching

## Installation

```bash
pip install keyword-template-matcher
```

## Usage

### 1. Expand a template with slots

```python
from kw_template_matcher import expand_slots

template = "change [the ]brightness to {brightness_level} and color to {color_name}"
slots = {
    "brightness_level": ["low", "medium", "high"],
    "color_name": ["red", "green", "blue"]
}

for sentence in expand_slots(template, slots):
    print(sentence)
```

**Output:**

```
change the brightness to low and color to red
change brightness to high and color to blue
... (all combinations)
```

### 2. Match a template

```python
from kw_template_matcher import TemplateMatcher

matcher = TemplateMatcher()
matcher.add_templates([
    "[hello,] (call me|my name is) {name}",
    "tell me a [{joke_type}] joke"
])

query = "hello, my name is Alice"
results = matcher.match(query)

for match in results:
    print(match)
```

## How it works

### Template syntax

| Syntax      | Description                              |
|-------------|------------------------------------------|
| `{slot}`    | Placeholder to be replaced with values   |
| `[optional]`| Optional word or phrase                  |
| `(a\|b\|c)`   | Alternatives - only one is chosen        |

### Test example templates

```python
templates = [
    "[hello,] (call me|my name is) {name}",
    "tell me a [{joke_type}] joke",
    "play {query} [in ({device_name}|{skill_name}|{zone_name})]"
]
```

These templates expand to sentences like:

```
- call me {name}
- hello, my name is {name}
- tell me a {joke_type} joke
- play {query}
- play {query} in {device_name}
```

## Related projects

- [OpenVoiceOS/simplematch](https://github.com/OpenVoiceOS/simplematch) - the lightweight template parser this library builds on

## Contributions

Open an issue or submit a pull request to report a bug or propose an improvement.

## Acknowledgements

- [`rapidfuzz`](https://github.com/maxbachmann/RapidFuzz) for fast fuzzy matching
- [`simplematch`](https://github.com/OpenVoiceOS/simplematch) for lightweight template parsing
