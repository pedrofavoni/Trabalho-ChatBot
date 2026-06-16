from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Tuple

from entities import Team, Player, Coach


# ---------------------------------------------------------------------------
# Interface abstrata (Contrato)
# ---------------------------------------------------------------------------
class IBrasileiraoRepository(ABC):
    @abstractmethod
    def get_team_by_name(self, name: str) -> Optional[Team]:
        pass

    @abstractmethod
    def get_all_teams(self) -> List[Team]:
        pass

    @abstractmethod
    def get_standings(self) -> List[Team]:
        """Retorna os times ordenados pela classificação (1º ao último)."""
        pass

    @abstractmethod
    def get_g4(self) -> List[Team]:
        """Retorna os 4 primeiros colocados (zona de Libertadores)."""
        pass

    @abstractmethod
    def get_relegation_zone(self) -> List[Team]:
        """Retorna os times na zona de rebaixamento (Z4)."""
        pass

    @abstractmethod
    def get_top_scorers(self, limit: int = 5) -> List[Tuple[str, str, int]]:
        """Retorna os artilheiros: lista de (nome, time, gols)."""
        pass

    @abstractmethod
    def get_best_attack(self) -> Optional[Team]:
        pass

    @abstractmethod
    def get_best_defense(self) -> Optional[Team]:
        pass

    @abstractmethod
    def get_classics(self) -> List[Dict]:
        pass

    @abstractmethod
    def get_coach_by_name(self, name: str) -> Optional[Coach]:
        pass

    @abstractmethod
    def get_all_coaches(self) -> List[Coach]:
        pass

    @abstractmethod
    def search_player(self, name: str) -> List[Tuple[str, str, str]]:
        """Busca um jogador pelo nome. Retorna lista de (nome, time, posição)."""
        pass

    @abstractmethod
    def reset_turno(self):
        pass

    @abstractmethod
    def foi_consultado(self) -> bool:
        pass


# ---------------------------------------------------------------------------
# Implementação concreta que lê o dataset.json local
# ---------------------------------------------------------------------------
class LocalJsonRepository(IBrasileiraoRepository):
    def __init__(self, data: Dict):
        self._teams: List[Team] = []
        self._coaches: List[Coach] = []
        self._classics: List[Dict] = data.get("classics", [])
        self._consultado = False

        for t in data.get("teams", []):
            players = [
                Player(p["name"], p["position"], p["number"], p["goals"], p.get("biography", ""))
                for p in t.get("players", [])
            ]
            team = Team(
                name=t["name"],
                nicknames=t.get("nicknames", []),
                city=t.get("city", ""),
                state=t.get("state", ""),
                stadium=t.get("stadium", ""),
                founded=t.get("founded", 0),
                titles_brasileirao=t.get("titles_brasileirao", 0),
                coach_name=t.get("coach", ""),
                position=t.get("position", 0),
                points=t.get("points", 0),
                goals_for=t.get("goals_for", 0),
                goals_against=t.get("goals_against", 0),
                players=players,
                trivia=t.get("trivia", []),
                rivals=t.get("rivals", []),
            )
            self._teams.append(team)

        for c in data.get("coaches", []):
            self._coaches.append(
                Coach(c["name"], c.get("biography", ""), c.get("teams", []), c.get("style", ""))
            )

    # ---- consulta por time --------------------------------------------------
    def get_team_by_name(self, name: str) -> Optional[Team]:
        name_lower = name.lower().strip()
        for team in self._teams:
            if name_lower == team.name.lower():
                self._consultado = True
                return team
        # busca por apelido ou correspondência parcial
        for team in self._teams:
            if name_lower in team.name.lower():
                self._consultado = True
                return team
            for nick in team.nicknames:
                if name_lower == nick.lower() or name_lower in nick.lower():
                    self._consultado = True
                    return team
        return None

    def get_all_teams(self) -> List[Team]:
        return self._teams

    # ---- classificação ------------------------------------------------------
    def get_standings(self) -> List[Team]:
        self._consultado = True
        return sorted(self._teams, key=lambda t: t.position if t.position else 999)

    def get_g4(self) -> List[Team]:
        return self.get_standings()[:4]

    def get_relegation_zone(self) -> List[Team]:
        # Zona de rebaixamento clássica: 4 últimas posições (17 a 20).
        self._consultado = True
        return sorted(
            [t for t in self._teams if t.position >= 17],
            key=lambda t: t.position,
        )

    # ---- artilharia / ataque / defesa --------------------------------------
    def get_top_scorers(self, limit: int = 5) -> List[Tuple[str, str, int]]:
        self._consultado = True
        artilheiros = []
        for team in self._teams:
            for player in team.players:
                if player.goals > 0:
                    artilheiros.append((player.name, team.name, player.goals))
        artilheiros.sort(key=lambda x: x[2], reverse=True)
        return artilheiros[:limit]

    def get_best_attack(self) -> Optional[Team]:
        if not self._teams:
            return None
        self._consultado = True
        return max(self._teams, key=lambda t: t.goals_for)

    def get_best_defense(self) -> Optional[Team]:
        if not self._teams:
            return None
        self._consultado = True
        return min(self._teams, key=lambda t: t.goals_against)

    def get_classics(self) -> List[Dict]:
        if self._classics:
            self._consultado = True
        return self._classics

    # ---- técnicos -----------------------------------------------------------
    def get_coach_by_name(self, name: str) -> Optional[Coach]:
        name_lower = name.lower().strip()
        for coach in self._coaches:
            if name_lower in coach.name.lower():
                self._consultado = True
                return coach
        return None

    def get_all_coaches(self) -> List[Coach]:
        return self._coaches

    # ---- jogadores ----------------------------------------------------------
    def search_player(self, name: str) -> List[Tuple[str, str, str]]:
        name_lower = name.lower().strip()
        encontrados = []
        for team in self._teams:
            for player in team.players:
                if name_lower in player.name.lower():
                    self._consultado = True
                    encontrados.append((player.name, team.name, player.position))
        return encontrados

    # ---- controle de turno --------------------------------------------------
    def reset_turno(self):
        self._consultado = False

    def foi_consultado(self) -> bool:
        return self._consultado
