from auth import check_auth, check_password, hash_password
from crud import create_item, delete_item, get_item, patch_item
from errors import ApiError
from flask import jsonify, request, Response

from flask.views import MethodView
from models import Token, User, get_session_maker, Advert
from schema import Login, PatchUser, Register, validate, PostPatchAdvert

Session = get_session_maker()


def register() -> Response:
    if not request.json:
        raise ApiError(400, "request error")
    user_data = validate(Register, request.json)
    with Session() as session:
        user_data["password"] = hash_password(user_data["password"])
        user = create_item(session, User, **user_data)
        return jsonify({"id": user.id})


def login() -> Response:
    if not request.json:
        raise ApiError(400, "request error")
    login_data = validate(Login, request.json)
    with Session() as session:
        user = (
            session.query(User)
            .filter(User.email == login_data["email"])
            .first()
        )
        if user is None or not check_password(
            user.password, login_data["password"]
        ):
            raise ApiError(401, "Invalid user or password")

        token = Token(user=user)
        session.add(token)
        session.commit()
        return jsonify({"token": token.id})


class UserView(MethodView):
    def get(self, user_id) -> Response:
        with Session() as session:
            user = get_item(session, User, user_id)
            return jsonify(
                {
                    "id": user.id,
                    "email": user.email,
                    "registration_time": user.registration_time.isoformat(),
                }
            )

    def patch(self, user_id: int):
        if not request.json:
            raise ApiError(400, "request error")
        with Session() as session:
            patch_data = validate(PatchUser, request.json)
            if "password" in patch_data:
                patch_data["password"] = hash_password(patch_data["password"])

            token = check_auth(session)
            user = get_item(session, User, user_id)
            if token.user_id != user.id:
                raise ApiError(403, "user has no access")
            user = patch_item(session, user, **patch_data)

            return jsonify(
                {
                    "id": user.id,
                    "email": user.email,
                    "registration_time": user.registration_time.isoformat(),
                }
            )

    def delete(self, user_id: int) -> Response:
        with Session() as session:
            user = get_item(session, User, user_id)
            token = check_auth(session)
            if token.user_id != user.id:
                raise ApiError(403, "user has no access")

            delete_item(session, user)

            return jsonify({"deleted": True})


class AdvertView(MethodView):
    def post(self) -> Response:
        if not request.json:
            raise ApiError(400, "request error")
        with Session() as session:
            token = check_auth(session)
            advert_data = validate(PostPatchAdvert, request.json)
            advert_data["owner"] = token.user
            advert = create_item(session, Advert, **advert_data)
            return jsonify(
                {
                    "id": advert.id,
                    "title": advert.title,
                    "description": advert.description,
                    "owner_id": advert.owner_id,
                })

    def get(self, advert_id: int) -> Response:
        with Session() as session:
            advert = get_item(session, Advert, advert_id)
            return jsonify(
                {
                    "id": advert.id,
                    "title": advert.title,
                    "description": advert.description,
                    "owner_id": advert.owner_id,
                    "creation_time": advert.creation_time.isoformat(),
                }
            )

    def patch(self, advert_id: int) -> Response:
        if not request.json:
            raise ApiError(400, "request error")
        with Session() as session:
            patch_data = validate(PostPatchAdvert, request.json)
            token = check_auth(session)
            advert = get_item(session, Advert, advert_id)
            if token.user_id != advert.owner.id:
                raise ApiError(403, "user has no access")
            advert = patch_item(session, advert, **patch_data)

            return jsonify(
                {
                    "id": advert.id,
                    "title": advert.title,
                    "description": advert.description,
                    "owner_id": advert.owner_id,
                    "creation_time": advert.creation_time.isoformat(),
                }
            )

    def delete(self, advert_id: int) -> Response:
        with Session() as session:
            advert = get_item(session, Advert, advert_id)
            token = check_auth(session)
            if token.user_id != advert.owner.id:
                raise ApiError(403, "user has no access")
            delete_item(session, advert)
            return jsonify({"deleted": True})
