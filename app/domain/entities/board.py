from app.domain.entities.cell import Cell
from app.domain.exceptions import FixedCellError, InvalidCellValueError, InvalidBoardCellsAmount
from app.domain.value_objects.cell_position import BOARD_SIZE, CellPosition
from app.domain.value_objects.cell_value import CellValue


class Board:
    SIZE = BOARD_SIZE
    SQUARE_SIZE = 3

    def __init__(self, rows: list[list[Cell]] | None = None):
        if rows is None:
            rows: list[list[Cell]] = []
            for row_idx in range(self.SIZE):
                row = []
                for column_idx in range(self.SIZE):
                    row.append(Cell(position=CellPosition(row_idx=row_idx, column_idx=column_idx)))
                rows.append(row)
        else:
            rows = [list(row) for row in rows]

        if rows and (len(rows) != self.SIZE or any(len(row) != self.SIZE for row in rows)):
            raise InvalidBoardCellsAmount(
                f"Board must be a {self.SIZE}x{self.SIZE} grid of rows"
            )

        self._rows: list[list[Cell]] = rows

    @classmethod
    def empty(cls) -> "Board":
        return cls()

    def set_value(self, position: CellPosition, value: CellValue | None) -> None:
        cell = self.get_cell(position=position)
        if cell.is_fixed:
            raise FixedCellError(f"Cell at {position} is fixed and cannot be modified")
        if value is not None and not self._is_value_valid(position=position, value=value):
            raise InvalidCellValueError(
                f"Value {value} conflicts with an existing value in the same row, column or square"
            )
        cell.value = value

    def force_set(self, position: CellPosition, value: CellValue | None, is_fixed: bool = False) -> None:
        cell: Cell = self.get_cell(position=position)
        cell.value = value
        cell.is_fixed = is_fixed

    def get_rows(self) -> list[list[Cell]]:
        return self._rows

    def get_cell(self, position: CellPosition) -> Cell:
        return self._rows[position.row_idx][position.column_idx]

    def get_row(self, row_idx: int) -> list[Cell]:
        return self._rows[row_idx]

    def get_column(self, column_idx: int) -> list[Cell]:
        return [row[column_idx] for row in self._rows]

    def get_square(self, square_idx: int) -> list[Cell]:
        start_row = (square_idx // 3) * 3
        start_col = (square_idx % 3) * 3
        square: list[Cell] = []
        for row_idx in range(start_row, start_row + 3):
            for column_idx in range(start_col, start_col + 3):
                square.append(self._rows[row_idx][column_idx])
        return square

    def is_full(self) -> bool:
        for row in self._rows:
            for cell in row:
                if cell.value is None:
                    return False
        return True

    def is_valid(self) -> bool:
        groups: list[list[Cell]] = []
        for i in range(self.SIZE):
            groups.append(self.get_row(row_idx=i))
            groups.append(self.get_column(column_idx=i))
            groups.append(self.get_square(square_idx=i))
        for group in groups:
            values = [cell.value for cell in group if cell.value is not None]
            if len(values) != len(set(values)):
                return False
        return True

    def is_solved(self) -> bool:
        return self.is_full() and self.is_valid()

    def clone(self) -> "Board":
        cloned_rows: list[list[Cell]] = []
        for row in self._rows:
            cloned_row: list[Cell] = []
            for cell in row:
                cloned_row.append(cell.clone())
            cloned_rows.append(cloned_row)
        return Board(rows=cloned_rows)

    def to_grid(self) -> list[list[int | None]]:
        # Convert the board into a plain 2D list of ints/None, suitable for
        # serialization or simple equality comparisons.
        grid: list[list[int | None]] = []
        for row in self._rows:
            grid_row: list[int | None] = []
            for cell in row:
                grid_row.append(cell.value.value if cell.value is not None else None)
            grid.append(grid_row)
        return grid

    def _is_value_valid(self, position: CellPosition, value: CellValue) -> bool:
        neighbors = (
                self.get_row(row_idx=position.row_idx)
                + self.get_column(column_idx=position.column_idx)
                + self.get_square(square_idx=position.square_idx)
        )
        for neighbor in neighbors:
            if neighbor.position != position and neighbor.value == value:
                return False
        return True

    def __eq__(self, other: object) -> bool:
        # Two boards are equal if they have the same values in every cell;
        # fixed/editable status is intentionally not compared.
        if not isinstance(other, Board):
            return NotImplemented
        return self.to_grid() == other.to_grid()
