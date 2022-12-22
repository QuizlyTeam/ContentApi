from asyncio import TimeoutError, sleep, wait_for
from collections import defaultdict
from random import shuffle
from typing import List
from uuid import uuid4

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

    def get_rooms(self, sid: str) -> List[str]:
        return list(filter(lambda x: x != sid, self.rooms(sid)))

    def end_connection(self, sid: str) -> None:
        if len(self.rooms(sid)) > 1:
            room = self.get_rooms(sid)[0]
            if len(self.connections[room]["current_players"]) > 0:
                self.connections[room]["current_players"].remove(sid)
            if len(self.connections[room]["current_players"]) <= 0:
                self.connections.pop(room, None)
        else:
            self.connections.pop(sid, None)

    def is_active_connection(self, sid: str) -> bool:
        return sid in self.connections

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
            self.connections[sid]["questions"] = questions
        else:
            await self.emit("error", "Connection error", room=sid)
            await self.disconnect(sid)

    async def send_results(self, sid: str) -> None:
        session = self.connections[sid]
        points = session["points"]
        names = session["names"]
        await self.emit("results", {names[k]: points[k] for k in names})

    async def send_questions(self, sid: str) -> None:
        if not self.is_active_connection(sid):
            return
        session_data = self.connections[sid]
        questions = session_data["questions"]
        for index, q in enumerate(questions):
            if self.is_active_connection(sid):
                q = questions[index]
                shuffle(q["answers"])
                question = {"question": q["question"], "answers": q["answers"]}
                print(self.connections[sid])
                await self.emit("question", question, room=sid)
                self.connections[sid]["current_question"] = index
                await sleep(
                    12
                )  # 12 seconds for answer and 3 seconds for showing results
                await self.emit("answer", q["correct_answer"], room=sid)
                await sleep(3)
            else:
                return
        await self.send_results(sid)

    async def wait_for_players(self, sid: str) -> None:
        async def periodic():
            while True:
                if not self.is_active_connection(sid):
                    return
                elif (
                    len(self.connections[sid]["current_players"])
                    == self.connections[sid]["game_options"]["max_players"]
                ):  # noqa
                    return
                await sleep(1)

        try:
            await wait_for(periodic(), timeout=30)
        except TimeoutError:
            print("No more users connect")

    async def on_connect(self, sid: str, environ: dict) -> None:
        pass

    async def on_join(self, sid: str, options) -> None:
        try:
            game_options = GameJoinModel(**options)  # validate input

            if game_options.max_players == 1:
                self.connections[sid] = {
                    "current_players": [sid],
                    "points": {sid: 0},
                    "current_question": 0,
                    "names": {sid: game_options.name},
                    "answered": {
                        sid: [False] * game_options.limit  # type: ignore
                    },
                }
                await self.get_questions(sid, game_options.dict())
                await self.send_questions(sid)
                await self.disconnect(sid)
            else:  # online game
                if len(self.connections.keys()) > 0:
                    game_options_withou_name = game_options.dict().copy()
                    game_options_withou_name.pop("name")
                    for room, connection in self.connections.items():
                        if "game_options" in connection:
                            connection_game_options_withou_name = connection[
                                "game_options"
                            ].copy()  # noqa
                            connection_game_options_withou_name.pop("name")
                            if (
                                connection_game_options_withou_name
                                == game_options_withou_name
                            ):  # noqa
                                print("it is", room)
                                self.enter_room(sid, room)
                                self.connections[room]["names"][
                                    sid
                                ] = game_options.name  # noqa
                                await self.emit("join", room, to=sid)
                                return

                # if no connections found, create one
                room = str(uuid4())
                self.enter_room(sid, room)
                self.connections[room] = {
                    "current_players": [],
                    "points": {},
                    "current_question": 0,
                    "names": {sid: game_options.name},
                    "answered": {},
                    "game_options": game_options.dict(),
                }
                await self.get_questions(sid=room, options=game_options.dict())
                await self.emit("join", room, to=sid)
                await self.wait_for_players(sid=room)
                if len(self.connections[room]["current_players"]) > 0:
                    await self.send_questions(sid=room)
                if self.is_active_connection(room):
                    for s in self.connections[room]["current_players"]:
                        await self.disconnect(s)
                await self.close_room(room)
                self.end_connection(room)

        except ValidationError:
            await self.emit("error", "Invalid input", room=sid)
            await self.disconnect(sid)

    async def on_ready(self, sid: str) -> None:
        room = self.get_rooms(sid)[0]
        if sid not in self.connections[room]["current_players"]:
            self.connections[room]["points"][sid] = 0
            self.connections[room]["answered"][sid] = [
                False
            ] * self.connections[room]["game_options"][
                "limit"
            ]  # noqa
            self.connections[room]["current_players"].append(sid)

    async def on_answer(self, sid: str, data: dict) -> None:
        room = sid if len(self.get_rooms(sid)) == 0 else self.get_rooms(sid)[0]
        if self.is_active_connection(room):
            try:
                answer_data = GameAnswerModel(**data)

                session_data = self.connections[room]
                current_question = session_data["current_question"]
                correct_answer = session_data["questions"][current_question][
                    "correct_answer"
                ]
                answered = session_data["answered"][sid][current_question]

                if not answered:
                    print("ANSWER => ", answer_data.answer, correct_answer)
                    if answer_data.answer == correct_answer:
                        self.connections[room]["points"][
                            sid
                        ] += 1  # time function go here
                    await self.emit("answer", correct_answer, sid)
                    self.connections[room]["answered"][sid][
                        current_question
                    ] = True

            except ValidationError:
                await self.emit("error", "Invalid input", sid)
                await self.disconnect(sid)

    async def on_end(self, sid: str) -> None:
        self.end_connection(sid)

    def on_disconnect(self, sid: str) -> None:
        self.end_connection(sid)
        print("disconnect")
