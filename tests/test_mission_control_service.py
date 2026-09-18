from core.analysis import MeetingAnalyzer
from core.mission_control_service import (
    MissionControlSuiviService,
    action_to_grist_fields,
    format_confirmation,
)
from core.models import ActionItem, Decision, MeetingAnalysis


def _make_analysis() -> MeetingAnalysis:
    return MeetingAnalysis(
        meeting_id="meeting-001",
        title="Compte-rendu de suivi — Déploiement du service",
        language="fr",
        summary="Suivi du déploiement.",
        decisions=[
            Decision(description="Pilote validé dans trois départements."),
            Decision(description="Prochain point de suivi lundi à 14h."),
        ],
        actions=[
            ActionItem(
                id="action-1",
                description="Transmettre la liste des agents concernés",
                assignee="Karim",
                due_date="Mercredi",
                status="todo",
                dependency="Bloque la préparation technique prévue vendredi",
            ),
            ActionItem(
                id="action-2",
                description="Préparer la configuration technique",
                assignee="Sarah",
                due_date="Vendredi",
                status="todo",
                dependency="Dépend de la transmission de la liste des agents mercredi",
            ),
        ],
    )


class FakeAnalyzer(MeetingAnalyzer):
    def __init__(self, analysis: MeetingAnalysis) -> None:
        self._analysis = analysis

    def analyze(self, transcript: str) -> MeetingAnalysis:
        return self._analysis


class FakeDocsPublisher:
    def __init__(self, fail: bool = False) -> None:
        self.fail = fail
        self.received = None
        self.last_created_document_id = None

    def __call__(self, analysis: MeetingAnalysis) -> None:
        if self.fail:
            raise RuntimeError("docs unavailable")
        self.received = analysis
        self.last_created_document_id = "doc-999"


class FakeGristPublisher:
    def __init__(self, fail: bool = False) -> None:
        self.fail = fail
        self.received = None
        self.last_created_record_ids: list[int] = []

    def __call__(self, actions: list[dict]) -> None:
        if self.fail:
            raise RuntimeError("grist unavailable")
        self.received = actions
        self.last_created_record_ids = list(range(1, len(actions) + 1))


def test_action_to_grist_fields_preserves_dependency() -> None:
    action = ActionItem(
        id="action-1",
        description="Transmettre la liste des agents concernés",
        assignee="Karim",
        due_date="Mercredi",
        status="todo",
        dependency="Bloque la préparation technique prévue vendredi",
    )

    fields = action_to_grist_fields(action)

    assert fields == {
        "Action": "Transmettre la liste des agents concernés",
        "Responsable": "Karim",
        "Echeance": "Mercredi",
        "Statut": "À faire",
        "Dependance": "Bloque la préparation technique prévue vendredi",
        "Source": "Conversation Buzz",
    }


def test_organise_le_suivi_calls_docs_publisher_with_analysis() -> None:
    analysis = _make_analysis()
    docs_publisher = FakeDocsPublisher()
    grist_publisher = FakeGristPublisher()
    service = MissionControlSuiviService(
        analyzer=FakeAnalyzer(analysis), docs_publisher=docs_publisher, grist_publisher=grist_publisher
    )

    service.organise_le_suivi("some transcript")

    assert docs_publisher.received is analysis


def test_organise_le_suivi_calls_grist_publisher_with_mapped_records() -> None:
    analysis = _make_analysis()
    grist_publisher = FakeGristPublisher()
    service = MissionControlSuiviService(
        analyzer=FakeAnalyzer(analysis),
        docs_publisher=FakeDocsPublisher(),
        grist_publisher=grist_publisher,
    )

    service.organise_le_suivi("some transcript")

    assert grist_publisher.received == [
        action_to_grist_fields(analysis.actions[0]),
        action_to_grist_fields(analysis.actions[1]),
    ]


def test_organise_le_suivi_preserves_dependency_end_to_end() -> None:
    analysis = _make_analysis()
    grist_publisher = FakeGristPublisher()
    service = MissionControlSuiviService(
        analyzer=FakeAnalyzer(analysis),
        docs_publisher=FakeDocsPublisher(),
        grist_publisher=grist_publisher,
    )

    service.organise_le_suivi("some transcript")

    assert grist_publisher.received[0]["Dependance"] == "Bloque la préparation technique prévue vendredi"
    assert grist_publisher.received[1]["Dependance"] == (
        "Dépend de la transmission de la liste des agents mercredi"
    )


def test_organise_le_suivi_reports_success_and_counts() -> None:
    analysis = _make_analysis()
    service = MissionControlSuiviService(
        analyzer=FakeAnalyzer(analysis),
        docs_publisher=FakeDocsPublisher(),
        grist_publisher=FakeGristPublisher(),
    )

    result = service.organise_le_suivi("some transcript")

    assert result.success
    assert result.docs_document_id == "doc-999"
    assert result.grist_record_ids == [1, 2]


def test_format_confirmation_contains_counts_and_blockers() -> None:
    analysis = _make_analysis()
    service = MissionControlSuiviService(
        analyzer=FakeAnalyzer(analysis),
        docs_publisher=FakeDocsPublisher(),
        grist_publisher=FakeGristPublisher(),
    )

    result = service.organise_le_suivi("some transcript")
    confirmation = format_confirmation(result)

    assert "Suivi préparé." in confirmation
    assert "2 décision(s) identifiée(s)." in confirmation
    assert "2 action(s) ajoutée(s) dans Grist." in confirmation
    assert "Compte-rendu créé dans Docs." in confirmation
    assert "Bloque la préparation technique prévue vendredi" in confirmation


def test_organise_le_suivi_handles_docs_failure_without_blocking_grist() -> None:
    analysis = _make_analysis()
    grist_publisher = FakeGristPublisher()
    service = MissionControlSuiviService(
        analyzer=FakeAnalyzer(analysis),
        docs_publisher=FakeDocsPublisher(fail=True),
        grist_publisher=grist_publisher,
    )

    result = service.organise_le_suivi("some transcript")

    assert not result.success
    assert result.docs_error == "docs unavailable"
    assert result.grist_error is None
    assert grist_publisher.received is not None
    assert "Échec de la création du compte-rendu dans Docs" in format_confirmation(result)


def test_organise_le_suivi_handles_grist_failure_without_blocking_docs() -> None:
    analysis = _make_analysis()
    docs_publisher = FakeDocsPublisher()
    service = MissionControlSuiviService(
        analyzer=FakeAnalyzer(analysis),
        docs_publisher=docs_publisher,
        grist_publisher=FakeGristPublisher(fail=True),
    )

    result = service.organise_le_suivi("some transcript")

    assert not result.success
    assert result.grist_error == "grist unavailable"
    assert result.docs_error is None
    assert docs_publisher.received is not None
    assert "Échec de l'ajout des actions dans Grist" in format_confirmation(result)
