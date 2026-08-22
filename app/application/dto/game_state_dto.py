from dataclasses import dataclass

from app.domain.entities.game import Game
from app.domain.value_objects.game_difficulty import GameDifficulty
from app.domain.value_objects.game_status import GameStatus


@dataclass(frozen=True, slots=True)
class GameStateDTO:
    """Read-only, transport-friendly snapshot of a game for the UI layer.

    Deliberately excludes the solution board so presentation code can never
    accidentally leak the answer.
    """

    game_id: str
    grid: list[list[int | None]]
    fixed_mask: list[list[bool]]
    difficulty: GameDifficulty
    status: GameStatus

    @classmethod
    def from_game(cls, game: Game) -> "GameStateDTO":
        cells = game.board.get_rows()
        fixed_mask: list[list[bool]] = []
        for row in cells:
            fixed_row: list[bool] = []
            for cell in row:
                fixed_row.append(cell.is_fixed)
            fixed_mask.append(fixed_row)
        return cls(
            game_id=game.id,
            grid=game.board.to_grid(),
            fixed_mask=fixed_mask,
            difficulty=game.difficulty,
            status=game.status,
        )
