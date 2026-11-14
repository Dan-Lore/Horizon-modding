# Mod sourcing policy

Agreed 2026-11-11.

## Rules (priority order)

1. **If a Horizon mod already exists — use it** (install from registry / Releases). Prefer the maintained, highest-quality option when several compete (e.g. two JEIs).
2. **If we need fixes or missing pieces — try to contribute upstream** (PR, issues, discussion) before forking.
3. **If we need more than the current alpha/release can give** (e.g. Create beyond `0.7.0-alpha.x` for pack goals) — **start our own version** in `mods/<id>/`, with clear attribution and “why not upstream” notes.
4. **If contributing is blocked** (no response, rejected scope, license/governance mismatch, abandoned repo) — **build our own** and document the fork/rewrite rationale in that mod’s README.

Do **not** invent a parallel “inspired by” mod while an adequate registry mod covers the need.

## TFG-adjacent defaults

**Locked transfer list:** [`docs/mod-transfer-list.md`](mod-transfer-list.md) (Batch A Nightly MVP → Batch B Create → post-MVP own TFC/GT).

| Need | Current Horizon pick | Stance |
| --- | --- | --- |
| Recipe viewer | JEI for Horizon (`jei`) — watch `justenoughitems` / REI | Use; contribute if gaps |
| Look-at tooltip | Jade (`jade`) — LookAt as fallback | Use |
| Create | Create for Horizon (`create`, alpha) | Wait for Nightly ≥ pin; then use; contrib/own only if alpha insufficient |
| AE2 | Applied Energistics 2 (`ae2`) | Use on Nightly MVP batch |
| Soft QoL | AppleSkin, Continuity | Soft; drop if left out |
| TFC / GregTech / TFG core | *(none)* | Post-MVP own slices; no fake “almost TFC” under TFG name |

## Horizon versions (how we pick a base)

| Channel | What it is |
| --- | --- |
| **Nightly** (e.g. `nightly-2026-11-08-fdc87ae`) | Published rolling build in the launcher — **our default “current Horizon”** for the draft pack. Not the same as numbered “stable” releases (`v0.2.x`). |
| **Stable / numbered** (`v0.2.97`, …) | Slower release train; use only if we explicitly pin the pack to it. |
| **Main commit pin** (e.g. Create 0.9 → `4e5296d`) | A specific Horizon git commit a native mod was built against. Can be **ahead of the latest published Nightly** (features on `main`, no Nightly cut yet). Launcher then builds a `native-<pin>-…` that is **not** “the Nightly everyone updates to”. |

**Policy**

1. **Prefer one pack instance** on the **latest published Nightly** we can actually play.
2. **Do not** keep parallel instances for “Create pin” vs “Nightly” long-term — confusing and doubles native builds.
3. If a mod already has a **good build for a newer Horizon than our Nightly** (e.g. Create 0.9 → `4e5296d`):
   - **wait for that Horizon Nightly** — do not burn native builds / backports / parallel instances on it;
   - only chase an older mod build if one exists **and** still works on our Nightly (Create: none on `fdc87ae`);
   - own work / contrib only when nothing usable exists ahead of us, or upstream is stuck.
4. **Native builds are expensive** — rebuild only when the mod set or Horizon base changes for real. No speculative rebuilds. Never two full stacks “just in case”.
5. **Don’t redo what’s already ahead.** If someone shipped a solid native port for tomorrow’s Nightly, we track it and adopt it — we don’t spend the team reinventing it on yesterday’s Nightly.

## Daily registry monitor (≤ 1× / day)

**Mandatory, at most once per calendar day** — do not poll more often.

Purpose: catch better Create (or other tracked) releases, new TFC/GT-related ports, competing JEI/Jade quality jumps.

- Script: `tools/check-registry.ps1`
- State: `docs/registry-watch/last-check.json` (date + fingerprints)
- Log: append to `docs/registry-watch/changelog.md` only when something **changed**

Tracked ids (edit script to extend): `create`, `ae2`, `jei`, `justenoughitems`, `roughlyenoughitems`, `jade`, `lookat`, plus keyword scan for `tfc` / `greg` / `gtceu` / `terrafirma` / `firmalife` / `greate`.
