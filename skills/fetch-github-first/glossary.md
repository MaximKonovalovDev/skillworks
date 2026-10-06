# Glossary

- repos call: `gh api repos/OWNER/REPO`, the record that proves exists plus default branch plus licence.
- contents call: `gh api repos/OWNER/REPO/contents/FILE?ref=REF`, the pinned read that replaces a guessed fetch.
- directory listing: `gh api repos/OWNER/REPO/contents/DIR`, the listing that gives the exact path.
- pinned ref: a ref resolved from the record, never assumed.
- backoff: on a 403, call once, wait, retry once.
- fallback: when the web fetch misses, read with the contents call.
- unverified: gaps the closing report states instead of hiding.
