from flet.auth.oauth_provider import OAuthProvider


class DiscordOAuth2(OAuthProvider):
    def __init__(self,
        client_id: str,
        client_secret: str,
        redirect_url: str = "https://trovetools.slynx.xyz/api/oauth/redirect"
    ):
        super().__init__(
            client_id=client_id,
            client_secret=client_secret,
            authorization_endpoint="https://discord.com/oauth2/authorize",
            token_endpoint="https://discord.com/api/oauth2/token",
            redirect_url=redirect_url,
            scopes=["identify"],
            user_endpoint="https://discord.com/api/users/@me"
        )
