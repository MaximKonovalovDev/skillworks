## Steals

2026-10-03 | S3 | cchao123/skills-manager@f5ab5fb, src-tauri/src/commands/marketplace.rs | MIT | skills/progit-branching/listing.md | open
  what to change, and the number it moves: adopt the marketplace listing fields (author, repository, stars, weekly-installs) into the listing shape; marketplace-field count 0 -> 4, S3 proof `python tools/finish_proof.py s3` exit 1 -> 0 once the Live listing line lands.
2026-10-03 | S3 | cchao123/skills-manager@f5ab5fb, src-tauri/src/linker.rs + src-tauri/src/commands/skills.rs | MIT | book2skill/export.py | landed c66e231 ZIP proven 2026-10-03T22:19Z
  what to change, and the number it moves: add a verified installable artifact per target (link-or-copy install with fallback, SKILL.md-at-root check); importable ZIPs 0 -> 1, K-41 done-when unmet -> met.
2026-10-03 | S3 | openclaw/clawhub@00f356544bd4624542cf10b69b5f8097fe397b7a, convex/lib/skillPublish.ts | MIT | book2skill/export.py | open
  what to change, and the number it moves: add a publish-readiness gate to export (require SKILL.md, semver version, frontmatter description, files manifest with path+size+sha256, bundle-size cap, junk-file filter); publish-readiness checks 0 -> 6, new tests 0 -> 5 in tests/test_export_publish.py.
2026-10-03 | S3 | factory preflight tool (own fleet, via arsenal --list) | own | tools/finish_proof.py | open
   what to change, and the number it moves: extend the S3 proof with the buyer-file gate (upload ZIP present and importable, store copy fields, price line, AI-disclosure line) next to the Live-listing line and eval gate; S3 proof checks 2 -> 6, python tools/finish_proof.py s3 exit 1 -> 0 once the pack passes all six.
2026-10-04 | doctor | our-fleet: center metrics.json + skill-feed-scan.mjs | own | tools/fleet_failures.py | landed uncommitted (judge reviews, lead lands)
  what to change, and the number it moves: read the fleet's own failure fingerprints (center metrics.json) through the skill-feed classes (skill-feed-scan.mjs) into a scanner the doctor lane runs every round; doctor-visible failure classes 0 -> all of the 48 h window, TS-1 done-when unmet -> met.
