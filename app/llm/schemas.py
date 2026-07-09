from enum import StrEnum

from pydantic import BaseModel


class ChangeType(StrEnum):
    BUFF = "buff"
    NERF = "nerf"
    ADJUSTMENT = "adjustment"
    REWORK = "rework"
    BUG_FIX = "bug_fix"
    NEW = "new"
    REMOVED = "removed"


class EntityType(StrEnum):
    CHAMPION = "champion"
    ITEM = "item"
    SYSTEM = "system"
    RUNE = "rune"
    OTHER = "other"


class PatchNoteChange(BaseModel):
    entity_name: str
    entity_type: EntityType
    change_type: ChangeType
    summary: str


class PatchNoteClassification(BaseModel):
    patch_version: str
    source_url: str
    changes: list[PatchNoteChange]
    overall_summary: str
