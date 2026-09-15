import os

from core.integrations.la_suite_docs_client import create_document_for_owner
from core.integrations.markdown_formatter import format_meeting_analysis_as_markdown
from core.models import MeetingAnalysis

DEFAULT_BASE_URL = "http://localhost:18071/api/v1.0"


class LaSuiteDocsPublisher:
    def __init__(
        self,
        base_url: str | None = None,
        token: str | None = None,
        owner_sub: str | None = None,
        owner_email: str | None = None,
    ) -> None:
        self.base_url = base_url or os.environ.get("LA_SUITE_DOCS_BASE_URL", DEFAULT_BASE_URL)
        self.token = token or os.environ["LA_SUITE_DOCS_TOKEN"]
        self.owner_sub = owner_sub or os.environ["LA_SUITE_DOCS_OWNER_SUB"]
        self.owner_email = owner_email or os.environ["LA_SUITE_DOCS_OWNER_EMAIL"]
        self.last_created_document_id: str | None = None

    def __call__(self, analysis: MeetingAnalysis) -> None:
        content = format_meeting_analysis_as_markdown(analysis)

        result = create_document_for_owner(
            base_url=self.base_url,
            token=self.token,
            title=analysis.title,
            content=content,
            sub=self.owner_sub,
            email=self.owner_email,
        )

        self.last_created_document_id = result.get("id")
