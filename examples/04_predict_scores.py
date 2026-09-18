"""Example — rank candidate matches by the share of the query the template pins down with predict().

Run::

    python examples/04_predict_scores.py
"""
from kw_template_matcher import TemplateMatcher


def main() -> None:
    matcher = TemplateMatcher()
    matcher.add_templates([
        "acende {divisao}",
        "acende as luzes [d]a {divisao}",
        "liga a luz [d]a {divisao}",
    ])

    query = "acende as luzes da cozinha"
    print("query:", query)
    print("ranked candidates (score, slots):")
    for score, slots in matcher.predict(query):
        print("   ", score, slots)


if __name__ == "__main__":
    main()
