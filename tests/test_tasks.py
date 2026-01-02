# tests/test_tasks.py
async def test_create_task(auth_client, db_session):
    # First create a group (since tasks need group_id)
    group = await auth_client.post("/groups/", json={"name": "Work"})
    group_id = group.json()["id"]

    # Now create the task
    resp = await auth_client.post("/tasks/", json={
        "title": "Test Task",
        "group_id": group_id
    })
    assert resp.status_code == 201
    assert resp.json()["user_id"] == auth_client.user.id