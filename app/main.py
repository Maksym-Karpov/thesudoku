"""Composition root: wires domain/application/infrastructure together and
starts the presentation-layer CLI. No business logic lives here."""

from app.dependencies import Dependencies, dependencies_facade
from app.presentation.cli.cli_app import SudokuCLI


def main() -> None:
    deps: Dependencies = dependencies_facade()

    cli = SudokuCLI(
        new_game_use_case=deps.new_game_use_case,
        set_cell_value_use_case=deps.set_cell_value_use_case,
        restart_game_use_case=deps.restart_game_use_case,
        get_hint_use_case=deps.get_hint_use_case,
    )
    cli.run()


if __name__ == "__main__":
    main()
