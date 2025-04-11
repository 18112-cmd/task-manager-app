from google.cloud import firestore
from datetime import datetime

# ---------------------- GROUP 1 ----------------------

def get_user_boards(db, uid):
    boards = []
    boards_ref = db.collection("taskboards")
    query = boards_ref.where("members", "array_contains", uid)
    for doc in query.stream():
        data = doc.to_dict()
        data["id"] = doc.id
        boards.append(data)
    return boards

def create_board(db, uid, name):
    board_ref = db.collection("taskboards").document()
    board_ref.set({
        "name": name,
        "creator": uid,
        "members": [uid],
        "created_at": firestore.SERVER_TIMESTAMP
    })

def get_board(db, board_id):
    board = db.collection("taskboards").document(board_id).get()
    if board.exists:
        data = board.to_dict()
        data["id"] = board.id
        return data
    return {}

def get_board_tasks(db, board_id):
    task_ref = db.collection("taskboards").document(board_id).collection("tasks")
    tasks = []
    for doc in task_ref.stream():
        data = doc.to_dict()
        data["id"] = doc.id
        tasks.append(data)
    return tasks

# ---------------------- GROUP 2 ----------------------

def add_user_to_board_service(db, board_id, requester_uid, new_user_uid):
    board_ref = db.collection("taskboards").document(board_id)
    board = board_ref.get().to_dict()

    if board["creator"] != requester_uid:
        return False

    if new_user_uid not in board["members"]:
        board["members"].append(new_user_uid)
        board_ref.update({"members": board["members"]})
    return True

def add_task(db, board_id, title, due_date, assigned_to=None, created_by=None):
    task = {
        "title": title,
        "due_date": due_date,
        "assigned_to": assigned_to,
        "created_by": created_by,
        "completed": False,
        "created_at": firestore.SERVER_TIMESTAMP,
        "unassigned": False
    }
    db.collection("taskboards").document(board_id).collection("tasks").add(task)

def mark_task_complete(db, board_id, task_id):
    task_ref = db.collection("taskboards").document(board_id).collection("tasks").document(task_id)
    task_ref.update({
        "completed": True,
        "completed_at": datetime.utcnow()
    })

# ---------------------- GROUP 3 ----------------------

def edit_task(db, board_id, task_id, updates):
    db.collection("taskboards").document(board_id).collection("tasks").document(task_id).update(updates)

def delete_task(db, board_id, task_id):
    db.collection("taskboards").document(board_id).collection("tasks").document(task_id).delete()

def rename_board(db, board_id, new_name):
    db.collection("taskboards").document(board_id).update({"name": new_name})

def remove_user_from_board(db, board_id, user_id):
    board_ref = db.collection("taskboards").document(board_id)
    board = board_ref.get().to_dict()

    if user_id in board["members"]:
        updated_members = [uid for uid in board["members"] if uid != user_id]
        board_ref.update({"members": updated_members})

        task_ref = board_ref.collection("tasks")
        for doc in task_ref.stream():
            task = doc.to_dict()
            if task.get("assigned_to") == user_id:
                doc.reference.update({
                    "assigned_to": None,
                    "unassigned": True
                })

# ---------------------- GROUP 4 ----------------------

def delete_board(db, board_id):
    board_ref = db.collection("taskboards").document(board_id)
    board_ref.delete()
