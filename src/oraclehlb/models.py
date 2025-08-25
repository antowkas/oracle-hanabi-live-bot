from enum import Enum
from typing import List, Dict

from pydantic import BaseModel, Field


class ActionType(str, Enum):
    PLAY = "play"
    DISCARD = "discard"
    RANK_CLUE = "clueRank"
    SUIT_CLUE = "clueSuit"


class Card(BaseModel):
    order: int
    suit_index: int
    rank: int


class GameState(BaseModel):
    table_id: int
    player_names: List[str] = []
    our_player_index: int = -1
    hands: Dict[int, List[Card]] = Field(default_factory=dict)
    clue_tokens: int = 8
    mistake_tokens: int = 3
    current_player_index: int = 0
