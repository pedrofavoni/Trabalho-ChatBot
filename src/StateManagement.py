from dataclasses import dataclass
from entities import Team, Coach


@dataclass
class Message:
    role: str  # "user" ou "bot"
    content: str


class ConversationContext:
    def __init__(self):
        self.current_team: Team = None
        self.current_coach: Coach = None
        self.current_player: str = None
        self.last_topic: str = None
        self.last_full_intent = None
        self.last_hook_intent = None
        self.last_resolved_intent = None
        self.history = []
        self.last_user_text = ""

    def set_team(self, team: Team):
        self.current_team = team
        self.last_topic = "team"
        self.last_full_intent = None
        self.last_hook_intent = None  # evita follow-up apontando para o time anterior

    def set_coach(self, coach: Coach):
        self.current_coach = coach
        self.last_topic = "coach"

    def add_message(self, role: str, content: str):
        self.history.append(Message(role=role, content=content))
