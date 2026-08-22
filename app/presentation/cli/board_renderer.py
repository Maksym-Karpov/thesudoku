from app.application.dto.game_state_dto import GameStateDTO


class BoardRenderer:
    """Renders a :class:`GameStateDTO` as a plain-text 9x9 grid.

    Given (fixed) digits are shown as-is; player-entered digits are shown
    the same way but could easily be styled differently by a richer UI
    since ``fixed_mask`` is exposed in the DTO.
    """

    _COLUMN_SEPARATOR_EVERY = 3
    _ROW_SEPARATOR_EVERY = 3

    def render(self, state: GameStateDTO) -> str:
        lines: list[str] = []
        lines.append(f"Game: {state.game_id}  |  Difficulty: {state.difficulty}  |  Status: {state.status}")
        lines.append(self._divider())
        for row_idx, row in enumerate(state.grid):
            cells = []
            for col_idx, value in enumerate(row):
                text = str(value) if value is not None else "."
                cells.append(text)
                if (col_idx + 1) % self._COLUMN_SEPARATOR_EVERY == 0 and col_idx != len(row) - 1:
                    cells.append("|")
            lines.append(" ".join(cells))
            if (row_idx + 1) % self._ROW_SEPARATOR_EVERY == 0 and row_idx != len(state.grid) - 1:
                lines.append(self._divider())
        lines.append(self._divider())
        return "\n".join(lines)

    @staticmethod
    def _divider() -> str:
        return "-" * 21
