from app.application.dto.game_state_dto import GameStateDTO
from app.application.exceptions import ApplicationError
from app.application.use_cases.get_hint import GetHintUseCase
from app.application.use_cases.new_game import NewGameUseCase
from app.application.use_cases.restart_game import RestartGameUseCase
from app.application.use_cases.set_cell_value import SetCellValueUseCase
from app.domain.exceptions import DomainError
from app.domain.value_objects.game_difficulty import GameDifficulty
from app.domain.value_objects.game_status import GameStatus
from app.presentation.cli.board_renderer import BoardRenderer

HELP_TEXT = """
Commands:
  new <easy|medium|hard>   start a new game
  set <row> <col> <value>  place a digit (1-9) at row/col (1-9, 1-indexed)
  clear <row> <col>        clear a cell you previously filled in
  hint <row> <col>         reveal the correct value for a cell
  restart                  clear your entries, keep the original puzzle
  show                     redraw the board
  help                     show this message
  quit                     exit the game
"""


class SudokuCLI:
    """Simple, dependency-free terminal UI for playing Sudoku.

    Talks exclusively to application-layer use cases and DTOs, never to
    domain entities directly, keeping the presentation layer decoupled
    from business rules.
    """

    def __init__(
        self,
        new_game_use_case: NewGameUseCase,
        set_cell_value_use_case: SetCellValueUseCase,
        restart_game_use_case: RestartGameUseCase,
        get_hint_use_case: GetHintUseCase,
        renderer: BoardRenderer | None = None,
    ):
        self._new_game_use_case = new_game_use_case
        self._set_cell_value_use_case = set_cell_value_use_case
        self._restart_game_use_case = restart_game_use_case
        self._get_hint_use_case = get_hint_use_case
        self._renderer = renderer or BoardRenderer()
        self._state: GameStateDTO | None = None

    def run(self) -> None:
        print("Welcome to Sudoku!")
        print(HELP_TEXT)
        print("Start with: new <easy|medium|hard>")
        while True:
            try:
                raw = input("> ").strip()
            except EOFError:
                break
            if not raw:
                continue
            if not self._dispatch(raw):
                break
        print("Goodbye!")

    def _dispatch(self, raw: str) -> bool:
        """Handle one command line. Returns False to stop the loop."""
        parts = raw.split()
        command, args = parts[0].lower(), parts[1:]
        try:
            if command in ("quit", "exit"):
                return False
            if command == "help":
                print(HELP_TEXT)
            elif command == "new":
                self._handle_new(args)
            elif command == "show":
                self._print_state()
            elif command == "set":
                self._handle_set(args)
            elif command == "clear":
                self._handle_clear(args)
            elif command == "hint":
                self._handle_hint(args)
            elif command == "restart":
                self._handle_restart()
            else:
                print(f"Unknown command: {command!r}. Type 'help' for a list of commands.")
        except (ApplicationError, DomainError, ValueError) as exc:
            print(f"Error: {exc}")
        return True

    def _handle_new(self, args: list[str]) -> None:
        if len(args) != 1:
            print("Usage: new <easy|medium|hard>")
            return
        difficulty = GameDifficulty(args[0].upper())
        self._state = self._new_game_use_case.execute(difficulty=difficulty)
        self._print_state()

    def _handle_set(self, args: list[str]) -> None:
        row, col, value = self._parse_move_args(args=args, expect_value=True)
        self._state = self._set_cell_value_use_case.execute(
            game_id=self._require_game_id(), row_idx=row, column_idx=col, value=value
        )
        self._print_state()
        self._print_win_banner()

    def _handle_clear(self, args: list[str]) -> None:
        row, col, _ = self._parse_move_args(args=args, expect_value=False)
        self._state = self._set_cell_value_use_case.execute(
            game_id=self._require_game_id(), row_idx=row, column_idx=col, value=None
        )
        self._print_state()

    def _handle_hint(self, args: list[str]) -> None:
        row, col, _ = self._parse_move_args(args=args, expect_value=False)
        self._state = self._get_hint_use_case.execute(
            game_id=self._require_game_id(), row_idx=row, column_idx=col
        )
        self._print_state()
        self._print_win_banner()

    def _handle_restart(self) -> None:
        self._state = self._restart_game_use_case.execute(game_id=self._require_game_id())
        self._print_state()

    def _require_game_id(self) -> str:
        if self._state is None:
            raise ApplicationError("No active game. Start one with: new <easy|medium|hard>")
        return self._state.game_id

    @staticmethod
    def _parse_move_args(args: list[str], expect_value: bool) -> tuple[int, int, int | None]:
        expected_len = 3 if expect_value else 2
        if len(args) != expected_len:
            raise ValueError("row and column (1-9)" + (" and value (1-9)" if expect_value else "") + " are required")
        row_1_indexed, col_1_indexed = int(args[0]), int(args[1])
        value = int(args[2]) if expect_value else None
        return row_1_indexed - 1, col_1_indexed - 1, value

    def _print_state(self) -> None:
        if self._state is not None:
            print(self._renderer.render(state=self._state))

    def _print_win_banner(self) -> None:
        if self._state is not None and self._state.status == GameStatus.WON:
            print("\U0001F389 Solved! Congratulations! \U0001F389")
