from dataclasses import dataclass

from app.domain.value_objects.cell_position import CellPosition
from app.domain.value_objects.cell_value import CellValue
from app.domain.exceptions import FixedCellError


@dataclass(slots=True)
class Cell:
    position: CellPosition
    value: CellValue | None = None
    is_fixed: bool = False

    def clear(self) -> None:
        if self.is_fixed:
            raise FixedCellError(f"Cell fixed at {self.position}")
        self.value = None

    def clone(self) -> "Cell":
        return Cell(position=self.position, value=self.value, is_fixed=self.is_fixed)
