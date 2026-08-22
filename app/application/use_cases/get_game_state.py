from app.application.dto.game_state_dto import GameStateDTO
from app.domain.repositories.game_repository import BaseRepository


class GetGameStateUseCase:
    def __init__(self, repository: BaseRepository):
        self._repository = repository

    def execute(self, game_id: str) -> GameStateDTO:
        game = self._repository.get_or_raise(game_id=game_id)
        return GameStateDTO.from_game(game=game)
