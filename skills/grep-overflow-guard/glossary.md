# Glossary

- overflow: a `Grep` call answered with `Ripgrep JSON record exceeded N bytes`, nothing searched.
- narrow scope: searching one folder first instead of the whole tree.
- chunked search: rerunning the search folder by folder or page by page, then merging.
- file-type filter: an include such as `*.md` that limits which files are read.
- glob narrow: a glob such as `*.md` that limits the search before the rerun.
- exact literal: the plain text to find, used instead of a broad regex.
- merged hits: the per-chunk hit lists joined into one report.
- unverified: gaps the closing report states instead of hiding.
