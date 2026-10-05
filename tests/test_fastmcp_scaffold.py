"""SK-07: fastmcp scaffold + evals for one EPUB tool (list_chapters).

Runs the 3 YAML cases (evals/mcp_eval_toc_extract_cite.yaml) for real:
builds the fixture EPUB into tmp, calls list_chapters, checks assertions
and QA-row phrases. Falls back to text-shape checks when PyYAML is absent.
Touches only its own fixture; never the live server or the skills tree.
"""
import inspect
import json
from pathlib import Path

import pytest

import mcp_server.fastmcp_scaffold as sc

EVAL_YAML = Path(__file__).resolve().parent.parent / "evals" / "mcp_eval_toc_extract_cite.yaml"
CASE_NAMES = ("toc-lists-in-order", "extract-one-section", "cite-spots-check")


def _load_eval():
    yaml = pytest.importorskip("yaml")
    return yaml.safe_load(EVAL_YAML.read_text(encoding="utf-8"))


def _build_fixture(spec: dict, root: Path) -> Path:
    for rel, content in spec["files"].items():
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    return root


def test_eval_yaml_shape_and_qa_rows() -> None:
    """Every case names its tool call, assertions, and QA rows (q + must)."""
    try:
        spec = _load_eval()
    except pytest.skip.Exception:
        text = EVAL_YAML.read_text(encoding="utf-8")
        for name in CASE_NAMES:
            assert name in text, name
        assert "q:" in text and "must:" in text
        return
    assert spec["tool"] == "list_chapters"
    assert spec["target"] == "mcp_server.fastmcp_scaffold"
    assert [c["name"] for c in spec["cases"]] == list(CASE_NAMES)
    assert set(spec["fixture"]["files"]) >= {
        "META-INF/container.xml", "OEBPS/content.opf", "OEBPS/toc.ncx",
        "OEBPS/Text/ch1.xhtml", "OEBPS/Text/ch2.xhtml", "OEBPS/Text/ch3.xhtml",
    }
    for case in spec["cases"]:
        assert case["call"]["tool"] == "list_chapters"
        assert case["call"]["args"] == {"epub_dir": "<fixture>"}
        assert isinstance(case["qa"]["q"], str) and case["qa"]["q"].strip()
        assert len(case["qa"]["must"]) >= 2


def test_case_toc_lists_in_spine_order(tmp_path: Path) -> None:
    spec = _load_eval()
    case = next(c for c in spec["cases"] if c["name"] == "toc-lists-in-order")
    epub = _build_fixture(spec["fixture"], tmp_path)
    out = sc.list_chapters(str(epub))
    assert [c["href"] for c in out] == case["assert"]["order"]
    blob = json.dumps(out)
    for phrase in case["qa"]["must"]:
        assert phrase in blob, phrase


def test_case_extract_one_section(tmp_path: Path) -> None:
    spec = _load_eval()
    case = next(c for c in spec["cases"] if c["name"] == "extract-one-section")
    epub = _build_fixture(spec["fixture"], tmp_path)
    out = sc.list_chapters(str(epub))
    text = (epub / out[case["assert"]["read_index"]]["href"]).read_text(encoding="utf-8")
    for phrase in case["assert"]["must_contain"] + case["qa"]["must"]:
        assert phrase in text, phrase


def test_case_cite_spots_check(tmp_path: Path) -> None:
    spec = _load_eval()
    case = next(c for c in spec["cases"] if c["name"] == "cite-spots-check")
    epub = _build_fixture(spec["fixture"], tmp_path)
    out = sc.list_chapters(str(epub))
    assert len(out) >= case["assert"]["min_chapters"]
    assert case["assert"]["require_href_and_title"] is True
    for chap in out:
        assert chap["href"] and chap["title"]
        assert set(chap) >= {"index", "id", "href", "title"}


def test_input_schema_derived_from_signature() -> None:
    sig = inspect.signature(sc.list_chapters)
    assert list(sig.parameters) == ["epub_dir"]
    assert sc.INPUT_SCHEMA["type"] == "object"
    assert set(sc.INPUT_SCHEMA["properties"]) == {"epub_dir"}
    assert sc.INPUT_SCHEMA["required"] == ["epub_dir"]
    assert sc.TOOL["name"] == "list_chapters"
    assert "table of contents" in sc.TOOL["description"].lower()


def test_validate_args_accepts_good_rejects_bad() -> None:
    ok, cleaned = sc._validate_list_chapters_args({"epub_dir": "some/dir"})
    assert ok and cleaned == {"epub_dir": "some/dir"}
    for bad in ({}, {"epub_dir": ""}, {"epub_dir": "  "},
                {"epub_dir": 7}, {"epub_dir": None}, "epub_dir"):
        ok, _ = sc._validate_list_chapters_args(bad)
        assert not ok, bad


def test_bad_dirs_raise_value_error(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="non-empty"):
        sc.list_chapters("  ")
    with pytest.raises(ValueError, match="not found"):
        sc.list_chapters(str(tmp_path / "missing"))
    lone = tmp_path / "file.txt"
    lone.write_text("x", encoding="utf-8")
    with pytest.raises(ValueError, match="not a directory"):
        sc.list_chapters(str(lone))


def test_fallback_without_opf_lists_sorted(tmp_path: Path) -> None:
    (tmp_path / "b.html").write_text("<p>b</p>", encoding="utf-8")
    (tmp_path / "a.xhtml").write_text("<p>a</p>", encoding="utf-8")
    out = sc.list_chapters(str(tmp_path))
    assert [c["href"] for c in out] == ["a.xhtml", "b.html"]
    assert [c["index"] for c in out] == [0, 1]


def test_tool_registered_on_mcp_app() -> None:
    if sc.BACKEND == "stdlib-shim":
        assert sc.mcp.tools["list_chapters"] is sc.list_chapters
    else:
        assert sc.BACKEND == "fastmcp"
