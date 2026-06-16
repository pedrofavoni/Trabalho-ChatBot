import re
import unicodedata
from abc import ABC, abstractmethod
from typing import List
from nltk.stem import RSLPStemmer


def _normalizar(texto: str) -> str:
    texto = texto.lower()
    texto = unicodedata.normalize("NFKD", texto)
    return "".join(c for c in texto if not unicodedata.combining(c))


class IntentHandler(ABC):
    def __init__(self, stemmer: RSLPStemmer):
        self._stemmer = stemmer
        self._stemmed_keywords = [
            stemmer.stem(_normalizar(kw)) for kw in self._raw_keywords()
        ]

    def _raw_keywords(self) -> List[str]:
        raise NotImplementedError

    def matches(self, tokens: List[str]) -> bool:
        return any(word in self._stemmed_keywords for word in tokens)

    def get_stemmed_keywords(self) -> List[str]:
        return self._stemmed_keywords

    @abstractmethod
    def get_intent_name(self) -> str:
        pass


# ---------------------------------------------------------------------------
# Handlers do domínio Brasileirão
# ---------------------------------------------------------------------------
class StandingsHandler(IntentHandler):
    def _raw_keywords(self):
        return ["classificacao", "tabela", "lider", "lidera", "liderança",
                "colocado", "colocacao", "posicao", "primeiro", "pontos", "pontuacao"]

    def get_intent_name(self):
        return "ask_standings"


class G4Handler(IntentHandler):
    def _raw_keywords(self):
        # Apenas "g4": termos como "libertadores" são ambíguos (podem ser
        # perguntas históricas) e devem cair no LLM quando não houver match.
        return ["g4"]

    def get_intent_name(self):
        return "ask_g4"


class RelegationHandler(IntentHandler):
    def _raw_keywords(self):
        return ["rebaixamento", "rebaixado", "rebaixar", "z4", "zona", "degola"]

    def get_intent_name(self):
        return "ask_relegation"


class TopScorerHandler(IntentHandler):
    def _raw_keywords(self):
        return ["artilheiro", "artilharia", "goleador", "artilheiros"]

    def get_intent_name(self):
        return "ask_top_scorer"


class AttackHandler(IntentHandler):
    def _raw_keywords(self):
        return ["ataque", "ofensivo", "ataca", "ataques"]

    def get_intent_name(self):
        return "ask_attack"


class DefenseHandler(IntentHandler):
    def _raw_keywords(self):
        return ["defesa", "defensivo", "zaga", "defesas"]

    def get_intent_name(self):
        return "ask_defense"


class ClassicsHandler(IntentHandler):
    def _raw_keywords(self):
        # "rivalidade"/"rivalidades" reduzem para o stem "rival" e colidiriam
        # com o RivalsHandler (rivais de um time). Clássicos ficam só com
        # termos inequívocos; perguntas sobre rivais vão para ask_rivals.
        return ["classico", "classicos", "derby", "derbi"]

    def get_intent_name(self):
        return "ask_classics"


class TitlesHandler(IntentHandler):
    def _raw_keywords(self):
        return ["titulo", "titulos", "campeao", "campea",
                "conquista", "conquistas", "taca", "tacas"]

    def get_intent_name(self):
        return "ask_titles"


class CoachHandler(IntentHandler):
    def _raw_keywords(self):
        return ["tecnico", "treinador", "comandante", "comandado", "estilo", "esquema"]

    def get_intent_name(self):
        return "ask_coach"


class SquadHandler(IntentHandler):
    def _raw_keywords(self):
        return ["elenco", "plantel", "escalacao", "jogadores", "titulares", "time titular"]

    def get_intent_name(self):
        return "ask_squad"


class StadiumHandler(IntentHandler):
    def _raw_keywords(self):
        return ["estadio", "arena", "casa", "manda"]

    def get_intent_name(self):
        return "ask_stadium"


class RivalsHandler(IntentHandler):
    def _raw_keywords(self):
        return ["rival", "rivais", "maior rival"]

    def get_intent_name(self):
        return "ask_rivals"


class TriviaHandler(IntentHandler):
    def _raw_keywords(self):
        return ["curiosidade", "curiosidades", "fato", "fatos", "interessante", "historia"]

    def get_intent_name(self):
        return "ask_trivia"


class TeamInfoHandler(IntentHandler):
    def _raw_keywords(self):
        return ["informacao", "informacoes", "ficha", "dados", "fundado",
                "fundacao", "cidade", "apresenta"]

    def get_intent_name(self):
        return "ask_team_info"


class ContextualHandler(IntentHandler):
    def _raw_keywords(self):
        return ["ele", "ela", "mais", "outro", "isso"]

    def get_intent_name(self):
        return "contextual_followup"


class PlayerSearchHandler(IntentHandler):
    """Detecta perguntas sobre um jogador específico citado pelo nome próprio.

    Exemplos que ativam:
        "fale sobre o jogador Pedro"
        "em que time joga o Gabigol"
        "quem é o Arrascaeta"

    O método matches() padrão sempre retorna False; o IntentClassifier chama
    matches_original() com o texto original (caixa preservada) para detectar
    nomes próprios pela capitalização.
    """

    PREP_PATTERNS = {"do", "da", "dos", "das", "o", "a", "sobre", "de"}
    TRIGGER_WORDS = {"jogador", "atleta", "craque", "camisa", "joga", "jogou"}

    def _raw_keywords(self) -> List[str]:
        return ["jogador", "atleta", "craque"]

    def matches(self, tokens: List[str]) -> bool:
        return False

    def matches_original(self, original_text: str) -> bool:
        text_clean = re.sub(r'[^\w\s]', ' ', original_text).strip()
        words = text_clean.split()
        if not words:
            return False
        words_lower = [w.lower() for w in words]

        # Gatilho 1: palavra de jogador + nome próprio em qualquer posição
        if any(w in self.TRIGGER_WORDS for w in words_lower):
            for word in words[1:]:
                if word and word[0].isupper():
                    return True

        # Gatilho 2: "quem é/quem joga + [Nome Próprio]" sem outra intenção clara
        if "quem" in words_lower:
            for word in words[1:]:
                if word and word[0].isupper():
                    return True

        return False

    def get_intent_name(self) -> str:
        return "ask_player_search"
