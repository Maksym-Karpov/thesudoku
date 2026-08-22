"""FastAPI presentation adapter: a minimal server-rendered HTML UI.

Talks exclusively to application-layer use cases and DTOs (never to domain
entities directly), the same way the CLI adapter does -- this is just an
alternative delivery mechanism for the same business logic. No database is
used: game state lives in the same in-memory repository used by the CLI.
"""

from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from app.application.exceptions import ApplicationError
from app.dependencies import Dependencies, dependencies_facade
from app.domain.exceptions import DomainError, GameNotFoundError
from app.domain.value_objects.game_difficulty import GameDifficulty

_TEMPLATES_DIR = __file__.rsplit("/", 1)[0] + "/templates"
templates = Jinja2Templates(directory=_TEMPLATES_DIR)

_deps: Dependencies = dependencies_facade()

app = FastAPI(title="Sudoku")


@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")


@app.post("/new")
def new_game(difficulty: str = Form(...)):
    state = _deps.new_game_use_case.execute(difficulty=GameDifficulty(difficulty.upper()))
    return RedirectResponse(url=f"/game/{state.game_id}", status_code=303)


@app.get("/game/{game_id}", response_class=HTMLResponse)
def show_game(request: Request, game_id: str):
    try:
        state = _deps.get_game_state_use_case.execute(game_id=game_id)
    except GameNotFoundError:
        return RedirectResponse(url="/", status_code=303)
    return templates.TemplateResponse(request=request, name="game.html", context={"state": state, "errors": []})


@app.post("/game/{game_id}/update", response_class=HTMLResponse)
async def update_game(request: Request, game_id: str):
    form = await request.form()
    errors: list[str] = []

    try:
        state = _deps.get_game_state_use_case.execute(game_id=game_id)
    except GameNotFoundError:
        return RedirectResponse(url="/", status_code=303)

    for row in range(9):
        for col in range(9):
            if state.fixed_mask[row][col]:
                continue
            raw = str(form.get(f"cell_{row}_{col}", "")).strip()
            value = int(raw) if raw.isdigit() and raw != "0" else None
            try:
                state = _deps.set_cell_value_use_case.execute(
                    game_id=game_id, row_idx=row, column_idx=col, value=value
                )
            except (ApplicationError, DomainError, ValueError) as exc:
                errors.append(f"Cell ({row + 1}, {col + 1}): {exc}")
                state = _deps.get_game_state_use_case.execute(game_id=game_id)

    return templates.TemplateResponse(
        request=request, name="game.html", context={"state": state, "errors": errors}
    )


@app.post("/game/{game_id}/hint", response_class=HTMLResponse)
def get_hint(request: Request, game_id: str, row: int = Form(...), col: int = Form(...)):
    errors: list[str] = []
    try:
        state = _deps.get_hint_use_case.execute(game_id=game_id, row_idx=row - 1, column_idx=col - 1)
    except (ApplicationError, DomainError, ValueError) as exc:
        errors.append(str(exc))
        state = _deps.get_game_state_use_case.execute(game_id=game_id)
    return templates.TemplateResponse(
        request=request, name="game.html", context={"state": state, "errors": errors}
    )


@app.post("/game/{game_id}/restart", response_class=HTMLResponse)
def restart(request: Request, game_id: str):
    state = _deps.restart_game_use_case.execute(game_id=game_id)
    return templates.TemplateResponse(
        request=request, name="game.html", context={"state": state, "errors": []}
    )
