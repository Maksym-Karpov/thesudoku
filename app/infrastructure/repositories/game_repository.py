from app.domain.entities.game import Game
from app.domain.repositories.game_repository import BaseRepository


class GameRepository(BaseRepository):
    def __init__(self):
        self._games: dict[str, Game] = {}

    def save(self, game: Game) -> None:
        self._games[game.id] = game

    def get(self, game_id: str) -> Game | None:
        return self._games.get(game_id)
