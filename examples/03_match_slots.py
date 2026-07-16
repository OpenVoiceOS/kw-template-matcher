"""Example — register templates and extract slots from an utterance.

Run::

    python examples/03_match_slots.py
"""
from kw_template_matcher import TemplateMatcher


def main() -> None:
    matcher = TemplateMatcher()
    matcher.add_templates([
        "[ola, ](chamo-me|o meu nome e) {nome} [e sou de {local}]",
    ])

    query = "o meu nome e Alice e sou de Lisboa"
    slots = matcher.match(query)
    print("query :", query)
    print("slots :", slots)


if __name__ == "__main__":
    main()
