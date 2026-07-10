"""Q.1a structural contract for `KClaimExtraction` (`core/schemas.py`).

Structural only — semantic mechanism-vs-recipe discipline (name-deletion on
`statement`) is enforced later in Q.2b/Q.3, NOT here.
"""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from core.schemas import ClaimFlag, EdgeProposal, ExtractedClaim, KClaimExtraction


def _claim(**overrides: object) -> dict:
    base = {
        "statement": "Retrieval latency is bounded by index shard fan-out, not corpus size.",
        "falsification": "Doubling corpus size while holding shard count fixed leaves p99 latency unchanged.",
        "sources": ["shard_count=8 ← paper.md «we shard the index into 8 partitions»"],
        "status": "supported",
        "tags": ["retrieval"],
        "flags": [],
    }
    base.update(overrides)
    return base


def _edge(**overrides: object) -> dict:
    base = {
        "target_stem": "some-vault-node",
        "edge_type": "derives_from",
        "source_citation": "Smith et al. 2024, related work section",
    }
    base.update(overrides)
    return base


def test_model_json_schema_renders() -> None:
    schema = KClaimExtraction.model_json_schema()
    assert isinstance(schema, dict)
    assert "properties" in schema


def test_valid_instance_validates_and_provenance_defaults() -> None:
    instance = KClaimExtraction(claims=[_claim()], proposed_edges=[])
    assert len(instance.claims) == 1
    assert instance.proposed_edges == []
    assert instance.provenance == "ai-suggested"


def test_kclaim_extraction_rejects_unknown_key() -> None:
    with pytest.raises(ValidationError):
        KClaimExtraction(claims=[_claim()], proposed_edges=[], unexpected_field="nope")


def test_extracted_claim_rejects_unknown_key() -> None:
    with pytest.raises(ValidationError):
        ExtractedClaim(**_claim(unexpected_field="nope"))


def test_claims_zero_raises() -> None:
    with pytest.raises(ValidationError):
        KClaimExtraction(claims=[], proposed_edges=[])


def test_claims_six_raises() -> None:
    with pytest.raises(ValidationError):
        KClaimExtraction(claims=[_claim() for _ in range(6)], proposed_edges=[])


def test_claims_one_passes() -> None:
    instance = KClaimExtraction(claims=[_claim() for _ in range(1)], proposed_edges=[])
    assert len(instance.claims) == 1


def test_claims_five_passes() -> None:
    instance = KClaimExtraction(claims=[_claim() for _ in range(5)], proposed_edges=[])
    assert len(instance.claims) == 5


def test_edge_proposal_rejects_bad_edge_type() -> None:
    with pytest.raises(ValidationError):
        EdgeProposal(**_edge(edge_type="relates_to"))


def test_edge_proposal_accepts_valid_edge_types() -> None:
    EdgeProposal(**_edge(edge_type="derives_from"))
    EdgeProposal(**_edge(edge_type="contradicts"))


_ITD_TOKENS = ("insight", "thought", "decision")


def _assert_no_itd_fields(model: type) -> None:
    field_names = set(model.model_fields)
    for name in field_names:
        lowered = name.lower()
        assert not any(token in lowered for token in _ITD_TOKENS), (
            f"{model.__name__}.{name} looks like an Insight/Thought/Decision field"
        )


def test_no_model_admits_an_itd_field() -> None:
    for model in (ExtractedClaim, EdgeProposal, KClaimExtraction):
        _assert_no_itd_fields(model)


def test_claim_flag_is_functional_defect_vocabulary() -> None:
    # Sanity: the flag vocabulary is closed and by-function, not by paper type.
    assert {flag.value for flag in ClaimFlag} == {
        "no_ablation",
        "math_decoration",
        "result_ungrounded",
        "method_orphaned",
        "suspicious_dependency",
    }
