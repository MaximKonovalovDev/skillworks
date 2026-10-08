# repomap: skillworks
_generated 2026-10-08T20:52:58.992Z | 9345 files mapped | 248 hot (commits, last 14d) | cap 25KB__

## tree
- `.claude-plugin/` - 1 file
- `.env` - 1 file
- `.gitignore` - 1 file
- `.ignore` - 1 file
- `.opencode/` - 20 files
- `.pytest_cache/` - 5 files
- `.tools/` - 7048 files
- `AGENTS.md` - 1 file
- `CLAUDE.md` - 1 file
- `FINISH-LINE.md` - 1 file
- `LICENSE` - 1 file
- `README.md` - 1 file
- `THIRD_PARTY_NOTICES.md` - 1 file
- `VISION-TABLES.md` - 1 file
- `VISION.md` - 1 file
- `arsenal.json` - 1 file
- `book2skill/` - 31 files
- `dist/` - 9 files
- `docs/` - 2 files
- `evals/` - 130 files
- `findings/` - 1 file
- `from-design-studio/` - 12 files
- `mcp_server/` - 5 files
- `opencode.jsonc` - 1 file
- `orders.csv` - 1 file
- `packs/` - 58 files
- `prompts/` - 2 files
- `requirements.txt` - 1 file
- `research/` - 31 files
- `skills/` - 661 files
- `sprint/` - 35 files
- `steal-spec-mcp.md` - 1 file
- `team/` - 9 files
- `tests/` - 219 files
- `tools/` - 57 files
- `work/` - 993 files

## symbols (hot first, xN = commits last 14d)
### `book2skill/gates.py` x35 (12KB)
- `def frontmatter`
- `def body_of`
- `def body_tokens`
- `def skill_files`
- `def skill_text`
- `def _strip_code_spans`
- `def forge_english_hits`
- `def check_format`
- `def check_sources`
- `def check_eval`
- `def test_file_for`
- `def fingerprint`
- `def check_proof`
### `tools/install_fleet_skills.py` x33 (4.7KB)
- `def payload`
- `def stale`
- `def install`
- `def main`
### `.opencode/plugin/loop-keeper.js` x26 (185KB) - loop-keeper: continues THIS repo's /sprint when its session goes idle, and
### `book2skill/export.py` x9 (8.5KB)
- `def layout_for`
- `def load_eval_report`
- `def _is_link`
- `def _skip_names`
- `def _own_output_ignore`
- `def _refuse`
- `def _check_paths`
- `def _write_zip`
- `def skill_version`
- `def export`
### `tests/test_pipeline.py` x9 (14KB)
- `def test_split_chunk_sizes`
- `def test_frontmatter_rule`
- `def test_eval_gate_threshold`
- `def test_docx_table_walk`
- `def test_extract_receipt_counts`
- `def test_build_skill_pack_layout`
- `def test_grow_qa_from_chapter`
- `def test_gutenberg_marker_strip`
- `def test_export_gate_refuses_failing_skill`
- `def test_export_skips_own_output_dir_no_nesting`
- `def test_build_refuses_name_dir_mismatch`
- `def test_export_unknown_target_clean_error`
- `def _write_epub`
- `def test_epub_nav_heavy_body_only`
- `def test_epub_pagebreak_label_map`
- `def test_audit_skips_export_dupes`
### `book2skill/build.py` x7 (11KB)
- `def is_noncommercial_text`
- `def skill_is_noncommercial`
- `def find_price_markers`
- `def refuse_nc_price`
- `def validate_name`
- `def strip_gutenberg_boilerplate`
- `def _clean_chunk`
- `def _scaffold_body`
- `def scaffold_leftovers`
- `def prompt_version`
- `def _frontmatter`
- `def build`
### `book2skill/cli.py` x6 (7.3KB)
- `def main`
- `def extract`
- `def split`
- `def index_mod_split`
- `def index_cmd`
- `def build`
- `def audit`
- `def eval`
- `def refresh`
- `def export`
- `def distill`
- `def distill_plan`
- `def distill_check`
- `def make`
### `book2skill/extract.py` x6 (17KB)
- `def _ensure_local_tools`
- `def strip_gutenberg_markers`
- `def _is_link`
- `def _read_folder`
- `def _read_text_file`
- `def _read_pdf_classic`
- `def _md_table_row`
- `def _pdf_tables_as_markdown`
- `def _pdf_code_as_markdown`
- `def _read_pdf_markitdown`
- `def _pdf_page_count`
- `def _read_epub_classic`
- `def _read_epub_markitdown`
- `def _read_docx`
- `def _read_docx_markitdown`
- `def md_counts`
- `def _use_markitdown`
- `def extract`
### `tools/finish_proof.py` x6 (16KB)
- `class counts`
- `def _db_path`
- `def _skill_names`
- `def _repo_of`
- `def skill_loads`
- `def skill_loads_detail`
- `def _warm_loads`
- `def _loads`
- `def _breadth`
- `def s1`
- `def s2`
- `def _pack_tested`
- `def s3`
- `def _halved`
- `def s5`
- `def _live_current`
- `def _trial_passes`
- `def s6`
- `def main`
### `book2skill/eval.py` x5 (6.5KB)
- `def _check_item`
- `def validate_qa`
- `def grow_qa`
- `def skill_answer_texts`
- `def _rank`
- `def run_eval`
### `tests/test_bash_spawn_guard.py` x5 (11KB)
- `def _load`
- `def doc`
- `def results`
- `def test_pair_file_is_well_formed`
- `def test_pairs_md_is_current`
- `def test_every_rule_line_carries_a_source`
- `def test_every_pair_behaves_as_written`
- `def test_the_harness_can_fail`
- `def test_error_fragments_come_from_real_failures`
- `def test_three_dispatch_bad_cases_fail_bare_and_pass_bounded`
- `def test_new_five_pairs_fail_bare_and_pass_bounded`
- `def test_new_five_pairs_v130_fail_bare_and_pass_bounded`
- `def test_new_five_pairs_v140_fail_bare_and_pass_bounded`
### `tests/test_finish_proof.py` x5 (14KB)
- `def _world`
- `def _repo`
- `def _load`
- `def test_loads_count_only_real_skill_calls_of_this_repo_in_other_repos`
- `def test_a_folder_inside_a_repo_or_a_parent_with_git_is_not_a_repo`
- `def test_s1_and_s2_read_the_database`
- `def test_s1_and_s2_without_a_database_are_open`
- `def _csv`
- `def test_s5_needs_one_adopted_class_cut_by_half`
- `def test_s5_without_the_record_is_open`
- `def _skill`
- `def test_s6_counts_current_live_proofs_and_passing_trials`
- `def test_s6_on_the_real_skills_names_the_four_fleet_skills`
- `def _pack`
- `def test_s3_needs_a_live_url_and_a_tested_pack`
- `def test_s3_met`
- `def test_s3_a_pack_folder_counts_only_when_pack_check_passes`
- `def test_s1_met_cache_answers_with_no_scan`
- `def test_s1_open_cache_answers_from_cached_meter_reads`
- `def test_s1_explicit_path_scans_as_is_despite_a_met_cache`
- `def test_s2_met_cache_answers_with_no_scan`
- `def _stale_cache`
- `def test_s1_stale_met_cache_answers_with_no_scan`
- `def test_s2_stale_met_cache_answers_with_no_scan`
- `def test_s1_open_warm_cache_still_refreshes`
- `def test_command_line_exit_codes`
### `tools/pack_check.py` x5 (30KB)
- `class Report`
- `def default_skill_problems`
- `def fetch_status`
- `def sections_of`
- `def field`
- `def check_manifest`
- `def check_skills`
- `def slot_finding`
- `def check_buyer_files`
- `def check_listing`
- `def check_evidence`
- `def zip_problems`
- `def differs`
- `def referenced_files`
- `def check_zips`
- `def check_assets`
- `def find_factory_preflight`
- `def load_factory_audit`
- `def judge_text`
- `def stage_factory_product`
- `def check_factory_preflight`
- `def check_pack`
- `def resolve_pack_dir`
- `def resolve_dist_dir`
- `def main`
### `book2skill/make.py` x4 (5.3KB)
- `def _inside`
- `def _check_places`
- `def _quiet`
- `def make`
- `def _write`
### `mcp_server/server.py` x4 (14KB)
- `def _parse_skills_dir_override`
- `def _skills_dir`
- `def _parse_skill_frontmatter`
- `def _skill_meta`
- `def _skills`
- `def _skill_md_files`
- `def _search`
- `def _input_schema`
- `def _preview`
- `def _preview_input_schema`
- `def _validate_preview_args`
- `def _validate_args`
- `def _error_envelope`
- `def _reply`
- `def _unknown_skill_message`
- `def main`
### `tests/test_adopted_after.py` x4 (27KB)
- `def call`
- `def test_each_target_class_is_counted`
- `def test_ordinary_calls_are_not_counted`
- `def test_only_shell_calls_count_for_pwsh_git_and_browser_and_bevy_counts_in_engine2040_only`
- `def test_a_call_that_hits_two_classes_counts_twice_and_the_error_text_may_carry_colour`
- `def test_spawn_kills_and_policy_denials_count_per_repo`
- `def test_spawn_kills_and_policy_denials_count_per_repo_in_history`
- `class World`
- `def world`
- `def test_a_row_is_not_due_before_48_hours_after_the_install`
- `def test_a_paused_loop_never_gets_its_row_filled_it_would_look_halved`
- `def test_a_few_busy_hours_do_not_pass_for_a_full_run`
- `def test_an_idle_loop_with_every_hour_covered_but_few_calls_waits`
- `def test_a_full_run_fills_the_number_scaled_to_the_before_workload`
- `def test_the_install_moment_in_adopted_meta_json_replaces_the_end_of_the_day`
- `def test_only_adopted_rows_without_an_after_number_are_touched_and_the_rest_stays_as_it_was`
- `def test_a_dry_run_measures_and_prints_but_writes_nothing`
- `def test_use_rows_say_up_is_good`
- `def test_a_missing_database_or_record_says_so_and_does_not_raise`
- `def _full_run`
- `def test_s5_measures_the_due_rows_of_the_real_record_before_it_reads_it`
- `def test_s5_reads_a_file_given_to_it_as_it_is_and_never_measures_for_it`
- `def test_s5_prints_a_measuring_fault_instead_of_raising`
- `def test_s5_already_met_returns_without_any_database_scan`
- `def test_second_refresh_reuses_the_meter_cache`
- `def test_a_fall_in_use_rows_is_not_a_cured_class`
- `def test_the_command_line_status_prints_one_line_per_row_and_a_summary`
- `class SkillWorld`
- `def skillworld`
- `def test_cached_skill_loads_counts_only_real_loads_then_answers_from_cache`
- `def test_an_explicit_database_without_a_cache_file_is_read_as_it_is`
- `def test_a_stale_cache_or_a_different_window_rescans`
- `def test_a_corrupt_cache_and_a_missing_database_are_a_miss_never_a_raise`
- `def test_the_port_reproduces_the_before_numbers_center_counted_in_the_same_window`
### `tests/test_fleet_skills.py` x4 (3.0KB)
- `def _built`
- `def test_fleet_skill_format`
- `def test_frontmatter_folds_folded_description_scalar`
- `def test_gates_frontmatter_reads_git_one_branch_folded_description`
- `def test_fleet_skill_sources_and_notices`
- `def test_fleet_skill_eval_gate`
- `def test_fleet_skill_matches_its_last_live_proof`
- `def test_reseal_keeps_a_fresh_seal`
- `def test_reseal_rewrites_a_changed_skill`
### `tests/test_pack_check.py` x4 (22KB)
- `def make_skill`
- `def fix`
- `def run`
- `def fails`
- `def set_listing`
- `def set_pack`
- `def test_a_good_pack_passes_and_lists_the_assets_it_still_needs`
- `def test_the_factory_buyer_gate_passes_a_good_pack_on_a_staged_product_layout`
- `def test_factory_findings_become_pack_failures`
- `def test_an_unavailable_factory_gate_warns_instead_of_failing`
- `def test_the_buyer_zip_holds_the_skills_each_as_its_own_zip_and_a_manifest_with_sha256`
- `def test_the_build_is_reproducible`
- `def test_a_dist_folder_inside_skills_is_refused`
- `def test_a_noncommercial_skill_is_never_in_a_priced_pack`
- `def test_a_licence_nobody_may_sell_under_fails`
- `def test_the_vol0_skill_cannot_also_be_a_paid_skill`
- `def test_the_price_must_agree_in_listing_price_txt_and_pack_json`
- `def test_a_missing_listing_field_fails`
- `def test_a_missing_section_and_template_text_fail`
- `def test_the_ai_disclosure_must_say_what`
- `def test_every_skill_must_be_named_with_its_licence_and_its_own_proof_line`
- `def test_the_free_sample_section_must_name_the_vol0_skill_and_its_licence`
- `def test_a_private_path_or_another_repos_name_in_the_listing_fails`
- `def test_a_failing_skill_gate_fails_the_pack`
- `def test_a_skill_that_changed_after_the_zip_was_built_makes_the_zip_stale`
- `def test_a_missing_or_extra_archive_fails`
- `def _rewrite`
- `def test_junk_unsafe_paths_and_a_wrong_manifest_in_the_zip_fail`
- `def test_the_free_skill_inside_the_paid_zip_fails`
- `def test_a_skill_that_names_a_file_the_zip_does_not_hold_fails`
- `def test_a_private_path_inside_a_skill_in_the_zip_fails`
- `def test_price_evidence_needs_three_pages_and_a_gone_page_fails`
- `def test_store_assets_present_must_be_real_files_of_enough_size`
- `def test_a_listing_must_say_something_about_every_asset`
- `def test_with_a_live_listing_line_every_needed_asset_is_a_failure`
- `def test_the_command_line_ends_with_one_result_line_and_the_exit_code_follows`
- `def test_the_pack_folder_resolves_from_any_working_folder`
- `def test_the_real_pack_files_match_what_the_listing_says`
- `def test_the_real_pack_passes_the_gate_and_the_readme_install_commands_work`
### `tools/adopted_after.py` x4 (29KB)
- `def classify`
- `def repo_dirs`
- `def repo_of`
- `def _connect`
- `def shell_activity`
- `def shell_calls`
- `def class_counts`
- `def read_rows`
- `def write_rows`
- `def install_day_end`
- `def load_meta`
- `def install_end`
- `def verdict`
- `def _load_cache`
- `def _save_cache`
- `def _before_window`
- `def _load_after`
- `def _store_after`
- `def _loads_hit`
- `def _loads_store`
- `def cached_skill_loads`
- `def plan`
- `def refresh`
- `def main`
### `.opencode/agents/planner.md` x3 (1.7KB)
- # Planner
- ## Dispatch discipline
- ## Contract
### `book2skill/audit.py` x3 (7.9KB)
- `def _tokens`
- `def _frontmatter`
- `def _skill_files`
- `def audit`
### `packs/mcp-template/server.py` x3 (2.8KB)
- `def _schema_for`
- `class ToolBinding`
- `def tool`
- `def ping`
- `def add`
- `def echo`
- `def list_tools`
- `def selftest`
### `sprint/check.mjs` x3 (8.0KB) - sprint/check.mjs: the skillworks loop's own check (generated by center/loopkit.mjs).
### `tests/skill_gates.py` x3 (646B)
### `tests/test_cron_skip_clean.py` x3 (8.4KB)
- `def tick`
- `def word`
- `def make_watch`
- `def test_skip_on_clean_proven`
- `def test_a_skip_touches_nothing`
- `def test_a_missing_or_unusable_state_is_one_run_then_clean`
- `def test_the_content_decides_not_the_clock`
- `def test_the_fingerprint_is_the_documented_one`
- `def test_a_state_file_inside_the_watch_dir_is_refused`
- `def test_a_missing_watch_dir_is_an_error_and_writes_no_state`
- `def test_a_hebrew_folder_name_in_a_message_does_not_crash_a_legacy_code_page_pipe`
- `def test_an_unreadable_file_is_an_error_not_a_traceback`
- `def test_help_runs_without_a_prompt`
- `def test_skill_md_documents_what_the_script_prints`
- `def test_an_installed_copy_runs_from_another_folder_through_pwsh`
### `tests/test_inbox_file_reader.py` x3 (11KB)
- `def run_reader`
- `def tree`
- `def test_inbox_file_reader_files_one_item`
- `def test_one_item_per_run_in_order_and_only_the_two_files_change`
- `def test_line_endings_of_the_other_lines_are_kept`
- `def test_a_board_without_a_final_line_break_does_not_swallow_the_item`
- `def test_a_byte_order_mark_stays_at_the_start_of_the_inbox_and_out_of_the_board`
- `def test_a_board_that_cannot_be_written_leaves_the_inbox_alone`
- `def test_a_hebrew_item_is_filed_and_echoed_even_on_a_legacy_code_page_pipe`
- `def test_a_new_board_is_created_with_its_folders`
- `def test_allowed_suffixes`
- `def test_a_path_outside_the_allowlist_is_refused_on_either_side`
- `def test_the_same_file_twice_is_refused_even_spelled_differently`
- `def test_a_missing_inbox_is_an_error_and_creates_nothing`
- `def test_an_empty_or_blank_inbox_is_an_error_and_the_board_is_untouched`
- `def test_an_inbox_that_is_not_utf8_text_is_an_error_not_a_traceback`
- `def test_help_runs_without_a_prompt`
- `def test_skill_md_documents_what_the_script_prints`
- `def test_an_installed_copy_runs_from_another_folder_through_pwsh`
### `tests/test_pipe_run.py` x3 (11KB)
- `def run_pipe`
- `def items`
- `def test_pipe_run_cap_dry_run_and_run`
- `def test_the_cap_is_a_ceiling_spend_equal_to_it_runs`
- `def test_the_price_of_an_item_is_chars_over_four_with_a_minimum_of_one`
- `def test_a_line_break_costs_one_character_on_every_system`
- `def test_only_top_level_txt_files_are_items_in_any_letter_case`
- `def test_items_are_copied_byte_for_byte`
- `def test_dry_run_over_the_cap_still_exits_zero_and_writes_nothing`
- `def test_empty_input_runs_with_zero_items`
- `def test_an_item_that_is_not_utf8_text_is_refused_before_anything_is_written`
- `def test_a_hebrew_file_name_in_a_message_does_not_crash_a_legacy_code_page_pipe`
- `def test_bad_input_is_an_error_with_exit_two`
- `def test_a_cap_that_is_not_a_whole_number_is_a_usage_error`
- `def test_a_second_run_into_the_same_out_overwrites_the_items_and_the_receipt`
- `def test_help_runs_without_a_prompt`
- `def test_skill_md_documents_what_the_script_prints`
- `def test_an_installed_copy_runs_from_another_folder_through_pwsh`
### `tools/fleet_failures.py` x3 (26KB)
- `def norm`
- `def head_of`
- `def chained_of`
- `def base_of`
- `def classify_call`
- `def family_of`
- `def resolve_db`
- `def connect_ro`
- `def repo_dirs`
- `def repo_of`
- `def parse_ms`
- `def scan_db`
- `def loads_detail`
- `def read_rows`
- `def skill_now`
- `def skill_before`
- `def verdict_for`
- `def cmd_scan`
- `def cmd_loads`
- `def cmd_compare`
- `def _token`
- `def board_open`
- `def compute_lanes`
- `def cmd_lanes`
- `def round_numbers`
- `def cmd_round`
- `def main`
### `book2skill/split_chapters.py` x2 (6.2KB)
- `def _fence_kind`
- `def is_fence`
- `def iter_headings`
- `def slug`
- `def detect_chapters`
- `def split_chapters`
### `skills/cron-skip-clean/scripts/cron_skip_clean.py` x2 (3.1KB)
- `def fingerprint`
- `def previous_fingerprint`
- `def main`
### `skills/inbox-file-reader/scripts/file_one_item.py` x2 (4.0KB)
- `def allowed`
- `def split_lines`
- `def main`
### `skills/pipe-run/scripts/pipe_run.py` x2 (3.5KB)
- `def estimate`
- `def read_item`
- `def main`
### `tests/live_proof.py` x2 (3.8KB)
- `def versions`
- `def same_seal`
- `def prove`
- `def main`
### `tests/test_audit_grades.py` x2 (5.2KB)
- `def _skill`
- `def test_audit_reports_three_cost_numbers_on_progit`
- `def test_audit_flags_an_over_budget_body`
- `def test_audit_grades_description_name_and_links`
- `def test_audit_reads_folded_yaml_description`
- `def test_audit_git_one_branch_has_no_folded_length_flag`
- `def test_make_prints_over_budget_on_a_big_fixture`
### `tests/test_book_to_skill.py` x2 (16KB)
- `def b2s`
- `def project`
- `def make_args`
- `def write_the_skill`
- `def test_make_prints_the_documented_lines_and_keeps_its_output_in_the_folder_you_stand_in`
- `def test_the_stage_commands_one_by_one`
- `def test_export_is_held_until_you_write_the_skill_then_the_zip_has_skill_md_at_its_root`
- `def test_an_old_export_folder_inside_the_skill_never_ships`
- `def test_a_destination_path_over_240_characters_is_refused_before_anything_is_copied`
- `def test_the_eval_gate_refuses_and_nothing_is_exported`
- `def test_make_refusals_exit_two_and_build_no_skill`
- `def test_a_question_ends_without_a_question_mark_because_punctuation_sticks_to_the_word`
- `def test_glob_takes_only_the_matching_files_of_a_folder`
- `def test_a_docx_file_is_a_source`
- `def test_help_lists_every_stage`
- `def test_the_budget_numbers_in_the_skill_match_the_gates`
- `def test_it_runs_through_pwsh_from_a_folder_with_spaces_and_writes_there`
### `tests/test_edit_verify.py` x2 (4.9KB)
- `def _load`
- `def doc`
- `def results`
- `def test_pair_file_is_well_formed`
- `def test_pairs_md_is_current`
- `def test_every_rule_line_carries_a_source`
- `def test_every_pair_behaves_as_written`
- `def test_the_harness_can_fail`
- `def test_error_fragments_come_from_real_failures`
- `def test_stale_oldstring_replays_red_then_reread_fixes_it`
### `tests/test_eval_persist.py` x2 (1.8KB)
- `def test_eval_persists_report_beside_skill`
- `def test_readme_order_eval_then_export`
### `tests/test_fleet_failures.py` x2 (11KB)
- `def _db`
- `def _session`
- `def _part`
- `def _world`
- `def test_norm_blanks_numbers_hashes_and_paths`
- `def test_scan_groups_github_deepwiki_and_wrongshell`
- `def test_scan_cli_prints_top_five_and_writes_failures`
- `def test_loads_shares_one_counter_with_s1_s2`
- `def test_compare_before_and_verdict`
- `def test_lanes_tokens_stable_without_new_work`
- `def test_round_line_check_exits_1_when_nothing_moved`
- `def test_board_add_refuses_pipe_inside_cell`
- `def test_scan_exact_window_matches_metrics_entry`
- `def test_loads_exact_window_pins_single_day`
- `def test_command_line_help_exits_zero`
### `tests/test_make.py` x2 (9.2KB)
- `def _manual`
- `def _run`
- `def test_extract_reads_a_docs_folder`
- `def test_extract_folder_does_not_read_its_own_output`
- `def test_extract_folder_glob_and_empty`
- `def _make_args`
- `def test_make_one_command_builds_evals_audits`
- `def test_make_export_is_held_until_an_author_wrote_the_placeholders`
- `def test_make_gate_refuses_a_failing_skill`
- `def test_make_refuses_early`
- `def test_make_refuses_wrong_shaped_qa`
- `def test_scaffold_leftovers_reads_the_real_scaffold`
### `tests/test_mcp_rank.py` x2 (2.6KB)
- `def test_ranked_search_progit_before_freud_with_rank_and_trust_fields`
### `tests/test_mcp_schema.py` x2 (4.7KB)
- `def test_input_schema_derived_from_search_signature`
- `def test_validate_args_accepts_good_rejects_bad`
- `def _stdio_session`
- `def test_stdio_handshake_list_call_and_bad_call`
- `def test_skill_preview_returns_head_and_unknown_skill_errors`
### `tools/g16-install5.py` x2 (6.6KB)
- `def _installer`
- `def dest_of`
- `def built_skills`
- `def check_repo`
- `def prove_shape`
- `def inside`
- `def main`
### `tools/pack_build.py` x2 (20KB)
- `def load_pack`
- `def skill_files`
- `def zip_bytes`
- `def licences_text`
- `def pack_files`
- `def manifest_for`
- `def build_pack_zip`
- `def build_vol0_zip`
- `def build`
- `def slot`
- `def open_slots`
- `def proof_line`
- `def listing_starter`
- `def readme_starter`
- `def vol0_starter`
- `def starter_files`
- `def write_starters`
- `def main`
### `book2skill/distill.py` x1 (9.2KB)
- `def _scaffold_hits`
- `def _ascii_escape`
- `def prompt_version`
- `def _tokens`
- `def plan`
- `def _body`
- `def _rules`
- `def _pairs_with_prints`
- `def _trials`
- `def _chunk_refs_ok`
- `def check`
### `book2skill/index.py` x1 (1.9KB)
- `def build_index`
- `def search`
### `book2skill/refresh.py` x1 (1.1KB)
- `def fingerprint`
- `def refresh`
### `docs/INDEX.md` x1 (3.0KB)
- # Index: skillworks
- ## Read first
- ## Folders
- ## Root files
- ## Rules to know
### `docs/VIDEO-PACK.md` x1 (805B)
- # VIDEO-PACK spec
- ## Skills
- ## Price tier idea
- ## Gumroad mapping
### `mcp_server/fastmcp_scaffold.py` x1 (7.3KB)
- `def _local`
- `def _prettify`
- `def _find_opf`
- `def _ncx_labels`
- `def _rel`
- `def _spine_chapters`
- `def _fallback_chapters`
- `def list_chapters`
- `def _input_schema`
- `def _validate_list_chapters_args`
### `packs/mcp-template/selftest.py` x1 (445B)
- `def ping_dup`
### `packs/video-ffmpeg/server.py` x1 (3.3KB)
- `class ToolBinding`
- `def tool`
- `def cut`
- `def concat`
- `def overlay`
- `def clip`
- `def log_tail`
- `def list_tools`
- `def selftest`
### `research/folded-mcp-forge/packs/server-template/server.py` x1 (1.4KB)
- `def ping`
- `def add`
- `def echo`
### `skills/bash-abort-guard/scripts/pairs_to_md.py` x1 (2.3KB)
- `def render`
- `def main`
### `skills/bash-abort-guard/scripts/run_abort.py` x1 (5.5KB)
- `def scratch_root`
- `def run_pairs`
- `def main`
### `skills/bash-allowlist/scripts/pairs_to_md.py` x1 (2.4KB)
- `def render`
- `def main`
### `skills/bash-allowlist/scripts/run_allow.py` x1 (5.5KB)
- `def scratch_root`
- `def run_pairs`
- `def main`
### `skills/bash-spawn-guard/scripts/pairs_to_md.py` x1 (2.4KB)
- `def render`
- `def main`
### `skills/bash-spawn-guard/scripts/run_spawn.py` x1 (5.5KB)
- `def scratch_root`
- `def run_pairs`
- `def main`
### `skills/bat-cat/scripts/pairs_to_md.py` x1 (2.3KB)
- `def render`
- `def main`
### `skills/bat-cat/scripts/run_bat.py` x1 (6.0KB)
- `def scratch_root`
- `def run_pairs`
- `def main`
### `skills/batch-first/scripts/pairs_to_md.py` x1 (2.3KB)
- `def render`
- `def main`
### `skills/batch-first/scripts/run_batch.py` x1 (5.5KB)
- `def scratch_root`
- `def run_pairs`
- `def main`
### `skills/bevy-rust-ecs/scripts/check-sim-outside-bevy.mjs` x1 (12KB)
- `function isBevyName`
- `function statements`
- `function splitDotted`
- `function parseInline`
- `function parseManifest`
- `function bevyDeps`
- `function checkTargets`
### `skills/bevy-rust-ecs/scripts/plugin-bevy-version.mjs` x1 (12KB)
- `function readBevyRequirements`
- `function matchesBevy`
- `function readCompatTable`
### `skills/brief-gate/scripts/pairs_to_md.py` x1 (2.3KB)
- `def render`
- `def main`
### `skills/brief-gate/scripts/run_brief.py` x1 (5.5KB)
- `def scratch_root`
- `def run_pairs`
- `def main`
### `skills/cargo-book/scripts/cargo_book.py` x1 (6.4KB)
- `def scratch_root`
- `def run_step`
- `def run_side`
- `def run_pairs`
- `def main`
### `skills/cargo-book/scripts/pairs_to_md.py` x1 (3.6KB)
- `def step_lines`
- `def render`
- `def main`
### `skills/delta-diff/scripts/pairs_to_md.py` x1 (2.3KB)
- `def render`
- `def main`
### `skills/delta-diff/scripts/run_delta.py` x1 (6.0KB)
- `def scratch_root`
- `def run_pairs`
- `def main`
### `skills/edit-abort-guard/scripts/pairs_to_md.py` x1 (2.5KB)
- `def render`
- `def main`
### `skills/edit-abort-guard/scripts/run_edit.py` x1 (5.6KB)
- `def scratch_root`
- `def run_pairs`
- `def main`
### `skills/edit-identical/scripts/pairs_to_md.py` x1 (2.4KB)
- `def render`
- `def main`
### `skills/edit-identical/scripts/run_identical.py` x1 (5.5KB)
- `def scratch_root`
- `def run_pairs`
- `def main`
### `skills/edit-reread/scripts/pairs_to_md.py` x1 (2.2KB)
- `def render`
- `def main`
### `skills/edit-reread/scripts/run_pairs.py` x1 (5.5KB)
- `def scratch_root`
- `def run_pairs`
- `def main`
### `skills/edit-unique/scripts/pairs_to_md.py` x1 (2.3KB)
- `def render`
- `def main`
### `skills/edit-unique/scripts/run_unique.py` x1 (5.5KB)
- `def scratch_root`
- `def run_pairs`
- `def main`
### `skills/edit-verify/scripts/pairs_to_md.py` x1 (2.3KB)
- `def render`
- `def main`
### `skills/edit-verify/scripts/run_verify.py` x1 (5.5KB)
- `def scratch_root`
- `def run_pairs`
- `def main`
### `skills/engine-builder/scripts/pairs_to_md.py` x1 (2.3KB)
- `def render`
- `def main`
### `skills/engine-builder/scripts/run_pairs.py` x1 (5.5KB)
- `def scratch_root`
- `def run_pairs`
- `def main`
### `skills/fetch-github-first/scripts/pairs_to_md.py` x1 (2.3KB)
- `def render`
- `def main`
### `skills/fetch-github-first/scripts/run_fetch.py` x1 (5.5KB)
- `def scratch_root`
- `def run_pairs`
- `def main`
### `skills/github-file-guard/scripts/pairs_to_md.py` x1 (2.4KB)
- `def render`
- `def main`

_3192 cold files dropped to fit cap_
