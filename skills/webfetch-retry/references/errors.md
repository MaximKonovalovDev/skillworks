# Error lines the pairs replay (all thrown live by scripts/run_fetch_retry.py in pwsh 7)

Each fragment below is a substring of the real `bad_text` of the named pair. The good side of the same pair prints the retry report instead.

- `timed out after 30000ms fetching slow page`: wait exceeded on a slow page. Pair `wf-retry`
- `timed out after 30000ms fetching <url> on repeat two`: wait exceeded on the second repeat. Pair `wf-once`
- `timed out after 30000ms fetching <url> chained three`: wait exceeded after chained calls. Pair `wf-backoff`
- `timed out after 30000ms fetching large page`: wait exceeded on a large page. Pair `wf-narrow`
- `timed out after 30000ms fetching full listing`: wait exceeded on the full listing. Pair `wf-subpath`
- `timed out after 30000ms fetching <url> twice in a row`: wait exceeded twice in a row. Pair `wf-cap`
- `timed out after 30000ms fetching api path`: wait exceeded on an API path. Pair `wf-record`
- `timed out after 30000ms fetching raw file`: wait exceeded on a raw file. Pair `wf-raw`
- `timed out after 30000ms fetching store page`: wait exceeded on a store page. Pair `wf-cache`
- `timed out after 30000ms fetching listing <url> during check`: wait exceeded during a listing check. Pair `wf-stamp`
- `timed out after 30000ms fetching <url> keeps timing out`: wait exceeded on a kept miss. Pair `wf-paths`
- `timed out after 30000ms fetching <url> no report`: wait exceeded with no report. Pair `wf-result`
