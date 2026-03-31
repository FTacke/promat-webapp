# PROMAT Repository Guidance

- `docs/PROMAT_ Plattform-, Daten- und Filestruktur.md` is the binding source of truth for target architecture, routing, data model, and filesystem semantics.
- Root `AGENTS.md` operationalizes repo-wide behavior; scoped `AGENTS.md` files add local rules.
- `app/` is the only application source root.
- `data/`, `public/`, and `secure/` are runtime boundaries and stay outside the versioned app core.
- `AUTH_DATABASE_URL`, `PROMAT_RUNTIME_ROOT`, and `PROMAT_PUBLIC_ROOT` are the canonical runtime variables.
- Do not reintroduce old German technical slugs, legacy public routes, or old runtime path names.
- The bootstrap stays free of search and corpus-engine integrations until they are intentionally introduced.