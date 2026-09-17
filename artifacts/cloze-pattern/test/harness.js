// Builds a standalone page that imitates the DOM Moodle produces for a Cloze
// (embedded-answers) question, so a generated game can be exercised in a real
// browser before it is pasted into Moodle.
//
// What is imitated:
//   - the .que wrapper Moodle puts around every question on the page
//   - the Cloze {n:NUMERICAL:...} placeholder rendered as a text input inside
//     the author's hidden <span>
//   - the readonly input Moodle renders when the attempt is being reviewed
//
// Not imitated: server-side grading, the question engine, form submission.
const fs = require('fs');

function buildPage(questionHtml, { readOnly = false, restoreValue = '' } = {}) {
  // Moodle replaces the Cloze placeholder with an <input>. The author's
  // hidden span stays, which is what makes the field invisible on the page.
  const rendered = questionHtml.replace(
    /\{[^{}]*:NUMERICAL:[^{}]*\}/g,
    `<input type="text" id="cloze-input" name="q1:1_sub1_answer" ` +
    `class="form-control answerinputfield" value="${restoreValue}" ` +
    `${readOnly ? 'readonly' : ''}>`
  );

  return `<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><title>Moodle Cloze harness</title></head>
<body>
  <div class="que multianswer deferredfeedback">
    <div class="formulation">
      <form method="post" onsubmit="return false">
        ${rendered}
      </form>
    </div>
  </div>
</body></html>`;
}

if (require.main === module) {
  const [, , src, out, mode, restore] = process.argv;
  const html = fs.readFileSync(src, 'utf8');
  fs.writeFileSync(out, buildPage(html, {
    readOnly: mode === 'readonly',
    restoreValue: restore || ''
  }));
  console.log('wrote', out, '(mode:', mode || 'interactive', ')');
}

module.exports = { buildPage };
