# The Cloze answer-field bridge

The mechanism at the centre of this project: a generated HTML/JavaScript game runs **inside a Moodle
Cloze question**, and writes its score into a hidden Cloze answer field. Moodle then autogrades the
game play with no plugin, no H5P, no LTI tool and no server-side code.

```
learner plays generated game  →  setScore(n)  →  hidden {…:NUMERICAL:…} input
                                                          ↓
                          Moodle question engine grades the response as normal
                                                          ↓
                                   gradebook, reports, question statistics
```

This is the lightest of the integration patterns in the paper (`paper/main.md`, Pattern E) and the
only one a teacher can deploy alone, without asking anyone to install anything.

## Files

| File | What it is |
|---|---|
| `template-hardened.html` | Drop-in replacement for the original template, with the fixes below. |
| `fractions-game.html` | Complete worked example — fraction shading game for 10-year-olds, ready to paste. |
| `make-cloze-field.js` | Generates the partial-credit Cloze field for a game worth N points. |
| `prompt-template.md` | The authoring prompt, updated to match the hardened template. |
| `test/harness.js` | Builds a page imitating the DOM Moodle produces for a Cloze question. |
| `test/play-test.js` | Drives the game in Chromium and asserts the whole contract. |

## Running the tests

```bash
npm install playwright-core
node artifacts/cloze-pattern/test/play-test.js
```

The test plays all ten questions, deliberately failing one, and checks that the hidden field tracks
the visible score at every step, that review mode restores the saved mark without accepting further
input, that every shape part is keyboard-operable, and that `#score-display` is never destroyed.

---

## Two problems in the original template

### 1. The grading was silently wrong

The original score field was:

```
{1:NUMERICAL:=7:2}
```

A `NUMERICAL` Cloze answer is graded **right or wrong against a tolerance**. It does not scale the
mark with the value. With `=7:2`, any score from **5 to 9 earns 100%**, and everything else —
including a perfect 10 — earns **0%**.

For a ten-point game that is close to the opposite of the intended behaviour. The fix is one accepted
answer per attainable score, each with its own percentage:

```
{1:NUMERICAL:=10:0~%90%9:0~%80%8:0~%70%7:0~%60%6:0~%50%5:0~%40%4:0~%30%3:0~%20%2:0~%10%1:0~%0%0:0}
```

Generate it for any maximum with `node make-cloze-field.js 10`.

### 2. Hiding the field does not prevent editing

`style="display:none"` hides the input from the page. It does not protect it. Anyone who opens the
browser console can set the value directly, and the browser test in `test/play-test.js` includes this
as an explicit check so that the limitation is recorded rather than assumed away:

```js
document.querySelector('#cloze-input').value = '10';
```

Nothing done in client-side JavaScript can fix this, because the code enforcing the rule is the code
the learner controls. A checksum or an obfuscated token raises the effort from *type a number* to
*read the JavaScript*, which is a real increase for a ten-year-old and no obstacle at all to a
motivated undergraduate.

**The honest framing is that this pattern is excellent for formative and low-stakes work and should
not carry high-stakes marks on its own.** For the fractions game — a ten-year-old practising
fractions, where the child who fakes the score is only cheating themselves out of the practice — that
is entirely fine. For a summative university assessment it is not, and the paper's Pattern C (LTI
with server-side scoring) exists for that case.

What *does* help, without pretending to be security:

- **Record the trajectory as well as the total** (`logStep()` in the hardened template). A forged
  `10` with an empty or incoherent trace is visible in the response report. This is a signal for a
  conversation, never evidence for a misconduct case.
- **Keep the stakes proportionate.** A game worth 2% of a course attracts no effort to defeat.
- **Anchor the mark elsewhere** if it matters — a few invigilated or oral checkpoints validate a
  semester of unsupervised play far better than trying to harden the play itself.

## Eight smaller fixes in the hardened template

| | Problem | Consequence |
|---|---|---|
| FIX 1 | `NUMERICAL` graded right/wrong, not proportionally | Marks wrong for every score (above) |
| FIX 2 | `document.currentScript.closest(...)` throws if `currentScript` is null | Game silently fails to appear |
| FIX 3 | No maximum score defined | Score can exceed the field's accepted answers and grade 0 |
| FIX 4 | `parseFloat` result used unchecked | `NaN` written to the field submits as blank and scores 0 |
| FIX 5 | `isReadOnly` false when the answer field is absent | Game stays live in review; points go nowhere |
| FIX 6 | Only the total is recorded | No way for an instructor to see *how* the learner played |
| FIX 7 | `<button>` inside Moodle's form defaults to `type="submit"` | Pressing a game button submits the attempt |
| FIX 8 | No keyboard or non-colour encoding requirement in the prompt | Generated games are routinely mouse-only |

## Deployment notes

- Question type: **Embedded answers (Cloze)**. Question text format: **HTML**.
- Some Moodle sites strip `<script>` from question text depending on how the site is configured and
  what capabilities the author holds. Test with one question before authoring a set.
- Use the **Deferred feedback** behaviour. Behaviours that re-render the question in place can
  reinsert the script node without executing it, which makes the game vanish mid-attempt.
- Set the question penalty to **0** for a no-penalty game.
- Preview the question, play it, and check the response in the attempt review before releasing it:
  the score in the gradebook is the only thing that proves the bridge is connected.
