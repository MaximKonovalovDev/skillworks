# Error lines the pairs replay (all thrown live by scripts/run_batch.py in pwsh 7)

Each fragment below is a substring of the real `bad_text` of the named pair. The good side of the same pair prints the batch report instead.

- `timed out after scattered GitHub calls`: timeout on scattered calls. Pair `bf-batch`
- `timed out fetching repo records one by one`: timeout on one-by-one fetches. Pair `bf-cap`
- `timed out on mixed read-write dispatch with the writes first`: timeout with writes first. Pair `bf-readonly`
- `timed out on sequential file-content fetches`: timeout on sequential fetches. Pair `bf-pool`
- `timed out retrying the GitHub search singly five times`: timeout on the retry storm. Pair `bf-search`
- `timed out fetching several repo records under no timeout`: timeout with no timeout bound. Pair `bf-timeout`
- `timed out on single-path content fetch with no fallback`: timeout with no fallback. Pair `bf-fallback`
- `timed out on multi-repo search with no cap`: timeout with no cap. Pair `bf-quote`
- `timed out with the write before the reads`: timeout with the write first. Pair `bf-after`
- `timed out on license record with API only and no raw fallback`: timeout with API only. Pair `bf-risk`
- `timed out on slow endpoint with unbounded wait`: timeout on the slow endpoint. Pair `bf-first`
- `timed out on flaky batched call with no recorded outcomes`: timeout with no recorded outcomes. Pair `bf-result`
