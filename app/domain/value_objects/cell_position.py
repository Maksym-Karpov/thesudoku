from dataclasses import dataclass

from app.domain.exceptions import InvalidCellPositionValueError


BOARD_SIZE = 9


@dataclass(frozen=True, slots=True)
class CellPosition:
    row_idx: int
    column_idx: int

    def __post_init__(self) -> None:
        if not (0 <= self.row_idx < BOARD_SIZE):
            raise InvalidCellPositionValueError(f"row index must be from 0 to {BOARD_SIZE - 1}, got {self.row_idx}")

        if not (0 <= self.column_idx < BOARD_SIZE):
            raise InvalidCellPositionValueError(
                f"column index must be from 0 to {BOARD_SIZE - 1}, got {self.column_idx}"
            )

    @property
    def square_idx(self) -> int:
        return (self.row_idx // 3) * 3 + (self.column_idx // 3)
