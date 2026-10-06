# Error lines the pairs replay (all thrown live by scripts/run_search.py in pwsh 7)

Each fragment below is a substring of the real `bad_text` of the named pair. The good side of the same pair prints the retry report instead.

- `StatusCode: non 2xx status code (503 POST https://mcp.exa.ai/mcp)`: busy backend on the first try. Pair `ws-retry`
- `503 POST https://mcp.exa.ai/mcp) on repeat three`: busy backend on the third repeat. Pair `ws-once`
- `503 POST https://mcp.exa.ai/mcp) chained five`: busy backend after five chained calls. Pair `ws-backoff`
- `503 POST https://mcp.exa.ai/mcp) broad query`: busy backend on a broad query. Pair `ws-narrow`
- `503 POST https://mcp.exa.ai/mcp) five chained`: busy backend after five chained searches. Pair `ws-single`
- `503 POST https://mcp.exa.ai/mcp) same wording`: busy backend on the same wording. Pair `ws-fallback`
- `Missing key at ["result"] on first read`: wrong result shape on the first read. Pair `ws-guard`
- `Missing key at ["result"] on same shape`: wrong shape kept on the same shape. Pair `ws-shape`
- `Missing key at ["result"] on identical repeat`: wrong shape on the identical repeat. Pair `ws-change`
- `web_search_exa request timed out on wide scope`: wait exceeded on a wide scope. Pair `ws-bound`
- `web_search_exa request timed out after long wait`: wait exceeded after a long wait. Pair `ws-timeout`
- `503 POST https://mcp.exa.ai/mcp) no report`: busy backend closed with no report. Pair `ws-report`
