# Notebook review

The review page and the live bridge shared by two writing skills:

- [İnsanlık öldü mü?](https://github.com/MesutARIDORU/insanlik-oldu-mu) for Turkish
- [Still Human?](https://github.com/MesutARIDORU/still-human) for English

Both skills rewrite a text and then show the user what changed on a notebook page. On that page the user goes through the changes one by one: keeps one, reverts one, picks another option or writes their own, then sends the decisions back to the agent. The page, and the small local server that connects it to the agent, live here. Each skill keeps its own content: patterns, references, audit and docs.

A change made here reaches both skills. The page itself has no language: each skill describes itself in a product file, and the page's text comes from `strings/<language>.json`.

## What is in it

```
notebook/
  page.py         builds the page: aligns the two texts, ties the agent's notes to the changes
  bridge.py       the live bridge: a local server between the page and Claude Code, Codex or Gemini CLI
  template.html   the page: markup, style and script, with {{key}} slots for text
  product.py      reads a skill's notebook.json and serves its texts
  languages.py    lowercasing and abbreviations, per language
  strings/en.json the page's and the bridge's text in English
  strings/tr.json the same keys in Turkish
  fonts/          Patrick Hand, the handwriting the page is written in, with its license
  textures/       paper grain, masking tape, highlighter and wood
  VERSION
tools/sync.py     copies notebook/ into a skill
tests/            texts, round trips, the rendered page and the bridge
```

Only the Python 3 standard library is used. The page is a single HTML file with no outside requests: the font and the textures are embedded in it.

## How a skill uses it

A skill keeps a copy of `notebook/` at its root, next to a `notebook.json`:

```json
{
  "name": "Still Human?",
  "slug": "still-human",
  "repo": "MesutARIDORU/still-human",
  "language": "en",
  "title_html": "Still Human<b>?</b>",
  "date_format": "%Y-%m-%d %H:%M",
  "root_env": "STILL_HUMAN_ROOT",
  "patterns": {"R1": "Contrast polish"},
  "strings": {}
}
```

| Field | What it does |
|---|---|
| `name` | Product name on the page, in the feedback header and in the bridge's messages |
| `slug` | Settings folder (`~/.config/<slug>`), temp folder, browser storage keys, download name |
| `repo` | The GitHub repository whose releases the daily update check compares with (`owner/name`) |
| `language` | Picks `strings/<language>.json` and the language rules |
| `title_html` | The page title next to the logo |
| `date_format` | How the date is written in the page's details |
| `root_env` | Environment variable that can move the bridge's session folder |
| `patterns` | Names shown on the card for the pattern codes in the agent's notes |
| `strings` | Any key from the strings file the skill wants to say differently |

Its `scripts/review.py` and `scripts/bridge.py` are thin wrappers:

```python
# scripts/review.py
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))
import audit, bridge
from notebook import page
from notebook.product import load_product

if __name__ == "__main__":
    page.main(load_product(os.path.join(HERE, "..", "notebook.json")), audit, bridge, bridge.__file__)
```

```python
# scripts/bridge.py
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
from notebook import bridge
from notebook.product import load_product

bridge.configure(load_product(os.path.join(HERE, "..", "notebook.json")), __file__)
start, call, read_info = bridge.start, bridge.call, bridge.read_info

if __name__ == "__main__":
    bridge.main()
```

The skill's own `audit.py` gives the page four functions: `read(source)`, `measure(text)` (with at least `"words"`), `alarms(measurement)` and `guess_profile(text)`.

## Whether the page opens

After a rewrite the agent asks the bridge what to do with the page:

```bash
python3 scripts/bridge.py preview
```

It prints one word: `first` (nothing chosen yet: the agent opens the page, and a note on it asks the user), `always`, `ask` or `request` (only when the user asks). `--set always|ask|request` saves the default; `--chat on|off|clear` saves a choice for the current chat session alone, which Claude Code and Codex can identify. Both live in `~/.config/<slug>/preferences.json`, next to the page's own settings, so the agent can read them before any page exists. The page offers the same choice on its first run and on the Preview line of its settings.

## Daily update check

Once a day, the first time the skill runs, the agent asks the bridge whether a newer release is out:

```bash
python3 scripts/bridge.py update
```

The first line is one word:
- `available`: the newest GitHub release of `repo` is newer than the version in the skill's `SKILL.md` (`metadata: version`). The lines after it give `installed`, `latest`, `name` and `url`, and `reverted_from` when the user once went back from a release. The skill decides whether to update first and ask afterwards, or to ask first.
- `current`: the installed version is the newest.
- `checked`: today's look is done; the agent says nothing. A "not now" from the user therefore waits until the next day, and so does a look that failed.
- `unknown`: no `repo`, no version, or GitHub out of reach; the agent says nothing.

The look and its day are kept in `~/.config/<slug>/update.json`. `--now` looks again even if today's look is done.

`--apply` updates the skill where it is installed and prints `updated`, `current`, `failed` (with `error`) or `manual`:
- in the shared folder `~/.agents/skills/<slug>`: `npx -y skills update -g <slug>`. A copy pinned to an older release stays where it is with `update`, so it is then added again from the repository: `npx -y skills add <repo> -g -y -a codex [claude-code]`, with Claude Code only when it has a link to the copy,
- in a git clone: `git pull --ff-only`,
- anywhere else (a copy, a zip in a chat app): `manual`, with the `npx skills add` command and the releases page.

`--revert` goes back to the version the last `--apply` replaced and prints `reverted`, `failed` or `manual`. In the shared folder it adds that release's tag again (`npx -y skills add https://github.com/<repo>/tree/v<version> -g -y -a …`) and records the release it went back from as `reverted_from`, which the next looks print so the skill asks before offering it again. A clone may hold the user's own work, so there it prints the `git checkout` command instead of running it.

The request goes to `api.github.com` with a 4-second limit. Python from python.org on macOS has no root certificates until "Install Certificates" is run, so a failed certificate check is retried with the system's bundle (`/etc/ssl/cert.pem` and the usual Linux paths), then with `curl`.

## Notes the agent writes

```json
{
  "title": "Team announcement",
  "mode": "Full rewrite",
  "profile": {"label": "Business correspondence", "sector": "software", "audience": "the support team"},
  "changes": [
    {"before": "sentence in the original", "after": "sentence that replaced it",
     "reason": "short reason", "pattern": "R1",
     "alternatives": [{"kind": "Shorter", "text": "..."}, {"kind": "More formal", "text": "..."}, {"kind": "Warmer", "text": "..."}]}
  ]
}
```

Every field is optional. The `before` and `after` sentences anchor the changes, so a heavy rewrite still lines up sentence by sentence. A deleted sentence has an empty `after`, an added one an empty `before`.

## Keeping the skills in step

Each skill has a workflow (`tools/skill-workflow.yml`, copied to `.github/workflows/sync-notebook.yml`) that checks out this repository, runs `tools/sync.py` and commits the new `notebook/` when it changed. It runs every day, by hand, and when this repository asks for it.

On every push to `main`, CI runs the tests. When they pass and the `NOTEBOOK_SYNC_TOKEN` secret is set, it asks both skills to sync right away. Running CI by hand (Actions → CI → Run workflow) does the same. The token is a fine-grained personal access token with **Contents: read and write** on the two skill repositories. Without it, the daily run picks the change up.

By hand:

```bash
python3 tools/sync.py ../insanlik-oldu-mu
```

```bash
python3 tools/sync.py ../still-human --check
```

## Adding a language

Copy `strings/en.json` to `strings/<code>.json` and translate the values. Keep the keys, the `{placeholders}` and the `{"one", "other"}` forms. Add the language's abbreviations, and its lowercasing rule if it has one, to `languages.py`. The tests check that every strings file has the same keys and placeholders.

## Tests

```bash
python3 -m unittest discover -s tests -v
```

They check that both strings files match, that every key the code uses exists, that keeping every change gives the new text and reverting every change gives the old one (including added and deleted sentences), that the rendered page has no empty slot left, and that the bridge starts, takes the user's decisions and closes. When `node` is installed they also check that the page's script parses.

## License

MIT. Patrick Hand, in `notebook/fonts/`, is under the SIL Open Font License 1.1 (`notebook/fonts/OFL.txt`).
