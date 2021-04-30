import re

from dadguide.models.monster_model import MonsterModel
from dadguide.token_mappings import AWAKENING_TOKENS, inverse_map, AWOKEN_MAP, AWAKENING_EQUIVALENCES


def regexlist(tokens):
    return '(?:' + '|'.join(re.escape(t) for t in tokens) + ")"


class Token:
    def __init__(self, value, *, negated=False, exact=False):
        self.value = value
        self.negated = negated
        self.exact = exact

    def matches(self, other: MonsterModel) -> bool:
        return True

    def __eq__(self, other):
        if isinstance(other, Token):
            return self.__dict__ == other.__dict__
        elif isinstance(other, str):
            return self.value == other

    def __hash__(self):
        return hash(self.value)

    def __repr__(self):
        return ("-" if self.negated else "") + (repr(self.value) if self.exact else self.value)


class SpecialToken(Token):
    RE_MATCH = r""

    def __init__(self, value, *, negated=False, exact=False, database):
        self.database = database
        super().__init__(value, negated=negated, exact=exact)

    def matches(self, other: MonsterModel) -> bool:
        return False

    def __repr__(self):
        return f"{self.__class__.__name__}(token={super().__repr__()})"


class MultipleAwakeningToken(SpecialToken):
    RE_MATCH = rf"(\d+)-(sa-)?-?({regexlist(AWAKENING_TOKENS)})"

    def __init__(self, value, *, negated=False, exact=False, database):
        count, sa, value = re.fullmatch(self.RE_MATCH, value).groups()
        self.count = int(count)
        self.sa = bool(sa)
        super().__init__(value, negated=negated, exact=exact, database=database)

    def matches(self, other):
        awlist = other.awakenings
        if not self.sa:
            awlist = awlist[:-other.superawakening_count]

        c = 0
        for aw in inverse_map(AWOKEN_MAP)[self.value]:
            aw = self.database.awoken_skill_map[aw.value]
            for maw in awlist:
                if maw == aw:
                    c += 1
                elif (eq := AWAKENING_EQUIVALENCES.get(maw.awoken_skill_id)) and eq[1] == aw.awoken_skill_id:
                    # Hack - if we are matching a plus version of an awakening here, then we're adding
                    # the correct number of awakenings FOR THE PLUS VERSION here. However, we will
                    # have also, on another pass, matched the token against the base version of
                    # the awakening, adding 1 too many to the total. So subtract one from the total
                    # here to compensate.
                    # A better approach would be to identify the case when we match the base awakening
                    # and not add that in the first place, but doing so is difficult and this works.
                    c += eq[0] - 1
            if c >= self.count:
                return True
        return False

    def __repr__(self):
        return super().__repr__() + f"<sa:{self.sa}, count:{self.count}>"



SPECIAL_TOKEN_TYPES = [
    MultipleAwakeningToken,
]