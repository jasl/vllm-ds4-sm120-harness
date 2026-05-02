import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REFERENCE_SELECTION = ROOT / "baselines" / "20260502_correctness_reference_selection.json"


def _load_selection():
    return json.loads(REFERENCE_SELECTION.read_text(encoding="utf-8"))


def test_correctness_reference_selection_records_complete_baseline_dirs():
    selection = _load_selection()

    assert selection["schema_version"] == 1
    assert selection["complete_baseline_dirs"] == [
        "baselines/20260502_b200_tp2_main_5737770c6",
        "baselines/20260502_b200_tp4_main_5737770c6",
        "baselines/20260502_deepseek_official_api_deepseek_v4_flash",
    ]
    for baseline_dir in selection["complete_baseline_dirs"]:
        assert (ROOT / baseline_dir).is_dir()


def test_correctness_reference_selection_identifies_primary_token_oracle():
    selection = _load_selection()
    primary = selection["primary_token_oracle"]

    assert primary["label"] == "b200_tp4_main_5737770c6_nomtp"
    assert primary["variant"] == "nomtp"
    assert primary["baseline_dir"] == "baselines/20260502_b200_tp4_main_5737770c6"
    assert primary["oracle_dir"] == (
        "baselines/20260502_b200_tp4_main_5737770c6/oracle/nomtp"
    )
    assert primary["compatibility_oracle_dir"] == (
        "baselines/20260502_b200_tp4_main_5737770c6/oracle"
    )
    assert primary["token_level_reference"] is True
    assert (ROOT / primary["oracle_dir"]).is_dir()
    assert (ROOT / primary["compatibility_oracle_dir"]).is_dir()


def test_correctness_reference_selection_keeps_variant_and_api_boundaries():
    selection = _load_selection()

    variant_oracles = {item["label"]: item for item in selection["variant_token_oracles"]}
    assert variant_oracles["b200_tp4_main_5737770c6_mtp"]["oracle_dir"] == (
        "baselines/20260502_b200_tp4_main_5737770c6/oracle/mtp"
    )
    assert variant_oracles["b200_tp4_main_5737770c6_mtp"]["compare_only_with"] == "mtp"

    official = {
        item["label"]: item for item in selection["behavior_references"]
    }["deepseek_official_api_deepseek_v4_flash"]
    assert official["baseline_dir"] == (
        "baselines/20260502_deepseek_official_api_deepseek_v4_flash"
    )
    assert official["token_level_reference"] is False
    assert official["use_for"] == [
        "hosted API smoke behavior",
        "hosted API generation behavior",
        "hosted API ToolCall-15 behavior",
    ]


def test_correctness_reference_selection_records_non_interchangeability_evidence():
    selection = _load_selection()
    evidence = selection["non_interchangeable_references"]

    tp2_tp4 = evidence["b200_tp2_vs_b200_tp4_nomtp"]
    assert tp2_tp4["baseline_dirs"] == [
        "baselines/20260502_b200_tp2_main_5737770c6",
        "baselines/20260502_b200_tp4_main_5737770c6",
    ]
    assert tp2_tp4["common_cases"] == 5
    assert tp2_tp4["prompt_token_id_matches"] == 5
    assert tp2_tp4["generated_token_sequence_matches"] == 1
    assert tp2_tp4["token_oracles_are_interchangeable"] is False

    assert evidence["mtp_vs_nomtp"]["token_oracles_are_interchangeable"] is False
