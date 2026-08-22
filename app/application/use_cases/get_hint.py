from app.application.dto.game_state_dto import GameStateDTO
from app.application.exceptions import ApplicationError
from app.domain.exceptions import FixedCellError
from app.infrastructure.repositories.base_repository import BaseRepository
from app.domain.value_objects.cell_position import CellPosition


class GetHintUseCase:
    def __init__(self, repository: BaseRepository):
        self._repository = repository

    def execute(self, game_id: str, row_idx: int, column_idx: int) -> GameStateDTO:
        game = self._repository.get_or_raise(game_id=game_id)
        position = CellPosition(row_idx=row_idx, column_idx=column_idx)
        if game.board.get_cell(position=position).is_fixed:
            raise ApplicationError("Cannot reveal a hint for a fixed cell")
        try:
            game.reveal_hint(position=position)
        except FixedCellError as exc:
            raise ApplicationError(str(exc)) from exc
        self._repository.save(game=game)
        return GameStateDTO.from_game(game=game)
