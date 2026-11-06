# Git workflow

- `main` is protected by convention: nobody commits to it directly.
- One branch per module, named `module-<number>-<short-name>`, for example `module-12-scaling`.
- Open a pull request into `main` and get one teammate to review before merging.
- Pull from `main` before you start work each day: `git pull origin main`.
- Keep commits small, with messages like `module 12: add fixed vs autoscale cost calc`.
- Each person edits only their own page files. If you need to change something in `common/`, tell the group first, since everyone imports it.
- Never commit `.env` or any credentials.
