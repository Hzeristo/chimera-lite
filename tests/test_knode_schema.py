"""Structural contract for the rebuilt Phase Q extraction schema (`core/schemas.py`).

friction-260710-02 rebuild: the payload is a READER'S node (synthesis + lens + attack + claims),
with claims as the epistemic floor. Structural only — semantic mechanism-vs-recipe discipline
(name-deletion on `statement`) is enforced by the extraction prompt + human review, NOT here.
"""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from core.schemas import (
    AttackVectors,
    ClaimFlag,
    ClaimSource,
    EdgeProposal,
    ExtractedClaim,
    KNodeExtraction,
    LensCritique,
    LensFinding,
    PaperSynthesis,
)


def _claim(**overrides: object) -> dict:
    base = {
        "title": "Latency bounded by shard fan-out, not corpus size",
        "statement": "Retrieval latency is bounded by index shard fan-out, not corpus size.",
        "falsification": "Doubling corpus size while holding shard count fixed leaves p99 latency unchanged.",
        "status": "supported",
        "sources": [{"quote": "we shard the index into 8 partitions", "location": "Section 3"}],
        "tags": ["retrieval"],
        "flags": [],
    }
    base.update(overrides)
    return base


def _lens(name: str = "Forensic Leakage Audit") -> dict:
    return {
        "lens_name": name,
        "triggered_by": "Reports benchmark gains without ablating prompt asymmetry.",
        "findings": [{"heading": "Baseline Asymmetry", "body": "Baselines run 0-shot; method gets CoT."}],
        "verdict": "The gain is real but the comparison is not fairly matched.",
    }


def _node(n_claims: int = 1, n_lenses: int = 1, **overrides: object) -> dict:
    base = {
        "title": "MemAgent: RL-Driven Memory Overwrite for Unbounded Context",
        "synthesis": {
            "bb_analysis": "A competent buffer trick wearing a memory costume.",
            "mechanism": "Chunks are read sequentially; a fixed token buffer is overwritten each step.",
            "algorithm_steps": ["Split into chunks", "Overwrite buffer", "Answer from buffer"],
        },
        "lenses": [_lens() for _ in range(n_lenses)],
        "attack": {
            "vectors": ["Monolithic overwrite discards contradictory early evidence."],
            "beat_baseline": "Hybrid memory: compression cache + retrieval over raw chunks.",
            "exploit_flaw": "Ask a question needing early+late contradictory evidence.",
        },
        "claims": [_claim() for _ in range(n_claims)],
    }
    base.update(overrides)
    return base


def test_model_json_schema_renders() -> None:
    schema = KNodeExtraction.model_json_schema()
    assert isinstance(schema, dict)
    assert "properties" in schema


def test_valid_node_validates() -> None:
    node = KNodeExtraction(**_node())
    assert node.title.startswith("MemAgent")
    assert len(node.lenses) == 1
    assert node.lenses[0].lens_name == "Forensic Leakage Audit"
    assert node.synthesis.algorithm_steps  # populated
    assert len(node.claims) == 1


def test_node_rejects_unknown_key() -> None:
    with pytest.raises(ValidationError):
        KNodeExtraction(**_node(), unexpected_field="nope")


def test_lenses_zero_raises() -> None:
    with pytest.raises(ValidationError):
        KNodeExtraction(**_node(n_lenses=0))


def test_lenses_default_one_hybrid_two_pass_three_raises() -> None:
    # Default is one lens; a second fires only for a genuine hybrid; never more than two.
    assert len(KNodeExtraction(**_node(n_lenses=1)).lenses) == 1
    assert len(KNodeExtraction(**_node(n_lenses=2)).lenses) == 2
    with pytest.raises(ValidationError):
        KNodeExtraction(**_node(n_lenses=3))


def test_claim_source_requires_quote_and_location() -> None:
    ClaimSource(quote="we shard into 8", location="Section 3")
    with pytest.raises(ValidationError):
        ClaimSource(quote="only a quote")  # location required — quote-or-drop discipline


def test_claims_zero_raises() -> None:
    with pytest.raises(ValidationError):
        KNodeExtraction(**_node(n_claims=0))


def test_claims_six_raises() -> None:
    with pytest.raises(ValidationError):
        KNodeExtraction(**_node(n_claims=6))


def test_claims_one_and_five_pass() -> None:
    assert len(KNodeExtraction(**_node(n_claims=1)).claims) == 1
    assert len(KNodeExtraction(**_node(n_claims=5)).claims) == 5


def test_extracted_claim_rejects_unknown_key() -> None:
    with pytest.raises(ValidationError):
        ExtractedClaim(**_claim(unexpected_field="nope"))


def test_edge_proposal_rejects_bad_edge_type() -> None:
    with pytest.raises(ValidationError):
        EdgeProposal(target_stem="x", edge_type="relates_to", source_citation="y")


def test_edge_proposal_accepts_valid_edge_types() -> None:
    EdgeProposal(target_stem="x", edge_type="derives_from", source_citation="y")
    EdgeProposal(target_stem="x", edge_type="contradicts", source_citation="y")


def test_extraction_payload_proposes_no_edges() -> None:
    # D4: extraction produces content only; grounding (citation-resolution) mints edges.
    # The LLM payload must therefore carry NO edge field.
    assert not any("edge" in name.lower() for name in KNodeExtraction.model_fields)


_ITD_TOKENS = ("insight", "thought", "decision")


def _assert_no_itd_fields(model: type) -> None:
    for name in model.model_fields:
        lowered = name.lower()
        assert not any(token in lowered for token in _ITD_TOKENS), (
            f"{model.__name__}.{name} looks like an Insight/Thought/Decision field"
        )


def test_no_model_admits_an_itd_field() -> None:
    for model in (
        ClaimSource,
        ExtractedClaim,
        PaperSynthesis,
        LensFinding,
        LensCritique,
        AttackVectors,
        EdgeProposal,
        KNodeExtraction,
    ):
        _assert_no_itd_fields(model)


def test_claim_flag_is_functional_defect_vocabulary() -> None:
    # The flag vocabulary is closed and by-function, not by paper type.
    assert {flag.value for flag in ClaimFlag} == {
        "no_ablation",
        "math_decoration",
        "result_ungrounded",
        "method_orphaned",
        "suspicious_dependency",
    }
