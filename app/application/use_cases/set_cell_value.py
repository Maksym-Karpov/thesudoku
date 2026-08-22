from app.application.dto.game_state_dto import GameStateDTO
from app.infrastructure.repositories.base_repository import BaseRepository
from app.domain.value_objects.cell_position import CellPosition
from app.domain.value_objects.cell_value import CellValue


class SetCellValueUseCase:
    def __init__(self, repository: BaseRepository):
        self._repository = repository

    def execute(
        self, game_id: str, row_idx: int, column_idx: int, value: int | None
    ) -> GameStateDTO:
        game = self._repository.get_or_raise(game_id=game_id)
        position = CellPosition(row_idx=row_idx, column_idx=column_idx)
        cell_value = CellValue(value) if value is not None else None
        game.set_cell_value(position=position, value=cell_value)
        self._repository.save(game=game)
        return GameStateDTO.from_game(game=game)
