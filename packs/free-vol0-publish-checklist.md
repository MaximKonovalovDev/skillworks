# Free Vol 0 publish checklist

Ship the free Vol 0 only when every gate below is green.
Public paths hold only free Vol 0 files. Never paid pack files.

## 1. pack_check green

Command:

```text
python tools/pack_check.py packs/<slug>
```

Expect:

```text
RESULT PASS
```

No FAIL. No NEEDS once a `Live listing:` line exists.

## 2. skills-ref validate

Command:

```text
npx skills-ref validate ./packs/<slug>/vol0-sample.md
```

Expect: `valid` with zero errors. Fix shape first if it fails.

## 3. Cisco skill-scanner scan

Command:

```text
skill-scanner scan ./dist/<slug>-vol0.zip
```

Expect: zero high findings. Any high finding blocks ship.

## 4. Semgrep scan

Command:

```text
semgrep scan --config auto ./skills/<vol0-skill>/
```

Expect: no blocking findings. Clean or triaged only.

## 5. .claude-plugin/marketplace.json present

Check the file exists and names only the free Vol 0 skill.
No paid skill names. No paid zip names. No price text.

Expect: JSON parses and install from it works.

## 6. skills.sh listing entry

Check the listing names the Vol 0 skill and its licence.
Check proof lines match live-proof.json.
Check no private paths (no user folders, no other repo names).

Expect: entry renders with skill name, licence, proof line.

## 7. ClawHub entry ready

Check SKILL.md at zip root. Check semver version.
Check files manifest with path, size, sha256. Check no junk files.

Expect: publish dry run passes. No upload until gates 1-6 pass.

## Privacy rule

Public: Vol 0 zip and sample only. Never: paid zip, paid skills,
listing price, price evidence, buyer README internals.
