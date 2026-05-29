# OVOS plugin

`kw_template_matcher.opm.KeywordTemplateMatcher` is an OVOS `IntentTransformer`
that runs `TemplateMatcher` as a named-entity step inside the intent pipeline. It
adds slot values to a matched intent's `match_data` without owning intent
selection itself.

It is published under the entry-point group **`opm.transformer.intent`** as
`ovos-keyword-template-matcher`, so an OVOS install discovers it automatically.

The plugin imports `ovos-bus-client`, `ovos-plugin-manager`, and `ovos-utils`,
which come from the host OVOS environment rather than this package's runtime
dependencies.

## What it does

```python
from kw_template_matcher.opm import KeywordTemplateMatcher

transformer = KeywordTemplateMatcher()
```

On `bind(bus)` it subscribes to `padatious:register_intent`. For each registered
intent it:

1. reads `samples` (or reads them from `file_name`),
2. expands every sample with `ovos_utils.bracket_expansion.expand_template`,
3. keeps only expansions containing a `{slot}` — pure keyword extractors,
4. builds a `TemplateMatcher` per `(lang, intent_name)` and feeds it those
   samples.

The matchers live in `transformer.matchers[lang][intent_name]`.

## The transform step

During `transform(intent)` the plugin looks up the matcher for the session
language and the intent's `match_type`. If one exists, it runs
`matcher.match(intent.utterance)` and merges any captured slots into
`intent.match_data`:

```python
# inside the OVOS pipeline, conceptually:
entities = matchers[intent.match_type].match(intent.utterance)
if entities:
    intent.match_data.update(entities)
```

So a Padatious intent that matched on phrasing gets its slots filled by the
template matcher, with no extra model.

## Using the core matcher directly

You do not need OVOS to use the matching logic — that is plain
`TemplateMatcher`. Reach for the plugin only when you want this behaviour wired
into a running OVOS intent pipeline; otherwise see [quickstart.md](quickstart.md).

## Where next

- [quickstart.md](quickstart.md) — the standalone matcher
- [api.md](api.md) — `TemplateMatcher` signatures
- [advanced.md](advanced.md) — scoring and routing internals
