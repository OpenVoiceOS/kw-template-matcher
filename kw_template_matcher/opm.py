from os.path import isfile

from ovos_bus_client.message import Message
from ovos_bus_client.session import SessionManager
from ovos_plugin_manager.templates.pipeline import IntentHandlerMatch, PipelineMatch
from ovos_plugin_manager.templates.transformers import IntentTransformer
from ovos_utils.bracket_expansion import expand_template
from ovos_utils.lang import standardize_lang_tag
from ovos_utils.list_utils import deduplicate_list, flatten_list
from ovos_utils.log import LOG
from typing import Union

from kw_template_matcher import TemplateMatcher


class KeywordTemplateMatcher(IntentTransformer):
    def __init__(self, config=None):
        """
        Initializes the KeywordTemplateMatcher with support for dynamic intent registration.
        
        Sets up the matcher with the name "keyword-templates" and version 1, initializes
        an empty dictionary for language-specific intent matchers, and registers an event
        listener to handle intent registration messages.
        """
        super().__init__("keyword-templates", 1, config)
        self.matchers = {}
        self.bus.on('padatious:register_intent', self.handle_register_intent)

    def _unpack_object(self, message: Message):
        """
        Extracts and processes training data for intent matching from a message.
        
        The method retrieves the skill ID, intent name, language, sample templates, and blacklisted words from the message. If samples are not provided, it attempts to read them from a specified file. The language tag is standardized, and sample templates are expanded, flattened, and deduplicated before returning.
        
        Returns:
            A tuple containing the standardized language tag, skill ID, intent name, processed sample templates, and blacklisted words.
        
        Raises:
            FileNotFoundError: If neither sample templates nor a valid file is provided.
        """
        skill_id = message.data.get("skill_id") or message.context.get("skill_id")
        if not skill_id:
            skill_id = "anonymous_skill"
        file_name = message.data.get('file_name')
        samples = message.data.get("samples")
        name = message.data['name']
        lang = message.data.get('lang', self.lang)
        lang = standardize_lang_tag(lang)
        blacklisted_words = message.data.get('blacklisted_words', [])
        if (not file_name or not isfile(file_name)) and not samples:
            raise FileNotFoundError('Could not find file ' + file_name)
        if not samples and isfile(file_name):
            with open(file_name) as f:
                samples = [line.strip() for line in f.readlines()]
        samples = deduplicate_list(flatten_list([expand_template(s) for s in samples]))
        return lang, skill_id, name, samples, blacklisted_words

    def handle_register_intent(self, message: Message):
        """
        Registers a new intent's keyword templates for a specific language.
        
        Extracts language, intent name, and sample templates from the incoming message, then ensures a template matcher exists for the language and intent. Adds the provided templates to the matcher for future intent matching.
        """
        lang, _, intent_name, samples, _ = self._unpack_object(message)
        if lang not in self.matchers:
            self.matchers[lang] = {}
        if intent_name not in self.matchers[lang]:
            self.matchers[lang][intent_name] = TemplateMatcher()
        self.matchers[lang][intent_name].add_templates(samples)

    def transform(self, intent: Union[IntentHandlerMatch, PipelineMatch]) -> Union[IntentHandlerMatch, PipelineMatch]:
        """
        Attempts to match the intent's utterance against registered keyword templates and updates match data with extracted entities if a match is found.
        
        If a template matcher exists for the current session language and intent type, the utterance is matched against stored templates. Any entities extracted from the match are merged into the intent's match data.
        
        Args:
            intent: The intent object containing the utterance and match data.
        
        Returns:
            The intent object, potentially updated with additional entities from template matching.
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
