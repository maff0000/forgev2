# Stage 1 Environment Reconciliation — FORGEV2-STAGE1-ENV-001

**Date:** 2026-10-24
**Purpose:** Record approved environment boundaries and attribute workspace evidence for Stage 1.
**Disclosure:** Public-safe summary; excludes host identity, network addressing, access configuration and detailed security findings.

## Approved environment decisions

- ForgeV2 source development is rooted at `/srv/src/forgev2/`.
- The canonical ForgeV2 source checkout is `/srv/src/forgev2/main/`.
- Engine-development worktrees are reserved under `/srv/src/forgev2/worktrees/`.
- `/srv/forgev2/` is the protected engine installation and is not an application workspace.
- `/srv/pacman/` is the independent PACMAN application root.
- Network perimeter security is managed externally by the infrastructure provider. No host firewall installation is required.

These are approved deployment-specific decisions. They do not establish global FOUNDRY path conventions or prove that any host is ready for delivery workloads.

## Workspace report

**Initially reported by Claude; the later source checkout and synchronization state was independently checked by Codex:**

- The ForgeV2 source repository is cloned at the approved canonical source location.
- Its HEAD matches the approved ForgeV2 baseline `071426b4cf2b39c39e6e6dd5be619e8afd06d8cb`, and its working tree is clean.
- The separate engine-development worktrees directory exists.
- The protected engine installation and PACMAN locations were left untouched.
- No delivery account or GitHub write credentials are yet available in that reported workspace.

This record preserves the attribution of the original Claude report. Codex's later read-only check independently verified the checkout and source synchronization described below. Neither check establishes enforced delivery isolation or credential/security readiness.

## Independent repository checks

At the original environment reconciliation check, Codex independently read these GitHub references:

- `maff0000/forgev2` `main`: `071426b4cf2b39c39e6e6dd5be619e8afd06d8cb`, the verified baseline at that time.
- `maff0000/foundry` `main`: `aee86185aac6aa0d2ab7a243138c423292af191a`, the verified governing baseline at that time.
- [Initiation Issue #1](https://github.com/maff0000/forgev2/issues/1): open, with the stated initiation baseline and scope.

The subsequent ForgeV2 source-sync read-back is recorded below. The original GitHub checks did not independently verify the reported Linux workspace.

## Independent workspace verification and controlled source synchronization

Codex connected to the authorised development host using strict host-key checking and verified its identity against the assignment. Host-specific identity and access details are omitted from this public record.

At verification, Codex confirmed:

- `/srv/src/forgev2/main/` was the `maff0000/forgev2` repository, on branch `main`, at the expected pre-sync SHA `071426b4cf2b39c39e6e6dd5be619e8afd06d8cb`, with a clean working tree.
- `/srv/src/forgev2/worktrees/` existed separately; the only registered Git worktree was `/srv/src/forgev2/main/`.
- `/srv/forgev2/` and `/srv/pacman/` were absent at that verification. No changes were made to those paths.

Under the separately authorised source-sync operation, Codex fetched the existing remote, verified `origin/main` was exactly `6da78603478093ff799a2aa70c83a6fdc0d328c3`, checked ancestry and confirmed the intervening diff contained only `DECISIONS.md`, `PROJECT-INITIATION-MANDATE.md`, `README.md` and this evidence record. `git merge --ff-only origin/main` succeeded. The canonical checkout and GitHub `main` both read back at `6da78603478093ff799a2aa70c83a6fdc0d328c3`, branch `main`, clean tree, with only the canonical worktree registered.

The source synchronization changed documentation only. No ForgeV2 or application script was run, and no dependency inventory, security test, engine installation or implementation was performed.

## Readiness status

Workspace identity, checkout lineage, cleanliness, worktree boundary and source synchronization were independently verified as described above. Security and delivery readiness remain **PENDING**: the external-code register reports incomplete coverage; a non-root delivery identity or equivalent enforceable engine protection and appropriately scoped credentials have not been verified; and runtime/host security acceptance remains outstanding. The approved IONOS-managed network perimeter remains in force; no host firewall installation is required. Nothing here declares Stage 1 closed or grants engineering implementation authority.
