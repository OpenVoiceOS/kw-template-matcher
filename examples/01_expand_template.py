"""Example — expand template syntax into concrete sentences.

Run::

    python examples/01_expand_template.py
"""
from kw_template_matcher import expand_template


def main() -> None:
    templates = [
        "[hello,] (call me|my name is) {name}",
        "sentence[s] can have (pre|suf)fixes mid word too",
        "[(this|that) is optional]",
        "play {query} [in ({device_name}|{zone_name})]",
    ]
    for template in templates:
        print("###", template)
        for sentence in expand_template(template):
            print("   -", repr(sentence))


if __name__ == "__main__":
    main()
