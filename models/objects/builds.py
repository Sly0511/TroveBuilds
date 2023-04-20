from pydantic import BaseModel
from enum import Enum
from typing import Optional


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

    @property
    def image_path(self):
        return f"assets/images/classes/{self.name.name}.png"

    @property
    def icon_path(self):
        return f"assets/images/classes/icons/{self.name.name}.png"


class StarChartConfig(BaseModel):
    ...


class Food(Enum):
    freerange = "Freerange Electrolytic Crystals"
    soup = "Premium Fish Soup"
    fillet = "Premium Fish Fillet"
    kabobs = "Premium Fish Kabobs"


class BuildConfig(BaseModel):
    build_type: BuildType = BuildType.light
    character: Class = Class.bard
    subclass: Class = Class.boomeranger
    food: Food = Food.freerange
    berserker_battler: bool = False
    critical_damage_count: int = 3
    no_face: bool = False
    light: int = 0
    subclass_active: bool = False
    star_chart: Optional[StarChartConfig] = None
    # Prediction based
    cosmic_primordial: bool = False
    crystal_5: bool = False
