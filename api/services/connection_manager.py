from asyncio import sleep
from collections import defaultdict

from pydantic import ValidationError
from requests import get
from socketio import AsyncNamespace

from ..config import settings
from ..schemas.quizzes import GameAnswerModel, GameJoinModel


class ConnectionManager(AsyncNamespace):
    """
    Manages chat room sessions and members along with message routing
    """

    def __init__(self, *args, **kwargs):
        super(ConnectionManager, self).__init__(*args, **kwargs)
        self.connections: dict = defaultdict(dict)

    async def update_session(self, sid, content: dict):
        current_session = await self.get_session(sid=sid)
        updated_session = {**current_session, **content}
        await self.save_session(sid=sid, session=updated_session)

    async def update_points(self, sid: str, points: int):
        current_session = await self.get_session(sid=sid)
        current_points = current_session["points"]
        updated_points = {**current_points, sid: current_points[sid] + points}
        updated_session = {**current_session, "points": updated_points}
        await self.save_session(sid=sid, session=updated_session)

    def parseUrl(self, url: str, options: dict) -> str:
        _url = url + "?"
        for key, value in options.items():
            if value is not None:
                if isinstance(value, list):
                    _url += key + "=" + ",".join(value)
                else:
                    _url += key + "=" + str(value)
                _url += "&"

        return _url[:-1]

    async def get_questions(self, sid: str, options: dict):
        url = settings.server.quiz_api + "/questions"
        exclude_keys = ["max_players", "with_friends", "name"]
        options_without_exclude_keys = {
            k: options[k]
            for k in set(list(options.keys())) - set(exclude_keys)
        }
        result = get(self.parseUrl(url, options_without_exclude_keys))
        if result.status_code == 200:
            questions = [
                {
                    "question": q["question"],
                    "correct_answer": q["correctAnswer"],
                    "answers": [q["correctAnswer"]] + q["incorrectAnswers"],
                }
                for q in result.json()
            ]
            await self.update_session(sid, content={"questions": questions})
        else:
            await self.emit("error", "Connection error", room=sid)
            await self.disconnect(sid)

    async def send_results(self, sid: str):
        session = await self.get_session(sid=sid)
        points = session["points"]
        names = session["names"]
        await self.emit("results", {names[k]: points[k] for k in names})

    async def send_questions(self, sid: str):
        session_data = await self.get_session(sid)
        questions = session_data["questions"]
        for index, q in enumerate(questions):
            q = questions[index]
            question = {"question": q["question"], "answers": q["answers"]}
            print(await self.get_session(sid))
            await self.emit("question", question, room=sid)
            await self.update_session(sid, content={"current_question": index})
            await sleep(
                18
            )  # 15 seconds for answer and 3 seconds for showing results
        await self.send_results(sid)

    async def on_connect(self, sid: str, environ: dict):
        pass

    async def on_join(self, sid: str, options):
        try:
            GameJoinModel(**options)  # validate input
        except ValidationError:
            await self.emit("error", "Invalid input", room=sid)
            await self.disconnect(sid)

        if options["max_players"] == 1:
            await self.get_questions(sid, options)
            await self.update_session(
                sid,
                {
                    "points": {sid: 0},
                    "current_question": 0,
                    "names": {sid: options["name"]},
                },
            )
            await self.send_questions(sid)
            await self.disconnect(sid)
        else:  # online game
            pass

    async def on_answer(self, sid: str, data: dict):
        try:
            GameAnswerModel(**data)
        except ValidationError:
            await self.emit("error", "Invalid input", room=sid)
            await self.disconnect(sid)

        session_data = await self.get_session(sid)
        current_question = session_data["current_question"]
        correct_answer = session_data["questions"][current_question][
            "correct_answer"
        ]
        print("ANSWER => ", data["answer"], correct_answer)
        if data["answer"] == correct_answer:
            await self.update_points(sid, 1)  # time function go here
        await self.emit("answer", correct_answer)

    def on_disconnect(self, sid: str):
        print("disconnect")
