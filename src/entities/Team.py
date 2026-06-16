from dataclasses import dataclass, field
from typing import List
from .Player import Player


@dataclass
class Team:
    name: str
    nicknames: List[str] = field(default_factory=list)   # apelidos: "Mengão", "Verdão"...
    city: str = ""
    state: str = ""
    stadium: str = ""
    founded: int = 0
    titles_brasileirao: int = 0
    coach_name: str = ""
    position: int = 0                                     # posição atual na tabela
    points: int = 0                                       # pontos no campeonato
    goals_for: int = 0                                    # gols marcados (ataque)
    goals_against: int = 0                               # gols sofridos (defesa)
    players: List[Player] = field(default_factory=list)
    trivia: List[str] = field(default_factory=list)
    rivals: List[str] = field(default_factory=list)
