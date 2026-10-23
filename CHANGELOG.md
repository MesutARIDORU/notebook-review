# Changelog

## 1.3.0

- **Preview on first use:** `bridge.py preview` tells the agent what to do with the page after a rewrite. It prints `first` while nothing has been chosen, then `always`, `ask` or `request`. `--set` saves the default, and `--chat on|off|clear` saves a choice for the current chat session alone, which Claude Code and Codex can identify. The choices live in `~/.config/<slug>/preferences.json`, where the agent can read them before any page exists.
- **The first page asks:** on its first run the page shows a taped note with three choices: open every time, ask first, or only when asked. "Only when asked" shows a chat box typing the ways to ask ("preview", "show it on the page"…). With a known chat session, the note also offers "always open in this chat" and "don't open in this chat", sent to the bridge's new `POST /api/preview-chat`. Closing the note without a choice saves "ask first".
- **Settings:** a Preview line changes the default later. It shows only with the live bridge, which writes the file.
- **Preferences keep what they are not sent:** the page's settings no longer wipe keys they leave out, such as the preview choice; keys from older versions are dropped.
- **Title:** the product name is back in its felt-tip marker (Marker Felt where available); the rest of the page stays in the handwriting.

## 1.2.0

- **A notebook on a desk:** the page is a sheet of ruled paper with punched holes and a red margin, lying on a wooden desk. The text, the title and the card are written in Patrick Hand, a handwriting font embedded in the page (SIL Open Font License, see `fonts/OFL.txt`), so the page still makes no outside requests. The paper grain, the masking tape, the highlighter stroke and the wood come from `textures/` and are embedded the same way.
- **The text:** changed words sit on a green highlighter. Once a change is approved, its original stays readable, struck through, just above or before the new text. The handwriting is drawn a little thinner than the font so it reads like a pen line.
- **The margin:** each change has a numbered circle at its middle, and a change over several lines gets an orange crayon brace. The first sentence of its reason is written in the right margin with a small arrow. Circles of changes that sit close together stack instead of covering each other.
- **The card:** a taped note card, fixed beside the page at the top; a long card scrolls under its tape. "Apply the suggestion" (key `1`) approves the change and opens the next one, with "Keep the original" (`2`) and "Edit it myself" (`3`) below it. Each of the other versions has an arrow button. The reason sits in a dashed box.
- **The versions bubble:** hovering over a change opens a hand-drawn speech bubble above its first word, written in the red of the title's underline. It names the version in the text and its place in the list. ‹ › step through the versions and ▾ lists them all, with a tick on the current one. With the live bridge and nothing to choose from, the list can ask the agent for the usual three. The bubble shows in the final-text preview too.
- **Progress:** the last line counts the approved changes: "3 / 5 approved".
- **Preferences:** the type setting is stored as `type` (hand, airy, soft, book) and defaults to hand. An earlier `font` setting is ignored, so everyone sees the new page once.

## 1.1.0

- **Versions in place:** hovering over a change shows small arrows above its first word. They step through the suggestion, its shorter, more formal and warmer versions, the user's own text and the original, right in the text; the version's name shows beside them for a moment. The arrows sit at the start of the part, so they don't move when its text gets longer or shorter.
- **Final text:** the eye button next to the title, or the `p` key, shows the text with the decisions applied and nothing else on the page. Hovering over a changed part there shows the same arrows.
- **Card at the top:** on a wide screen the card opens beside the page at the top and stays there while the page scrolls. The dashed line runs from the sentence into the gap and along it to the card.
- **The page's last line:** progress, open questions, "Keep the rest" and "Send to agent" moved from the floating bar onto the last ruled line of the page. Clicking "1 open question" goes to the next question.
- **Divider:** a thin highlighter stroke separates the skill's notes in the header from the text.
- **Readable card:** section names are clearer. The original is written in red pen, and its removed words are crossed out with a faint marker that runs behind the letters.
- The Edit menu's "preview" is now "show the feedback", so it isn't confused with the final text.

## 1.0.0

First release. The review page and the live bridge move out of İnsanlık öldü mü? 1.3.0 and Still Human? into one place.

- The page has no language of its own: its text comes from `strings/tr.json` and `strings/en.json`, and each skill describes itself in `notebook.json`.
- Sentence splitting knows each language's abbreviations, so "Dr. Ayşe" and "Ms. Patel" no longer end a sentence.
- Text the user writes can no longer be read as one of the page's slots.
- `tools/sync.py` copies the notebook into a skill; a daily workflow in each skill does the same.
