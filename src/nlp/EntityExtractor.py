import re
from difflib import SequenceMatcher
from typing import Optional, List


def _similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, a, b).ratio()


class EntityExtractor:
    """Extrai nomes de times (e apelidos) e de jogadores a partir do texto.

    Trabalha somente com a base local (sem chamadas externas), comparando
    o texto com os nomes/apelidos conhecidos e tolerando pequenas variações
    de digitação via similaridade de strings.
    """

    MATCH_THRESHOLD = 0.82
    # Similaridade aproximada só vale para termos longos. Apelidos curtos
    # ("Fla", "SPFC", "Fiel") colidem com palavras comuns — ex.: "Fla" tem
    # 0.857 de similaridade com "fala" em "me fala do Palmeiras".
    FUZZY_MIN_LEN = 6

    def __init__(self, repository):
        self.repository = repository
        # mapa apelido/nome (lower) -> nome canônico do time
        self.team_aliases = {}
        self.players = []  # nomes de jogadores (lower)
        self._load_entities()

    def _load_entities(self):
        for team in self.repository.get_all_teams():
            self.team_aliases[team.name.lower()] = team.name
            for nick in team.nicknames:
                self.team_aliases[nick.lower()] = team.name
            for player in team.players:
                pl = player.name.lower()
                if pl not in self.players:
                    self.players.append(pl)

    def _find_in_text(self, text_lower: str, candidates: list) -> Optional[str]:
        """Match exato por palavra inteira primeiro (em TODOS os candidatos),
        depois aproximado apenas para termos longos.

        A ordem importa: antes, um match aproximado de um apelido curto no
        início da lista (ex.: "Fla" ~ "fala") era retornado antes do match
        exato do time correto que viria depois (ex.: "palmeiras").
        """
        text_words = text_lower.split()

        # 1) match exato por palavra inteira — prefere o mais específico (maior),
        #    ex.: "sao paulo" em vez de um eventual "paulo".
        exact = [
            c for c in candidates
            if re.search(r'\b' + re.escape(c) + r'\b', text_lower)
        ]
        if exact:
            return max(exact, key=len)

        # 2) fallback aproximado (tolera erros de digitação), ignorando termos
        #    curtos que colidem com palavras comuns.
        best, best_score = None, self.MATCH_THRESHOLD
        for candidate in candidates:
            if len(candidate) < self.FUZZY_MIN_LEN:
                continue
            cand_words = candidate.split()
            n = len(cand_words)
            for i in range(len(text_words) - n + 1):
                window = " ".join(text_words[i:i + n])
                score = _similarity(window, candidate)
                if score >= best_score:
                    best, best_score = candidate, score
        return best

    def extract_team(self, clean_text: str) -> Optional[str]:
        """Retorna o nome canônico do time encontrado no texto, ou None."""
        text_lower = clean_text.lower()
        match = self._find_in_text(text_lower, list(self.team_aliases.keys()))
        if match:
            return self.team_aliases[match]
        return None

    def extract_player_name(self, text: str) -> Optional[str]:
        """Extrai o nome de um jogador a partir do texto original.

        Estratégia 1: comparar com os jogadores conhecidos da base.
        Estratégia 2: capturar nome próprio após preposição (do/da/sobre/o/a).
        """
        text_lower = text.lower()
        match = self._find_in_text(text_lower, self.players)
        if match:
            return match

        text_clean = re.sub(r'[^\w\s]', ' ', text).strip()
        words = text_clean.split()
        PREPOSICOES = {"do", "da", "dos", "das", "sobre", "o", "a", "de"}

        name_tokens = []
        collecting = False
        for word in words:
            if word.lower() in PREPOSICOES:
                name_tokens = []
                collecting = True
                continue
            if collecting:
                if word and word[0].isupper():
                    name_tokens.append(word)
                else:
                    if name_tokens:
                        break

        if name_tokens:
            return " ".join(name_tokens)

        # Fallback: qualquer nome próprio que não seja a primeira palavra
        for word in words[1:]:
            if word and word[0].isupper():
                return word
        return None
