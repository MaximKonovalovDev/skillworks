# Steal port: fuzzitdev/pythonfuzz@2434a92, pythonfuzz/ + examples/ (licence Apache-2.0/AGPL dual)
# Source: https://github.com/fuzzitdev/pythonfuzz/tree/2434a92c69fdb2d0f83e88194ffafd32f70d2f3e/pythonfuzz
# IDEA-ONLY, never pasted: coverage-guided pattern (Fuzz(buf) entry + corpus/crashes dirs + examples)
# rebuilt fresh here as a stdlib-only deterministic seeded mutator over our own split/extract pure functions.
"""Seed-corpus fuzz harness for extract/split parsers (stdlib only, no new dep)."""
from __future__ import annotations
import random
from pathlib import Path
from book2skill import extract as extract_mod
from book2skill import split as split_mod
from book2skill import split_chapters as sc_mod
SEED = 20261009
N_CASES = 200
CORPUS_DIR_NAME = "corpus"
CRASHES_DIR_NAME = "crashes"
TOKENS: tuple[bytes, ...] = (b"# ", b"## ", b"```", b"~~~~", b"----", b"====", b"=======", b"*** START OF THE PROJECT GUTENBERG ***", b"*** END OF THE PROJECT GUTENBERG ***", b"| a | b |", b"| --- | --- |", b"---\ntitle: x\n---\n", b"\x00", b"\xff\xfe", b"\r\n", b"\t", b"cafe", b"\n", b"A" * 64)
SEED_CORPUS: tuple[bytes, ...] = (b"# Alpha\n\nplain body\n", b"== Real\n\nbody\n\n----\n== Fake\n# Also fake\n----\n\n== Next\n\nmore\n", b"*** START OF THE PROJECT GUTENBERG ***\nheader\nbody line\n*** END OF THE PROJECT GUTENBERG ***\n", b"```\n# hidden\n```\n# Visible\n", b"`````\n# Hidden one\n```\n# Hidden two\n`````\n# Visible\n", b"| a | b |\n| --- | --- |\n| 1 | 2 |\n", b"---\ntitle: demo\n---\n# T\n\ntext\n", b"Cafe au lait\n\n# Test\n", b"", b"\x00\xff\xfe\r\n\t ", b"A" * 6000 + b"\n# Tail\n", b"== Same\n\na\n\n== Same\n\nb\n")
EXAMPLES: tuple[bytes, ...] = (b"# Example one\n\nbody\n", b"== Example two\n\n----\ncode\n----\n", b"*** START OF THE PROJECT GUTENBERG ***\nintro\n")
def _mutate(rng: random.Random, data: bytes) -> bytes:
    if not data:
        data = rng.choice(SEED_CORPUS)
    op = rng.randrange(4)
    if op == 0 and data:
        pos = rng.randrange(len(data))
        return data[:pos] + bytes((rng.randrange(256),)) + data[pos + 1:]
    if op == 1:
        pos = rng.randrange(len(data) + 1)
        return data[:pos] + rng.choice(TOKENS) + data[pos:]
    if op == 2 and data:
        pos = rng.randrange(len(data))
        end = min(len(data), pos + rng.randrange(1, 9))
        return data[:pos] + data[end:]
    if data:
        pos = rng.randrange(len(data))
        end = min(len(data), pos + rng.randrange(1, 9))
        ins = rng.randrange(len(data) + 1)
        return data[:ins] + data[pos:end] + data[ins:]
    return rng.choice(TOKENS)
def _chunk_spans(n: int, chunk: int = split_mod.CHUNK, overlap: int = split_mod.OVERLAP) -> list[tuple[int, int]]:
    spans: list[tuple[int, int]] = []
    i = 0
    while i < n:
        spans.append((i, min(n, i + chunk)))
        if i + chunk >= n:
            break
        i += chunk - overlap
    return spans
def fuzz(buf: bytes) -> None:
    text = bytes(buf).decode("utf-8", errors="replace")
    extract_mod.strip_gutenberg_markers(text)
    extract_mod.md_counts(text)
    extract_mod._md_table_row(text.split("|"))
    extract_mod._FRONT_MATTER.sub("", text, count=1)
    extract_mod._use_markitdown("auto", ".pdf")
    sc_mod.slug(text[:80] or "x")
    lines = text.splitlines()[:50]
    for line in lines:
        sc_mod._fence_kind(line)
        sc_mod.is_fence(line)
    sc_mod.iter_headings(text)
    sc_mod.detect_chapters(text)
    spans = _chunk_spans(len(text))
    assert all(a < b for a, b in spans)
    if spans:
        assert spans[0][0] == 0 and spans[-1][1] == len(text)
def _run_harness(n: int = N_CASES) -> list[tuple[int, bytes, str]]:
    rng = random.Random(SEED)
    crashes: list[tuple[int, bytes, str]] = []
    for case in range(n):
        base = SEED_CORPUS[case % len(SEED_CORPUS)]
        buf = _mutate(rng, base)
        try:
            fuzz(buf)
        except Exception as exc:
            crashes.append((case, buf, "%r: %s" % (type(exc).__name__, exc)))
    return crashes
def _write_crash(tmpdir: Path, case: int, buf: bytes) -> Path:
    out = tmpdir / CRASHES_DIR_NAME
    out.mkdir(parents=True, exist_ok=True)
    path = out / ("seed-%d.bin" % case)
    path.write_bytes(buf)
    return path
def test_fuzz_seed_corpus_no_crash(tmp_path: Path) -> None:
    crashes = _run_harness()
    if crashes:
        for case, buf, err in crashes[:3]:
            _write_crash(tmp_path, case, buf)
        first, first_buf, first_err = crashes[0]
        raise AssertionError("parser crash: seed=%d case=%d error=%s input=%r (%d/%d crashed; repro in %s/)" % (SEED, first, first_err, first_buf[:120], len(crashes), N_CASES, CRASHES_DIR_NAME))
    assert N_CASES >= 100
def test_fuzz_examples_stay_total() -> None:
    for buf in EXAMPLES:
        fuzz(buf)
def test_fuzz_mutator_is_deterministic() -> None:
    first = _run_harness(20)
    second = _run_harness(20)
    assert [(c, b) for c, b, _ in first] == [(c, b) for c, b, _ in second]
def test_split_consumer_survives_fuzz_sample(tmp_path: Path) -> None:
    rng = random.Random(SEED)
    buf = _mutate(rng, SEED_CORPUS[0])
    text = buf.decode("utf-8", errors="replace")
    if not text.strip():
        text = "# fallback\n\nbody\n"
    work = tmp_path / "work"
    work.mkdir()
    (work / "full_text.txt").write_text(text, encoding="utf-8")
    receipt = split_mod.split(work)
    assert receipt["chunks"] >= 1
    assert sc_mod.detect_chapters(text) is not None
