from enum import Enum
from typing import Optional

from beanie import Document
from pydantic import BaseModel, Field

from utils.functions import random_id


class BuildType(Enum):
    light = "Light"
    farm = "Farm"
    health = "Health"


class Class(Enum):
    bard = "Bard"
    boomeranger = "Boomeranger"
    candy_barbarian = "Candy Barbarian"
    chloromancer = "Chloromancer"
    dino_tamer = "Dino Tamer"
    dracolyte = "Dracolyte"
    fae_trickster = "Fae Trickster"
    gunslinger = "Gunslinger"
    ice_sage = "Ice Sage"
    knight = "Knight"
    lunar_lancer = "Lunar Lancer"
    neon_ninja = "Neon Ninja"
    pirate_captain = "Pirate Captain"
    revenant = "Revenant"
    shadow_hunter = "Shadow Hunter"
    solarion = "Solarion"
    tomb_raiser = "Tomb Raiser"
    vanguardian = "Vanguardian"


class DamageType(Enum):
    magic = "Magic"
    physical = "Physical"


class Weapon(Enum):
    sword = "Sword"
    bow = "Bow"
    gun = "Gun"
    staff = "Staff"
    spear = "Spear"
    fist = "Fist"


class Attribute(Enum):
    infinite_attackspeed = "Infinite Attack Speed"


class StatName(Enum):
    magic_damage = "Magic Damage"
    physical_damage = "Physical Damage"
    maximum_health = "Maximum Health"
    maximum_health_per = "Maximum Health %"
    energy = "Energy"
    health_regen = "Health Regen"
    energy_regen = "Energy Regen"
    movement_speed = "Movement Speed"
    attack_speed = "Attack Speed"
    jump = "Jump"
    critical_hit = "Critical Hit"
    critical_damage = "Critical Damage"
    light = "Light"


class Stat(BaseModel):
    name: StatName
    value: Optional[float]
    percentage: bool


class AbilityType(Enum):
    active = "Active"
    passive = "Passive"
    upgrade = "Upgrade"


class AbilityStage(BaseModel):
    name: str
    base: float
    multiplier: float


class Ability(BaseModel):
    name: str
    icon: str
    type: AbilityType
    stages: list[AbilityStage]

    @property
    def icon_path(self):
        return f"assets/images/abilities/{self.icon}.png"


class TroveClass(BaseModel):
    name: Class
    qualified_name: str
    shorts: list[str]
    damage_type: DamageType
    weapons: list[Weapon]
    attributes: list[Attribute]
    stats: list[Stat]
    bonuses: list[Stat]
    subclass: dict
    abilities: list[Ability] = []

    @property
    def image_path(self):
        return f"assets/images/classes/{self.name.name}.png"

    @property
    def icon_path(self):
        return f"assets/images/classes/icons/{self.name.name}.png"


class Food(Enum):
    freerange = "Freerange Electrolytic Crystals"
    soup = "Premium Fish Soup"
    fillet = "Premium Fish Fillet"
    kabobs = "Premium Fish Kabobs"


class BuildConfig(Document):
    build_id: str = Field(default_factory=random_id)
    build_type: BuildType = BuildType.light
    character: Class = Class.bard
    subclass: Class = Class.boomeranger
    food: str = "delve_freerange"
    ally: str = "boot_clown"
    berserker_battler: bool = False
    critical_damage_count: int = 3
    no_face: bool = False
    light: int = 0
    subclass_active: bool = False
    star_chart: Optional[str] = None
    # Prediction based
    cosmic_primordial: bool = False
    crystal_5: bool = False

    def __eq__(self, other):
        if not isinstance(other, BuildConfig):
            return False
        keys = [
            "build_type",
            "character",
            "subclass",
            "food",
            "ally",
            "berserker_battler",
            "critical_damage_count",
            "no_face",
            "light",
            "subclass_active",
            "star_chart",
            "cosmic_primordial",
            "crystal_5"
        ]
        for key in keys:
            if getattr(self, key) != getattr(other, key):
                return False
        return True

    def __ne__(self, other):
        return not self.__eq__(other)
