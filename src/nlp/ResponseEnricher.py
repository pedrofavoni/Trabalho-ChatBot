import random
from typing import Tuple, Optional


class ResponseEnricher:
    """Adiciona um 'gancho' de follow-up ao final da resposta, sugerindo o
    próximo assunto — torna a conversa mais natural e guiada."""

    HOOKS = {
        "ask_standings": [
            " Quer ver quais times estão no G4?",
            " Quer saber quem está na zona de rebaixamento?",
            " Quer saber quem é o artilheiro do campeonato?",
        ],
        "ask_g4": [
            " Quer saber mais sobre algum desses times?",
            " Quer ver a tabela completa de classificação?",
        ],
        "ask_relegation": [
            " Quer ver quem está brigando pelo título?",
            " Quer saber a classificação completa?",
        ],
        "ask_top_scorer": [
            " Quer saber qual time tem o melhor ataque?",
            " Quer conhecer melhor algum desses jogadores?",
        ],
        "ask_team_info": [
            " Quer conhecer o elenco desse time?",
            " Quer saber quantos títulos ele tem?",
            " Quer saber quem é o técnico?",
        ],
        "ask_coach": [
            " Quer conhecer o elenco do time?",
            " Quer saber uma curiosidade sobre o clube?",
        ],
        "ask_squad": [
            " Quer saber quem é o técnico?",
            " Quer uma curiosidade sobre o time?",
        ],
        "ask_titles": [
            " Quer saber uma curiosidade sobre esse clube?",
            " Quer conhecer o elenco atual?",
        ],
        "ask_trivia": [
            " Quer ouvir outra curiosidade?",
            " Quer saber quantos títulos esse time tem?",
        ],
        "ask_stadium": [
            " Quer conhecer o elenco que joga lá?",
            " Quer uma curiosidade sobre o clube?",
        ],
        "ask_rivals": [
            " Quer saber quais são os maiores clássicos do Brasileirão?",
            " Quer conhecer melhor um desses times?",
        ],
        "ask_classics": [
            " Quer saber mais sobre algum desses times?",
            " Quer ver quem lidera o campeonato?",
        ],
    }

    HOOK_INTENT_MAP = {
        "ask_standings": "ask_g4",
        "ask_g4": "ask_team_info",
        "ask_relegation": "ask_standings",
        "ask_top_scorer": "ask_attack",
        "ask_team_info": "ask_squad",
        "ask_coach": "ask_squad",
        "ask_squad": "ask_coach",
        "ask_titles": "ask_trivia",
        "ask_trivia": "ask_trivia",
        "ask_stadium": "ask_squad",
        "ask_rivals": "ask_classics",
        "ask_classics": "ask_standings",
    }

    def enrich(self, intent: str, base_response: str, team) -> Tuple[str, Optional[str]]:
        hooks = self.HOOKS.get(intent)
        if not hooks:
            return base_response, None
        hook_intent = self.HOOK_INTENT_MAP.get(intent)
        return base_response + "\n\n" + random.choice(hooks), hook_intent
