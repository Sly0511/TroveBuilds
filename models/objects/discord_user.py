from pydantic import BaseModel, Field
from typing import Optional


class DiscordUser(BaseModel):
    id: int
    username: str
    global_name: Optional[str]
    display_name: Optional[str]
    avatar: Optional[str]
    discriminator: Optional[str]
    public_flags: int
    flags: int
    banner: Optional[str]
    banner_color: Optional[str]
    accent_color: Optional[str]
    locale: Optional[str]
    mfa_enabled: bool
    premium_type: int
    avatar_decoration: Optional[str]

    @property
    def display_name(self):
        return self.username

    @property
    def formatted_display_name(self):
        return "@" + self.username + f" [{self.id}]"

    def avatar_url(self, size=64):
        return "https://cdn.discordapp.com/avatars/" + str(self.id) + "/" + self.avatar + f".png?size={size}"
