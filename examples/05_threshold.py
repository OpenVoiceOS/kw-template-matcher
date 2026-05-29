"""Example — how the threshold filters loose matches.

Run::

    python examples/05_threshold.py
"""
from kw_template_matcher import TemplateMatcher


def main() -> None:
    matcher = TemplateMatcher()
    matcher.add_templates(["marca um temporizador para {duracao}"])

    query = "marca um temporizador para cinco minutos"
    print("query:", query)
    for threshold in (0.2, 0.4, 0.6):
        results = matcher.predict(query, threshold=threshold)
        kept = [(round(s, 3), d) for s, d in results]
        print(f"   threshold={threshold}: {kept or 'no match'}")


if __name__ == "__main__":
    main()
