import random
from typing import List

from nlp import NLPProcessor, IntentClassifier, EntityExtractor, ResponseEnricher
from StateManagement import ConversationContext
from learningModel.ILLMFallback import ILLMFallback

# Intents globais (sobre o campeonato) que NÃO dependem de um time em contexto.
INTENTS_GLOBAIS = {
    "ask_standings", "ask_g4", "ask_relegation", "ask_top_scorer",
    "ask_attack", "ask_defense", "ask_classics",
}
# Intents resolvidos pela base que nunca devem acionar o LLM.
INTENTS_SEM_FALLBACK = INTENTS_GLOBAIS | {"ask_greeting", "ask_affirmation"}


class ChatbotOrchestrator:
    def __init__(self, repository, fallback: ILLMFallback = None):
        self.repository = repository
        self.fallback = fallback
        self.nlp_processor = NLPProcessor()
        self.intent_classifier = IntentClassifier(self.nlp_processor.stemmer)
        self.entity_extractor = EntityExtractor(repository)
        self.context = ConversationContext()
        self.enricher = ResponseEnricher()
        self.affirmation_handler = self.intent_classifier.get_affirmation_handler()

    # =======================================================================
    # Fluxo principal: base de conhecimento -> (se preciso) LLM
    # =======================================================================
    def handle_message(self, user_text: str) -> dict:
        self.repository.reset_turno()
        self.context.last_user_text = user_text
        tokens, _ = self.nlp_processor.process_text(user_text)

        # Identifica um time citado (nome ou apelido) antes de classificar:
        # isso evita que perguntas de conteúdo sejam tratadas como saudação/afirmação.
        team_name = self.entity_extractor.extract_team(user_text)

        intent = self.intent_classifier.classify(
            tokens, original_text=user_text, has_team=bool(team_name)
        )
        print(f"[DEBUG] tokens: {tokens}")
        print(f"[DEBUG] intent: {intent} | time citado: {team_name}")

        # Atualiza o contexto com o time citado
        is_new_team = False
        if team_name and intent not in {"ask_greeting", "ask_affirmation", "ask_player_search"}:
            team = self.repository.get_team_by_name(team_name)
            if team:
                if self.context.current_team is None or self.context.current_team.name != team.name:
                    is_new_team = True
                self.context.set_team(team)

        sub_intent = "default"
        full_intent = f"{intent}:{sub_intent}"
        is_repeat = (full_intent == self.context.last_full_intent and intent != "unknown")

        response = self._generate_response(intent, tokens, is_repeat=is_repeat, is_new_team=is_new_team)
        print(f"[DEBUG] response base: {response}")
        print(f"[DEBUG] should_fallback: {self._should_use_fallback(intent, response)}")

        source = "local"
        if self._should_use_fallback(intent, response) and self.fallback:
            context_summary = self._build_context_summary()
            response = self.fallback.answer(user_text, context_summary)
            source = "llm"

        effective_intent = self.context.last_resolved_intent or intent
        self.context.last_resolved_intent = None
        response, hook_intent = self.enricher.enrich(effective_intent, response, self.context.current_team)
        self.context.last_hook_intent = hook_intent
        self.context.last_full_intent = (
            f"{effective_intent}:default" if intent == "ask_affirmation" else full_intent
        )
        return {"text": response, "source": source}

    # =======================================================================
    # Decisão de fallback
    # =======================================================================
    def _should_use_fallback(self, intent: str, response: str) -> bool:
        if intent in INTENTS_SEM_FALLBACK:
            return False
        if intent == "unknown":
            return True  # LLM responde qualquer pergunta fora do domínio
        if "não encontrei" in response.lower() or "não tenho" in response.lower():
            return True
        return False

    def _build_context_summary(self) -> str:
        parts = []
        if self.context.current_team:
            t = self.context.current_team
            parts.append(f"Time em contexto: {t.name} ({t.position}º lugar, {t.points} pontos)")
            if t.coach_name:
                parts.append(f"Técnico: {t.coach_name}")
            if t.titles_brasileirao:
                parts.append(f"Títulos brasileiros: {t.titles_brasileirao}")
            if t.players:
                nomes = ", ".join(p.name for p in t.players[:3])
                parts.append(f"Alguns jogadores: {nomes}")
        if self.context.last_topic:
            parts.append(f"Último tópico: {self.context.last_topic}")
        if not parts:
            return "Nenhum contexto de conversa disponível ainda."
        return " | ".join(parts)

    # =======================================================================
    # Geração de resposta a partir da base de conhecimento
    # =======================================================================
    def _generate_response(self, intent: str, tokens: List[str], is_repeat=False, is_new_team=False) -> str:
        if intent == "ask_greeting":
            return self._resp_greeting(tokens)
        if intent == "ask_affirmation":
            return self._resp_affirmation(tokens)

        # ----- intents globais (campeonato) -----
        if intent == "ask_standings":
            return self._resp_standings(tokens)
        if intent == "ask_g4":
            return self._resp_g4()
        if intent == "ask_relegation":
            return self._resp_relegation()
        if intent == "ask_top_scorer":
            return self._resp_top_scorer()
        if intent == "ask_attack":
            return self._resp_attack()
        if intent == "ask_defense":
            return self._resp_defense()
        if intent == "ask_classics":
            return self._resp_classics()
        if intent == "ask_player_search":
            return self._resp_player_search()

        # ----- intents que dependem de um time em contexto -----
        team = self.context.current_team
        if intent in {"ask_coach", "ask_squad", "ask_stadium", "ask_rivals",
                      "ask_titles", "ask_trivia", "ask_team_info"} and not team:
            return "Sobre qual time você gostaria de saber? Me diga o nome do clube."

        if intent == "ask_coach":
            return self._resp_coach(team)
        if intent == "ask_squad":
            return self._resp_squad(team)
        if intent == "ask_stadium":
            return f"O {team.name} manda seus jogos no {team.stadium}, em {team.city}/{team.state}."
        if intent == "ask_rivals":
            if not team.rivals:
                return f"Não tenho os rivais do {team.name} cadastrados."
            return f"Os principais rivais do {team.name} são: {', '.join(team.rivals)}."
        if intent == "ask_titles":
            return f"O {team.name} tem {team.titles_brasileirao} título(s) do Campeonato Brasileiro."
        if intent == "ask_trivia":
            if team.trivia:
                return f"Uma curiosidade sobre o {team.name}: {random.choice(team.trivia)}"
            return f"Não tenho curiosidades cadastradas sobre o {team.name}."
        if intent == "ask_team_info":
            return self._resp_team_info(team)

        if intent == "contextual_followup":
            if team:
                return (f"Sobre o {team.name}, posso falar do elenco, técnico, títulos, "
                        f"estádio ou uma curiosidade. O que você prefere?")
            return "Sobre o que você quer saber mais? Posso falar da tabela, artilharia ou de um time específico."

        # ----- intent desconhecido -----
        if intent == "unknown" and team and is_new_team:
            return self._resp_team_info(team)
        return self._resp_unknown(tokens)

    def _resp_unknown(self, tokens: List[str] = None) -> str:
        STOP = {"o", "a", "e", "de", "da", "do", "em", "um", "uma", "que",
                "nao", "me", "se", "eu", "tu", "ele", "ela", "nos", "voce",
                "por", "para", "com", "mas", "ou", "ja", "ai", "eh", "so",
                "vc", "tá", "ta", "is", "foi", "ser", "tem", "ter"}

        pivot = None
        if tokens:
            candidatos = [t for t in tokens if t not in STOP and len(t) > 2]
            if candidatos:
                pivot = random.choice(candidatos)

        if pivot:
            templates = [
                f"Hm, {pivot}? Nunca pensei nisso no contexto do Brasileirão... mas sabe o que tem tudo a ver com {pivot}? A pressão de quem tá no Z4! 😅",
                f"{pivot.capitalize()}?? Cara, isso me lembrou aquele gol do Flamengo no último minuto. Falando em emoção — quer saber da tabela?",
                f"Interessante você falar em {pivot}. Aqui a gente só entende de chute, gol e classificação, mas prometo que {pivot} tem mais a ver com futebol do que parece. Pergunta sobre o Brasileirão! ⚽",
                f"Juro que tentei relacionar {pivot} com o Brasileirão e quase consegui! Mas o que posso mesmo é te falar do G4, do artilheiro ou de algum time.",
                f"{pivot.capitalize()} e futebol? Tô processando... ⚙️ Enquanto isso, quer saber quem é o líder da tabela?",
                f"Olha, {pivot} é um assunto rico, mas meu cérebro só funciona pra futebol. Me faz uma pergunta sobre o Brasileirão que eu respondo na hora!",
            ]
        else:
            templates = [
                "Cara, isso tá além do meu sistema! 🤯 Mas qualquer coisa sobre o Brasileirão, pode mandar.",
                "Não entendi bulhufas, mas tô aqui pra falar de futebol. Me pergunta sobre tabela, artilheiros ou algum time!",
                "Isso me deu um curto-circuito... ⚡ Sou especialista em Brasileirão, não em filosofia. Manda uma pergunta de futebol!",
                "Processando... processando... erro! 🤖 Só funciono no modo futebol. Tenta me perguntar sobre o G4 ou algum clube.",
            ]

        return random.choice(templates)

    # ------------------------------------------------------------------ helpers
    def _resp_greeting(self, tokens: List[str]) -> str:
        saudacoes = [
            "Olá! ⚽ Sou o BrasileirãoBot, seu assistente sobre o Campeonato Brasileiro.\n\nPosso falar da tabela, artilharia, G4, rebaixamento, clássicos e de cada time. Sobre o que quer saber?",
            "Oi! ⚽ Aqui é o BrasileirãoBot.\n\nPergunta o que quiser sobre o Brasileirão: classificação, times, técnicos, títulos e muito mais!",
            "Salve! ⚽ Bem-vindo ao BrasileirãoBot.\n\nQuer saber quem é o líder, o artilheiro ou detalhes de um clube? É só perguntar.",
        ]
        despedidas = [
            "Até logo! Foi um prazer falar de futebol com você.",
            "Valeu! Volte quando quiser saber mais sobre o Brasileirão.",
            "Tchau! Bons jogos e até a próxima rodada! ⚽",
        ]
        tokens_despedida = {"tchau", "xau", "ate", "falou", "flw", "logo", "amanha", "valeu"}
        if any(t in tokens for t in tokens_despedida):
            return random.choice(despedidas)
        return random.choice(saudacoes)

    def _resp_affirmation(self, tokens: List[str]) -> str:
        rotulo = self.affirmation_handler.get_label()
        if rotulo == "afirmacao":
            hook = self.context.last_hook_intent
            if hook:
                self.context.last_hook_intent = None
                self.context.last_resolved_intent = hook
                return self._generate_response(hook, tokens)
            return "Claro! Posso falar da tabela, artilharia, G4, rebaixamento, clássicos ou de um time específico. O que prefere?"
        return "Tudo bem! Se quiser, posso falar da classificação, dos artilheiros ou de algum clube. É só dizer."

    def _resp_standings(self, tokens: List[str]) -> str:
        standings = self.repository.get_standings()
        if not standings:
            return "Não tenho a classificação cadastrada no momento."
        if any(t in tokens for t in [self.nlp_processor.stem(w) for w in ["lider", "primeiro", "lidera"]]):
            lider = standings[0]
            return f"O líder do Brasileirão é o {lider.name}, com {lider.points} pontos."
        linhas = ["📊 Classificação do Brasileirão:\n"]
        for t in standings[:6]:
            linhas.append(f"{t.position}º - {t.name} ({t.points} pts)")
        return "\n".join(linhas)

    def _resp_g4(self) -> str:
        g4 = self.repository.get_g4()
        linhas = ["🏆 Times no G4 (zona de Libertadores):\n"]
        for t in g4:
            linhas.append(f"{t.position}º - {t.name} ({t.points} pts)")
        return "\n".join(linhas)

    def _resp_relegation(self) -> str:
        z4 = self.repository.get_relegation_zone()
        if not z4:
            return "Não tenho times na zona de rebaixamento cadastrados no momento."
        linhas = ["🔻 Zona de rebaixamento (Z4):\n"]
        for t in z4:
            linhas.append(f"{t.position}º - {t.name} ({t.points} pts)")
        return "\n".join(linhas)

    def _resp_top_scorer(self) -> str:
        scorers = self.repository.get_top_scorers()
        if not scorers:
            return "Não tenho dados de artilharia no momento."
        linhas = ["⚽ Artilheiros do Brasileirão:\n"]
        for i, (nome, time, gols) in enumerate(scorers, 1):
            linhas.append(f"{i}. {nome} ({time}) — {gols} gols")
        return "\n".join(linhas)

    def _resp_attack(self) -> str:
        t = self.repository.get_best_attack()
        if not t:
            return "Não tenho dados de ataque no momento."
        return f"O melhor ataque do Brasileirão é o do {t.name}, com {t.goals_for} gols marcados."

    def _resp_defense(self) -> str:
        t = self.repository.get_best_defense()
        if not t:
            return "Não tenho dados de defesa no momento."
        return f"A melhor defesa do Brasileirão é a do {t.name}, com apenas {t.goals_against} gols sofridos."

    def _resp_classics(self) -> str:
        classics = self.repository.get_classics()
        if not classics:
            return "Não tenho clássicos cadastrados no momento."
        linhas = ["🔥 Principais clássicos do Brasileirão:\n"]
        for c in classics:
            times = " x ".join(c.get("teams", []))
            linhas.append(f"• {c.get('name')}: {times} — {c.get('description', '')}")
        return "\n".join(linhas)

    def _resp_player_search(self) -> str:
        nome = self.entity_extractor.extract_player_name(self.context.last_user_text)
        if not nome:
            return "Não consegui identificar o nome do jogador. Pode repetir com o nome completo?"
        resultados = self.repository.search_player(nome)
        if not resultados:
            return f"Não encontrei o jogador {nome.title()} na minha base local."
        linhas = []
        for nome_j, time, posicao in resultados:
            # busca o objeto Player para detalhes
            detalhe = ""
            team = self.repository.get_team_by_name(time)
            if team:
                for p in team.players:
                    if p.name == nome_j:
                        detalhe = f" — {p.goals} gols no campeonato." if p.goals else "."
                        if p.biography:
                            detalhe += f" {p.biography}"
            linhas.append(f"{nome_j} joga no {time} como {posicao}{detalhe}")
        return "\n".join(linhas)

    def _resp_coach(self, team) -> str:
        coach = self.repository.get_coach_by_name(team.coach_name)
        if not coach:
            return f"O técnico do {team.name} é o {team.coach_name}."
        self.context.set_coach(coach)
        info = f"O técnico do {team.name} é o {coach.name}."
        if coach.style:
            info += f" Seu estilo é marcado por {coach.style}."
        return info

    def _resp_squad(self, team) -> str:
        if not team.players:
            return f"Não tenho o elenco do {team.name} cadastrado."
        linhas = [f"Alguns destaques do elenco do {team.name}:\n"]
        for p in team.players:
            linhas.append(f"• {p.name} (#{p.number}) — {p.position}")
        return "\n".join(linhas)

    def _resp_team_info(self, team) -> str:
        return (
            f"📌 {team.name} ({', '.join(team.nicknames) if team.nicknames else ''})\n"
            f"Cidade: {team.city}/{team.state} | Fundação: {team.founded}\n"
            f"Estádio: {team.stadium}\n"
            f"Técnico: {team.coach_name}\n"
            f"Posição atual: {team.position}º com {team.points} pontos\n"
            f"Títulos brasileiros: {team.titles_brasileirao}"
        )
