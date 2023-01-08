from collections import OrderedDict
from firebase_admin.exceptions import FirebaseError

################################################################################
##                                 POST USER                                  ##
################################################################################


def test_post_user_success(mocker, api_client):
    mocker.patch(
        "firebase_admin.auth.verify_id_token",
        return_value={
            "uid": "XXXXXXXXXXXXXXXXXXXXXXXXXXXX",
            "name": "Alan Turing",
            "picture": "https://firebasestorage.googleapis.com/v0/b/quizly-70118.appspot.com/o/unknown_user.png?alt=media&token=082b6b49-2ad6-4d57-a93f-47f5a82041e4",  # noqa
        },
    )

    expected_result = {
        "uid": "XXXXXXXXXXXXXXXXXXXXXXXXXXXX",
        "name": "Alan Turing",
        "nickname": "turingComplete",
        "picture": "https://firebasestorage.googleapis.com/v0/b/quizly-70118.appspot.com/o/unknown_user.png?alt=media&token=082b6b49-2ad6-4d57-a93f-47f5a82041e4",  # noqa
        "win": 0,
        "lose": 0,
        "favourite_category": "-",
        "max_points": 0,
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
            return None

        def push(self):
            return self

        def set(self, arg):
            pass

    mocker.patch("firebase_admin.db.reference", return_value=MockDB())

    response = api_client.post(
        "/v1/users/",
        headers={"Authorization": "Bearer firebaserusertokenid"},
        json={"nickname": "turingComplete"},
    )

    assert response.status_code == 201
    result = response.json()
    assert result == expected_result


def test_post_user_success_without_data(mocker, api_client):
    mocker.patch("api.routes.users.get_timestamp", return_value=420)

    mocker.patch(
        "firebase_admin.auth.verify_id_token",
        return_value={"uid": "XXXXXXXXXXXXXXXXXXXXXXXXXXXX"},
    )

    expected_result = {
        "uid": "XXXXXXXXXXXXXXXXXXXXXXXXXXXX",
        "name": "somebody420",
        "nickname": "turingComplete",
        "picture": "https://firebasestorage.googleapis.com/v0/b/quizly-70118.appspot.com/o/unknown_user.png?alt=media&token=082b6b49-2ad6-4d57-a93f-47f5a82041e4",  # noqa
        "win": 0,
        "lose": 0,
        "favourite_category": "-",
        "max_points": 0,
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
            return None

        def push(self):
            return self

        def set(self, arg):
            pass

    mocker.patch("firebase_admin.db.reference", return_value=MockDB())

    response = api_client.post(
        "/v1/users/",
        headers={"Authorization": "Bearer firebaserusertokenid"},
        json={"nickname": "turingComplete"},
    )

    assert response.status_code == 201
    result = response.json()
    assert result == expected_result


def test_post_user_failure_unauthorized_no_credential(mocker, api_client):
    expected_result = {"detail": "Bearer authentication is needed"}

    response = api_client.post(
        "/v1/users/", json={"nickname": "turingComplete"}
    )

    assert response.status_code == 401
    result = response.json()
    assert result == expected_result


def test_post_user_failure_unauthorized_invalid_credential(mocker, api_client):
    def verify_id_token(arg):
        raise FirebaseError(code=401, message="")

    mocker.patch("firebase_admin.auth.verify_id_token", verify_id_token)

    expected_result = {"detail": "Invalid authentication from Firebase. "}

    response = api_client.post(
        "/v1/users/",
        headers={"Authorization": "Bearer firebaserusertokenid"},
        json={"nickname": "turingComplete"},
    )

    assert response.status_code == 401
    result = response.json()
    assert result == expected_result


def test_post_user_failure_account(mocker, api_client):
    mocker.patch(
        "firebase_admin.auth.verify_id_token",
        return_value={
            "uid": "XXXXXXXXXXXXXXXXXXXXXXXXXXXX",
            "name": "Alan Turing",
            "picture": "https://firebasestorage.googleapis.com/v0/b/quizly-70118.appspot.com/o/unknown_user.png?alt=media&token=082b6b49-2ad6-4d57-a93f-47f5a82041e4",  # noqa
        },
    )

    expected_result = {"detail": "Account already exists"}

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
                    (
                        "XXXXXXXXXXXXXXXXXXXX",
                        {
                            "uid": "XXXXXXXXXXXXXXXXXXXXXXXXXXXX",
                            "name": "Alan Turing",
                            "nickname": "turingComplete",
                            "picture": "https://firebasestorage.googleapis.com/v0/b/quizly-70118.appspot.com/o/unknown_user.png?alt=media&token=082b6b49-2ad6-4d57-a93f-47f5a82041e4",  # noqa
                            "win": 0,
                            "lose": 0,
                            "favourite_category": "-",
                            "max_points": 0,
                        },
                    )
                ]
            )

        def push(self):
            return self

        def set(self, arg):
            pass

    mocker.patch("firebase_admin.db.reference", return_value=MockDB())

    response = api_client.post(
        "/v1/users/",
        headers={"Authorization": "Bearer firebaserusertokenid"},
        json={"nickname": "turingComplete"},
    )

    assert response.status_code == 409
    result = response.json()
    assert result == expected_result


def test_post_user_failure_nickname(mocker, api_client):
    mocker.patch(
        "firebase_admin.auth.verify_id_token",
        return_value={
            "uid": "XXXXXXXXXXXXXXXXXXXXXXXXXXXX",
            "name": "Alan Turing",
            "picture": "https://firebasestorage.googleapis.com/v0/b/quizly-70118.appspot.com/o/unknown_user.png?alt=media&token=082b6b49-2ad6-4d57-a93f-47f5a82041e4",  # noqa
        },
    )

    expected_result = {"detail": "Nickname turingComplete was already taken"}

    class MockDB:
        def __init__(self):
            self.order = ""

        def order_by_child(self, arg):
            self.order = arg
            return self

        def equal_to(self, arg):
            return self

        def limit_to_first(self, arg):
            return self

        def get(self):
            if self.order == "uid":
                return None
            else:
                return OrderedDict(
                    [
                        (
                            "YYYYYYYYYYYYYYYYYYYY",
                            {
                                "uid": "YYYYYYYYYYYYYYYYYYYYYYYYYYYY",
                                "name": "Alan Turing",
                                "nickname": "turingComplete",
                                "picture": "https://firebasestorage.googleapis.com/v0/b/quizly-70118.appspot.com/o/unknown_user.png?alt=media&token=082b6b49-2ad6-4d57-a93f-47f5a82041e4",  # noqa
                                "win": 0,
                                "lose": 0,
                                "favourite_category": "-",
                                "max_points": 0,
                            },
                        )
                    ]
                )

        def push(self):
            return self

        def set(self, arg):
            pass

    mocker.patch("firebase_admin.db.reference", return_value=MockDB())

    response = api_client.post(
        "/v1/users/",
        headers={"Authorization": "Bearer firebaserusertokenid"},
        json={"nickname": "turingComplete"},
    )

    assert response.status_code == 409
    result = response.json()
    assert result == expected_result


def test_post_user_failure_validation(mocker, api_client):
    mocker.patch(
        "firebase_admin.auth.verify_id_token",
        return_value={
            "uid": "XXXXXXXXXXXXXXXXXXXXXXXXXXXX",
            "name": "Alan Turing",
            "picture": "https://firebasestorage.googleapis.com/v0/b/quizly-70118.appspot.com/o/unknown_user.png?alt=media&token=082b6b49-2ad6-4d57-a93f-47f5a82041e4",  # noqa
        },
    )

    response = api_client.post(
        "/v1/users/",
        headers={"Authorization": "Bearer firebaserusertokenid"},
        json={},
    )

    assert response.status_code == 422


def test_post_user_failure_firebase(mocker, api_client):
    mocker.patch(
        "firebase_admin.auth.verify_id_token",
        return_value={
            "uid": "XXXXXXXXXXXXXXXXXXXXXXXXXXXX",
            "name": "Alan Turing",
            "picture": "https://firebasestorage.googleapis.com/v0/b/quizly-70118.appspot.com/o/unknown_user.png?alt=media&token=082b6b49-2ad6-4d57-a93f-47f5a82041e4",  # noqa
        },
    )

    class MockDB:
        def __init__(self):
            pass

        def order_by_child(self, arg):
            raise FirebaseError(code=503, message="error")

    mocker.patch("firebase_admin.db.reference", return_value=MockDB())

    response = api_client.post(
        "/v1/users/",
        headers={"Authorization": "Bearer firebaserusertokenid"},
        json={"nickname": "turingComplete"},
    )

    assert response.status_code == 500


################################################################################
##                                 GET USER                                   ##
################################################################################


def test_get_user_success(mocker, api_client):
    mocker.patch(
        "firebase_admin.auth.verify_id_token",
        return_value={"uid": "XXXXXXXXXXXXXXXXXXXXXXXXXXXX"},
    )

    expected_result = {
        "uid": "XXXXXXXXXXXXXXXXXXXXXXXXXXXX",
        "name": "Alan Turing",
        "nickname": "turingComplete",
        "picture": "https://firebasestorage.googleapis.com/v0/b/quizly-70118.appspot.com/o/unknown_user.png?alt=media&token=082b6b49-2ad6-4d57-a93f-47f5a82041e4",  # noqa
        "win": 0,
        "lose": 0,
        "favourite_category": "-",
        "max_points": 0,
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
            return OrderedDict([("XXXXXXXXXXXXXXXXXXXX", expected_result)])

    mocker.patch("firebase_admin.db.reference", return_value=MockDB())

    response = api_client.get(
        "/v1/users/", headers={"Authorization": "Bearer firebaserusertokenid"}
    )

    assert response.status_code == 200
    result = response.json()
    assert result == expected_result


def test_get_user_failure_unauthorized_no_credential(mocker, api_client):
    expected_result = {"detail": "Bearer authentication is needed"}

    response = api_client.get("/v1/users/")

    assert response.status_code == 401
    result = response.json()
    assert result == expected_result


def test_get_user_failure_unauthorized_invalid_credential(mocker, api_client):
    def verify_id_token(arg):
        raise FirebaseError(code=401, message="")

    mocker.patch("firebase_admin.auth.verify_id_token", verify_id_token)

    expected_result = {"detail": "Invalid authentication from Firebase. "}

    response = api_client.get(
        "/v1/users/", headers={"Authorization": "Bearer firebaserusertokenid"}
    )

    assert response.status_code == 401
    result = response.json()
    assert result == expected_result


def test_get_user_failure_not_found(mocker, api_client):
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
        "/v1/users/", headers={"Authorization": "Bearer firebaserusertokenid"}
    )

    assert response.status_code == 404
    result = response.json()
    assert result == expected_result


def test_get_user_failure_firebase(mocker, api_client):
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
        "/v1/users/", headers={"Authorization": "Bearer firebaserusertokenid"}
    )

    assert response.status_code == 500
