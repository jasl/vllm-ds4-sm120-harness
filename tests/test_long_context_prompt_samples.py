from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROMPT_ROOT = ROOT / "prompts" / "long_context"


def test_bundled_long_context_prompt_samples_are_available():
    expected = {
        "ds4_story_recall.txt": 100_000,
        "ds4_security_audit.txt": 100_000,
    }

    for name, min_bytes in expected.items():
        path = PROMPT_ROOT / name
        assert path.exists()
        assert path.stat().st_size >= min_bytes
        assert not path.read_text(encoding="utf-8").startswith("/")


def test_bundled_long_context_prompt_samples_do_not_include_local_paths():
    forbidden = ("/Users/", "/home/", "10.0.0.")

    for path in PROMPT_ROOT.glob("*.txt"):
        text = path.read_text(encoding="utf-8")
        for item in forbidden:
            assert item not in text


def test_bundled_long_context_prompt_samples_preserve_ds4_license_notice():
    readme = (PROMPT_ROOT / "README.md").read_text(encoding="utf-8")
    license_text = (PROMPT_ROOT / "LICENSE.ds4").read_text(encoding="utf-8")

    assert "ds4.c" in readme
    assert "MIT License" in license_text
    assert "Copyright (c) 2026 The ds4.c authors" in license_text
