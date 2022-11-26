import pytest
import socketio
import asyncio


@pytest.mark.asyncio
async def test_game_solo_join_error(server):
    """Server should capture invalid input data and end connection"""
    await server.up()

    sio = socketio.AsyncClient()
    future = asyncio.get_running_loop().create_future()

    @sio.on("error")
    def on_error(data):
        future.set_result(data)

    await sio.connect("http://127.0.0.1:8080", socketio_path="/socket.io/")

    quiz_options = {}

    await sio.emit("join", quiz_options)
    await asyncio.wait_for(future, timeout=1.0)
    await sio.disconnect()
    assert future.result() == "Invalid input"
    await server.down()


@pytest.mark.asyncio
async def test_game_solo_connection_error(server, settings, mock_request):
    """Server should end connection due to inaccessible external API"""
    mock_request.get(
        url=f"{settings.server.quiz_api}/questions",
        json={},
        status_code=500,
    )

    await server.up()

    sio = socketio.AsyncClient()
    future = asyncio.get_running_loop().create_future()

    @sio.on("error")
    def on_error(data):
        future.set_result(data)

    await sio.connect("http://127.0.0.1:8080", socketio_path="/socket.io/")

    quiz_options = {
        "name": "me",
        "max_players": 1,
        "categories": "arts_and_literature",
        "limit": 5,
        "difficulty": "medium",
        "tags": ["young_adult", "wine"],
    }

    await sio.emit("join", quiz_options)
    await asyncio.wait_for(future, timeout=1.0)
    await sio.disconnect()
    assert future.result() == "Connection error"
    await server.down()

@pytest.mark.asyncio
async def test_game_solo_answer_error(server, settings, mock_request):
    """Server should capture invalid input data and end connection"""
    questions = [
        {
            "question": "question 1",
            "correctAnswer": "A",
            "incorrectAnswers": ["B", "C", "D"],
        }
    ]
    mock_request.get(
        url=f"{settings.server.quiz_api}/questions",
        json=questions,
        status_code=200,
    )

    await server.up()

    sio = socketio.AsyncClient()
    future = asyncio.get_running_loop().create_future()
    future_error = asyncio.get_running_loop().create_future()

    
    @sio.on("question")
    def on_question(data):
        future.set_result(data)

    @sio.on("error")
    def on_error(data):
        future_error.set_result(data)

    await sio.connect("http://127.0.0.1:8080", socketio_path="/socket.io/")

    quiz_options = {
        "name": "me",
        "max_players": 1,
        "categories": "arts_and_literature",
        "limit": 1,
        "difficulty": "medium",
        "tags": ["young_adult", "wine"],
    }

    await sio.emit("join", quiz_options)
    await asyncio.wait_for(future, timeout=20.0)
    results = future.result()
    assert results["question"] == questions[0]["question"]
    assert results["answers"] == ["A", "B", "C", "D"]
    await sio.emit("answer", {})
    await asyncio.wait_for(future_error, timeout=1.0)
    assert future_error.result() == "Invalid input"
    await sio.disconnect()
    await server.down()

@pytest.mark.asyncio
async def test_game_solo(server, settings, mock_request):
    """Server should connect user and start sending questions"""
    questions = [
        {
            "question": "question 1",
            "correctAnswer": "A",
            "incorrectAnswers": ["B", "C", "D"],
        },
        {
            "question": "question 2",
            "correctAnswer": "D",
            "incorrectAnswers": ["A", "B", "C"],
        }
    ]
    mock_request.get(
        url=f"{settings.server.quiz_api}/questions",
        json=questions,
        status_code=200,
    )
    await server.up()

    sio = socketio.AsyncClient()
    futures = [asyncio.get_running_loop().create_future() for i in range(0, 2)]

    @sio.on("question")
    def on_question(data):
        print("on_question ==> ", data)
        for i, f in enumerate(futures):
            if not f.done():
                print("done", i)
                f.set_result(data)
                break

    result_future = asyncio.get_running_loop().create_future()

    @sio.on("results")
    def on_results(data):
        result_future.set_result(data)

    await sio.connect("http://127.0.0.1:8080", socketio_path="/socket.io/")

    quiz_options = {
        "name": "me",
        "max_players": 1,
        "categories": "arts_and_literature",
        "limit": 5,
        "difficulty": "medium",
        "tags": ["young_adult", "wine"],
    }

    await sio.emit("join", quiz_options)
    for i, q in enumerate(questions):
        await asyncio.wait_for(futures[i], timeout=20.0)
        results = futures[i].result()
        print(q, results, " === ")
        assert results["question"] == q["question"]
        assert sorted(results["answers"]) == ["A", "B", "C", "D"]
        await sio.emit("answer", {"answer": "A", "time": 0})
    await asyncio.wait_for(result_future, timeout=20.0)
    assert result_future.result() == {"me": 1}
    await sio.disconnect()
    await server.down()
