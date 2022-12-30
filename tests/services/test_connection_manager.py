import pytest
import socketio
import asyncio
from collections import OrderedDict


class MockDB:
    def __init__(self):
        pass

    def order_by_child(self, arg):
        return self

    def equal_to(self, arg):
        return self

    def limit_to_first(self, arg):
        return self

    def get(self):
        return None

    def child(self, arg):
        return self

    def set(self, arg):
        pass


@pytest.mark.asyncio
async def test_game_solo_join_error(mocker, server):
    """Server should capture invalid input data and end connection"""
    mocker.patch("firebase_admin.db.reference", return_value=MockDB())
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
async def test_game_solo_connection_error(
    mocker, server, settings, mock_request
):
    """Server should end connection due to inaccessible external API"""
    mocker.patch("firebase_admin.db.reference", return_value=MockDB())
    mock_request.get(
        url=f"{settings.server.quiz_api}/questions", json={}, status_code=500
    )

    await server.up()

    sio = socketio.AsyncClient()
    future = asyncio.get_running_loop().create_future()

    @sio.on("error")
    def on_error(data):
        future.set_result(data)

    await sio.connect("http://127.0.0.1:8080", socketio_path="/socket.io/")

    quiz_options = {
        "nickname": "me1",
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
async def test_game_solo_answer_error(mocker, server, settings, mock_request):
    """Server should capture invalid input data and end connection"""
    mocker.patch("firebase_admin.db.reference", return_value=MockDB())
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
        "nickname": "me1",
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
    assert sorted(results["answers"]) == ["A", "B", "C", "D"]
    await sio.emit("answer", {})
    await asyncio.wait_for(future_error, timeout=1.0)
    assert future_error.result() == "Invalid input"
    await sio.disconnect()
    await server.down()


@pytest.mark.asyncio
async def test_game_solo(mocker, server, settings, mock_request):
    """Server should connect user and start sending questions"""
    mocker.patch("firebase_admin.db.reference", return_value=MockDB())
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
        },
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
        "nickname": "me1",
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
    assert result_future.result() == {"me1": 500}
    await sio.disconnect()
    await server.down()


@pytest.mark.asyncio
async def test_game_solo_own_quiz(mocker, server):
    """Server should connect user and start sending questions from user's quiz"""
    questions = [
        {
            "question": "question 1",
            "correct_answer": "A",
            "incorrect_answers": ["B", "C", "D"],
        }
    ]

    class MockDB:
        def __init__(self):
            self.limit = False

        def order_by_child(self, arg):
            return self

        def equal_to(self, arg):
            return self

        def limit_to_first(self, arg):
            self.limit = True
            return self

        def get(self):
            if self.limit:
                self.limit = False
                return {}
            else:
                return OrderedDict(
                    [
                        (
                            "YYYYYYYYYYYYYYYYYYYY",
                            {
                                "category": "History",
                                "difficulty": "easy",
                                "questions": questions,
                                "tags": "1910's",
                                "title": "The father of the computer",
                                "uid": "XXXXXXXXXXXXXXXXXXXXXXXXXXXX",
                            },
                        )
                    ]
                )

        def child(self, arg):
            return self

        def set(self, arg):
            pass

    mocker.patch("firebase_admin.db.reference", return_value=MockDB())
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
        "nickname": "me1",
        "max_players": 1,
        "uid": "XXXXXXXXXXXXXXXXXXXXXXXXXXXX",
        "quiz_id": "YYYYYYYYYYYYYYYYYYYY",
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
    assert result_future.result() == {"me1": 500}
    await sio.disconnect()
    await server.down()


@pytest.mark.asyncio
async def test_game_multi(mocker, server, settings, mock_request):
    """Server should connect two users, one of them create game and second join found game"""
    mocker.patch("firebase_admin.db.reference", return_value=MockDB())
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

    sio1 = socketio.AsyncClient()
    sio2 = socketio.AsyncClient()
    futures1 = [
        asyncio.get_running_loop().create_future() for i in range(0, 2)
    ]
    futures2 = [
        asyncio.get_running_loop().create_future() for i in range(0, 2)
    ]

    @sio1.on("question")
    def on_question1(data):
        for i, f in enumerate(futures1):
            if not f.done():
                f.set_result(data)
                break

    @sio2.on("question")
    def on_question2(data):
        for i, f in enumerate(futures2):
            if not f.done():
                f.set_result(data)
                break

    result_future1 = asyncio.get_running_loop().create_future()
    result_future2 = asyncio.get_running_loop().create_future()

    @sio1.on("results")
    def on_results1(data):
        result_future1.set_result(data)

    @sio2.on("results")
    def on_results2(data):
        result_future2.set_result(data)

    await sio1.connect("http://127.0.0.1:8080", socketio_path="/socket.io/")
    await sio2.connect("http://127.0.0.1:8080", socketio_path="/socket.io/")

    quiz_options = {
        "nickname": "me1",
        "max_players": 2,
        "categories": "arts_and_literature",
        "limit": 5,
        "difficulty": "medium",
        "tags": ["young_adult", "wine"],
    }

    await sio1.emit("join", quiz_options)
    await sio2.emit("join", {**quiz_options, "nickname": "me2"})
    await sio1.emit("ready")
    await sio2.emit("ready")
    for i, q in enumerate(questions):
        await asyncio.wait_for(futures1[i], timeout=20.0)
        results1 = futures1[i].result()
        await asyncio.wait_for(futures2[i], timeout=20.0)
        results2 = futures2[i].result()
        assert results1["question"] == q["question"]
        assert results2["question"] == q["question"]
        assert sorted(results1["answers"]) == ["A", "B", "C", "D"]
        assert sorted(results2["answers"]) == ["A", "B", "C", "D"]
        await sio1.emit("answer", {"answer": "A", "time": 0})
        await sio2.emit("answer", {"answer": "B", "time": 0})
    await asyncio.wait_for(result_future1, timeout=20.0)
    assert result_future1.result() == {"me1": 500, "me2": 0}
    await asyncio.wait_for(result_future2, timeout=20.0)
    assert result_future2.result() == {"me1": 500, "me2": 0}
    await sio1.disconnect()
    await sio2.disconnect()
    await server.down()


@pytest.mark.asyncio
async def test_game_multi_code(mocker, server, settings, mock_request):
    """Server should connect two users, one of them create game and second join to room"""
    mocker.patch("firebase_admin.db.reference", return_value=MockDB())
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

    sio1 = socketio.AsyncClient()
    sio2 = socketio.AsyncClient()
    futures1 = [
        asyncio.get_running_loop().create_future() for i in range(0, 2)
    ]
    futures2 = [
        asyncio.get_running_loop().create_future() for i in range(0, 2)
    ]

    @sio1.on("question")
    def on_question1(data):
        for i, f in enumerate(futures1):
            if not f.done():
                f.set_result(data)
                break

    @sio2.on("question")
    def on_question2(data):
        for i, f in enumerate(futures2):
            if not f.done():
                f.set_result(data)
                break

    result_future1 = asyncio.get_running_loop().create_future()
    result_future2 = asyncio.get_running_loop().create_future()

    @sio1.on("results")
    def on_results1(data):
        result_future1.set_result(data)

    @sio2.on("results")
    def on_results2(data):
        result_future2.set_result(data)

    await sio1.connect("http://127.0.0.1:8080", socketio_path="/socket.io/")
    await sio2.connect("http://127.0.0.1:8080", socketio_path="/socket.io/")

    quiz_options = {
        "nickname": "me1",
        "max_players": 2,
        "categories": "arts_and_literature",
        "limit": 5,
        "difficulty": "medium",
        "tags": ["young_adult", "wine"],
    }

    join_future = asyncio.get_running_loop().create_future()

    @sio1.on("join")
    def on_join1(data):
        join_future.set_result(data)

    await sio1.emit("join", quiz_options)
    await asyncio.wait_for(join_future, timeout=5.0)
    await sio2.emit(
        "join", {"room": join_future.result()["room"], "nickname": "me2"}
    )
    await sio1.emit("ready")
    await sio2.emit("ready")
    for i, q in enumerate(questions):
        await asyncio.wait_for(futures1[i], timeout=20.0)
        results1 = futures1[i].result()
        await asyncio.wait_for(futures2[i], timeout=20.0)
        results2 = futures2[i].result()
        assert results1["question"] == q["question"]
        assert results2["question"] == q["question"]
        assert sorted(results1["answers"]) == ["A", "B", "C", "D"]
        assert sorted(results2["answers"]) == ["A", "B", "C", "D"]
        await sio1.emit("answer", {"answer": "A", "time": 0})
        await sio2.emit("answer", {"answer": "B", "time": 0})
    await asyncio.wait_for(result_future1, timeout=20.0)
    assert result_future1.result() == {"me1": 500, "me2": 0}
    await asyncio.wait_for(result_future2, timeout=20.0)
    assert result_future2.result() == {"me1": 500, "me2": 0}
    await sio1.disconnect()
    await sio2.disconnect()
    await server.down()


@pytest.mark.asyncio
async def test_game_multi_code_own_quiz(mocker, server):
    """Server should connect two users, one of them create game with own quiz and second join to room"""
    questions = [
        {
            "question": "question 1",
            "correct_answer": "A",
            "incorrect_answers": ["B", "C", "D"],
        }
    ]

    class MockDB:
        def __init__(self):
            self.limit = False

        def order_by_child(self, arg):
            return self

        def equal_to(self, arg):
            return self

        def limit_to_first(self, arg):
            self.limit = True
            return self

        def get(self):
            if self.limit:
                self.limit = False
                return {}
            else:
                return OrderedDict(
                    [
                        (
                            "YYYYYYYYYYYYYYYYYYYY",
                            {
                                "category": "History",
                                "difficulty": "easy",
                                "questions": questions,
                                "tags": "1910's",
                                "title": "The father of the computer",
                                "uid": "XXXXXXXXXXXXXXXXXXXXXXXXXXXX",
                            },
                        )
                    ]
                )

        def child(self, arg):
            return self

        def set(self, arg):
            pass

    mocker.patch("firebase_admin.db.reference", return_value=MockDB())
    await server.up()

    sio1 = socketio.AsyncClient()
    sio2 = socketio.AsyncClient()
    futures1 = [
        asyncio.get_running_loop().create_future() for i in range(0, 2)
    ]
    futures2 = [
        asyncio.get_running_loop().create_future() for i in range(0, 2)
    ]

    @sio1.on("question")
    def on_question1(data):
        for i, f in enumerate(futures1):
            if not f.done():
                f.set_result(data)
                break

    @sio2.on("question")
    def on_question2(data):
        for i, f in enumerate(futures2):
            if not f.done():
                f.set_result(data)
                break

    result_future1 = asyncio.get_running_loop().create_future()
    result_future2 = asyncio.get_running_loop().create_future()

    @sio1.on("results")
    def on_results1(data):
        result_future1.set_result(data)

    @sio2.on("results")
    def on_results2(data):
        result_future2.set_result(data)

    await sio1.connect("http://127.0.0.1:8080", socketio_path="/socket.io/")
    await sio2.connect("http://127.0.0.1:8080", socketio_path="/socket.io/")

    quiz_options = {
        "nickname": "me1",
        "max_players": 2,
        "uid": "XXXXXXXXXXXXXXXXXXXXXXXXXXXX",
        "quiz_id": "YYYYYYYYYYYYYYYYYYYY",
    }

    join_future = asyncio.get_running_loop().create_future()

    @sio1.on("join")
    def on_join1(data):
        join_future.set_result(data)

    await sio1.emit("join", quiz_options)
    await asyncio.wait_for(join_future, timeout=5.0)
    await sio2.emit(
        "join",
        {
            "room": join_future.result()["room"],
            "nickname": "me2",
            "uid": "ZZZZZZZZZZZZZZZZZZZZZZZZZZZZ",
        },
    )
    await sio1.emit("ready")
    await sio2.emit("ready")
    for i, q in enumerate(questions):
        await asyncio.wait_for(futures1[i], timeout=20.0)
        results1 = futures1[i].result()
        await asyncio.wait_for(futures2[i], timeout=20.0)
        results2 = futures2[i].result()
        assert results1["question"] == q["question"]
        assert results2["question"] == q["question"]
        assert sorted(results1["answers"]) == ["A", "B", "C", "D"]
        assert sorted(results2["answers"]) == ["A", "B", "C", "D"]
        await sio1.emit("answer", {"answer": "A", "time": 0})
        await sio2.emit("answer", {"answer": "B", "time": 0})
    await asyncio.wait_for(result_future1, timeout=20.0)
    assert result_future1.result() == {"me1": 500, "me2": 0}
    await asyncio.wait_for(result_future2, timeout=20.0)
    assert result_future2.result() == {"me1": 500, "me2": 0}
    await sio1.disconnect()
    await sio2.disconnect()
    await server.down()
