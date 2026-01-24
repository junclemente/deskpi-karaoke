# Contributing to deskpi-karaoke

Thanks for contributing! This document captures the **intended workflow** for development, releases, and maintenance so future-you (and collaborators) stay consistent.

---

## Branching Model

- **main**
  - Production-ready code only
  - Tagged releases live here (e.g. `v0.3.5`)
  - Installer users on main are version-gated by Git tags

- **dev**
  - Active development
  - May include experimental or unfinished changes
  - Installer users on dev are gated by commit SHA

> Rule of thumb: **All features land in `dev` first.**

---

## Development Workflow

1. Create or update features on `dev`
2. Commit early and often
3. Test on real hardware if possible (Raspberry Pi)

```bash
git checkout dev
# make changes
git commit -m "Describe change"
git push origin dev
```

---

## Releasing a New Version (Stable)

When `dev` is stable and ready for release:

### 1. Open a Pull Request
- Source: `dev`
- Target: `main`
- Title example: `Release 0.3.6`
- Ensure:
  - Installer runs cleanly
  - No debug-only code remains
  - README / CHANGELOG are updated if needed

### 2. Merge the PR
- Use **Squash & merge** or **Merge commit**
- Do **not** rebase main

---

## Tagging a Release

After the PR is merged into `main`:

### Via GitHub Web UI (Recommended)

1. Go to **Releases**
2. Click **Draft a new release**
3. Create a new tag:
   - Tag: `vX.Y.Z`
   - Target: `main`
4. Release title:
   - `vX.Y.Z – Short Description`
5. Paste relevant CHANGELOG notes
6. Publish release

> Stable users update based on this tag.

---

## Documentation-Only Changes

- README, CHANGELOG, or comments **do not require a new tag**
- These can be committed directly to `main` or merged via PR
- Example:
  - Clarifying `pk` usage
  - Expanding troubleshooting notes

---

## Versioning Guidelines

Follow **semantic versioning**:

- **Patch (0.3.x)**  
  Bug fixes, installer improvements, dependency handling

- **Minor (0.x.0)**  
  New features, workflow changes

- **Major (x.0.0)**  
  Breaking changes or installer rewrites

---

## Maintenance Philosophy

- Prefer **idempotent installers**
- Avoid destructive actions without clear user intent
- Default to safe behavior for production users
- Document behavior instead of relying on tribal knowledge 🙂

---

## Questions?

Open an issue or check the README / CHANGELOG first.
