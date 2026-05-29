"""Example — generate utterances with expand_slots, then match each one back.

Run::

    python examples/06_generate_and_match.py
"""
from kw_template_matcher import TemplateMatcher, expand_slots


def main() -> None:
    template = "poe {genero} [na {divisao}]"

    matcher = TemplateMatcher()
    matcher.add_templates([template])

    generated = expand_slots(template, {
        "genero": ["fado", "morna"],
        "divisao": ["sala", "quarto"],
    })

    print("round-trip: generate then re-extract slots")
    for utterance in generated:
        slots = matcher.match(utterance)
        print(f"   {utterance!r:42} -> {slots}")


if __name__ == "__main__":
    main()
