# Developer site

From the repository root, install the pinned site dependencies in a virtual
environment, then build or preview the current documentation:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r developer-docs/requirements.txt
.venv/bin/mkdocs build --strict -f developer-docs/mkdocs.yml
.venv/bin/mkdocs serve -f developer-docs/mkdocs.yml --dev-addr 127.0.0.1:8000
```

Open <http://127.0.0.1:8000/>. The preview reloads when documentation changes.
Generated output goes to the ignored `developer-docs/site/` directory; do not
commit it.

Navigation is defined in `docs/.pages`: seven current pages plus the archive
index. Update those current pages in place. Archived studies remain available
for targeted lookup and are excluded from normal search. Figures under
`docs/assets/` are copied into the rendered site.

This is a local preview. Publishing uses the separately gated shared developer
site workflow described in the repository README.
