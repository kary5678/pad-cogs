from typing import TYPE_CHECKING

from discordmenu.embed.base import Box
from discordmenu.embed.components import EmbedField, EmbedMain
from discordmenu.embed.text import LabeledText
from discordmenu.embed.view import EmbedView
from tsutils.menu.components.footers import embed_footer_with_state
from tsutils.tsubaki.custom_emoji import get_attribute_emoji_by_monster
from tsutils.tsubaki.monster_header import MonsterHeader

if TYPE_CHECKING:
    from dbcog.models.monster_model import MonsterModel


class IdTracebackViewProps:
    def __init__(self, monster: "MonsterModel", score: int, name_tokens: str,
                 modifier_tokens: str, lower_priority_monsters: str):
        self.lower_priority_monsters = lower_priority_monsters
        self.modifier_tokens = modifier_tokens
        self.name_tokens = name_tokens
        self.score = score
        self.monster = monster


def get_title(monster: "MonsterModel"):
    return f"{get_attribute_emoji_by_monster(monster)} {monster.name_en} ({monster.monster_id})"


def get_description(score: int):
    return Box(
        LabeledText(
            'Total score',
            str(round(score, 2))
        )
    )


class IdTracebackView:
    VIEW_TYPE = 'IdTraceback'

    @staticmethod
    def embed(state, props: IdTracebackViewProps):
        return EmbedView(
            EmbedMain(
                color=state.color,
                title=MonsterHeader.menu_title(props.monster, use_emoji=True),
                description=get_description(props.score)
            ),
            embed_fields=[
                EmbedField('Matched Name Tokens', Box(props.name_tokens)),
                EmbedField('Matched Modifier Tokens', Box(props.modifier_tokens)),
                EmbedField('Equally-scoring matches', Box(props.lower_priority_monsters)),
            ],
            embed_footer=embed_footer_with_state(state),
        )
