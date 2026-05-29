"""Example — fill slots with a vocabulary to generate utterances.

Run::

    python examples/02_expand_slots.py
"""
from kw_template_matcher import expand_slots


def main() -> None:
    template = "toca [um pouco de ]{genero} [na {divisao}]"
    slots = {
        "genero": ["fado", "jazz", "rock"],
        "divisao": ["cozinha", "sala"],
    }
    sentences = expand_slots(template, slots)
    print(f"{len(sentences)} generated utterances:")
    for sentence in sentences:
        print("   -", sentence)


if __name__ == "__main__":
    main()
