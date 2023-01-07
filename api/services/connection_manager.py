from asyncio import TimeoutError, sleep, wait_for
from collections import defaultdict
from random import shuffle
from typing import List
from uuid import uuid4

from firebase_admin import db
from firebase_admin.exceptions import FirebaseError
from pydantic import ValidationError
from requests import get
from socketio import AsyncNamespace

from ..config import settings
from ..schemas.quizzes import GameAnswerModel, GameCodeJoinModel, GameJoinModel
from ..schemas.users import UserAccount
from ..utils.parse_url import parse_url
from ..utils.points import points_function


class ConnectionManager(AsyncNamespace):
    """
    Manages chat room sessions and members along with message routing
    """

    def __init__(self, *args, **kwargs):
        super(ConnectionManager, self).__init__(*args, **kwargs)
        self.connections: dict = defaultdict(dict)

    def get_rooms(self, sid: str) -> List[str]:
        """
        Given a session id, return a list of all the rooms.
        :param sid: - the session id
        :return: a list of all the rooms
        """
        return list(filter(lambda x: x != sid, self.rooms(sid)))

    def end_connection(self, sid: str) -> None:
        """
        When a player disconnects, remove them from the list of current players in the room.
        :param sid: - the session id of the player disconnecting
        """
        if len(self.rooms(sid)) > 1:
            room = self.get_rooms(sid)[0]
            if len(self.connections[room]["current_players"]) > 0:
                self.connections[room]["current_players"].remove(sid)
            if len(self.connections[room]["current_players"]) <= 0:
                self.connections.pop(room, None)
        else:
            self.connections.pop(sid, None)

    def is_active_connection(self, sid: str) -> bool:
        """
        Check if the session id is in the active connections dictionary.
        :param sid: - the session id
        :return: True if the session id is in the active connections dictionary, False otherwise.
        """
        return sid in self.connections

    async def get_questions_from_db(self, sid: str, options: dict) -> None:
        """
        Get the questions from the database for the quiz with the given id.
        :param sid: - the socket id of the client requesting the questions.
        :param options: - the options dictionary containing the quiz id.
        """
        try:
            ref = db.reference("Users")
            user_details = (
                ref.order_by_child("uid")
                .equal_to(options["uid"])
                .limit_to_first(1)
                .get()
            )
            if user_details is None:
                await self.emit("error", "User cannot be found", room=sid)
                await self.disconnect(sid)
            ref = db.reference("Quizzes")
            user_quizzes = (
                ref.order_by_child("uid").equal_to(options["uid"]).get()
            )
            print(user_quizzes)
            if options["quiz_id"] in user_quizzes:
                questions = [
                    {
                        "question": q["question"],
                        "correct_answer": q["correct_answer"],
                        "answers": [q["correct_answer"]]
                        + q["incorrect_answers"],
                    }
                    for q in user_quizzes[options["quiz_id"]]["questions"]
                ]
                print(questions)
                self.connections[sid]["questions"] = questions
            else:
                await self.emit(
                    "error",
                    f"Cannot find quiz with id {options['quiz_id']}",
                    room=sid,
                )
                await self.disconnect(sid)
        except FirebaseError:
            await self.emit("error", "Connection error", room=sid)
            await self.disconnect(sid)

    async def get_questions(self, sid: str, options: dict) -> None:
        """
        Get the questions from the server.
        :param sid: - the socket id of the client requesting questions.
        :param options: - the options for the game.
        """
        url = settings.server.quiz_api + "/questions"
        exclude_keys = ["max_players", "nickname", "game_options"]
        options_without_exclude_keys = {
            k: options[k]
            for k in set(list(options.keys())) - set(exclude_keys)
        }
        result = get(parse_url(url, options_without_exclude_keys))
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
        """
        Send the results of the game to the database.
        :param sid: - the session id
        """
        session = self.connections[sid]
        points = session["points"]
        nicknames = session["nicknames"]
        await self.emit(
            "results", {nicknames[k]: points[k] for k in nicknames}
        )
        uids = session["uids"]
        ref = db.reference("Users")
        for (user, uid) in uids.items():
            if user in points:
                user_details = (
                    ref.order_by_child("uid")
                    .equal_to(uid)
                    .limit_to_first(1)
                    .get()
                )
                if user_details is not None:
                    (key, values) = next(iter(user_details.items()))
                    update = dict()
                    if len(points.keys()) > 1:
                        if (
                            points[user] == max(points.values())
                            and max(points.values()) > 0
                            and list(points.values()).count(
                                max(points.values())
                            )
                            == 1
                        ):
                            update["win"] = values["win"] + 1  # win
                        elif (
                            points[user] == max(points.values())
                            and max(points.values()) > 0
                            and list(points.values()).count(
                                max(points.values())
                            )
                            != 1
                        ):
                            pass  # draw
                        else:
                            update["lose"] = values["lose"] + 1  # lose
                    if points[user] > values["max_points"]:
                        update["max_points"] = points[user]
                    user_account = UserAccount(**{**values, **update})
                    ref.child(key).set(user_account.dict())

    async def send_questions(self, sid: str) -> None:
        """
        Send the questions, the correct answer and results to the client.
        :param sid: - the session id of the client.
        """
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
        """
        Wait for the players to connect before starting the game.
        :param sid: - the session id
        """

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
        """
        Handle joining players to games
        :param sid: - the session id
        :param options: - the options for the game
        """
        try:
            game_options = GameJoinModel(**options)  # validate input

            if game_options.max_players == 1:
                self.connections[sid] = {
                    "current_players": [sid],
                    "points": {sid: 0},
                    "current_question": 0,
                    "nicknames": {sid: game_options.nickname},
                    "uids": {},
                    "answered": {},
                }
                if game_options.uid is not None:
                    self.connections[sid]["uids"][sid] = game_options.uid
                if game_options.quiz_id is not None:
                    await self.get_questions_from_db(sid, game_options.dict())
                else:
                    await self.get_questions(sid, game_options.dict())
                self.connections[sid]["answered"][sid] = [False] * len(self.connections[sid]["questions"])  # type: ignore # noqa
                await self.send_questions(sid)
                await self.disconnect(sid)
            else:  # online game
                if len(self.connections.keys()) > 0:
                    game_options_withou_name = game_options.dict().copy()
                    game_options_withou_name.pop("nickname")
                    game_options_withou_name.pop("uid")
                    for room, connection in self.connections.items():
                        if "game_options" in connection:
                            connection_game_options_withou_name = connection[
                                "game_options"
                            ].copy()  # noqa
                            connection_game_options_withou_name.pop("nickname")
                            connection_game_options_withou_name.pop("uid")
                            if (
                                connection_game_options_withou_name
                                == game_options_withou_name
                            ):  # noqa
                                print("it is", room)
                                self.enter_room(sid, room)
                                self.connections[room]["nicknames"][
                                    sid
                                ] = game_options.nickname  # noqa
                                if game_options.uid is not None:
                                    self.connections[room]["uids"][
                                        sid
                                    ] = game_options.uid
                                await self.emit(
                                    "join",
                                    {
                                        "room": room,
                                        "number_of_players": len(
                                            self.connections[room][
                                                "current_players"
                                            ]
                                        ),
                                    },
                                    to=sid,
                                )
                                return

                # if no connections found, create one
                room = str(uuid4())
                self.enter_room(sid, room)
                self.connections[room] = {
                    "current_players": [],
                    "points": {},
                    "current_question": 0,
                    "nicknames": {sid: game_options.nickname},
                    "answered": {},
                    "uids": {},
                    "game_options": game_options.dict(),
                }
                if game_options.uid is not None:
                    self.connections[room]["uids"][sid] = game_options.uid
                if game_options.quiz_id is not None:
                    await self.get_questions_from_db(
                        sid=room, options=game_options.dict()
                    )
                else:
                    await self.get_questions(
                        sid=room, options=game_options.dict()
                    )
                await self.emit(
                    "join",
                    {
                        "room": room,
                        "number_of_players": len(
                            self.connections[room]["current_players"]
                        ),
                    },
                    to=sid,
                )
                await self.wait_for_players(sid=room)
                if (
                    "current_players" in self.connections[room]
                    and len(self.connections[room]["current_players"]) > 0
                ):
                    await self.send_questions(sid=room)
                if self.is_active_connection(room):
                    for s in self.connections[room]["current_players"]:
                        if s != sid:
                            await self.disconnect(s)
                await self.close_room(room)
                self.end_connection(room)
                await self.disconnect(sid)

        except ValidationError:
            try:
                game_code_options = GameCodeJoinModel(**options)
                if self.is_active_connection(game_code_options.room):
                    self.enter_room(sid, game_code_options.room)
                    self.connections[game_code_options.room]["nicknames"][
                        sid
                    ] = game_code_options.nickname  # noqa
                    self.connections[game_code_options.room]["uids"][
                        sid
                    ] = game_code_options.uid  # noqa
                    await self.emit(
                        "join",
                        {
                            "room": game_code_options.room,
                            "number_of_players": len(
                                self.connections[game_code_options.room][
                                    "current_players"
                                ]
                            ),
                        },
                        to=sid,
                    )
                else:
                    await self.emit("error", "No room found", to=sid)
                    await self.disconnect(sid)
            except ValidationError:
                await self.emit("error", "Invalid input", to=sid)
                await self.disconnect(sid)

    async def on_ready(self, sid: str) -> None:
        """
        This event is called when a player is ready.
        :param sid: - the session id
        """
        room = self.get_rooms(sid)[0]
        print(room, sid)
        if sid not in self.connections[room]["current_players"]:
            self.connections[room]["points"][sid] = 0
            self.connections[room]["answered"][sid] = [False] * len(self.connections[room]["questions"])  # type: ignore # noqa
            self.connections[room]["current_players"].append(sid)
            await self.emit(
                "join",
                {
                    "room": room,
                    "number_of_players": len(
                        self.connections[room]["current_players"]
                    ),
                },
                to=room,
            )

    async def on_answer(self, sid: str, data: dict) -> None:
        """
        When a user answers a question, this event is called. It will check if the answer is correct, and if so, it will award the user with points.
        :param sid: - the socket id of the user answering the question
        :param data: - the data sent by the user
        """
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
                        ] += points_function(
                            answer_data.time
                        )  # time function go here
                    await self.emit("answer", correct_answer, sid)
                    self.connections[room]["answered"][sid][
                        current_question
                    ] = True

            except ValidationError:
                await self.emit("error", "Invalid input", sid)
                await self.disconnect(sid)

    async def on_end(self, sid: str) -> None:
        """
        When a client end the game.
        :param sid: - the session id of the client ending game.
        """
        self.end_connection(sid)

    def on_disconnect(self, sid: str) -> None:
        """
        When a client disconnects, end the connection.
        :param sid: - the session id of the client disconnecting.
        """
        self.end_connection(sid)
        print("disconnect")
