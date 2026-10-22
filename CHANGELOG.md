# Changelog

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
