from asyncio import sleep
from collections import defaultdict
from random import shuffle

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

    def end_connection(self, sid: str) -> None:
        self.connections.pop(sid, None)

    def is_active_connection(self, sid: str) -> bool:
        return sid in self.connections

    async def update_session(self, sid, content: dict) -> None:
        current_session = await self.get_session(sid=sid)
        updated_session = {**current_session, **content}
        await self.save_session(sid=sid, session=updated_session)

    async def update_answered(self, sid: str, current_question: int) -> None:
        current_session = await self.get_session(sid=sid)
        current_answered = current_session["answered"]
        answered = current_answered[sid]
        answered[current_question] = True
        updated_answered = {**current_answered, sid: answered}
        updated_session = {**current_session, "answered": updated_answered}
        await self.save_session(sid=sid, session=updated_session)

    async def update_points(self, sid: str, points: int) -> None:
        current_session = await self.get_session(sid=sid)
        current_points = current_session["points"]
        updated_points = {**current_points, sid: current_points[sid] + points}
        updated_session = {**current_session, "points": updated_points}
        await self.save_session(sid=sid, session=updated_session)

    def parse_url(self, url: str, options: dict) -> str:
        _url = url + "?"
        for key, value in options.items():
            if value is not None:
                if isinstance(value, list):
                    _url += key + "=" + ",".join(value)
                else:
                    _url += key + "=" + str(value)
                _url += "&"

        return _url[:-1]

    async def get_questions(self, sid: str, options: dict) -> None:
        url = settings.server.quiz_api + "/questions"
        exclude_keys = ["max_players", "with_friends", "name"]
        options_without_exclude_keys = {
            k: options[k]
            for k in set(list(options.keys())) - set(exclude_keys)
        }
        result = get(self.parse_url(url, options_without_exclude_keys))
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

    async def send_results(self, sid: str) -> None:
        session = await self.get_session(sid=sid)
        points = session["points"]
        names = session["names"]
        await self.emit("results", {names[k]: points[k] for k in names})

    async def send_questions(self, sid: str) -> None:
        session_data = await self.get_session(sid)
        questions = session_data["questions"]
        for index, q in enumerate(questions):
            if self.is_active_connection(sid):
                q = questions[index]
                shuffle(q["answers"])
                question = {"question": q["question"], "answers": q["answers"]}
                print(await self.get_session(sid))
                await self.emit("question", question, room=sid)
                await self.update_session(
                    sid, content={"current_question": index}
                )
                await sleep(
                    12
                )  # 12 seconds for answer and 3 seconds for showing results
                await self.emit("answer", q["correct_answer"])
                await sleep(3)
            else:
                return
        await self.send_results(sid)

    async def on_connect(self, sid: str, environ: dict) -> None:
        pass

    async def on_join(self, sid: str, options) -> None:
        try:
            game_options = GameJoinModel(**options)  # validate input

            if game_options.max_players == 1:
                self.connections[sid] = {"number_of_players": 1}
                await self.get_questions(sid, game_options.dict())
                await self.update_session(
                    sid,
                    {
                        "points": {sid: 0},
                        "current_question": 0,
                        "names": {sid: game_options.name},
                        "answered": {
                            sid: [False] * game_options.limit  # type: ignore
                        },
                    },
                )
                await self.send_questions(sid)
                await self.disconnect(sid)
            else:  # online game
                pass

        except ValidationError:
            await self.emit("error", "Invalid input", room=sid)
            await self.disconnect(sid)

    async def on_answer(self, sid: str, data: dict) -> None:
        if self.is_active_connection(sid):
            try:
                answer_data = GameAnswerModel(**data)

                session_data = await self.get_session(sid)
                current_question = session_data["current_question"]
                correct_answer = session_data["questions"][current_question][
                    "correct_answer"
                ]
                answered = session_data["answered"][sid][current_question]

                if not answered:
                    print("ANSWER => ", answer_data.answer, correct_answer)
                    if answer_data.answer == correct_answer:
                        await self.update_points(
                            sid, 1
                        )  # time function go here
                    await self.emit("answer", correct_answer)
                    await self.update_answered(sid, current_question)

            except ValidationError:
                await self.emit("error", "Invalid input", room=sid)
                await self.disconnect(sid)

    async def on_end(self, sid: str) -> None:
        self.end_connection(sid)

    def on_disconnect(self, sid: str) -> None:
        self.end_connection(sid)
        print("disconnect")
