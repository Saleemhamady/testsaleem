# Authoring prompt — Cloze answer-field bridge

Drop-in replacement for the original prompt. Changes are marked `[FIX n]` and explained in
`README.md`. Everything the original got right — the fixed template, the "output the whole thing"
instruction, the explicit list of things not to redeclare — is kept, because those are what make the
output paste-ready instead of a fragment.

---

```text
################ EDIT THIS — describe your game ################
My game is needed to help 10 year olds interact with fractions in math. They should be able to
select parts of a pie or other shape to make a given fraction. The game has 10 questions each
worth 1 point. No penalty on wrong answers.
Maximum score: 10
Learner age: 10
##################################################################

Using the fixed template below, write the complete Moodle question text for this game. Do not
change anything in the template except the one spot marked "YOUR GAME CODE GOES HERE" — fill that
in with your game's HTML/JavaScript, then output the ENTIRE template back, merged with your code,
as one single ready-to-paste block. Don't explain your code or give me a fragment — I need the
whole thing, exactly like the template below but with your game inserted.

Rules for the code you insert:
- Do NOT wrap it in its own function or IIFE — it goes inside an existing one, so write plain
  top-level statements.
- Do not redeclare game-container, setScore, score, isReadOnly, MAX_SCORE, logStep or trace —
  they already exist (see the template).
- game-container already contains a div#score-display — APPEND your game's elements to it, never
  overwrite its innerHTML, or the score display disappears.
- Call setScore(value) every time the score changes, passing the new total, e.g. setScore(score + 1).
  Don't build your own "Score: ..." display — setScore() already updates it.
- When isReadOnly is true, don't attach any click/drag/keyboard handlers — just leave the restored
  score showing, and don't render interactive controls at all.
- No external libraries unless I explicitly ask for one, no network requests. Clean, commented code.

[FIX 3] - Set MAX_SCORE at the top of the template to this game's maximum. The score field in the
  template must be regenerated to match: run `node make-cloze-field.js <MAX_SCORE>` and paste the
  result over the #hidden-score line.

[FIX 7] - Every button you create must have type="button". A bare <button> inside Moodle's question
  form defaults to type="submit" and will submit the attempt when the learner presses it.

[FIX 8] - Accessibility, because this is graded work and some learners cannot use a mouse:
  - anything clickable gets role="button", tabindex="0", an aria-label, and Enter/Space handling
  - never signal state by colour alone — add a pattern, a border, a tick or a label
  - if you set outline:none to replace the browser focus ring, draw your own visible focus state
  - put status messages in an element with role="status" and aria-live="polite"

[FIX 9] - Do not use setTimeout/setInterval to auto-advance, and do not put the game on a timer
  unless I ask. A learner using a screen reader or thinking slowly must not lose points to a clock.

[FIX 6] - Call logStep('<short tag>') at each meaningful step (e.g. 'q3:wrong:shaded2of4') so the
  instructor can see the trajectory, not just the total. Keep the whole trace under 250 characters.

[FIX 10] - After the code, do not add commentary. But DO make the game deterministic: use a fixed
  question order rather than Math.random(), so that a learner describing "question 4" and the
  teacher looking at their screen see the same thing.

--- TEMPLATE (copy exactly, only fill in the marked section) ---

<paste the contents of template-hardened.html here>
```

---

## Why the fixed-template approach is right

The instruction to return the entire template merged, rather than a snippet, is the single most
valuable line in the original prompt and should be kept. It removes the step where a teacher has to
splice generated code into boilerplate — which is where this kind of workflow normally breaks, and
which is exactly the step a non-programmer cannot debug when it goes wrong.

The additions above are all of the same kind: they move a failure out of the teacher's hands and into
the prompt, so the model has to get it right before anyone sees the output.
