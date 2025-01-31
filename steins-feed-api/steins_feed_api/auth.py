import datetime
import os
import typing

import fastapi
import fastapi.security
import jwt
import jwt.exceptions
import passlib.context
import pydantic
import sqlalchemy as sqla
import sqlalchemy.orm as sqla_orm

import steins_feed_model
import steins_feed_model.users

import steins_feed_api.db

router = fastapi.APIRouter()
oauth2_scheme = fastapi.security.OAuth2PasswordBearer(tokenUrl="token")
pwd_context = passlib.context.CryptContext(schemes=["bcrypt"], deprecated="auto")

class User(pydantic.BaseModel):
    id: int
    name: str
    email: str

    @classmethod
    def from_model(cls, user: steins_feed_model.users.User) -> "User":
        return User(
            id = user.id,
            name = user.name,
            email = user.email,
        )

async def current_user(token: typing.Annotated[str, fastapi.Depends(oauth2_scheme)]) -> User:
    payload = jwt.decode(
        token,
        key = os.environ["SECRET_KEY"],
        algorithms = [os.getenv("ALGORITHM", "HS256")],
    )

    q = sqla.select(
        steins_feed_model.users.User,
    ).where(
        steins_feed_model.users.User.name == payload["sub"],
    )

    with sqla_orm.Session(steins_feed_api.db.engine) as session:
        user = session.execute(q).scalars().one()
        return User.from_model(user)

UserDep = typing.Annotated[User, fastapi.Depends(current_user)]

class Token(pydantic.BaseModel):
    access_token: str
    token_type: str

@router.post("/token")
async def login(
    form_data: typing.Annotated[
        fastapi.security.OAuth2PasswordRequestForm,
        fastapi.Depends(),
    ],
) -> Token:
    q = sqla.select(
        steins_feed_model.users.User,
    ).where(
        steins_feed_model.users.User.name == form_data.username,
    )

    with sqla_orm.Session(steins_feed_api.db.engine) as session:
        user = session.execute(q).scalars().one()

        if not pwd_context.verify(form_data.password, user.password):
            raise fastapi.HTTPException(
                status_code = fastapi.status.HTTP_401_UNAUTHORIZED,
                detail = "Incorrect username or password",
                headers = {"WWW-Authenticate": "Bearer"},
            )

    dt_now = datetime.datetime.now(datetime.timezone.utc)
    dt_seconds = int(os.getenv("ACCESS_TOKEN_EXPIRE_SECONDS", 1800))
    dt_delta = datetime.timedelta(seconds=dt_seconds)

    token = jwt.encode(
        {
            "sub": form_data.username,
            "exp": dt_now + dt_delta,
        },
        key = os.environ["SECRET_KEY"],
        algorithm = os.getenv("ALGORITHM", "HS256"),
    )

    return Token(
        access_token = token,
        token_type = "bearer",
    )
