import uuid

from app.domain.entities.board import Board
from app.domain.value_objects.cell_position import CellPosition
from app.domain.value_objects.cell_value import CellValue
from app.domain.value_objects.game_difficulty import GameDifficulty
from app.domain.value_objects.game_status import GameStatus


class Game:
    def __init__(
            self,
            board: Board,
            solution: Board,
            difficulty: GameDifficulty,
            game_id: str | None = None,
            status: GameStatus = GameStatus.IN_PROGRESS,
    ):
        self.id = game_id or str(uuid.uuid4())
        self.board = board
        self.solution = solution
        self.difficulty = difficulty
        self.status = status

    def set_cell_value(self, position: CellPosition, value: CellValue | None) -> None:
        if self.status == GameStatus.WON:
            return

        self.board.set_value(position=position, value=value)
        if self.board.is_solved():
            self.status = GameStatus.WON

    def is_move_correct(self, position: CellPosition, value: CellValue) -> bool:
        return self.solution.get_cell(position=position).value == value

    def reveal_hint(self, position: CellPosition) -> CellValue:
        value = self.solution.get_cell(position=position).value
        self.set_cell_value(position=position, value=value)
        return value

    def restart(self) -> None:
        for row in self.board.get_rows():
            for cell in row:
                if not cell.is_fixed:
                    self.board.set_value(position=cell.position, value=None)
        self.status = GameStatus.IN_PROGRESS
