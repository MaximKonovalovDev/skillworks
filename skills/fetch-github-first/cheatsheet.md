# Cheatsheet

- `gh api repos/OWNER/REPO` proves exists and gives default branch plus licence.
- `gh api repos/OWNER/REPO/contents/DIR` lists; take the exact path.
- `gh api repos/OWNER/REPO/contents/FILE?ref=REF` reads at the pinned ref.
- On 403: one repos call, backoff, retry once, then the contents call.
- Close: record plus ref plus results plus unverified.
