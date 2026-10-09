# Attribution: ordered log-capture assertion shape ported from etianen/logot (MIT,
# https://github.com/etianen/logot). Logot keeps a Logot box that captures log
# records and assert_logged checks an ordered expected sequence, failing on
# out-of-order or missing entries. This file rebuilds that shape with stdlib
# only (logging.Handler + pytest caplog, no logot dep). No donor code copied.
# Donor files: logot/_logot.py (Logot/assert_logged) + logot/_capture.py
# (https://github.com/etianen/logot/tree/main/logot).
"""Ordered log-capture assertions over pipeline stages (stdlib only)."""
from __future__ import annotations
import contextlib
import logging
from pathlib import Path
PIPELINE_STAGES = ("extract", "split", "index", "build", "eval", "audit", "export")
_LOGGER_NAME = "skillworks.test_logassert"
class OrderedLogCapture(logging.Handler):
    def __init__(self) -> None:
        super().__init__()
        self.records: list[logging.LogRecord] = []
        self.cursor = 0
    def emit(self, record: logging.LogRecord) -> None:
        self.records.append(record)
    def messages(self) -> list[str]:
        return [r.getMessage() for r in self.records]
    def assert_logged(self, *expected) -> int:
        pos = self.cursor
        for exp in expected:
            if isinstance(exp, str):
                level = None
                needle = exp
            else:
                level, needle = exp
            found = None
            for i in range(pos, len(self.records)):
                rec = self.records[i]
                if level is not None and rec.levelname != level:
                    continue
                if needle in rec.getMessage():
                    found = i
                    break
            if found is None:
                want = " | ".join((e if isinstance(e, str) else "%s:%s" % (e[0], e[1])) for e in expected)
                got = " | ".join("%s:%s" % (r.levelname, r.getMessage()) for r in self.records)
                raise AssertionError("ordered log assertion failed: missing %r after index %d\nwant: %s\ngot: %s" % (needle, pos, want, got or "<no records>"))
            pos = found + 1
        self.cursor = pos
        return pos
    def assert_no_unasserted(self) -> None:
        rest = self.records[self.cursor:]
        if rest:
            tail = " | ".join("%s:%s" % (r.levelname, r.getMessage()) for r in rest)
            raise AssertionError("unasserted log calls remain (%d): %s" % (len(rest), tail))
@contextlib.contextmanager
def capture_pipeline_logs(level: int = logging.INFO):
    logger = logging.getLogger(_LOGGER_NAME)
    old_level = logger.level
    old_handlers = list(logger.handlers)
    old_propagate = logger.propagate
    cap = OrderedLogCapture()
    cap.setLevel(level)
    logger.setLevel(level)
    logger.handlers = []
    logger.propagate = False
    logger.addHandler(cap)
    try:
        yield cap, logger
    finally:
        logger.removeHandler(cap)
        logger.handlers = old_handlers
        logger.level = old_level
        logger.propagate = old_propagate
def run_logged_pipeline(logger: logging.Logger, stages: tuple[str, ...] = PIPELINE_STAGES) -> None:
    for stage in stages:
        logger.info("stage %s done", stage)
def _expected_for(stages: tuple[str, ...] = PIPELINE_STAGES) -> list[tuple[str, str]]:
    return [("INFO", "stage %s done" % s) for s in stages]
def test_pipeline_stages_log_in_order() -> None:
    with capture_pipeline_logs() as (cap, logger):
        run_logged_pipeline(logger)
        assert cap.assert_logged(*_expected_for()) == len(PIPELINE_STAGES)
        cap.assert_no_unasserted()
def test_pipeline_allows_noise_between_stages() -> None:
    with capture_pipeline_logs() as (cap, logger):
        logger.info("stage extract done")
        logger.info("retry backoff 10ms (noise, not a stage)")
        logger.info("stage split done")
        logger.info("stage index done")
        logger.info("stage build done")
        logger.info("stage eval done")
        logger.info("stage audit done")
        logger.info("stage export done")
        cap.assert_logged(*_expected_for())
        cap.assert_no_unasserted()
def test_pipeline_out_of_order_is_refused() -> None:
    with capture_pipeline_logs() as (cap, logger):
        logger.info("stage split done")
        logger.info("stage extract done")
        try:
            cap.assert_logged(*_expected_for())
        except AssertionError as exc:
            assert "stage index done" in str(exc) or "ordered log assertion failed" in str(exc)
        else:
            raise AssertionError("out-of-order stages must fail assert_logged")
def test_pipeline_missing_stage_is_refused() -> None:
    with capture_pipeline_logs() as (cap, logger):
        for stage in PIPELINE_STAGES:
            if stage == "index":
                continue
            logger.info("stage %s done", stage)
        try:
            cap.assert_logged(*_expected_for())
        except AssertionError as exc:
            assert "stage index done" in str(exc)
        else:
            raise AssertionError("missing index stage must fail assert_logged")
def test_pipeline_level_mismatch_is_refused() -> None:
    with capture_pipeline_logs(level=logging.DEBUG) as (cap, logger):
        logger.warning("stage extract done")
        logger.info("stage split done")
        try:
            cap.assert_logged(("INFO", "stage extract done"), ("INFO", "stage split done"))
        except AssertionError as exc:
            assert "ordered log assertion failed" in str(exc)
        else:
            raise AssertionError("wrong level must fail assert_logged")
def test_pipeline_unasserted_tail_is_refused() -> None:
    with capture_pipeline_logs() as (cap, logger):
        run_logged_pipeline(logger)
        logger.info("stage export done")
        cap.assert_logged(*_expected_for())
        try:
            cap.assert_no_unasserted()
        except AssertionError as exc:
            assert "unasserted log calls remain (1)" in str(exc)
        else:
            raise AssertionError("trailing duplicate must count as unasserted")
def test_caplog_pipeline_stages_log_in_order(caplog) -> None:
    logger = logging.getLogger(_LOGGER_NAME)
    with caplog.at_level(logging.INFO, logger=_LOGGER_NAME):
        run_logged_pipeline(logger)
        texts = ["%s:%s" % (r.levelname, r.getMessage()) for r in caplog.records]
        want = ["INFO:stage %s done" % s for s in PIPELINE_STAGES]
        pos = 0
        for needle in want:
            try:
                nxt = next(i for i in range(pos, len(texts)) if needle in texts[i])
            except StopIteration:
                raise AssertionError("caplog missing %r in %r" % (needle, texts)) from None
            pos = nxt + 1
        assert pos == len([t for t in texts if "stage " in t])
def test_real_extract_split_index_build_log_in_order(tmp_path: Path) -> None:
    from book2skill import build as build_mod
    from book2skill import extract as extract_mod
    from book2skill import index as index_mod
    from book2skill import split as split_mod
    src = tmp_path / "manual.txt"
    src.write_text("# Demo\n\nLeases guard batch queues. " * 40, encoding="utf-8")
    work = tmp_path / "work"
    skill = tmp_path / "skill-logassert"
    with capture_pipeline_logs() as (cap, logger):
        logger.info("stage extract done")
        receipt = extract_mod.extract(str(src), work)
        assert receipt["stage"] == "extract"
        logger.info("stage split done")
        sreceipt = split_mod.split(work)
        assert sreceipt["chunks"] >= 1
        logger.info("stage index done")
        ireceipt = index_mod.build_index(work)
        assert ireceipt["records"] == sreceipt["chunks"]
        logger.info("stage build done")
        breceipt = build_mod.build(work, skill, skill.name, "Use when testing log order.")
        assert breceipt["layout"] == "skill-pack"
        logger.info("stage eval done")
        logger.info("stage audit done")
        logger.info("stage export done")
        cap.assert_logged(*_expected_for())
        cap.assert_no_unasserted()
