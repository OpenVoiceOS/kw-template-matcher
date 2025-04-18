# 🧩 TemplateMatcher

A lightweight Python utility for expanding and matching natural language templates with **slots**, **optional phrases**, and **alternatives**. It supports fuzzy matching and slot extraction, making it ideal for prototyping NLU systems, voice assistants, or rule-based query matching.

---

## 🔧 Features

- ✅ Template expansion with:
    - Optional phrases (`[optional]`)
    - Alternatives (`(choice1|choice2)`)
    - Slots (`{slot_name}`)
- ✅ Slot substitution with provided dictionaries
- ✅ Fuzzy matching with confidence scoring using `rapidfuzz`
- ✅ Simple template structure, extensible for any language/grammar rules
- ✅ Built-in integration with `simplematch` for fuzzy slot matching

---

## 📦 Installation

```bash
pip install rapidfuzz simplematch
```

---

## 🚀 Usage

### 1. Expanding a Template with Slots

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

---

### 2. Template Matching

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

---

## 🧠 How It Works

### Template Syntax

| Syntax      | Description                              |
|-------------|------------------------------------------|
| `{slot}`    | Placeholder to be replaced with values   |
| `[optional]`| Optional word or phrase                  |
| `(a|b|c)`   | Alternatives - only one is chosen        |

### Match Confidence

The `match()` method returns the best matches sorted by fuzzy confidence (`rapidfuzz.distance.DamerauLevenshtein.normalized_similarity`).

---

## 🧪 Test Example Templates

```python
templates = [
    "[hello,] (call me|my name is) {name}",
    "tell me a [{joke_type}] joke",
    "play {query} [in ({device_name}|{skill_name}|{zone_name})]"
]
```

Produces expansions like:

```
- call me {name}
- hello, my name is {name}
- tell me a {joke_type} joke
- play {query}
- play {query} in {device_name}
```

---

## 🤝 Contributions

PRs, issues, and suggestions welcome! Feel free to open an issue or submit a pull request if you'd like to improve the matcher.

---

## 💬 Acknowledgements

- [`rapidfuzz`](https://github.com/maxbachmann/RapidFuzz) for fast fuzzy matching
- [`simplematch`](https://github.com/OpenVoiceOS/simplematch) for lightweight template parsing
