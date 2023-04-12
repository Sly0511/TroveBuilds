from flet import Tab, Container, Column, ElevatedButton
from flet.auth.oauth_provider import OAuthProvider
from i18n import t
import flet_core.icons as ico
import os

class DiscordOAuth2(OAuthProvider):
    def __init__(self,
        client_id: str = "...",
        client_secret: str = "..."
    ):
        super().__init__(
            client_id=client_id,
            client_secret=client_secret,
            authorization_endpoint="https://discord.com/oauth2/authorize",
            token_endpoint="https://discord.com/api/oauth2/token",
            redirect_url="https://trovetools.slynx.xyz/",
            scopes=["identify"],
            user_endpoint="https://discord.com/api/users/@me"
        )

provider = DiscordOAuth2()

class Login(Tab):
    def __init__(self, page):
        async def on_login(e):
            print("Access token:", page.auth.token.access_token)
            print("User ID:", page.auth.user.id)
        async def login_click(e):
            await page.login_async(provider)

        page.on_login = on_login
        container = Container(
            content=Column(
                controls=[
                    ElevatedButton("Login with Discord", on_click=login_click)
                ]
            )
        )
        super().__init__(
            text=t("tabs.3"), content=container
        )
