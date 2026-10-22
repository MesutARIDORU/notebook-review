# Changelog

## 1.0.0

First release. The review page and the live bridge move out of İnsanlık öldü mü? 1.3.0 and Still Human? into one place.

- The page has no language of its own: its text comes from `strings/tr.json` and `strings/en.json`, and each skill describes itself in `notebook.json`.
- Sentence splitting knows each language's abbreviations, so "Dr. Ayşe" and "Ms. Patel" no longer end a sentence.
- Text the user writes can no longer be read as one of the page's slots.
- `tools/sync.py` copies the notebook into a skill; a daily workflow in each skill does the same.
