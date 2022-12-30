from collections import OrderedDict
from firebase_admin.exceptions import FirebaseError

################################################################################
##                                GET CATEGORIES                              ##
################################################################################


def test_get_categories(mock_request, settings, api_client):
    categories = {"Arts & Literature": 1, "Film & TV": 1}
    expected_result = {"categories": list(categories.keys())}
    mock_request.get(
        url=f"{settings.server.quiz_api}/categories",
        json=categories,
        status_code=200,
    )
    response = api_client.get("/v1/quizzes/categories")
    assert response.status_code == 200
    result = response.json()
    assert result == expected_result


################################################################################
##                                   GET TAGS                                 ##
################################################################################


def test_get_tags(mock_request, settings, api_client):
    tags = ["alcohol", "acting"]
    expected_result = {"tags": tags}
    mock_request.get(
        url=f"{settings.server.quiz_api}/tags",
        json=tags,
        status_code=200,
    )
    response = api_client.get("/v1/quizzes/tags")
    assert response.status_code == 200
    result = response.json()
    assert result == expected_result


################################################################################
##                               POST USER QUIZ                               ##
################################################################################


def test_post_user_quiz_success(mocker, api_client):
    mocker.patch(
        "firebase_admin.auth.verify_id_token",
        return_value={"uid": "XXXXXXXXXXXXXXXXXXXXXXXXXXXX"},
    )

    quiz = {
        "category": "History",
        "difficulty": "easy",
        "questions": [
            {
                "correct_answer": "in London in 1912",
                "incorrect_answers": [
                    "in Manchester in 1901",
                    "in Oxford in 1924",
                    "in Cambridge in 1935",
                ],
                "question": "Where and when was Alan Turing born?",
            },
            {
                "correct_answer": "a Turing Machine",
                "incorrect_answers": [
                    "the Bombe",
                    "Church's Computer",
                    "the Manchester Mach I",
                ],
                "question": "Turing, while solving the Decision Problem, proposed a hypothetical computing machine, which we now call ___",
            },
        ],
        "tags": "1910's",
        "title": "The father of the computer",
    }

    expected_result = {"uid": "XXXXXXXXXXXXXXXXXXXXXXXXXXXX", **quiz}

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
            return True

        def push(self):
            return self

        def set(self, arg):
            pass

    mocker.patch("firebase_admin.db.reference", return_value=MockDB())

    response = api_client.post(
        "/v1/quizzes/",
        headers={"Authorization": "Bearer firebaserusertokenid"},
        json={**quiz},
    )

    assert response.status_code == 201
    result = response.json()
    assert result == expected_result


def test_post_user_quiz_failure_unauthorized_no_credential(api_client):
    expected_result = {"detail": "Bearer authentication is needed"}

    response = api_client.post(
        "/v1/quizzes/",
        json={
            "category": "History",
            "difficulty": "easy",
            "questions": [
                {
                    "correct_answer": "in London in 1912",
                    "incorrect_answers": [
                        "in Manchester in 1901",
                        "in Oxford in 1924",
                        "in Cambridge in 1935",
                    ],
                    "question": "Where and when was Alan Turing born?",
                },
                {
                    "correct_answer": "a Turing Machine",
                    "incorrect_answers": [
                        "the Bombe",
                        "Church's Computer",
                        "the Manchester Mach I",
                    ],
                    "question": "Turing, while solving the Decision Problem, proposed a hypothetical computing machine, which we now call ___",
                },
            ],
            "tags": "1910's",
            "title": "The father of the computer",
        },
    )

    assert response.status_code == 401
    result = response.json()
    assert result == expected_result


def test_post_user_quiz_failure_unauthorized_invalid_credential(
    mocker, api_client
):
    def verify_id_token(arg):
        raise FirebaseError(code=401, message="")

    mocker.patch("firebase_admin.auth.verify_id_token", verify_id_token)

    expected_result = {"detail": "Invalid authentication from Firebase. "}

    response = api_client.post(
        "/v1/quizzes/",
        headers={"Authorization": "Bearer firebaserusertokenid"},
        json={
            "category": "History",
            "difficulty": "easy",
            "questions": [
                {
                    "correct_answer": "in London in 1912",
                    "incorrect_answers": [
                        "in Manchester in 1901",
                        "in Oxford in 1924",
                        "in Cambridge in 1935",
                    ],
                    "question": "Where and when was Alan Turing born?",
                },
                {
                    "correct_answer": "a Turing Machine",
                    "incorrect_answers": [
                        "the Bombe",
                        "Church's Computer",
                        "the Manchester Mach I",
                    ],
                    "question": "Turing, while solving the Decision Problem, proposed a hypothetical computing machine, which we now call ___",
                },
            ],
            "tags": "1910's",
            "title": "The father of the computer",
        },
    )

    assert response.status_code == 401
    result = response.json()
    assert result == expected_result


def test_post_user_quiz_failure_not_found_user(mocker, api_client):
    mocker.patch(
        "firebase_admin.auth.verify_id_token",
        return_value={"uid": "XXXXXXXXXXXXXXXXXXXXXXXXXXXX"},
    )

    expected_result = {"detail": "User cannot be found"}

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

    mocker.patch("firebase_admin.db.reference", return_value=MockDB())

    response = api_client.post(
        "/v1/quizzes/",
        headers={"Authorization": "Bearer firebaserusertokenid"},
        json={
            "category": "History",
            "difficulty": "easy",
            "questions": [
                {
                    "correct_answer": "in London in 1912",
                    "incorrect_answers": [
                        "in Manchester in 1901",
                        "in Oxford in 1924",
                        "in Cambridge in 1935",
                    ],
                    "question": "Where and when was Alan Turing born?",
                },
                {
                    "correct_answer": "a Turing Machine",
                    "incorrect_answers": [
                        "the Bombe",
                        "Church's Computer",
                        "the Manchester Mach I",
                    ],
                    "question": "Turing, while solving the Decision Problem, proposed a hypothetical computing machine, which we now call ___",
                },
            ],
            "tags": "1910's",
            "title": "The father of the computer",
        },
    )

    assert response.status_code == 404
    result = response.json()
    assert result == expected_result


def test_post_user_quiz_failure_validation(mocker, api_client):
    mocker.patch(
        "firebase_admin.auth.verify_id_token",
        return_value={"uid": "XXXXXXXXXXXXXXXXXXXXXXXXXXXX"},
    )

    response = api_client.post(
        "/v1/quizzes/",
        headers={"Authorization": "Bearer firebaserusertokenid"},
        json={},
    )

    assert response.status_code == 422


def test_post_user_quiz_failure_firebase(mocker, api_client):
    mocker.patch(
        "firebase_admin.auth.verify_id_token",
        return_value={"uid": "XXXXXXXXXXXXXXXXXXXXXXXXXXXX"},
    )

    class MockDB:
        def __init__(self):
            pass

        def order_by_child(self, arg):
            raise FirebaseError(code=503, message="error")

    mocker.patch("firebase_admin.db.reference", return_value=MockDB())

    response = api_client.post(
        "/v1/quizzes/",
        headers={"Authorization": "Bearer firebaserusertokenid"},
        json={
            "category": "History",
            "difficulty": "easy",
            "questions": [
                {
                    "correct_answer": "in London in 1912",
                    "incorrect_answers": [
                        "in Manchester in 1901",
                        "in Oxford in 1924",
                        "in Cambridge in 1935",
                    ],
                    "question": "Where and when was Alan Turing born?",
                },
                {
                    "correct_answer": "a Turing Machine",
                    "incorrect_answers": [
                        "the Bombe",
                        "Church's Computer",
                        "the Manchester Mach I",
                    ],
                    "question": "Turing, while solving the Decision Problem, proposed a hypothetical computing machine, which we now call ___",
                },
            ],
            "tags": "1910's",
            "title": "The father of the computer",
        },
    )

    assert response.status_code == 500


################################################################################
##                             GET USER QUIZZES                               ##
################################################################################


def test_get_user_quizzes_success(mocker, api_client):
    mocker.patch(
        "firebase_admin.auth.verify_id_token",
        return_value={"uid": "XXXXXXXXXXXXXXXXXXXXXXXXXXXX"},
    )

    quiz = {
        "category": "History",
        "difficulty": "easy",
        "questions": [
            {
                "correct_answer": "in London in 1912",
                "incorrect_answers": [
                    "in Manchester in 1901",
                    "in Oxford in 1924",
                    "in Cambridge in 1935",
                ],
                "question": "Where and when was Alan Turing born?",
            },
            {
                "correct_answer": "a Turing Machine",
                "incorrect_answers": [
                    "the Bombe",
                    "Church's Computer",
                    "the Manchester Mach I",
                ],
                "question": "Turing, while solving the Decision Problem, proposed a hypothetical computing machine, which we now call ___",
            },
        ],
        "tags": "1910's",
        "title": "The father of the computer",
        "uid": "XXXXXXXXXXXXXXXXXXXXXXXXXXXX",
    }

    expected_result = {"YYYYYYYYYYYYYYYYYYYY": quiz}

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
            return OrderedDict([("YYYYYYYYYYYYYYYYYYYY", quiz)])

    mocker.patch("firebase_admin.db.reference", return_value=MockDB())

    response = api_client.get(
        "/v1/quizzes/",
        headers={"Authorization": "Bearer firebaserusertokenid"},
    )

    assert response.status_code == 200
    result = response.json()
    assert result == expected_result


def test_get_user_quizzes_failure_unauthorized_no_credential(api_client):
    expected_result = {"detail": "Bearer authentication is needed"}

    response = api_client.get("/v1/quizzes/")

    assert response.status_code == 401
    result = response.json()
    assert result == expected_result


def test_get_user_quizzes_failure_unauthorized_invalid_credential(
    mocker, api_client
):
    def verify_id_token(arg):
        raise FirebaseError(code=401, message="")

    mocker.patch("firebase_admin.auth.verify_id_token", verify_id_token)

    expected_result = {"detail": "Invalid authentication from Firebase. "}

    response = api_client.get(
        "/v1/quizzes/",
        headers={"Authorization": "Bearer firebaserusertokenid"},
    )

    assert response.status_code == 401
    result = response.json()
    assert result == expected_result


def test_get_user_quizzes_failure_not_found_user(mocker, api_client):
    mocker.patch(
        "firebase_admin.auth.verify_id_token",
        return_value={"uid": "XXXXXXXXXXXXXXXXXXXXXXXXXXXX"},
    )

    expected_result = {"detail": "User cannot be found"}

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

    mocker.patch("firebase_admin.db.reference", return_value=MockDB())

    response = api_client.get(
        "/v1/quizzes/",
        headers={"Authorization": "Bearer firebaserusertokenid"},
    )

    assert response.status_code == 404
    result = response.json()
    assert result == expected_result


def test_get_user_quizzes_failure_firebase(mocker, api_client):
    mocker.patch(
        "firebase_admin.auth.verify_id_token",
        return_value={"uid": "XXXXXXXXXXXXXXXXXXXXXXXXXXXX"},
    )

    class MockDB:
        def __init__(self):
            pass

        def order_by_child(self, arg):
            raise FirebaseError(code=503, message="error")

    mocker.patch("firebase_admin.db.reference", return_value=MockDB())

    response = api_client.get(
        "/v1/quizzes/",
        headers={"Authorization": "Bearer firebaserusertokenid"},
    )

    assert response.status_code == 500


################################################################################
##                                GET USER QUIZ                               ##
################################################################################


def test_get_user_quiz_success(mocker, api_client):
    mocker.patch(
        "firebase_admin.auth.verify_id_token",
        return_value={"uid": "XXXXXXXXXXXXXXXXXXXXXXXXXXXX"},
    )

    expected_result = {
        "category": "History",
        "difficulty": "easy",
        "questions": [
            {
                "correct_answer": "in London in 1912",
                "incorrect_answers": [
                    "in Manchester in 1901",
                    "in Oxford in 1924",
                    "in Cambridge in 1935",
                ],
                "question": "Where and when was Alan Turing born?",
            },
            {
                "correct_answer": "a Turing Machine",
                "incorrect_answers": [
                    "the Bombe",
                    "Church's Computer",
                    "the Manchester Mach I",
                ],
                "question": "Turing, while solving the Decision Problem, proposed a hypothetical computing machine, which we now call ___",
            },
        ],
        "tags": "1910's",
        "title": "The father of the computer",
        "uid": "XXXXXXXXXXXXXXXXXXXXXXXXXXXX",
    }

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
            return OrderedDict([("YYYYYYYYYYYYYYYYYYYY", expected_result)])

    mocker.patch("firebase_admin.db.reference", return_value=MockDB())

    response = api_client.get(
        "/v1/quizzes/YYYYYYYYYYYYYYYYYYYY",
        headers={"Authorization": "Bearer firebaserusertokenid"},
    )

    assert response.status_code == 200
    result = response.json()
    assert result == expected_result


def test_get_user_quiz_failure_unauthorized_no_credential(api_client):
    expected_result = {"detail": "Bearer authentication is needed"}

    response = api_client.get("/v1/quizzes/YYYYYYYYYYYYYYYYYYYY")

    assert response.status_code == 401
    result = response.json()
    assert result == expected_result


def test_get_user_quiz_failure_unauthorized_invalid_credential(
    mocker, api_client
):
    def verify_id_token(arg):
        raise FirebaseError(code=401, message="")

    mocker.patch("firebase_admin.auth.verify_id_token", verify_id_token)

    expected_result = {"detail": "Invalid authentication from Firebase. "}

    response = api_client.get(
        "/v1/quizzes/YYYYYYYYYYYYYYYYYYYY",
        headers={"Authorization": "Bearer firebaserusertokenid"},
    )

    assert response.status_code == 401
    result = response.json()
    assert result == expected_result


def test_get_user_quiz_failure_not_found_user(mocker, api_client):
    mocker.patch(
        "firebase_admin.auth.verify_id_token",
        return_value={"uid": "XXXXXXXXXXXXXXXXXXXXXXXXXXXX"},
    )

    expected_result = {"detail": "User cannot be found"}

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

    mocker.patch("firebase_admin.db.reference", return_value=MockDB())

    response = api_client.get(
        "/v1/quizzes/YYYYYYYYYYYYYYYYYYYY",
        headers={"Authorization": "Bearer firebaserusertokenid"},
    )

    assert response.status_code == 404
    result = response.json()
    assert result == expected_result


def test_get_user_quiz_failure_not_found_quiz(mocker, api_client):
    mocker.patch(
        "firebase_admin.auth.verify_id_token",
        return_value={"uid": "XXXXXXXXXXXXXXXXXXXXXXXXXXXX"},
    )

    expected_result = {
        "detail": "Cannot find quiz with id YYYYYYYYYYYYYYYYYYYY"
    }

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
            return OrderedDict([("ZZZZZZZZZZZZZZZZZZZZ", expected_result)])

    mocker.patch("firebase_admin.db.reference", return_value=MockDB())

    response = api_client.get(
        "/v1/quizzes/YYYYYYYYYYYYYYYYYYYY",
        headers={"Authorization": "Bearer firebaserusertokenid"},
    )

    assert response.status_code == 404
    result = response.json()
    assert result == expected_result


def test_get_user_quiz_failure_firebase(mocker, api_client):
    mocker.patch(
        "firebase_admin.auth.verify_id_token",
        return_value={"uid": "XXXXXXXXXXXXXXXXXXXXXXXXXXXX"},
    )

    class MockDB:
        def __init__(self):
            pass

        def order_by_child(self, arg):
            raise FirebaseError(code=503, message="error")

    mocker.patch("firebase_admin.db.reference", return_value=MockDB())

    response = api_client.get(
        "/v1/quizzes/YYYYYYYYYYYYYYYYYYYY",
        headers={"Authorization": "Bearer firebaserusertokenid"},
    )

    assert response.status_code == 500


################################################################################
##                             DELETE USER QUIZZES                            ##
################################################################################


def test_delete_user_quizzes_success(mocker, api_client):
    mocker.patch(
        "firebase_admin.auth.verify_id_token",
        return_value={"uid": "XXXXXXXXXXXXXXXXXXXXXXXXXXXX"},
    )

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
            return OrderedDict(
                [
                    ("YYYYYYYYYYYYYYYYYYYY", {}),
                    ("ZZZZZZZZZZZZZZZZZZZZ", {}),
                ]
            )

        def child(self, arg):
            return self

        def delete(self):
            pass

    mocker.patch("firebase_admin.db.reference", return_value=MockDB())

    response = api_client.request(
        "DELETE",
        "/v1/quizzes/",
        headers={"Authorization": "Bearer firebaserusertokenid"},
        json={"quizzes_ids": ["YYYYYYYYYYYYYYYYYYYY", "ZZZZZZZZZZZZZZZZZZZZ"]},
    )

    assert response.status_code == 204


def test_delete_user_quizzes_failure_unauthorized_no_credential(api_client):
    expected_result = {"detail": "Bearer authentication is needed"}

    response = api_client.request(
        "DELETE",
        "/v1/quizzes/",
        json={"quizzes_ids": ["YYYYYYYYYYYYYYYYYYYY", "ZZZZZZZZZZZZZZZZZZZZ"]},
    )

    assert response.status_code == 401
    result = response.json()
    assert result == expected_result


def test_delete_user_quizzes_failure_unauthorized_invalid_credential(
    mocker, api_client
):
    def verify_id_token(arg):
        raise FirebaseError(code=401, message="")

    mocker.patch("firebase_admin.auth.verify_id_token", verify_id_token)

    expected_result = {"detail": "Invalid authentication from Firebase. "}

    response = api_client.request(
        "DELETE",
        "/v1/quizzes/",
        headers={"Authorization": "Bearer firebaserusertokenid"},
        json={"quizzes_ids": ["YYYYYYYYYYYYYYYYYYYY", "ZZZZZZZZZZZZZZZZZZZZ"]},
    )

    assert response.status_code == 401
    result = response.json()
    assert result == expected_result


def test_delete_user_quizzes_failure_not_found_user(mocker, api_client):
    mocker.patch(
        "firebase_admin.auth.verify_id_token",
        return_value={"uid": "XXXXXXXXXXXXXXXXXXXXXXXXXXXX"},
    )

    expected_result = {"detail": "User cannot be found"}

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

    mocker.patch("firebase_admin.db.reference", return_value=MockDB())

    response = api_client.request(
        "DELETE",
        "/v1/quizzes/",
        headers={"Authorization": "Bearer firebaserusertokenid"},
        json={"quizzes_ids": ["YYYYYYYYYYYYYYYYYYYY", "ZZZZZZZZZZZZZZZZZZZZ"]},
    )

    assert response.status_code == 404
    result = response.json()
    assert result == expected_result


def test_delete_user_quizzes_failure_firebase(mocker, api_client):
    mocker.patch(
        "firebase_admin.auth.verify_id_token",
        return_value={"uid": "XXXXXXXXXXXXXXXXXXXXXXXXXXXX"},
    )

    class MockDB:
        def __init__(self):
            pass

        def order_by_child(self, arg):
            raise FirebaseError(code=503, message="error")

    mocker.patch("firebase_admin.db.reference", return_value=MockDB())

    response = api_client.request(
        "DELETE",
        "/v1/quizzes/",
        headers={"Authorization": "Bearer firebaserusertokenid"},
        json={"quizzes_ids": ["YYYYYYYYYYYYYYYYYYYY", "ZZZZZZZZZZZZZZZZZZZZ"]},
    )

    assert response.status_code == 500


################################################################################
##                               DELETE USER QUIZ                             ##
################################################################################


def test_delete_user_quiz_success(mocker, api_client):
    mocker.patch(
        "firebase_admin.auth.verify_id_token",
        return_value={"uid": "XXXXXXXXXXXXXXXXXXXXXXXXXXXX"},
    )

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
            return OrderedDict([("YYYYYYYYYYYYYYYYYYYY", {})])

        def child(self, arg):
            return self

        def delete(self):
            pass

    mocker.patch("firebase_admin.db.reference", return_value=MockDB())

    response = api_client.delete(
        "/v1/quizzes/YYYYYYYYYYYYYYYYYYYY",
        headers={"Authorization": "Bearer firebaserusertokenid"},
    )

    assert response.status_code == 204


def test_delete_user_quiz_failure_unauthorized_no_credential(api_client):
    expected_result = {"detail": "Bearer authentication is needed"}

    response = api_client.delete("/v1/quizzes/YYYYYYYYYYYYYYYYYYYY")

    assert response.status_code == 401
    result = response.json()
    assert result == expected_result


def test_delete_user_quiz_failure_unauthorized_invalid_credential(
    mocker, api_client
):
    def verify_id_token(arg):
        raise FirebaseError(code=401, message="")

    mocker.patch("firebase_admin.auth.verify_id_token", verify_id_token)

    expected_result = {"detail": "Invalid authentication from Firebase. "}

    response = api_client.delete(
        "/v1/quizzes/YYYYYYYYYYYYYYYYYYYY",
        headers={"Authorization": "Bearer firebaserusertokenid"},
    )

    assert response.status_code == 401
    result = response.json()
    assert result == expected_result


def test_delete_user_quiz_failure_not_found_user(mocker, api_client):
    mocker.patch(
        "firebase_admin.auth.verify_id_token",
        return_value={"uid": "XXXXXXXXXXXXXXXXXXXXXXXXXXXX"},
    )

    expected_result = {"detail": "User cannot be found"}

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

    mocker.patch("firebase_admin.db.reference", return_value=MockDB())

    response = api_client.delete(
        "/v1/quizzes/YYYYYYYYYYYYYYYYYYYY",
        headers={"Authorization": "Bearer firebaserusertokenid"},
    )

    assert response.status_code == 404
    result = response.json()
    assert result == expected_result


def test_delete_user_quiz_failure_not_found_quiz(mocker, api_client):
    mocker.patch(
        "firebase_admin.auth.verify_id_token",
        return_value={"uid": "XXXXXXXXXXXXXXXXXXXXXXXXXXXX"},
    )

    expected_result = {
        "detail": "Cannot find quiz with id YYYYYYYYYYYYYYYYYYYY"
    }

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
            return OrderedDict([("ZZZZZZZZZZZZZZZZZZZZ", expected_result)])

    mocker.patch("firebase_admin.db.reference", return_value=MockDB())

    response = api_client.delete(
        "/v1/quizzes/YYYYYYYYYYYYYYYYYYYY",
        headers={"Authorization": "Bearer firebaserusertokenid"},
    )

    assert response.status_code == 404
    result = response.json()
    assert result == expected_result


def test_delete_user_quiz_failure_firebase(mocker, api_client):
    mocker.patch(
        "firebase_admin.auth.verify_id_token",
        return_value={"uid": "XXXXXXXXXXXXXXXXXXXXXXXXXXXX"},
    )

    class MockDB:
        def __init__(self):
            pass

        def order_by_child(self, arg):
            raise FirebaseError(code=503, message="error")

    mocker.patch("firebase_admin.db.reference", return_value=MockDB())

    response = api_client.delete(
        "/v1/quizzes/YYYYYYYYYYYYYYYYYYYY",
        headers={"Authorization": "Bearer firebaserusertokenid"},
    )

    assert response.status_code == 500


################################################################################
##                               PATCH USER QUIZ                              ##
################################################################################


def test_patch_user_quiz_success(mocker, api_client):
    mocker.patch(
        "firebase_admin.auth.verify_id_token",
        return_value={"uid": "XXXXXXXXXXXXXXXXXXXXXXXXXXXX"},
    )

    quiz = {
        "category": "History",
        "difficulty": "easy",
        "questions": [
            {
                "correct_answer": "in London in 1912",
                "incorrect_answers": [
                    "in Manchester in 1901",
                    "in Oxford in 1924",
                    "in Cambridge in 1935",
                ],
                "question": "Where and when was Alan Turing born?",
            },
            {
                "correct_answer": "a Turing Machine",
                "incorrect_answers": [
                    "the Bombe",
                    "Church's Computer",
                    "the Manchester Mach I",
                ],
                "question": "Turing, while solving the Decision Problem, proposed a hypothetical computing machine, which we now call ___",
            },
        ],
        "tags": "1910's",
        "title": "The father of the computer",
        "uid": "XXXXXXXXXXXXXXXXXXXXXXXXXXXX",
    }

    update = {"difficulty": "hard"}

    expected_result = {**quiz, **update}

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
            return OrderedDict([("YYYYYYYYYYYYYYYYYYYY", quiz)])

        def child(self, arg):
            return self

        def set(self, arg):
            pass

    mocker.patch("firebase_admin.db.reference", return_value=MockDB())

    response = api_client.patch(
        "/v1/quizzes/YYYYYYYYYYYYYYYYYYYY",
        headers={"Authorization": "Bearer firebaserusertokenid"},
        json={**update},
    )

    assert response.status_code == 200
    result = response.json()
    assert result == expected_result


def test_patch_user_quiz_failure_unauthorized_no_credential(api_client):
    expected_result = {"detail": "Bearer authentication is needed"}

    response = api_client.patch(
        "/v1/quizzes/YYYYYYYYYYYYYYYYYYYY", json={"difficulty": "hard"}
    )

    assert response.status_code == 401
    result = response.json()
    assert result == expected_result


def test_patch_user_quiz_failure_unauthorized_invalid_credential(
    mocker, api_client
):
    def verify_id_token(arg):
        raise FirebaseError(code=401, message="")

    mocker.patch("firebase_admin.auth.verify_id_token", verify_id_token)

    expected_result = {"detail": "Invalid authentication from Firebase. "}

    response = api_client.patch(
        "/v1/quizzes/YYYYYYYYYYYYYYYYYYYY",
        headers={"Authorization": "Bearer firebaserusertokenid"},
        json={"difficulty": "hard"},
    )

    assert response.status_code == 401
    result = response.json()
    assert result == expected_result


def test_patch_user_quiz_failure_not_found_user(mocker, api_client):
    mocker.patch(
        "firebase_admin.auth.verify_id_token",
        return_value={"uid": "XXXXXXXXXXXXXXXXXXXXXXXXXXXX"},
    )

    expected_result = {"detail": "User cannot be found"}

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

    mocker.patch("firebase_admin.db.reference", return_value=MockDB())

    response = api_client.patch(
        "/v1/quizzes/YYYYYYYYYYYYYYYYYYYY",
        headers={"Authorization": "Bearer firebaserusertokenid"},
        json={"difficulty": "hard"},
    )

    assert response.status_code == 404
    result = response.json()
    assert result == expected_result


def test_patch_user_quiz_failure_not_found_quiz(mocker, api_client):
    mocker.patch(
        "firebase_admin.auth.verify_id_token",
        return_value={"uid": "XXXXXXXXXXXXXXXXXXXXXXXXXXXX"},
    )

    expected_result = {
        "detail": "Cannot find quiz with id YYYYYYYYYYYYYYYYYYYY"
    }

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
            return OrderedDict([("ZZZZZZZZZZZZZZZZZZZZ", expected_result)])

    mocker.patch("firebase_admin.db.reference", return_value=MockDB())

    response = api_client.patch(
        "/v1/quizzes/YYYYYYYYYYYYYYYYYYYY",
        headers={"Authorization": "Bearer firebaserusertokenid"},
        json={"difficulty": "hard"},
    )

    assert response.status_code == 404
    result = response.json()
    assert result == expected_result


def test_patch_user_quiz_failure_firebase(mocker, api_client):
    mocker.patch(
        "firebase_admin.auth.verify_id_token",
        return_value={"uid": "XXXXXXXXXXXXXXXXXXXXXXXXXXXX"},
    )

    class MockDB:
        def __init__(self):
            pass

        def order_by_child(self, arg):
            raise FirebaseError(code=503, message="error")

    mocker.patch("firebase_admin.db.reference", return_value=MockDB())

    response = api_client.patch(
        "/v1/quizzes/YYYYYYYYYYYYYYYYYYYY",
        headers={"Authorization": "Bearer firebaserusertokenid"},
        json={"difficulty": "hard"},
    )

    assert response.status_code == 500
