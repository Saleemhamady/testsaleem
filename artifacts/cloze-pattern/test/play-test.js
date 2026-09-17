// Drives the generated fractions game in a real browser against the simulated
// Moodle Cloze DOM, and asserts the contract the pattern depends on:
//
//   1. the score display and the hidden Moodle answer field stay in step
//   2. a correct answer scores, a wrong answer does not, and neither penalises
//   3. the hidden field ends the game holding the mark Moodle will grade
//   4. review mode restores the saved score and accepts no further input
//   5. every shape part is reachable and operable from the keyboard
//   6. the game never overwrites #score-display
//
// Run: node artifacts/cloze-pattern/test/play-test.js
const path = require('path');
const fs = require('fs');
const os = require('os');
const { chromium } = require('playwright-core');
const { buildPage } = require('./harness');

const SRC = path.join(__dirname, '..', 'fractions-game.html');
const EXEC = '/opt/pw-browsers/chromium-1194/chrome-linux/chrome';

// Mirrors the question bank in the game, so the test knows the right answers.
const QUESTIONS = [
  { num: 1, den: 2 }, { num: 1, den: 4 }, { num: 3, den: 4 }, { num: 2, den: 3 },
  { num: 2, den: 6 }, { num: 5, den: 8 }, { num: 3, den: 5 }, { num: 4, den: 6 },
  { num: 5, den: 6 }, { num: 7, den: 8 }
];

let failures = 0;
function check(name, pass, detail = '') {
  console.log(`${pass ? '  ok  ' : ' FAIL '} ${name}${detail ? ' — ' + detail : ''}`);
  if (!pass) failures++;
}

function writeTemp(name, opts) {
  const p = path.join(fs.mkdtempSync(path.join(os.tmpdir(), 'cloze-')), name);
  fs.writeFileSync(p, buildPage(fs.readFileSync(SRC, 'utf8'), opts));
  return 'file://' + p;
}

(async () => {
  const browser = await chromium.launch({ executablePath: EXEC });

  // ---- 1. play the whole game, deliberately getting question 3 wrong ----
  {
    const page = await browser.newPage();
    await page.goto(writeTemp('play.html', {}));

    const WRONG_AT = 2; // 0-based: third question
    let expected = 0;

    for (let i = 0; i < QUESTIONS.length; i++) {
      const q = QUESTIONS[i];
      const parts = page.locator('#game-container svg [role="button"]');
      const count = await parts.count();
      if (count !== q.den) {
        check(`q${i + 1} renders ${q.den} parts`, false, `got ${count}`);
        break;
      }

      // Shade the right number of parts, except on the question we throw.
      const toShade = i === WRONG_AT ? Math.max(0, q.num - 1) : q.num;
      for (let k = 0; k < toShade; k++) await parts.nth(k).click();

      await page.getByRole('button', { name: 'Check' }).click();
      if (i !== WRONG_AT) expected++;

      const box = await page.locator('#cloze-input').inputValue();
      const shown = await page.locator('#score-display').textContent();
      if (box !== String(expected) || shown !== `Score: ${expected}`) {
        check(`q${i + 1} score propagates`, false, `field=${box} display=${shown} expected=${expected}`);
        break;
      }

      if (i < QUESTIONS.length - 1) await page.getByRole('button', { name: 'Next' }).click();
    }

    check('plays 10 questions, score tracks the hidden field', expected === 9, `final expected ${expected}`);
    check('one wrong answer costs exactly one point, no penalty',
      (await page.locator('#cloze-input').inputValue()) === '9');
    check('#score-display survived (never overwritten)',
      (await page.locator('#score-display').count()) === 1);
    check('hidden field is not visible to the learner',
      !(await page.locator('#cloze-input').isVisible()));
    check('final score message shown',
      (await page.locator('#game-container').textContent()).includes('You scored 9 out of 10'));
    await page.close();
  }

  // ---- 2. keyboard operability (WCAG: the shape must not be mouse-only) ----
  {
    const page = await browser.newPage();
    await page.goto(writeTemp('kbd.html', {}));
    const first = page.locator('#game-container svg [role="button"]').first();
    await first.focus();
    await page.keyboard.press('Enter');
    const pressed = await first.getAttribute('aria-pressed');
    check('shape parts are focusable and toggle with Enter', pressed === 'true');
    await page.keyboard.press(' ');
    check('Space toggles a part back off',
      (await first.getAttribute('aria-pressed')) === 'false');
    check('parts expose an accessible name',
      (await first.getAttribute('aria-label')) === 'Part 1 of 2');
    await page.close();
  }

  // ---- 3. review mode: restore the saved mark, accept no further input ----
  {
    const page = await browser.newPage();
    await page.goto(writeTemp('review.html', { readOnly: true, restoreValue: '7' }));
    check('review mode restores the saved score to the display',
      (await page.locator('#score-display').textContent()) === 'Score: 7');
    check('review mode renders no Check button',
      (await page.getByRole('button', { name: 'Check' }).count()) === 0);
    const parts = page.locator('#game-container svg [role="button"]');
    check('review mode renders no interactive shape', (await parts.count()) === 0);
    check('review mode does not alter the stored value',
      (await page.locator('#cloze-input').inputValue()) === '7');
    await page.close();
  }

  // ---- 4. the tamper case the pattern does NOT defend against -----------
  // Documenting this as a test rather than a footnote: the score field is
  // client-side, so anyone who can open the console can set it directly.
  {
    const page = await browser.newPage();
    await page.goto(writeTemp('tamper.html', {}));
    await page.evaluate(() => {
      const el = document.querySelector('#cloze-input');
      el.value = '10';
      el.dispatchEvent(new Event('change', { bubbles: true }));
    });
    check('KNOWN LIMITATION: console can set the score field to 10 without playing',
      (await page.locator('#cloze-input').inputValue()) === '10');
    await page.close();
  }

  await browser.close();
  console.log(failures ? `\n${failures} check(s) failed` : '\nall checks passed');
  process.exit(failures ? 1 : 0);
})();
