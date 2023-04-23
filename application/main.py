import atexit


from errors import ApiError, error_handler
from models import close_db, init_db
from views import UserView, login, register, AdvertView

from app import get_app


init_db()
atexit.register(close_db)

app = get_app()

app.add_url_rule("/register", view_func=register, methods=["POST"])
app.add_url_rule("/login", view_func=login, methods=["POST"])
app.add_url_rule(
    "/users/<int:user_id>",
    view_func=UserView.as_view("user"),
    methods=["GET", "PATCH", "DELETE"],
)
app.add_url_rule(
    "/adverts/<int:advert_id>",
    view_func=AdvertView.as_view("advert"),
    methods=["GET", "DELETE", "PATCH"]
)
app.add_url_rule(
    "/adverts", view_func=AdvertView.as_view("advert_new"), methods=["POST"]
)

app.errorhandler(ApiError)(error_handler)

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000)
