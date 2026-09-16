"""A `simplematch` hit is a structurally exact match: every literal token in
the template is present in the utterance. `TemplateMatcher` must never
discard such a hit just because the raw template literal (e.g. "play
{query}") happens to be short relative to a long slot value, which is what
the old Damerau-Levenshtein threshold check on the literal did.
"""
import unittest

from kw_template_matcher import TemplateMatcher
from kw_template_matcher.opm import KeywordTemplateMatcher
from ovos_bus_client.message import Message
from ovos_plugin_manager.templates.pipeline import IntentHandlerMatch


class TestExactTemplateMatches(unittest.TestCase):
    def test_short_template_long_slot_value(self):
        matcher = TemplateMatcher()
        matcher.add_templates(["play {query}"])
        self.assertEqual(matcher.match("play the beatles"),
                          {"query": "the beatles"})

    def test_short_template_very_long_slot_value(self):
        matcher = TemplateMatcher()
        matcher.add_templates(["play {query}"])
        self.assertEqual(matcher.match("play bohemian rhapsody by queen"),
                          {"query": "bohemian rhapsody by queen"})

    def test_alarm_template_long_slot_value(self):
        matcher = TemplateMatcher()
        matcher.add_templates(["set an alarm for {time}"])
        self.assertEqual(
            matcher.match("set an alarm for seven thirty in the morning"),
            {"time": "seven thirty in the morning"})

    def test_longer_template_still_matches(self):
        matcher = TemplateMatcher()
        matcher.add_templates(["what is the weather in {location}"])
        self.assertEqual(
            matcher.match("what is the weather in london"),
            {"location": "london"})

    def test_non_matching_utterance_returns_nothing(self):
        matcher = TemplateMatcher()
        matcher.add_templates(["play {query}"])
        self.assertEqual(matcher.match("turn off the lights"), {})

    def test_ranking_prefers_more_literal_tokens(self):
        # both templates structurally match "play jazz on spotify" (simplematch
        # is non-greedy, so "play {query}" swallows "jazz on spotify" whole),
        # but "play {query} on {device}" has more literal (non-slot) tokens
        # (2 vs 1) and correctly splits the device out, so it must rank first.
        matcher = TemplateMatcher()
        matcher.add_templates(["play {query}", "play {query} on {device}"])
        results = matcher.predict("play jazz on spotify")
        self.assertEqual(len(results), 2)
        self.assertGreater(results[0][0], results[1][0])
        self.assertEqual(results[0][1], {"query": "jazz", "device": "spotify"})
        self.assertEqual(matcher.match("play jazz on spotify"),
                          {"query": "jazz", "device": "spotify"})


class TestTransformFillsLongSlotValue(unittest.TestCase):
    def test_transform_fills_play_the_beatles(self):
        plugin = KeywordTemplateMatcher()
        message = Message("ovos.intent.register.template",
                           data={"intent_name": "demo.intent",
                                 "samples": ["play {query}"],
                                 "lang": "en-US", "skill_id": "test_skill"})
        plugin.handle_register_template(message)

        intent = IntentHandlerMatch(
            match_type="test_skill:demo.intent",
            match_data={},
            skill_id="test_skill",
            utterance="play the beatles",
        )
        result = plugin.transform(intent)
        self.assertEqual(result.match_data, {"query": "the beatles"})
