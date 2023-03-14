import base64
from enum import Enum
from json import loads
from random import randint, choice
from typing import Any
from copy import copy

from i18n import t
from pydantic import BaseModel, Field

from utils.calculations.gems import max_levels
from uuid import UUID, uuid4


class Stat(Enum):
    light = "Light"
    physical_damage = "Physical Damage"
    magic_damage = "Magic Damage"
    critical_damage = "Critical Damage"
    critical_hit = "Critical Hit"
    maximum_health = "Maximum Health"
    maximum_health_per = "Maximum Health %"


excluded_stats = {Stat.light, Stat.physical_damage, Stat.magic_damage}
all_gem_stats = [s for s in Stat if s not in excluded_stats]
arcane_gem_stats = all_gem_stats + [Stat.magic_damage]
fierce_gem_stats = all_gem_stats + [Stat.physical_damage]
empowered_gem_stats = all_gem_stats + [Stat.physical_damage, Stat.magic_damage]


class GemTier(Enum):
    radiant = "radiant"
    stellar = "stellar"
    # crystal = "crystal" # Disabled until tables are updated


class GemType(Enum):
    lesser = "Lesser"
    empowered = "Empowered"


class GemElement(Enum):
    fire = "Fire"
    water = "Water"
    air = "Air"
    cosmic = "Cosmic"


class GemRestriction(Enum):
    arcane = "Arcane"
    fierce = "Fierce"


class ElementalGemAbility(Enum):
    explosive_epilogue = "Explosive Epilogue"
    volatile_velocity = "Volatile Velocity"
    cubic_curtain = "Cubic Curtain"
    mired_mojo = "Mired Mojo"
    pyrodisc = "Pyrodisc"
    stunburst = "Stunburst"
    spirit_surge = "Spirit Surge"
    stinging_curse = "Stinging Curse"


class CosmicGemAbility(Enum):
    berseker_battler = "Berserker Battler"
    flower_power = "Flower Power"
    empyrean_barrier = "Empyrean Barrier"
    vampirian_vanquisher = "Vampirian Vanquisher"


class Gem(BaseModel):
    uuid: UUID = Field(default_factory=uuid4)
    level: int
    tier: GemTier
    type: GemType
    element: GemElement
    stats: list[list]

    def __eq__(self, other):
        if not hasattr(other, "uuid"):
            return False
        return self.uuid == other.uuid

    def __ne__(self, other):
        return not self.__eq__(other)

    @property
    def pseudo_name(self):
        return t(
            "gem_full_names." +
            " ".join(
                [
                    self.type.value,
                    self.element.value,
                    "Gem"
                ]
            )
        )

    @property
    def max_level(self):
        return max_levels[self.tier.name]

    @classmethod
    def load_gem(cls, raw_data):
        data = loads(base64.b64decode(raw_data).decode("utf-8"))
        return cls(**data)

    def save_gem(self):
        return base64.b64encode(self.json().encode('utf-8'))


class LesserGem(Gem):
    restriction: GemRestriction

    @property
    def name(self):
        return t(
            "gem_full_names." +
            " ".join(
                [
                    self.restriction.value,
                    self.element.value,
                    "Gem"
                ]
            )
        )

    @classmethod
    def random_gem(cls, tier: GemTier = None, element: GemElement = None):
        tier = tier or choice([c for c in GemTier])
        max_level = max_levels[tier.name]
        level = randint(1, max_level+1)
        type = GemType.lesser
        element = element or choice([c for c in GemElement])
        restriction = choice([c for c in GemRestriction])
        stat_names = generate_gem_stats(type, restriction, element)
        max_boosts = divmod(level, 5)[0]
        if max_boosts > 3:
            max_boosts = 3
        stats = []
        for i, stat_name in enumerate(stat_names):
            boosts = randint(0, max_boosts)
            max_boosts -= boosts
            stats.append(
                [
                    i,
                    stat_name.value,
                    boosts,
                    round(randint(0, 100)/100, 2)
                ]
            )
        if max_boosts:
            stats[-1][2] += max_boosts
        return cls(
            level=level,
            tier=tier,
            type=GemType.lesser,
            element=element,
            stats=stats,
            restriction=restriction
        )

    @classmethod
    def maxed_gem(cls, tier: GemTier = None, element: GemElement = None):
        tier = tier or choice([c for c in GemTier])
        level = max_levels[tier.name]
        type = GemType.lesser
        element = element or choice([c for c in GemElement])
        restriction = choice([c for c in GemRestriction])
        stat_names = generate_gem_stats(type, restriction, element)
        max_boosts = divmod(level, 5)[0]
        if max_boosts > 3:
            max_boosts = 3
        stats = []
        for i, stat_name in enumerate(stat_names):
            boosts = randint(0, max_boosts)
            max_boosts -= boosts
            stats.append(
                [
                    i,
                    stat_name.value,
                    boosts,
                    1.0
                ]
            )
        if max_boosts:
            stats[-1][2] += max_boosts
        return cls(
            level=level,
            tier=tier,
            type=GemType.lesser,
            element=element,
            stats=stats,
            restriction=restriction
        )

    def change_restriction(self, restriction: GemRestriction):
        self.restriction = restriction
        for stat in self.stats:
            if self.restriction == GemRestriction.arcane:
                if stat[1] == Stat.physical_damage.value:
                    self.stats[stat[0]][1] = Stat.magic_damage.value
            if self.restriction == GemRestriction.fierce:
                if stat[1] == Stat.magic_damage.value:
                    self.stats[stat[0]][1] = Stat.physical_damage.value

    @property
    def possible_change_stats(self):
        pstats = []
        if self.restriction == GemRestriction.arcane:
            pstats.extend(arcane_gem_stats)
        elif self.restriction == GemRestriction.fierce:
            pstats.extend(fierce_gem_stats)
        for stat in self.stats:
            for pstat in copy(pstats):
                if stat[1] == pstat.value:
                    pstats.remove(pstat)
        return pstats


class EmpoweredGem(Gem):
    ability: Any = None

    @property
    def name(self):
        return t("gem_abilities." + self.ability.value)

    @property
    def possible_abilities(self):
        return list(ElementalGemAbility) if self.element != GemElement.cosmic else list(CosmicGemAbility)

    @classmethod
    def random_gem(cls, tier: GemTier = None, element: GemElement = None):
        tier = tier or choice([c for c in GemTier])
        max_level = max_levels[tier.name]
        level = randint(1, max_level+1)
        type = GemType.empowered
        element = element or choice([c for c in GemElement])
        ability_set = ElementalGemAbility if element != GemElement.cosmic else CosmicGemAbility
        ability = choice(list(ability_set))
        stat_names = generate_gem_stats(type, None, element)
        max_boosts = divmod(level, 5)[0]
        if max_boosts > 3:
            max_boosts = 3
        stats = []
        for i, stat_name in enumerate(stat_names):
            boosts = randint(0, max_boosts)
            max_boosts -= boosts
            stats.append(
                [
                    i,
                    stat_name.value,
                    boosts,
                    round(randint(0, 1000)/1000, 3)
                ]
            )
        if max_boosts:
            stats[-1][2] += max_boosts
        return cls(
            level=level,
            tier=tier,
            type=type,
            element=element,
            stats=stats,
            ability=ability
        )

    @classmethod
    def maxed_gem(cls, tier: GemTier = None, element: GemElement = None):
        tier = tier or choice([c for c in GemTier])
        level = max_levels[tier.name]
        type = GemType.empowered
        element = element or choice([c for c in GemElement])
        ability_set = ElementalGemAbility if element != GemElement.cosmic else CosmicGemAbility
        ability = choice(list(ability_set))
        stat_names = generate_gem_stats(type, None, element)
        max_boosts = divmod(level, 5)[0]
        if max_boosts > 3:
            max_boosts = 3
        stats = []
        for i, stat_name in enumerate(stat_names):
            boosts = randint(0, max_boosts)
            max_boosts -= boosts
            stats.append(
                [
                    i,
                    stat_name.value,
                    boosts,
                    1.0
                ]
            )
        if max_boosts:
            stats[-1][2] += max_boosts
        return cls(
            level=level,
            tier=tier,
            type=type,
            element=element,
            stats=stats,
            ability=ability
        )

    @property
    def possible_change_stats(self):
        pstats = []
        pstats.extend(empowered_gem_stats)
        for stat in self.stats:
            for pstat in copy(pstats):
                if stat[1] == pstat.value:
                    pstats.remove(pstat)
        return pstats


def generate_gem_stats(type, restriction, element):
    stats = []
    if type == GemType.lesser:
        if restriction == GemRestriction.arcane:
            available_stats = arcane_gem_stats
        elif restriction == GemRestriction.fierce:
            available_stats = fierce_gem_stats
        if element == GemElement.cosmic:
            stats.append(Stat.light)
    elif type == GemType.empowered:
        available_stats = empowered_gem_stats
        if element == GemElement.cosmic:
            stats.append(Stat.light)
    while len(stats) < 3:
        stat = choice(available_stats)
        if stat in stats:
            continue
        if stat == Stat.physical_damage and Stat.magic_damage in stats:
            continue
        if stat == Stat.magic_damage and Stat.physical_damage in stats:
            continue
        stats.append(stat)
    return stats
