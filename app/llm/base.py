from abc import ABC, abstractmethod

from app.llm.schemas import PatchNoteClassification

CLASSIFICATION_RUBRIC = """\
You classify League of Legends patch notes. For each individual change described \
in the patch notes, identify:
- entity_name: the champion, item, rune, or system the change applies to, named \
exactly as it appears in the patch notes.
- entity_type: champion, item, system, rune, or other.
- change_type: buff (a numeric or qualitative improvement), nerf (a reduction), \
adjustment (a change that is neither strictly a buff nor a nerf, e.g. a numbers \
shuffle), rework (a substantial redesign), bug_fix, new (a newly added entity), \
or removed.
- summary: one concise sentence describing the specific change.

Also provide the patch_version (e.g. "14.3") and a short overall_summary of the \
patch's most notable themes.

Only report changes actually present in the patch notes. Do not invent changes or \
speculate about balance impact beyond what is stated.\
"""


class LLMProvider(ABC):
    """Shared contract for fetching and classifying League of Legends patch notes via an LLM."""

    def __init__(self, api_key: str, model: str):
        self.api_key = api_key
        self.model = model

    @abstractmethod
    async def fetch_and_classify(self, url: str) -> PatchNoteClassification:
        """Fetch the patch notes at `url` and return a validated classification.

        Raises:
            LLMFetchError: the provider could not retrieve the URL content.
            LLMClassificationError: the model call failed or its output did not
                validate against `PatchNoteClassification`.
        """

    def build_system_prompt(self) -> str:
        return CLASSIFICATION_RUBRIC

    def build_user_prompt(self, url: str) -> str:
        return (
            f"Fetch the League of Legends patch notes at {url} and classify every "
            "change according to the rubric in the system prompt."
        )
