from os.path import isfile

from ovos_bus_client.message import Message
from ovos_bus_client.session import SessionManager
from ovos_plugin_manager.templates.pipeline import IntentHandlerMatch
from ovos_plugin_manager.templates.transformers import IntentTransformer
from ovos_utils.bracket_expansion import expand_template
from ovos_utils.lang import standardize_lang_tag
from ovos_utils.list_utils import deduplicate_list, flatten_list
from ovos_utils.log import LOG
from typing import Union

from kw_template_matcher import TemplateMatcher


class KeywordTemplateMatcher(IntentTransformer):
    def __init__(self, config=None):
        super().__init__("keyword-templates", 1, config)
        self.matchers = {}

    def bind(self, bus):
        super().bind(bus)
        self.bus.on('padatious:register_intent', self.handle_register_intent)

    def _unpack_object(self, message: Message):
        """convert message to training data"""
        # standard info
        sess = SessionManager.get(message)
        skill_id = message.data.get("skill_id") or message.context.get("skill_id")
        if not skill_id:
            skill_id = "anonymous_skill"
        lang = message.data.get('lang') or sess.lang
        lang = standardize_lang_tag(lang)

        # intent specific
        file_name = message.data.get('file_name')
        samples = message.data.get("samples")
        name = message.data['name']
        blacklisted_words = message.data.get('blacklisted_words', [])
        if (not file_name or not isfile(file_name)) and not samples:
            raise FileNotFoundError('Could not find file ' + file_name)
        if not samples and isfile(file_name):
            with open(file_name) as f:
                samples = [line.strip() for line in f.readlines()]

        # expand templates
        samples = deduplicate_list(flatten_list([expand_template(s) for s in samples]))

        # we only care about keyword extractors, drop the rest
        samples = [s for s in samples if "{" in s]

        return lang, skill_id, name, samples, blacklisted_words

    def handle_register_intent(self, message: Message):
        lang, _, intent_name, samples, _ = self._unpack_object(message)
        if not samples:
            return
        if lang not in self.matchers:
            self.matchers[lang] = {}
        if intent_name not in self.matchers[lang]:
            self.matchers[lang][intent_name] = TemplateMatcher()
        self.matchers[lang][intent_name].add_templates(samples)
        LOG.debug(f"Registered {len(samples)} templates for {intent_name} ({lang})")

    def transform(self, intent: IntentHandlerMatch) -> IntentHandlerMatch:
        """
        Optionally transform intent handler data
        e.g. NER could be performed here by modifying intent.match_data
        """
        sess = intent.updated_session or SessionManager.get()
        matchers = self.matchers.get(sess.lang)
        if matchers:
            if intent.match_type in matchers:
                entities = matchers[intent.match_type].match(intent.utterance)
                LOG.debug(f"{intent.match_type} keyword templates match: {entities}")
                if entities:
                    intent.match_data.update(entities)
        return intent
