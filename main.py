from fastapi import FastAPI, Request, Form
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from google.cloud import firestore
from auth_service import validate_firebase_token
from firestore_service import (
    get_user_boards, create_board, get_board, get_board_tasks,
    add_user_to_board_service, add_task, mark_task_complete,
    edit_task, delete_task, rename_board, remove_user_from_board,
    delete_board
)
from auth_service import validate_firebase_token, db

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# --------------------- HOME ---------------------
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    id_token = request.cookies.get("token")
    user_token = await validate_firebase_token(id_token)
    if not user_token:
        return templates.TemplateResponse("login.html", {"request": request, "user_token": None})
    
    uid = user_token["user_id"]
    boards = get_user_boards(db, uid)
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "user_token": user_token,
        "boards": boards
    })

# --------------------- BOARD VIEW ---------------------
@app.get("/board/{board_id}", response_class=HTMLResponse)
async def view_board(request: Request, board_id: str):
    id_token = request.cookies.get("token")
    user_token = await validate_firebase_token(id_token)
    if not user_token:
        return RedirectResponse("/", status_code=302)

    board = get_board(db, board_id)
    tasks = get_board_tasks(db, board_id)
    return templates.TemplateResponse("board.html", {
        "request": request,
        "user_token": user_token,
        "board": board,
        "tasks": tasks
    })

# --------------------- CREATE BOARD ---------------------
@app.post("/create-board")
async def create_board_post(request: Request, board_name: str = Form(...)):
    id_token = request.cookies.get("token")
    user_token = await validate_firebase_token(id_token)
    if not user_token:
        return RedirectResponse("/", status_code=302)

    create_board(db, user_token["user_id"], board_name)
    return RedirectResponse("/", status_code=302)

# --------------------- ADD USER TO BOARD ---------------------
@app.post("/board/{board_id}/add-user")
async def add_user_to_board(request: Request, board_id: str, user_uid: str = Form(...)):
    id_token = request.cookies.get("token")
    user_token = await validate_firebase_token(id_token)
    if not user_token:
        return RedirectResponse("/", status_code=302)

    add_user_to_board_service(db, board_id, user_token["user_id"], user_uid)
    return RedirectResponse(f"/board/{board_id}", status_code=302)

# --------------------- ADD TASK ---------------------
@app.post("/add-task/{board_id}")
async def add_task_post(request: Request, board_id: str,
                        title: str = Form(...), due_date: str = Form(...),
                        assigned_to: str = Form("")):
    id_token = request.cookies.get("token")
    user_token = await validate_firebase_token(id_token)
    if not user_token:
        return RedirectResponse("/", status_code=302)

    add_task(db, board_id, title, due_date, assigned_to or None, user_token["user_id"])
    return RedirectResponse(f"/board/{board_id}", status_code=302)

# --------------------- MARK TASK COMPLETE ---------------------
@app.post("/complete-task/{board_id}/{task_id}")
async def complete_task(request: Request, board_id: str, task_id: str):
    id_token = request.cookies.get("token")
    user_token = await validate_firebase_token(id_token)
    if not user_token:
        return RedirectResponse("/", status_code=302)

    mark_task_complete(db, board_id, task_id)
    return RedirectResponse(f"/board/{board_id}", status_code=302)

# --------------------- EDIT TASK ---------------------
@app.post("/board/{board_id}/edit-task/{task_id}")
async def edit_task_route(request: Request, board_id: str, task_id: str,
                          title: str = Form(...), due_date: str = Form(...),
                          assigned_to: str = Form("")):
    id_token = request.cookies.get("token")
    user_token = await validate_firebase_token(id_token)
    if not user_token:
        return RedirectResponse("/", status_code=302)

    updates = {
        "title": title,
        "due_date": due_date,
        "assigned_to": assigned_to or None,
        "unassigned": False
    }
    edit_task(db, board_id, task_id, updates)
    return RedirectResponse(f"/board/{board_id}", status_code=302)

# --------------------- DELETE TASK ---------------------
@app.post("/board/{board_id}/delete-task/{task_id}")
async def delete_task_route(request: Request, board_id: str, task_id: str):
    id_token = request.cookies.get("token")
    user_token = await validate_firebase_token(id_token)
    if not user_token:
        return RedirectResponse("/", status_code=302)

    delete_task(db, board_id, task_id)
    return RedirectResponse(f"/board/{board_id}", status_code=302)

# --------------------- RENAME BOARD ---------------------
@app.post("/board/{board_id}/rename")
async def rename_board_route(request: Request, board_id: str, new_name: str = Form(...)):
    id_token = request.cookies.get("token")
    user_token = await validate_firebase_token(id_token)
    if not user_token:
        return RedirectResponse("/", status_code=302)

    board = get_board(db, board_id)
    if board["creator"] == user_token["user_id"]:
        rename_board(db, board_id, new_name)
    return RedirectResponse(f"/board/{board_id}", status_code=302)

# --------------------- REMOVE USER FROM BOARD ---------------------
@app.post("/board/{board_id}/remove-user")
async def remove_user_route(request: Request, board_id: str, user_uid: str = Form(...)):
    id_token = request.cookies.get("token")
    user_token = await validate_firebase_token(id_token)
    if not user_token:
        return RedirectResponse("/", status_code=302)

    board = get_board(db, board_id)
    if board["creator"] == user_token["user_id"]:
        remove_user_from_board(db, board_id, user_uid)
    return RedirectResponse(f"/board/{board_id}", status_code=302)

# --------------------- DELETE BOARD ---------------------
@app.post("/board/{board_id}/delete")
async def delete_board_route(request: Request, board_id: str):
    id_token = request.cookies.get("token")
    user_token = await validate_firebase_token(id_token)
    if not user_token:
        return RedirectResponse("/", status_code=302)

    board = get_board(db, board_id)
    if board["creator"] != user_token["user_id"]:
        return RedirectResponse("/", status_code=302)

    if len(board.get("members", [])) > 1:
        return RedirectResponse(f"/board/{board_id}", status_code=302)

    tasks = get_board_tasks(db, board_id)
    if len(tasks) > 0:
        return RedirectResponse(f"/board/{board_id}", status_code=302)

    delete_board(db, board_id)
    return RedirectResponse("/", status_code=302)
