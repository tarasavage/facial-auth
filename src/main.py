from authlib.integrations.starlette_client import OAuth
from fastapi import FastAPI, Request
from starlette.responses import RedirectResponse
from starlette.middleware.sessions import SessionMiddleware

from api.endpoints.auth import router as auth_router
from users.router import router as users_router
from core.config import get_settings

app = FastAPI()

app.include_router(users_router, prefix="/users")
app.include_router(auth_router, prefix="/auth")
app.add_middleware(
    SessionMiddleware,
    secret_key=get_settings().APP_SECRET_KEY,
)
oauth = OAuth()
oauth.register(
    name="oidc",
    client_id=get_settings().AWS_COGNITO_CLIENT_ID,
    client_secret=get_settings().AWS_COGNITO_CLIENT_SECRET,
    client_kwargs={"scope": "email openid phone"},
    server_metadata_url=get_settings().AWS_COGNITO_SERVER_METADATA_URL,
)


@app.get("/")
async def root(request: Request):
    return "Welcome! Please <a href='/login'>Login</a>."


@app.get("/logout")
async def logout(request: Request):
    return "You have been logged out. <a href='/login'>Login</a>."


@app.get("/login")
async def login(request: Request):
    redirect_uri = request.url_for("callback")
    return await oauth.oidc.authorize_redirect(request, redirect_uri)


@app.get("/callback")
async def callback(request: Request):
    token = await oauth.oidc.authorize_access_token(request)
    print(token)
    response = RedirectResponse("/", status_code=303)
    return response


@app.get("/health")
async def health():
    return {"status": "ok"}
