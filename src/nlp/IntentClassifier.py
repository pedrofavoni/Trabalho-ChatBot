from typing import List
from nltk.stem import RSLPStemmer
from . import IntentHandlers
from .GreetingMLHandler import GreetingMLHandler
from .AffirmationHandler import AffirmationHandler

# Acima deste número de tokens a mensagem é claramente "conteúdo" (uma pergunta),
# e não uma saudação/afirmação curta — então não consultamos os classificadores ML.
MAX_TOKENS_ML = 4


class IntentClassifier:
    def __init__(self, stemmer: RSLPStemmer):
        # Handlers de palavra-chave (intenções específicas do domínio) vêm primeiro,
        # para que termos como "artilheiro" ou "tabela" sempre tenham prioridade.
        self.keyword_handlers = [
            IntentHandlers.StandingsHandler(stemmer),
            IntentHandlers.G4Handler(stemmer),
            IntentHandlers.RelegationHandler(stemmer),
            IntentHandlers.TopScorerHandler(stemmer),
            IntentHandlers.AttackHandler(stemmer),
            IntentHandlers.DefenseHandler(stemmer),
            IntentHandlers.ClassicsHandler(stemmer),
            IntentHandlers.TitlesHandler(stemmer),
            IntentHandlers.CoachHandler(stemmer),
            IntentHandlers.SquadHandler(stemmer),
            IntentHandlers.StadiumHandler(stemmer),
            IntentHandlers.RivalsHandler(stemmer),
            IntentHandlers.TriviaHandler(stemmer),
            IntentHandlers.TeamInfoHandler(stemmer),
        ]
        self.player_handler = IntentHandlers.PlayerSearchHandler(stemmer)
        self.greeting_handler = GreetingMLHandler(stemmer)
        self.affirmation_handler = AffirmationHandler(stemmer)
        self.contextual_handler = IntentHandlers.ContextualHandler(stemmer)

        # Lista completa (usada por get_keywords_for_intent)
        self.handlers = (
            self.keyword_handlers
            + [self.player_handler, self.greeting_handler,
               self.affirmation_handler, self.contextual_handler]
        )

    def get_affirmation_handler(self) -> "AffirmationHandler":
        return self.affirmation_handler

    def classify(self, tokens: List[str], original_text: str = "", has_team: bool = False) -> str:
        # 1) Intenções específicas por palavra-chave (prioridade máxima)
        for handler in self.keyword_handlers:
            if handler.matches(tokens):
                return handler.get_intent_name()

        # 2) Busca por jogador (nome próprio no texto original)
        if original_text and self.player_handler.matches_original(original_text):
            return self.player_handler.get_intent_name()

        # 3) Saudação / afirmação (ML) — só para mensagens curtas e sem time citado,
        #    evitando sequestrar perguntas de conteúdo (ex.: "me fala do Flamengo").
        if not has_team and len(tokens) <= MAX_TOKENS_ML:
            if self.greeting_handler.matches(tokens):
                return self.greeting_handler.get_intent_name()
            if self.affirmation_handler.matches(tokens):
                return self.affirmation_handler.get_intent_name()

        # 4) Follow-up contextual (ele/ela/mais/outro)
        if self.contextual_handler.matches(tokens):
            return self.contextual_handler.get_intent_name()

        return "unknown"

    def get_keywords_for_intent(self, intent_name: str) -> List[str]:
        for handler in self.handlers:
            if handler.get_intent_name() == intent_name:
                return handler.get_stemmed_keywords()
        return []
