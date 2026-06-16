from dataclasses import dataclass


@dataclass
class Player:
    name: str
    position: str          # ex: "Atacante", "Goleiro", "Meio-campo"
    number: int            # número da camisa
    goals: int             # gols no campeonato (para artilharia)
    biography: str = ""
