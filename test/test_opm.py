"""Tests for the OPM intent-transformer plugin.

Locale files in the wild contain malformed Padatious templates
(translated slot names, truncated braces, adjacent slots, bracketed
markers).  A single bad line must never abort intent registration for
the remaining samples.
"""
import unittest

from ovos_bus_client.message import Message

from kw_template_matcher.opm import KeywordTemplateMatcher


def make_message(samples, name="test_skill:demo.intent", skill_id="test_skill"):
    return Message("padatious:register_intent",
                   data={"name": name, "samples": samples,
                         "lang": "en-US", "skill_id": skill_id})


class TestUnpackObject(unittest.TestCase):
    def setUp(self):
        self.plugin = KeywordTemplateMatcher()

    def unpack(self, samples):
        lang, skill_id, name, expanded, blacklist = self.plugin._unpack_object(
            make_message(samples))
        return expanded

    def test_valid_samples_expand(self):
        expanded = self.unpack(["play {media}", "(start|begin) {media}"])
        self.assertIn("play {media}", expanded)
        self.assertIn("start {media}", expanded)
        self.assertIn("begin {media}", expanded)

    def test_uppercase_slot_name_skipped(self):
        # translated slot names, e.g. German "{Medien}"
        expanded = self.unpack(["spiele {Medien}", "play {media}"])
        self.assertEqual(expanded, ["play {media}"])

    def test_truncated_brace_skipped(self):
        expanded = self.unpack(["weather in {location", "weather in {location}"])
        self.assertEqual(expanded, ["weather in {location}"])

    def test_adjacent_slots_skipped(self):
        expanded = self.unpack(["{first}{second}", "call {contact}"])
        self.assertEqual(expanded, ["call {contact}"])

    def test_bracketed_marker_does_not_raise(self):
        # "[UNUSED]" style markers must not abort registration
        expanded = self.unpack(["[UNUSED] play {media}"])
        self.assertIn("play {media}", expanded)

    def test_all_malformed_yields_empty(self):
        expanded = self.unpack(["{Medien}", "{a}{b}", "{oops"])
        self.assertEqual(expanded, [])


class TestHandleRegisterIntent(unittest.TestCase):
    def setUp(self):
        self.plugin = KeywordTemplateMatcher()

    def test_mixed_samples_register_valid_ones(self):
        self.plugin.handle_register_intent(make_message(
            ["play {Medien}", "tune to {station", "{a}{b}",
             "[UNUSED] noise", "play {media}", "listen to {media}"]))
        matchers = self.plugin.matchers["en-US"]
        self.assertIn("test_skill:demo.intent", matchers)
        result = matchers["test_skill:demo.intent"].match("play the beatles")
        self.assertEqual(result.get("media"), "the beatles")

    def test_malformed_only_does_not_raise_or_register(self):
        self.plugin.handle_register_intent(make_message(
            ["{Medien}", "{loc", "{a}{b}"]))
        self.assertNotIn("test_skill:demo.intent",
                         self.plugin.matchers.get("en-US", {}))


if __name__ == "__main__":
    unittest.main()
