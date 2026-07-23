const pptxgen = require('pptxgenjs');

/* ============================================================
   CSE476 Agentic AI and Intelligent Automation
   Lecture Zero. Flipbook format. Light theme.

   Design system carried over from the CSE205 / Launchpad decks:
   white background, Cambria headings, Calibri body, teal and
   indigo accents. Red box used sparingly and only as a pointer.

   Currency verified 23 July 2026:
     Azure AI Foundry renamed Microsoft Foundry, Jan 2026 Product Terms
     Bot Framework SDK retired Dec 2025, repo archived
     Microsoft Agent Framework 1.0 shipped 3 April 2026
     GitHub Models endpoint: https://models.github.ai/inference
     Azure for Students: 100 USD, 12 months, no credit card
   ============================================================ */

const pres = new pptxgen();
pres.layout = 'LAYOUT_WIDE';
pres.author = 'Rohit Bharti';
pres.title = 'CSE476 U1 L1';

const W = 13.333, H = 7.5;

// palette
const INK = '1F2937';
const MUTED = '6B7280';
const FAINT = '9CA3AF';
const TEAL = '0F766E';
const TEAL_T = 'E6FBF7';
const TEAL_M = 'A7E8DC';
const INDIGO = '3730A3';
const INDIGO_T = 'ECEBFB';
const INDIGO_M = 'B9B5EA';
const RED = 'C0392B';
const RED_T = 'FDECEA';
const AMBER = 'A16207';
const AMBER_T = 'FEF6E0';
const PANEL = 'F7F9FB';
const LINE = 'E3E8EE';

const SERIF = 'Cambria';
const SANS = 'Calibri';

let N = 0;

function base() {
  const s = pres.addSlide();
  s.background = { color: 'FFFFFF' };
  return s;
}

function footer(s) {
  N += 1;
  s.addText('CSE476  Unit 1  Lecture 1', {
    x: 0.62, y: 6.98, w: 8, h: 0.3, fontFace: SANS, fontSize: 9,
    color: FAINT, margin: 0, valign: 'middle'
  });
  s.addText(String(N), {
    x: 12.1, y: 6.98, w: 0.62, h: 0.3, fontFace: SANS, fontSize: 9,
    color: FAINT, align: 'right', margin: 0, valign: 'middle'
  });
}

// ---------- slide constructors ----------

function titleSlide(o) {
  const s = base();
  s.addShape(pres.ShapeType.rect, { x: 0, y: 0, w: W, h: H, fill: { color: PANEL } });
  s.addShape(pres.ShapeType.ellipse, {
    x: 9.4, y: -1.5, w: 6.2, h: 6.2, fill: { color: TEAL_T }
  });
  s.addShape(pres.ShapeType.ellipse, {
    x: 10.9, y: 3.4, w: 4.4, h: 4.4, fill: { color: INDIGO_T }
  });
  s.addText(o.kicker, {
    x: 0.9, y: 1.5, w: 8.4, h: 0.34, fontFace: SANS, fontSize: 12.5,
    color: TEAL, bold: true, charSpacing: 1.6, margin: 0
  });
  s.addText(o.code, {
    x: 0.9, y: 2.0, w: 8.4, h: 0.5, fontFace: SANS, fontSize: 26,
    color: MUTED, margin: 0
  });
  s.addText(o.title, {
    x: 0.9, y: 2.55, w: 9.0, h: 1.5, fontFace: SERIF, fontSize: 42,
    color: INK, bold: true, margin: 0, lineSpacing: 46
  });
  s.addShape(pres.ShapeType.rect, {
    x: 0.9, y: 4.25, w: 1.5, h: 0.045, fill: { color: TEAL }
  });
  s.addText(o.sub, {
    x: 0.9, y: 4.55, w: 8.6, h: 0.9, fontFace: SANS, fontSize: 17,
    color: MUTED, margin: 0, lineSpacing: 26
  });
  s.addText(o.foot, {
    x: 0.9, y: 6.15, w: 8.6, h: 0.4, fontFace: SANS, fontSize: 12,
    color: FAINT, margin: 0
  });
  N += 1;
  return s;
}

function divider(num, title, sub) {
  const s = base();
  s.addShape(pres.ShapeType.rect, { x: 0, y: 0, w: W, h: H, fill: { color: INDIGO } });
  s.addShape(pres.ShapeType.ellipse, {
    x: 10.2, y: -2.0, w: 6.6, h: 6.6, fill: { color: '4B41C4' }
  });
  s.addText(num, {
    x: 1.1, y: 2.35, w: 3, h: 0.5, fontFace: SANS, fontSize: 14,
    color: TEAL_M, bold: true, charSpacing: 3, margin: 0
  });
  s.addText(title, {
    x: 1.1, y: 2.85, w: 9.6, h: 1.5, fontFace: SERIF, fontSize: 40,
    color: 'FFFFFF', bold: true, margin: 0, lineSpacing: 46
  });
  if (sub) {
    s.addText(sub, {
      x: 1.1, y: 4.5, w: 9.0, h: 0.8, fontFace: SANS, fontSize: 16,
      color: INDIGO_M, margin: 0, lineSpacing: 24
    });
  }
  N += 1;
  return s;
}

function slide(title, kicker) {
  const s = base();
  if (kicker) {
    s.addText(kicker, {
      x: 0.62, y: 0.42, w: 11, h: 0.3, fontFace: SANS, fontSize: 11.5,
      color: TEAL, bold: true, charSpacing: 1.4, margin: 0
    });
    s.addText(title, {
      x: 0.62, y: 0.76, w: 12.1, h: 0.62, fontFace: SERIF, fontSize: 27,
      color: INK, bold: true, margin: 0
    });
  } else {
    s.addText(title, {
      x: 0.62, y: 0.55, w: 12.1, h: 0.7, fontFace: SERIF, fontSize: 29,
      color: INK, bold: true, margin: 0
    });
  }
  return s;
}

// ---------- content helpers ----------

function body(s, text, o) {
  o = o || {};
  s.addText(text, {
    x: o.x || 0.62, y: o.y || 1.65, w: o.w || 11.6, h: o.h || 1.0,
    fontFace: SANS, fontSize: o.size || 17, color: o.color || INK,
    margin: 0, lineSpacing: o.ls || 27, align: o.align || 'left', bold: o.bold || false
  });
}

function bullets(s, items, o) {
  o = o || {};
  const arr = items.map((t, i) => ({
    text: t, options: { bullet: { code: '25CF' }, breakLine: i < items.length - 1 }
  }));
  s.addText(arr, {
    x: o.x || 0.85, y: o.y || 2.0, w: o.w || 11.3, h: o.h || 3.4,
    fontFace: SANS, fontSize: o.size || 16, color: o.color || INK,
    margin: 0, paraSpaceAfter: o.gap === undefined ? 11 : o.gap, lineSpacing: o.ls || 23
  });
}

function teachCards(s, cards, o) {
  o = o || {};
  const y = o.y || 2.1;
  const h = o.h || 2.5;
  const n = cards.length;
  const gap = 0.32;
  const total = o.w || 12.1;
  const cw = (total - gap * (n - 1)) / n;
  const tints = [TEAL_T, INDIGO_T, AMBER_T, PANEL];
  const accents = [TEAL, INDIGO, AMBER, MUTED];
  cards.forEach((c, i) => {
    const x = 0.62 + i * (cw + gap);
    s.addShape(pres.ShapeType.roundRect, {
      x, y, w: cw, h, fill: { color: c.tint || tints[i % 4] },
      line: { color: 'FFFFFF', width: 0 }, rectRadius: 0.09
    });
    if (c.tag) {
      s.addText(c.tag, {
        x: x + 0.26, y: y + 0.22, w: cw - 0.5, h: 0.28, fontFace: SANS,
        fontSize: 10.5, color: c.accent || accents[i % 4], bold: true,
        charSpacing: 1.2, margin: 0
      });
    }
    s.addText(c.h, {
      x: x + 0.26, y: y + (c.tag ? 0.56 : 0.28), w: cw - 0.5, h: 0.6,
      fontFace: SERIF, fontSize: o.hsize || 17, color: INK, bold: true,
      margin: 0, lineSpacing: 21
    });
    s.addText(c.b, {
      x: x + 0.26, y: y + (c.tag ? 1.18 : 0.92), w: cw - 0.5, h: h - (c.tag ? 1.4 : 1.15),
      fontFace: SANS, fontSize: o.bsize || 13.5, color: MUTED, margin: 0, lineSpacing: 19
    });
  });
}

// WHY: boxes used to take a hand guessed height, and long text silently spilled
// out of the bottom. These compute the height they actually need.
function textLines(text, w, pt, face) {
  const factor = face === SERIF ? 0.52 : 0.47;
  const cpl = Math.max(1, Math.floor((w * 72) / (pt * factor)));
  return text.split('\n').reduce((n, p) => n + Math.max(1, Math.ceil(p.length / cpl)), 0);
}

function needH(text, w, pt, chrome) {
  return chrome + textLines(text, w, pt, SANS) * (pt * 1.34) / 72;
}

function importantBox(s, label, text, o) {
  o = o || {};
  const w = o.w || 12.1;
  const size = o.size || 15;
  const y = o.y || 5.05;
  const h = Math.max(o.h || 0, needH(text, w - 0.6, size, 0.85));
  s.addShape(pres.ShapeType.roundRect, {
    x: 0.62, y, w, h, fill: { color: AMBER_T },
    line: { color: 'FFFFFF', width: 0 }, rectRadius: 0.09
  });
  s.addText(label, {
    x: 0.92, y: y + 0.2, w: 4.5, h: 0.28, fontFace: SANS, fontSize: 10.5,
    color: AMBER, bold: true, charSpacing: 1.3, margin: 0
  });
  s.addText(text, {
    x: 0.92, y: y + 0.52, w: w - 0.6, h: h - 0.68,
    fontFace: SANS, fontSize: size, color: INK, margin: 0, lineSpacing: Math.round(size * 1.4)
  });
  return y + h;
}

function recallBox(s, text, o) {
  o = o || {};
  const w = o.w || 12.1;
  const size = o.size || 14.5;
  const y = o.y || 5.4;
  const h = Math.max(o.h || 0, needH(text, w - 0.6, size, 0.78));
  s.addShape(pres.ShapeType.roundRect, {
    x: 0.62, y, w, h, fill: { color: PANEL },
    line: { color: LINE, width: 1 }, rectRadius: 0.09
  });
  s.addText('HOLD ON TO THIS', {
    x: 0.92, y: y + 0.16, w: 3, h: 0.26, fontFace: SANS, fontSize: 10.5,
    color: TEAL, bold: true, charSpacing: 1.3, margin: 0
  });
  s.addText(text, {
    x: 0.92, y: y + 0.44, w: w - 0.6, h: h - 0.58,
    fontFace: SANS, fontSize: size, color: INK, margin: 0, lineSpacing: Math.round(size * 1.4)
  });
  return y + h;
}

function activityBox(s, label, text, o) {
  o = o || {};
  const size = o.size || 15;
  const y = o.y || 5.05;
  const h = Math.max(o.h || 0, needH(text, 11.5, size, 0.85));
  s.addShape(pres.ShapeType.roundRect, {
    x: 0.62, y, w: 12.1, h, fill: { color: TEAL_T },
    line: { color: 'FFFFFF', width: 0 }, rectRadius: 0.09
  });
  s.addText(label, {
    x: 0.92, y: y + 0.2, w: 5, h: 0.28, fontFace: SANS, fontSize: 10.5,
    color: TEAL, bold: true, charSpacing: 1.3, margin: 0
  });
  s.addText(text, {
    x: 0.92, y: y + 0.52, w: 11.5, h: h - 0.68, fontFace: SANS,
    fontSize: size, color: INK, margin: 0, lineSpacing: Math.round(size * 1.4)
  });
  return y + h;
}

function chip(s, text, x, y, o) {
  o = o || {};
  const w = o.w || (0.16 * text.length + 0.5);
  s.addShape(pres.ShapeType.roundRect, {
    x, y, w, h: o.h || 0.42, fill: { color: o.fill || INDIGO_T },
    line: { color: 'FFFFFF', width: 0 }, rectRadius: 0.2
  });
  s.addText(text, {
    x, y, w, h: o.h || 0.42, fontFace: SANS, fontSize: o.size || 12.5,
    color: o.color || INDIGO, bold: true, align: 'center', valign: 'middle', margin: 0
  });
  return w;
}

function arrow(s, x, y, w) {
  s.addShape(pres.ShapeType.line, {
    x, y, w, h: 0,
    line: { color: FAINT, width: 1.5, endArrowType: 'triangle' }
  });
}

// red box: pointer only. never decoration.
function redBox(s, x, y, w, h, label, labelSide) {
  s.addShape(pres.ShapeType.rect, {
    x, y, w, h, fill: { type: 'none' },
    line: { color: RED, width: 2.5 }
  });
  if (label) {
    const lx = labelSide === 'left' ? x - 3.2 : x + w + 0.18;
    s.addText(label, {
      x: lx, y: y + h / 2 - 0.22, w: 3.0, h: 0.45, fontFace: SANS, fontSize: 12.5,
      color: RED, bold: true, margin: 0,
      align: labelSide === 'left' ? 'right' : 'left', valign: 'middle'
    });
  }
}

function codeBox(s, lines, o) {
  o = o || {};
  const x = o.x || 0.62, y = o.y || 2.0, w = o.w || 7.4;
  const lh = o.lh || 0.315;
  const h = lines.length * lh + 0.5;
  s.addShape(pres.ShapeType.roundRect, {
    x, y, w, h, fill: { color: '1E2A38' },
    line: { color: 'FFFFFF', width: 0 }, rectRadius: 0.07
  });
  lines.forEach((ln, i) => {
    s.addText(ln.t, {
      x: x + 0.3, y: y + 0.25 + i * lh, w: w - 0.55, h: lh,
      fontFace: 'Consolas', fontSize: o.size || 13,
      color: ln.c || 'D6E2EE', margin: 0, valign: 'middle'
    });
  });
  return { x, y, w, h, lh };
}

function bigNum(s, num, cap, x, y, o) {
  o = o || {};
  s.addText(num, {
    x, y, w: o.w || 2.6, h: 0.9, fontFace: SERIF, fontSize: o.size || 46,
    color: o.color || TEAL, bold: true, margin: 0
  });
  s.addText(cap, {
    x, y: y + 0.85, w: o.w || 2.6, h: 0.8, fontFace: SANS, fontSize: 13.5,
    color: MUTED, margin: 0, lineSpacing: 19
  });
}

function rowItem(s, y, tag, head, text, accent, tint) {
  s.addShape(pres.ShapeType.roundRect, {
    x: 0.62, y, w: 12.1, h: 0.85, fill: { color: tint },
    line: { color: 'FFFFFF', width: 0 }, rectRadius: 0.08
  });
  s.addText(tag, {
    x: 0.88, y, w: 1.35, h: 0.85, fontFace: SANS, fontSize: 13,
    color: accent, bold: true, margin: 0, valign: 'middle'
  });
  s.addText(head, {
    x: 2.25, y, w: 3.5, h: 0.85, fontFace: SERIF, fontSize: 15.5,
    color: INK, bold: true, margin: 0, valign: 'middle'
  });
  s.addText(text, {
    x: 5.85, y, w: 6.6, h: 0.85, fontFace: SANS, fontSize: 13.5,
    color: MUTED, margin: 0, valign: 'middle', lineSpacing: 18
  });
}

/* ============================================================
   UNIT 1 LECTURE 1: What an Agent Actually Is
   ============================================================ */

let s;

// ---- 1 ----
s = titleSlide({
  kicker: 'UNIT 1, FOUNDATIONS OF AI AGENTS AND MICROSOFT FOUNDRY',
  code: 'LECTURE 1',
  title: 'What an Agent\nActually Is',
  sub: 'Where the boundary sits, why it is blurrier than\nanyone admits, and the four things a system needs\nbefore the word is honest.',
  foot: 'CSE476  |  Rohit Bharti'
});
s.addNotes('TEACHING NOTE (do not say): open the repo and the notebook before this slide goes up. The live build starts about halfway through and you do not want to be installing anything then.');

// ---- 2 ----
s = divider('SECTION 00', 'Where we left off', 'Three words, and one question they leave open.');
s.addNotes('');

// ---- 3 ----
s = slide('Last time, in one picture', 'RECALL');
const rc = [
  { t: 'THINK', sub: 'what should I do now', x: 0.9, fill: INDIGO_T, col: INDIGO },
  { t: 'ACT', sub: 'call a tool', x: 4.95, fill: TEAL_T, col: TEAL },
  { t: 'OBSERVE', sub: 'read what came back', x: 9.0, fill: AMBER_T, col: AMBER }
];
rc.forEach(nd => {
  s.addShape(pres.ShapeType.roundRect, {
    x: nd.x, y: 1.95, w: 3.4, h: 1.15, fill: { color: nd.fill },
    line: { color: 'FFFFFF', width: 0 }, rectRadius: 0.1
  });
  s.addText(nd.t, {
    x: nd.x, y: 2.1, w: 3.4, h: 0.45, fontFace: SERIF, fontSize: 20,
    color: nd.col, bold: true, align: 'center', margin: 0
  });
  s.addText(nd.sub, {
    x: nd.x, y: 2.57, w: 3.4, h: 0.35, fontFace: SANS, fontSize: 12.5,
    color: MUTED, align: 'center', margin: 0
  });
});
arrow(s, 4.42, 2.52, 0.45);
arrow(s, 8.47, 2.52, 0.45);
s.addShape(pres.ShapeType.line, { x: 10.7, y: 3.1, w: 0, h: 0.6, line: { color: FAINT, width: 1.5 } });
s.addShape(pres.ShapeType.line, { x: 2.6, y: 3.7, w: 8.1, h: 0, line: { color: FAINT, width: 1.5 } });
s.addShape(pres.ShapeType.line, {
  x: 2.6, y: 3.1, w: 0, h: 0.6,
  line: { color: FAINT, width: 1.5, beginArrowType: 'triangle' }
});
body(s, 'You saw this work. A goal went in, tools got used, and something finished. Nobody typed the intermediate steps.', { y: 4.35, h: 0.6, size: 17 });
importantBox(s, 'THE QUESTION IT LEAVES OPEN', 'That was a demo, and demos are chosen to work. Today we ask the harder question. When somebody hands you a product and calls it an agent, how do you check whether that word is honest?', { y: 5.15, h: 1.35 });
s.addNotes('Rebuild the loop verbally with them before the slide finishes. Ask for the three words. If the room cannot produce them, spend two extra minutes here rather than moving on.');

// ---- 4 ----
s = slide('What you will be able to do by the end of today');
bullets(s, [
  'State the four things a system must have before the word agent is honest, and apply them to any product you are shown.',
  'Explain exactly what happens when a model uses a tool, including the part almost everybody gets wrong.',
  'Write a working agent from scratch, in about forty lines, with no framework at all.',
  'Break it on purpose, in two different ways, and fix both.',
  'Say confidently when an agent is the wrong choice, which is more often than the internet suggests.'
], { y: 1.85, h: 3.2, size: 16 });
recallBox(s, 'The framework comes in Unit 3. Today you build it by hand, because a framework you cannot read underneath is a framework you cannot debug.', { y: 5.4, h: 1.0 });
s.addNotes('');

// ---- 5 ----
s = divider('SECTION 01', 'The word is broken', 'Before we define it, we need to admit it currently means nothing.');
s.addNotes('');

// ---- 6 ----
s = slide('Three products. All three are marketed as agents.');
teachCards(s, [
  { tag: 'PRODUCT A', h: 'A support chat window', b: 'Answers from a help centre. Cannot look at your order. Cannot change anything. Escalates to a human when stuck.', tint: PANEL, accent: MUTED },
  { tag: 'PRODUCT B', h: 'An email sorter', b: 'Reads incoming mail, applies one of five labels, files it. Same five labels every time, in the same order.', tint: PANEL, accent: MUTED },
  { tag: 'PRODUCT C', h: 'A coding assistant', b: 'Given a bug report, reads the repo, edits files, runs tests, reads failures, edits again, opens a pull request.', tint: PANEL, accent: MUTED }
], { y: 2.0, h: 2.6, bsize: 13 });
body(s, 'Every vendor here uses the same word. Only one of these three is doing what we described last session.', { y: 4.85, h: 0.6, size: 17 });
activityBox(s, 'THIRTY SECONDS, TALK TO THE PERSON NEXT TO YOU', 'Which one, and what exactly is your test for deciding? Do not say "it is smarter". Name the specific capability.', { y: 5.55, h: 1.05, size: 14.5 });
s.addNotes('Let them argue. Most rooms say C immediately and cannot articulate why. Push on the why. Someone will eventually say "it decides what to do next", which is exactly where you want them.');

// ---- 7 ----
s = slide('The layman version', 'HIRING SOMEBODY FOR YOUR SHOP');
const auto = [
  ['LEVEL 0', 'The intern who asks', 'Comes to you before every single action. "Should I call the supplier now?" You are still doing the deciding.', MUTED, PANEL],
  ['LEVEL 1', 'The intern with a checklist', 'You wrote the steps. They follow them exactly, every time, in order. Reliable and completely inflexible.', TEAL, TEAL_T],
  ['LEVEL 2', 'The employee with a goal', 'You said "sort out the Rao Logistics problem". They decide what to do first, second, third. They come back when it is done.', INDIGO, INDIGO_T]
];
auto.forEach((r, i) => rowItem(s, 1.95 + i * 1.12, r[0], r[1], r[2], r[3], r[4]));
importantBox(s, 'THE AXIS THAT MATTERS', 'Notice what is changing down that list. Not intelligence. Not knowledge. What changes is who decides the next step. That single question is the whole definition.', { y: 5.5, h: 1.25 });
s.addNotes('TEACHING NOTE (do not say): this analogy carries the entire lecture. Get it landed properly. Ask the room which level describes a for loop, which describes a support ticket queue.');

// ---- 8 ----
s = slide('Now the technical version');
body(s, 'Same three levels, in the language you will meet in documentation and job descriptions.', { y: 1.62, h: 0.45, size: 16.5, color: MUTED });
const tech = [
  ['LEVEL 0', 'Human in the loop', 'The system proposes, a person approves every action. Common in anything with legal or financial consequence.', MUTED, PANEL],
  ['LEVEL 1', 'Workflow', 'The sequence of steps is fixed by you, in code, at design time. The model fills in content but never chooses the path.', TEAL, TEAL_T],
  ['LEVEL 2', 'Agentic', 'The sequence of steps is decided by the model at run time, based on what it observes. You wrote the tools, not the order.', INDIGO, INDIGO_T]
];
tech.forEach((r, i) => rowItem(s, 2.25 + i * 1.12, r[0], r[1], r[2], r[3], r[4]));
recallBox(s, 'Level 1 versus Level 2 is a decision about who owns the control flow. In a workflow, you own it. In an agent, the model owns it and you own the boundaries.', { y: 5.6 });
s.addNotes('');

// ---- 9 ----
s = slide('The misconception to kill right now');
teachCards(s, [
  { tag: 'WHAT PEOPLE SAY', h: 'Chatbot or agent, pick one', b: 'As if there were a line, and a product sits cleanly on one side of it. Useful for marketing. Useless for engineering.', tint: RED_T, accent: RED },
  { tag: 'WHAT IS TRUE', h: 'Agency is a dial, not a switch', b: 'Real systems sit somewhere along the range, and the same product often sits at different points for different tasks.', tint: TEAL_T, accent: TEAL }
], { y: 2.0, h: 2.5 });
body(s, 'Product A from two slides ago escalates to a human. That is a decision. A small one, from a menu of two, but a decision. It is not at zero.', { y: 4.75, h: 0.85, size: 16 });
importantBox(s, 'SO THE USEFUL QUESTION IS NOT "IS IT AN AGENT"', 'The useful question is: how much of the control flow has been handed to the model, and what happens when it chooses badly? That is a question you can actually answer about a real system.', { y: 5.7, h: 1.15 });
s.addNotes('Students want a clean binary because it is easier to revise. Resist it. The dial framing is what makes Unit 2 (workflow versus agency) make sense later.');

// ---- 10 ----
s = divider('SECTION 02', 'The four requirements', 'Before the word is honest, all four have to be there.');
s.addNotes('');

// ---- 11 ----
s = slide('Four things. Miss any one and it is something else.');
const four = [
  ['01', 'A goal', 'Not a question. An outcome, with the steps left unspecified.', TEAL, TEAL_T],
  ['02', 'Tools', 'A way to affect or observe the world beyond its own text.', INDIGO, INDIGO_T],
  ['03', 'A loop with state', 'It runs more than once, and each run knows what the last one found.', AMBER, AMBER_T],
  ['04', 'A way to stop', 'A defined condition for being finished, and a budget for failing to be.', RED, RED_T]
];
four.forEach((r, i) => rowItem(s, 1.9 + i * 1.02, r[0], r[1], r[2], r[3], r[4]));
recallBox(s, 'Three of these are obvious once stated. The fourth is the one nobody builds first, and it is the one that costs money.', { y: 6.0, h: 0.85 });
s.addNotes('Write the four on the board and leave them there for the rest of the lecture. You will point back at them repeatedly, including during the live build.');

// ================= REQUIREMENT 1 =================
// ---- 12 ----
s = slide('Requirement 1, a goal, not a question', 'ONE OF FOUR');
s.addShape(pres.ShapeType.roundRect, {
  x: 0.62, y: 1.85, w: 5.85, h: 1.55, fill: { color: PANEL },
  line: { color: LINE, width: 1 }, rectRadius: 0.1
});
s.addText('A QUESTION', {
  x: 0.92, y: 2.05, w: 5.2, h: 0.3, fontFace: SANS, fontSize: 10.5, color: MUTED, bold: true, charSpacing: 1.3, margin: 0
});
s.addText('"What is our worst supplier?"', {
  x: 0.92, y: 2.4, w: 5.25, h: 0.85, fontFace: SERIF, fontSize: 17, color: INK, italic: true, margin: 0, valign: 'middle'
});
s.addShape(pres.ShapeType.roundRect, {
  x: 6.87, y: 1.85, w: 5.85, h: 1.55, fill: { color: TEAL_T },
  line: { color: 'FFFFFF', width: 0 }, rectRadius: 0.1
});
s.addText('A GOAL', {
  x: 7.17, y: 2.05, w: 5.2, h: 0.3, fontFace: SANS, fontSize: 10.5, color: TEAL, bold: true, charSpacing: 1.3, margin: 0
});
s.addText('"Find our worst supplier and draft the escalation email."', {
  x: 7.17, y: 2.4, w: 5.25, h: 0.85, fontFace: SERIF, fontSize: 17, color: INK, italic: true, margin: 0, valign: 'middle', lineSpacing: 22
});
body(s, 'A question has one answer and one step. A goal has an outcome, and how many steps it takes is not your problem. That second part is the whole point. You are declining to specify the path.', { y: 3.7, h: 1.0, size: 16.5 });
importantBox(s, 'THE MISCONCEPTION', 'A long, detailed question is still a question. "Open the supplier table, sort by delivery rate, take the lowest, then write an email" is not a goal. That is you doing the deciding and dictating it in English. If you already know the steps, write the steps in code. It will be cheaper, faster and more reliable.', { y: 4.95, h: 1.65 });
s.addNotes('This misconception is extremely common and shows up in student practicals all semester. Someone will submit a "goal" that is a numbered list of instructions. Point back at this slide.');

// ================= REQUIREMENT 2 =================
// ---- 13 ----
s = slide('Requirement 2, tools', 'TWO OF FOUR');
body(s, 'A model without tools is a very well read person locked in a room with no phone.', { y: 1.65, h: 0.45, size: 18, bold: true });
teachCards(s, [
  { tag: 'WITHOUT TOOLS', h: 'It can only produce text', b: 'It knows a great deal, up to a date. It cannot see your database, cannot check today\'s price, cannot send anything, cannot verify a single claim it makes.', tint: PANEL, accent: MUTED },
  { tag: 'WITH TOOLS', h: 'It can reach the world', b: 'Query a table. Call an API. Read a file. Run a search. Every one of those is an ordinary function you wrote, that you decided to expose.', tint: TEAL_T, accent: TEAL }
], { y: 2.3, h: 2.4 });
recallBox(s, 'Tools are the difference between a system that describes work and a system that does it. In Unit 6 you will learn that they are also the entire attack surface.', { y: 5.0, h: 1.0 });
s.addNotes('');

// ---- 14 ----
s = slide('A tool is just a function. Nothing special happens to it.');
codeBox(s, [
  { t: 'def get_room_availability(hotel: str, date: str) -> str:', c: 'A5D6FF' },
  { t: '    """How many rooms are free at a hotel on a date."""', c: '7E93A8' },
  { t: '    n = ROOMS.get((hotel, date))', c: 'D6E2EE' },
  { t: '    if n is None:', c: 'D6E2EE' },
  { t: '        return f"No record for {hotel} on {date}."', c: 'D6E2EE' },
  { t: '    return f"{hotel} on {date}: {n} rooms available."', c: 'D6E2EE' }
], { x: 0.62, y: 1.95, w: 12.1, size: 14 });
body(s, 'That is a tool. There is no decorator, no registration with a vendor, no special base class. It is the function you would have written anyway.', { y: 4.35, h: 0.85, size: 16.5 });
importantBox(s, 'ONE DESIGN RULE, STARTING NOW', 'One tool does one job. A tool called handle_booking that checks availability and computes price and sends confirmation will be called at the wrong moment and will fail in a way you cannot debug. We will watch that happen in Unit 2.', { y: 5.3, h: 1.4 });
s.addNotes('');

// ---- 15 ----
s = slide('The part almost everybody gets wrong');
s.addShape(pres.ShapeType.roundRect, {
  x: 0.62, y: 1.8, w: 12.1, h: 1.35, fill: { color: RED_T },
  line: { color: 'FFFFFF', width: 0 }, rectRadius: 0.12
});
s.addText('The model never calls your function. It cannot. It has no ability to execute anything at all.', {
  x: 1.05, y: 1.8, w: 11.25, h: 1.35, fontFace: SERIF, fontSize: 22,
  color: INK, bold: true, margin: 0, valign: 'middle', lineSpacing: 30
});
body(s, 'A language model produces text. That is the only thing it does, and giving it tools does not change that. What actually happens is a request and a reply, and your code sits in the middle of it.', { y: 3.4, h: 1.0, size: 17 });
importantBox(s, 'WHY THIS MATTERS MORE THAN IT SOUNDS', 'If you believe the model executes things, then security, error handling and cost control all look like the vendor\'s problem. Once you understand that your loop is the thing doing the executing, you realise every one of those is yours.', { y: 4.6, h: 1.5 });
s.addNotes('Pause here. This single misunderstanding is behind a large share of confused questions later in the semester, and behind most bad assumptions about agent security in Unit 6.');

// ---- 16 ----
s = slide('What actually happens, in three moves');
const hs = [
  ['1', 'You ask', 'You send the conversation plus a list of tool descriptions. Plain text and JSON. Nothing executable.', TEAL, TEAL_T],
  ['2', 'It requests', 'The model replies with a message that says: I would like get_room_availability with these arguments. That is text. Nothing has run.', INDIGO, INDIGO_T],
  ['3', 'You execute', 'Your code looks up that name, checks it is allowed, calls the real function, and sends the result back as a new message.', AMBER, AMBER_T]
];
hs.forEach((r, i) => {
  const y = 2.0 + i * 1.25;
  s.addShape(pres.ShapeType.roundRect, {
    x: 0.62, y, w: 12.1, h: 1.05, fill: { color: r[4] },
    line: { color: 'FFFFFF', width: 0 }, rectRadius: 0.09
  });
  s.addText(r[0], {
    x: 0.95, y, w: 0.6, h: 1.05, fontFace: SERIF, fontSize: 26, color: r[3], bold: true, margin: 0, valign: 'middle'
  });
  s.addText(r[1], {
    x: 1.7, y, w: 2.6, h: 1.05, fontFace: SERIF, fontSize: 17, color: INK, bold: true, margin: 0, valign: 'middle'
  });
  s.addText(r[2], {
    x: 4.4, y, w: 8.05, h: 1.05, fontFace: SANS, fontSize: 14, color: MUTED, margin: 0, valign: 'middle', lineSpacing: 19
  });
});
redBox(s, 0.62, 4.5, 12.1, 1.05);
s.addText('the red box is the only step where anything actually runs, and it is your code', {
  x: 0.62, y: 5.72, w: 12.1, h: 0.4, fontFace: SANS, fontSize: 13.5,
  color: RED, bold: true, align: 'center', margin: 0
});
body(s, 'Step 3 is where security lives, where errors happen, and where your bill is generated.', { y: 6.2, h: 0.45, size: 15, color: MUTED, align: 'center' });
s.addNotes('Make them say step 2 back to you: the model requests, it does not call. That phrasing matters and it will come back in the viva.');

// ---- 17 ----
s = slide('The schema is the only thing the model ever sees');
codeBox(s, [
  { t: '{', c: 'D6E2EE' },
  { t: '  "type": "function",', c: 'D6E2EE' },
  { t: '  "function": {', c: 'D6E2EE' },
  { t: '    "name": "get_room_availability",', c: 'A5D6FF' },
  { t: '    "description": "Get the number of rooms available at a', c: 'FFD479' },
  { t: '                    specific hotel on a specific date.",', c: 'FFD479' },
  { t: '    "parameters": {', c: 'D6E2EE' },
  { t: '      "type": "object",', c: 'D6E2EE' },
  { t: '      "properties": {', c: 'D6E2EE' },
  { t: '        "hotel": {"type": "string", "description": "..."},', c: 'D6E2EE' },
  { t: '        "date":  {"type": "string", "description": "YYYY-MM-DD"}', c: 'D6E2EE' },
  { t: '      },', c: 'D6E2EE' },
  { t: '      "required": ["hotel", "date"]', c: 'D6E2EE' },
  { t: '    }', c: 'D6E2EE' },
  { t: '  }', c: 'D6E2EE' },
  { t: '}', c: 'D6E2EE' }
], { x: 0.62, y: 1.75, w: 7.7, size: 12, lh: 0.27 });
s.addShape(pres.ShapeType.roundRect, {
  x: 8.65, y: 1.75, w: 4.07, h: 2.35, fill: { color: AMBER_T },
  line: { color: 'FFFFFF', width: 0 }, rectRadius: 0.09
});
s.addText('The description is not documentation', {
  x: 8.95, y: 1.95, w: 3.5, h: 0.75, fontFace: SERIF, fontSize: 16, color: INK, bold: true, margin: 0, lineSpacing: 21
});
s.addText('It is the instruction the model uses to decide whether to pick this tool over another one. Vague description, wrong tool chosen, and the bug is in your English, not your Python.', {
  x: 8.95, y: 2.75, w: 3.5, h: 1.25, fontFace: SANS, fontSize: 13, color: MUTED, margin: 0, lineSpacing: 18
});
s.addShape(pres.ShapeType.roundRect, {
  x: 8.65, y: 4.3, w: 4.07, h: 2.15, fill: { color: PANEL },
  line: { color: LINE, width: 1 }, rectRadius: 0.09
});
s.addText('The model cannot see', {
  x: 8.95, y: 4.5, w: 3.5, h: 0.4, fontFace: SERIF, fontSize: 16, color: INK, bold: true, margin: 0
});
s.addText('your function body, your variable names, your database, or what the function returns until after it has run.', {
  x: 8.95, y: 4.95, w: 3.5, h: 1.3, fontFace: SANS, fontSize: 13, color: MUTED, margin: 0, lineSpacing: 18
});
s.addNotes('Ask: if the model cannot see the function body, what happens when the description and the body disagree? Answer: the model behaves according to the description, and you get a bug that no amount of reading the Python will explain.');

// ================= REQUIREMENT 3 =================
// ---- 18 ----
s = slide('Requirement 3, a loop that carries state', 'THREE OF FOUR');
body(s, 'Running once is a function call. Running again, knowing what the first run found, is an agent.', { y: 1.62, h: 0.5, size: 18, bold: true });
teachCards(s, [
  { tag: 'THE LAYMAN VERSION', h: 'The notepad', b: 'Send someone to the godown three times. If they carry no notepad, the third trip starts exactly like the first. They will recount the same shelf and never finish.', tint: PANEL, accent: MUTED },
  { tag: 'THE TECHNICAL VERSION', h: 'The messages list', b: 'The notepad is a Python list. Every request, every tool result, every reply gets appended. You resend the whole list on every turn.', tint: TEAL_T, accent: TEAL }
], { y: 2.3, h: 2.4 });
importantBox(s, 'THE MISCONCEPTION', 'The model does not remember anything between calls. Not one word. Every call is the first call as far as it is concerned. The illusion of memory is entirely produced by you resending the transcript each time, and that is why long conversations cost more.', { y: 5.0, h: 1.55 });
s.addNotes('This explains token cost, context limits, and why memory is a whole session in Unit 3. Get it in early.');

// ---- 19 ----
s = slide('What the notepad looks like at step three');
const conv = [
  ['system', 'You are a hotel booking assistant. You have tools for...', MUTED, PANEL],
  ['user', 'Rooms and price at Taj Palace on 14 August?', INDIGO, INDIGO_T],
  ['assistant', 'tool_calls: get_room_availability(Taj Palace, 2026-08-14)', TEAL, TEAL_T],
  ['tool', 'Taj Palace on 2026-08-14: 3 rooms available.', AMBER, AMBER_T],
  ['assistant', 'tool_calls: get_nightly_rate(Taj Palace)', TEAL, TEAL_T],
  ['tool', 'Taj Palace: Rs 14500 per night.', AMBER, AMBER_T]
];
conv.forEach((r, i) => {
  const y = 1.85 + i * 0.72;
  s.addShape(pres.ShapeType.roundRect, {
    x: 0.62, y, w: 12.1, h: 0.6, fill: { color: r[3] },
    line: { color: 'FFFFFF', width: 0 }, rectRadius: 0.07
  });
  s.addText(r[0], {
    x: 0.9, y, w: 1.5, h: 0.6, fontFace: SANS, fontSize: 12, color: r[2], bold: true, margin: 0, valign: 'middle'
  });
  s.addText(r[1], {
    x: 2.5, y, w: 9.9, h: 0.6, fontFace: 'Consolas', fontSize: 12.5, color: INK, margin: 0, valign: 'middle'
  });
});
body(s, 'All six of those go up on every single request. The model reads the whole thing again each time and decides what happens next from scratch.', { y: 6.25, h: 0.55, size: 15.5, color: MUTED });
s.addNotes('Point at the two tool rows. Ask what happens if you forget to append them. Answer: the model asks for the same tool again, forever, because from its point of view it never got an answer.');

// ================= REQUIREMENT 4 =================
// ---- 20 ----
s = slide('Requirement 4, a way to stop', 'FOUR OF FOUR, AND THE ONE NOBODY BUILDS FIRST');
body(s, 'A shop with no closing time is not dedicated. It is broken.', { y: 1.62, h: 0.45, size: 18, bold: true });
const exits = [
  ['EXIT 1', 'The goal is met', 'The model stops asking for tools and produces a final answer. This is the happy path and the only one most tutorials handle.', TEAL, TEAL_T],
  ['EXIT 2', 'The budget ran out', 'You capped the number of steps or the spend. It stops and says so honestly, rather than pretending it succeeded.', AMBER, AMBER_T],
  ['EXIT 3', 'No progress is being made', 'It has called the same tool with the same arguments three times. Something is wrong. Stop and escalate rather than continue.', RED, RED_T]
];
exits.forEach((r, i) => rowItem(s, 2.05 + i * 1.12, r[0], r[1], r[2], r[3], r[4]));
importantBox(s, 'THE MISCONCEPTION, AND IT IS AN EXPENSIVE ONE', 'People assume the model knows when it is finished. Sometimes it does. When it does not, it will keep requesting tools until something external stops it, and every one of those requests is billed. You will watch this happen live in about twenty minutes.', { y: 5.3, size: 14 });
s.addNotes('Exit 3 is the one nobody writes and it catches the most realistic failure, which is a tool returning something the model cannot use. Flag that you will come back to it in Unit 2.');

// ---- 21 ----
s = slide('The four, one more time');
four.forEach((r, i) => rowItem(s, 1.8 + i * 0.95, r[0], r[1], r[2], r[3], r[4]));
importantBox(s, 'THE TEST YOU CAN NOW APPLY TO ANY PRODUCT', 'Go back to the three products from earlier. Product A has no tools and no loop. Product B has tools but the path is fixed by its author, so no real loop. Product C has all four. Only C earns the word.', { y: 5.6, size: 13.5 });
s.addNotes('Return to the three products explicitly. This is the payoff for the exercise at the start of the lecture and it is what makes the four requirements feel earned rather than asserted.');

// ================= ANATOMY =================
// ---- 22 ----
s = divider('SECTION 03', 'The anatomy', 'Six parts, and the syllabus words for each of them.');
s.addNotes('');

// ---- 23 ----
s = slide('Six components, and you build every one this semester');
const comps = [
  ['MODEL', 'The reasoning', 'Decides what happens next. Unit 1.', TEAL_T, TEAL],
  ['INSTRUCTIONS', 'The job description', 'Role, constraints, tone, what not to do. Unit 1.', TEAL_T, TEAL],
  ['TOOLS', 'The hands', 'Functions it may request. Units 2 and 3.', INDIGO_T, INDIGO],
  ['MEMORY', 'The notepad', 'What has happened so far. Unit 3.', INDIGO_T, INDIGO],
  ['LOOP', 'The engine', 'Runs the cycle, executes, feeds back. Unit 2.', AMBER_T, AMBER],
  ['GUARDRAILS', 'The boundaries', 'Budget, whitelist, filters, permissions. Units 5 and 6.', RED_T, RED]
];
comps.forEach((c, i) => {
  const col = i % 3, row = Math.floor(i / 3);
  const x = 0.62 + col * 4.15;
  const y = 1.95 + row * 2.15;
  s.addShape(pres.ShapeType.roundRect, {
    x, y, w: 3.8, h: 1.85, fill: { color: c[3] },
    line: { color: 'FFFFFF', width: 0 }, rectRadius: 0.1
  });
  s.addText(c[0], {
    x: x + 0.25, y: y + 0.2, w: 3.3, h: 0.3, fontFace: SANS, fontSize: 11, color: c[4], bold: true, charSpacing: 1.3, margin: 0
  });
  s.addText(c[1], {
    x: x + 0.25, y: y + 0.52, w: 3.3, h: 0.45, fontFace: SERIF, fontSize: 17, color: INK, bold: true, margin: 0
  });
  s.addText(c[2], {
    x: x + 0.25, y: y + 1.0, w: 3.3, h: 0.7, fontFace: SANS, fontSize: 13, color: MUTED, margin: 0, lineSpacing: 18
  });
});
body(s, 'Today you build four of the six by hand. Memory and guardrails get one line each and a promise that we will do them properly later.', { y: 6.3, h: 0.5, size: 15, color: MUTED });
s.addNotes('');

// ---- 24 ----
s = slide('The syllabus words for the same thing', 'PERCEPTION AND ACTION MODELS');
body(s, 'Your syllabus uses classical AI vocabulary. Here is the translation, so the exam paper and the code agree with each other.', { y: 1.62, h: 0.6, size: 16 });
const trans = [
  ['PERCEPTION', 'How the agent takes in the world', 'For us: the tool results coming back, plus whatever is in the conversation. That is the entire sensory apparatus.', TEAL, TEAL_T],
  ['ACTION', 'How the agent changes the world', 'For us: the tool calls your loop executes. Reading a database is an action too, not just writing to one.', INDIGO, INDIGO_T],
  ['ENVIRONMENT', 'Whatever the agent can sense or affect', 'For us: your database, your APIs, your file system. The environment is exactly as large as the tools you exposed, and no larger.', AMBER, AMBER_T]
];
trans.forEach((r, i) => rowItem(s, 2.4 + i * 1.15, r[0], r[1], r[2], r[3], r[4]));
recallBox(s, 'The last one is a security statement disguised as a definition. The agent reaches exactly as far as the tool list, and no further. Remember that in Unit 6.', { y: 5.62 });
s.addNotes('The classical vocabulary is worth taking seriously rather than dismissing, because the exam uses it and because it makes the security framing in Unit 6 land properly.');

// ================= LIVE BUILD =================
// ---- 25 ----
s = divider('SECTION 04', 'Live build', 'Laptops open. Forty lines, no framework, and we break it twice.');
s.addNotes('Stop presenting. Switch to the editor. Everything from here is typed live, and the slides are only there for people who fall behind.');

// ---- 26 ----
s = slide('What we are building');
body(s, 'A hotel assistant that can answer a question needing two different lookups, without you telling it which order to do them in.', { y: 1.65, h: 0.8, size: 17 });
s.addShape(pres.ShapeType.roundRect, {
  x: 0.62, y: 2.6, w: 12.1, h: 1.0, fill: { color: INDIGO_T },
  line: { color: 'FFFFFF', width: 0 }, rectRadius: 0.1
});
s.addText('"Can I get a room at Taj Palace on 14 August, and what would it cost?"', {
  x: 1.05, y: 2.6, w: 11.25, h: 1.0, fontFace: SERIF, fontSize: 19,
  color: INK, italic: true, margin: 0, valign: 'middle'
});
body(s, 'Two tools exist: one for availability, one for rates. Nowhere in our code will we say "check availability first". The model works that out, and we will watch it do so.', { y: 3.85, h: 0.85, size: 16 });
activityBox(s, 'OPEN THIS NOW', 'notebooks/u1/l1_first_agent.ipynb  in the course repository. Run the first cell. If it prints your lane, you are set. If it does not, put your hand up now rather than in ten minutes.', { y: 4.95, h: 1.25 });
s.addNotes('Give the room ninety seconds to get the notebook open and the first cell run. Do not start typing until most laptops show a lane line.');

// ---- 27 ----
s = slide('Step 1, the tools. Ordinary functions.');
codeBox(s, [
  { t: 'ROOMS = {("Taj Palace", "2026-08-14"): 3,', c: 'D6E2EE' },
  { t: '         ("Radisson Blu", "2026-08-14"): 11}', c: 'D6E2EE' },
  { t: 'RATES = {"Taj Palace": 14500, "Radisson Blu": 6200}', c: 'D6E2EE' },
  { t: '', c: 'D6E2EE' },
  { t: 'def get_room_availability(hotel: str, date: str) -> str:', c: 'A5D6FF' },
  { t: '    n = ROOMS.get((hotel, date))', c: 'D6E2EE' },
  { t: '    if n is None:', c: 'D6E2EE' },
  { t: '        return f"No record for {hotel} on {date}."', c: 'D6E2EE' },
  { t: '    return f"{hotel} on {date}: {n} rooms available."', c: 'D6E2EE' }
], { x: 0.62, y: 1.85, w: 12.1, size: 13.5 });
importantBox(s, 'NOTICE', 'Both tools return a string, not a dict. The result goes back to the model as text anyway, so returning something readable saves a serialisation step and makes your traces far easier to read at 2am.', { y: 5.4, size: 14.5 });
s.addNotes('');

// ---- 28 ----
s = slide('Step 2, the whitelist and the schema');
codeBox(s, [
  { t: 'REGISTRY = {', c: 'D6E2EE' },
  { t: '    "get_room_availability": get_room_availability,', c: 'D6E2EE' },
  { t: '    "get_nightly_rate": get_nightly_rate,', c: 'D6E2EE' },
  { t: '}', c: 'D6E2EE' }
], { x: 0.62, y: 1.9, w: 12.1, size: 14 });
body(s, 'The registry is not a convenience. It is the whitelist. If a name is not a key in this dict, it does not run, no matter what the model asks for. We will test that claim in ten minutes by making the model ask for something that does not exist.', { y: 3.85, h: 1.15, size: 16.5 });
importantBox(s, 'THE SCHEMA GOES NEXT TO IT', 'TOOL_SCHEMA is the JSON description from earlier, one entry per function. Two lists that must stay in step: one your code uses, one the model reads. Unit 3 shows you how frameworks generate both from one source.', { y: 5.15 });
s.addNotes('Type the registry live. Ask the room what happens if a function is in the schema but not the registry, and vice versa. Both are real bugs they will hit.');

// ---- 29 ----
s = slide('Step 3, the loop. This is the whole thing.');
const lb = codeBox(s, [
  { t: 'messages = [{"role": "system", "content": SYSTEM},', c: 'D6E2EE' },
  { t: '            {"role": "user",   "content": goal}]', c: 'D6E2EE' },
  { t: '', c: 'D6E2EE' },
  { t: 'for step in range(1, max_steps + 1):', c: 'FFD479' },
  { t: '    response = client.chat.completions.create(', c: 'D6E2EE' },
  { t: '        model=model, messages=messages, tools=TOOL_SCHEMA)', c: 'D6E2EE' },
  { t: '    message = response.choices[0].message', c: 'D6E2EE' },
  { t: '    messages.append(message.model_dump(exclude_none=True))', c: 'D6E2EE' },
  { t: '', c: 'D6E2EE' },
  { t: '    if not message.tool_calls:', c: 'A5D6FF' },
  { t: '        return message.content', c: 'A5D6FF' },
  { t: '', c: 'D6E2EE' },
  { t: '    for call in message.tool_calls:', c: 'D6E2EE' },
  { t: '        args = json.loads(call.function.arguments)', c: 'D6E2EE' },
  { t: '        result = REGISTRY[call.function.name](**args)', c: 'FF9E80' },
  { t: '        messages.append({"role": "tool",', c: 'D6E2EE' },
  { t: '                         "tool_call_id": call.id,', c: 'D6E2EE' },
  { t: '                         "content": result})', c: 'D6E2EE' }
], { x: 0.62, y: 1.72, w: 8.3, size: 12, lh: 0.245 });
redBox(s, lb.x + 0.15, lb.y + 0.25 + 14 * lb.lh - 0.04, lb.w - 0.35, lb.lh + 0.08);
s.addShape(pres.ShapeType.line, {
  x: 9.05, y: lb.y + 0.25 + 14 * lb.lh + 0.16, w: 0.42, h: 0,
  line: { color: RED, width: 1.75, endArrowType: 'triangle' }
});
s.addText('this line is the\nonly place code runs', {
  x: 9.55, y: lb.y + 0.25 + 14 * lb.lh - 0.25, w: 3.2, h: 0.85,
  fontFace: SANS, fontSize: 13, color: RED, bold: true, margin: 0, valign: 'middle', lineSpacing: 18
});
s.addShape(pres.ShapeType.roundRect, {
  x: 9.25, y: 1.75, w: 3.47, h: 3.0, fill: { color: PANEL },
  line: { color: LINE, width: 1 }, rectRadius: 0.09
});
s.addText('Three things to notice', {
  x: 9.55, y: 1.95, w: 2.9, h: 0.4, fontFace: SERIF, fontSize: 16, color: INK, bold: true, margin: 0
});
s.addText('The for loop is the budget guard.\n\nThe assistant turn is appended whether or not it asked for a tool.\n\nThe tool result is tied to call.id, so the model knows which request it answers.', {
  x: 9.55, y: 2.4, w: 2.9, h: 2.2, fontFace: SANS, fontSize: 12.5, color: MUTED, margin: 0, lineSpacing: 17
});
s.addNotes('Type this line by line. Do not paste. The rhythm of building it is the lesson. Point at the red line and say out loud: this is the only executing statement in the entire agent.');

// ---- 30 ----
s = slide('Run it. Read the trace.');
codeBox(s, [
  { t: '>>> run_agent(client, MODEL,', c: '7E93A8' },
  { t: '...     "Can I get a room at Taj Palace on 2026-08-14,', c: '7E93A8' },
  { t: '...      and what would it cost?")', c: '7E93A8' },
  { t: '', c: 'D6E2EE' },
  { t: '[step 1] get_room_availability({\'hotel\': \'Taj Palace\',', c: 'A5D6FF' },
  { t: '          \'date\': \'2026-08-14\'})', c: 'A5D6FF' },
  { t: '          -> Taj Palace on 2026-08-14: 3 rooms available.', c: 'D6E2EE' },
  { t: '[step 2] get_nightly_rate({\'hotel\': \'Taj Palace\'})', c: 'A5D6FF' },
  { t: '          -> Taj Palace: Rs 14500 per night.', c: 'D6E2EE' },
  { t: '[step 3] done', c: 'FFD479' },
  { t: '', c: 'D6E2EE' },
  { t: '\'Yes, Taj Palace has 3 rooms available on 14 August', c: 'D6E2EE' },
  { t: ' at Rs 14500 per night.\'', c: 'D6E2EE' }
], { x: 0.62, y: 1.72, w: 12.1, size: 11.5, lh: 0.235 });
importantBox(s, 'THE THING WORTH SEEING', 'Nowhere did we say "availability first, then price". The model chose that order. Ask only about price and step 1 disappears. That is control flow living in the model rather than in your code, which is the Level 2 definition from the start of the lecture.', { y: 5.4, size: 14 });
s.addNotes('Run it twice with different questions so they see the step count change. That variability is the point and it also previews why testing is hard in Unit 5.');

// ---- 31 ----
s = slide('Now break it. On purpose.', 'FAILURE ONE');
body(s, 'Delete the max_steps guard, and give it a goal that none of its tools can satisfy.', { y: 1.62, h: 0.5, size: 17 });
codeBox(s, [
  { t: 'while True:                    # the guard is gone', c: 'FF9E80' },
  { t: '    ...', c: 'D6E2EE' },
  { t: '', c: 'D6E2EE' },
  { t: 'run_agent(client, MODEL,', c: '7E93A8' },
  { t: '    "Book me a room at the Oberoi in Shimla for tonight")', c: '7E93A8' }
], { x: 0.62, y: 2.3, w: 12.1, size: 13.5 });
body(s, 'There is no Oberoi in the data and there is no booking tool. Watch what it does rather than what you expect it to do.', { y: 4.55, h: 0.55, size: 16 });
importantBox(s, 'WHAT ACTUALLY HAPPENS', 'It calls get_room_availability. Gets "no record". Tries a different date. Gets "no record". Tries the other hotel. Tries the first hotel again. Every attempt is a billed API call, and it is being helpful rather than broken. This is the most common way people get a surprise invoice.', { y: 5.2 });
s.addNotes('Let this run for about fifteen seconds so they feel it, then interrupt the kernel. The physical act of having to stop it manually is worth more than any slide about cost control.');

// ---- 32 ----
s = slide('The fix is one line, and it is not clever');
codeBox(s, [
  { t: 'for step in range(1, max_steps + 1):', c: 'FFD479' },
  { t: '    ...', c: 'D6E2EE' },
  { t: '', c: 'D6E2EE' },
  { t: 'return (f"Stopped after {max_steps} steps without reaching', c: 'D6E2EE' },
  { t: '        f"a final answer.")', c: 'D6E2EE' }
], { x: 0.62, y: 1.9, w: 12.1, size: 14 });
teachCards(s, [
  { tag: 'WHAT IT DOES', h: 'Bounds the cost', b: 'The worst case is now arithmetic you can do in advance instead of a number you discover on an invoice.', tint: TEAL_T, accent: TEAL },
  { tag: 'WHAT IT DOES NOT DO', h: 'Fix the underlying problem', b: 'The agent still cannot answer. An unbounded failure is now a bounded one. Worth a lot, and not a solution.', tint: PANEL, accent: MUTED }
], { y: 4.05, h: 1.75, bsize: 13 });
recallBox(s, 'Returning an honest failure message beats returning a confident guess. Unit 5 is largely about that distinction.', { y: 5.9 });
s.addNotes('');

// ---- 33 ----
s = slide('Break it again. Differently.', 'FAILURE TWO');
body(s, 'This time we do not touch the code. We just ask for something the model would like a tool for, and does not have.', { y: 1.62, h: 0.55, size: 17 });
codeBox(s, [
  { t: 'run_agent(client, MODEL,', c: '7E93A8' },
  { t: '    "Check the Taj Palace and email the result to the manager")', c: '7E93A8' },
  { t: '', c: 'D6E2EE' },
  { t: '[step 1] get_room_availability(...) -> 3 rooms available.', c: 'A5D6FF' },
  { t: '[step 2] send_email({...})', c: 'FF9E80' },
  { t: '          -> Error: no tool named \'send_email\'.', c: 'FFD479' },
  { t: '             Available: [\'get_room_availability\',', c: 'FFD479' },
  { t: '                        \'get_nightly_rate\']', c: 'FFD479' },
  { t: '[step 3] done', c: 'D6E2EE' },
  { t: '', c: 'D6E2EE' },
  { t: '\'Taj Palace has 3 rooms. I do not have an email tool,', c: 'D6E2EE' },
  { t: ' so I could not send that.\'', c: 'D6E2EE' }
], { x: 0.62, y: 2.35, w: 12.1, size: 13, lh: 0.29 });
s.addNotes('The model inventing a tool surprises students every time. It is not a malfunction. It is a plausible next token given a request that mentions email.');

// ---- 34 ----
s = slide('Why that did not blow up');
codeBox(s, [
  { t: 'if name in REGISTRY:', c: 'A5D6FF' },
  { t: '    result = REGISTRY[name](**args)', c: 'D6E2EE' },
  { t: 'else:', c: 'A5D6FF' },
  { t: '    result = f"Error: no tool named \'{name}\'."', c: 'FFD479' }
], { x: 0.62, y: 1.85, w: 12.1, size: 14 });
teachCards(s, [
  { tag: 'THE NAIVE VERSION', h: 'REGISTRY[name](**args)', b: 'A KeyError, an unhandled exception, and in a web service a 500 to your user. Caused by the model saying a word.', tint: RED_T, accent: RED },
  { tag: 'THE DEFENDED VERSION', h: 'Check, then tell it', b: 'The error goes back as an observation. The model reads it, adjusts, and answers honestly. The loop survives.', tint: TEAL_T, accent: TEAL }
], { y: 3.7, h: 1.8, bsize: 13 });
importantBox(s, 'THE PRINCIPLE, WHICH RETURNS IN UNIT 6', 'Anything the model produces is untrusted input. A tool name is a string that came from a language model. Validate it as carefully as a form field from the open internet.', { y: 5.6, size: 14 });
s.addNotes('This is the first appearance of the untrusted input principle. Say explicitly that it is the foundation of prompt injection defence in Unit 6.');

// ---- 35 ----
s = slide('What you just wrote, and what a framework adds');
teachCards(s, [
  { tag: 'YOURS, TODAY', h: 'About forty lines', b: 'Loop, whitelist, budget, tool results fed back, honest failure. Every requirement from section two, visible on one screen.', tint: TEAL_T, accent: TEAL },
  { tag: 'WHAT SEMANTIC KERNEL ADDS', h: 'Structure, not magic', b: 'Schema generated from your type hints, retries, streaming, memory backends, tracing, and a shape that survives more than two tools.', tint: INDIGO_T, accent: INDIGO },
  { tag: 'WHAT IT DOES NOT ADD', h: 'A different loop', b: 'Underneath, it is the same think, act, observe cycle you just typed. Every framework in this course is doing what is on your screen right now.', tint: PANEL, accent: MUTED }
], { y: 2.0, h: 2.7, bsize: 13 });
recallBox(s, 'This is why we built it by hand first. When something misbehaves in Unit 3, you will know what layer to look at, because you have already written that layer.', { y: 5.0, h: 1.0 });
s.addNotes('');

// ================= WHEN NOT TO =================
// ---- 36 ----
s = divider('SECTION 05', 'When not to use one', 'The most professional thing you will learn today.');
s.addNotes('');

// ---- 37 ----
s = slide('Three shapes. Only one is an agent.');
const shapes = [
  ['WORKFLOW', 'You wrote the path', 'Step one, then two, then three. Every time. The model fills in content but never chooses direction.', 'Extracting fields from ten thousand invoices.', TEAL_T, TEAL],
  ['ROUTER', 'One decision, then a path', 'The model picks a branch from a fixed set, and that branch is ordinary code.', 'Sorting support tickets into five queues.', INDIGO_T, INDIGO],
  ['AGENT', 'The model picks the path', 'Number of steps unknown in advance. Order decided from what it observes.', 'Investigating why a build broke.', AMBER_T, AMBER]
];
shapes.forEach((c, i) => {
  const x = 0.62 + i * 4.15;
  s.addShape(pres.ShapeType.roundRect, {
    x, y: 1.95, w: 3.8, h: 3.55, fill: { color: c[4] },
    line: { color: 'FFFFFF', width: 0 }, rectRadius: 0.1
  });
  s.addText(c[0], {
    x: x + 0.25, y: 2.15, w: 3.3, h: 0.3, fontFace: SANS, fontSize: 11, color: c[5], bold: true, charSpacing: 1.3, margin: 0
  });
  s.addText(c[1], {
    x: x + 0.25, y: 2.48, w: 3.3, h: 0.5, fontFace: SERIF, fontSize: 17, color: INK, bold: true, margin: 0, lineSpacing: 21
  });
  s.addText(c[2], {
    x: x + 0.25, y: 3.05, w: 3.3, h: 1.25, fontFace: SANS, fontSize: 13, color: MUTED, margin: 0, lineSpacing: 18
  });
  s.addText('GOOD FOR', {
    x: x + 0.25, y: 4.35, w: 3.3, h: 0.28, fontFace: SANS, fontSize: 10, color: c[5], bold: true, charSpacing: 1.2, margin: 0
  });
  s.addText(c[3], {
    x: x + 0.25, y: 4.65, w: 3.3, h: 0.75, fontFace: SANS, fontSize: 13, color: INK, margin: 0, lineSpacing: 18
  });
});
body(s, 'Most production systems that get called agents are actually the first or the second, and they are better for it.', { y: 5.75, h: 0.5, size: 16 });
s.addNotes('');

// ---- 38 ----
s = slide('The test, and it is one question');
s.addShape(pres.ShapeType.roundRect, {
  x: 0.62, y: 1.85, w: 12.1, h: 1.35, fill: { color: TEAL_T },
  line: { color: 'FFFFFF', width: 0 }, rectRadius: 0.12
});
s.addText('Can you write down the steps in advance? If yes, write them. You do not need an agent.', {
  x: 1.05, y: 1.85, w: 11.25, h: 1.35, fontFace: SERIF, fontSize: 23,
  color: INK, bold: true, margin: 0, valign: 'middle', lineSpacing: 30
});
body(s, 'An agent is the right tool when the number of steps genuinely depends on what you find partway through. Debugging. Research. Investigation. Anything where step three is unknowable until step two returns.', { y: 3.45, h: 1.0, size: 16.5 });
importantBox(s, 'WHAT AN AGENT COSTS YOU FOR THAT FLEXIBILITY', 'Several model calls instead of one, so more money and more latency. Non deterministic behaviour, so testing gets hard. A larger surface for things to go wrong. You are paying all of that specifically to buy an unknown step count. If you do not need that, you are paying for nothing.', { y: 4.6, h: 1.7 });
s.addNotes('This slide is the one to return to whenever a student proposes an agent for something a for loop would do. It will happen in the capstone. Repeatedly.');

// ---- 39 ----
s = slide('The misconception, stated plainly');
teachCards(s, [
  { tag: 'WHAT THE INTERNET SAYS', h: 'Agents are the advanced option', b: 'So a workflow must be the beginner version, and using one means you did not understand the material.', tint: RED_T, accent: RED },
  { tag: 'WHAT ENGINEERS SAY', h: 'Agents are the expensive option', b: 'You reach for one when the problem shape demands it. Choosing a workflow when a workflow fits is the senior answer, not the junior one.', tint: TEAL_T, accent: TEAL }
], { y: 2.0, h: 2.5 });
recallBox(s, 'In your practical viva, "why is this an agent and not a script" is a real question with real marks attached. "Because the course is called agentic AI" is not an answer.', { y: 4.8, h: 1.0 });
body(s, 'Unit 2 spends a full block on exactly this decision.', { y: 5.95, h: 0.45, size: 15, color: MUTED });
s.addNotes('');

// ================= CLOSE =================
// ---- 40 ----
s = slide('Hold on to this');
s.addShape(pres.ShapeType.roundRect, {
  x: 0.62, y: 1.8, w: 12.1, h: 1.5, fill: { color: TEAL_T },
  line: { color: 'FFFFFF', width: 0 }, rectRadius: 0.12
});
s.addText('An agent is a loop that decides its own next step, using tools you gave it, until a condition you defined is met.', {
  x: 1.05, y: 1.8, w: 11.25, h: 1.5, fontFace: SERIF, fontSize: 22,
  color: INK, bold: true, margin: 0, valign: 'middle', lineSpacing: 30
});
body(s, 'Every word in that sentence is load bearing. Loop, decides, tools you gave it, condition you defined. Remove any one and you have something else, and you should call it something else.', { y: 3.55, h: 0.9, size: 16.5 });
const held = [
  ['The model never executes anything', 'Your loop does. That is where security, errors and cost live.'],
  ['The model remembers nothing', 'You resend the transcript every turn. That is what memory is.'],
  ['A tool description is an instruction', 'Vague description, wrong tool, and the bug is in your English.'],
  ['Termination is a feature', 'Not an afterthought. It is requirement four for a reason.']
];
held.forEach((h, i) => {
  const y = 4.6 + i * 0.6;
  s.addText(h[0], {
    x: 0.75, y, w: 4.6, h: 0.5, fontFace: SANS, fontSize: 14.5, color: TEAL, bold: true, margin: 0, valign: 'middle'
  });
  s.addText(h[1], {
    x: 5.5, y, w: 7.1, h: 0.5, fontFace: SANS, fontSize: 14, color: MUTED, margin: 0, valign: 'middle'
  });
});
s.addNotes('These four are the viva questions for this lecture. Say that out loud.');

// ---- 41 ----
s = slide('Before next session');
const work = [
  ['DO', 'Practical 1', 'Environment setup across all four lanes. The verification script has to print "You are ready." Everything after this depends on it.', TEAL, TEAL_T],
  ['DO', 'Extend the agent', 'Add a third tool of your own to today\'s notebook. Something the hotel assistant would plausibly need. Commit it.', INDIGO, INDIGO_T],
  ['THINK', 'Find a bad example', 'Find one product online marketed as an AI agent. Apply the four requirements. Be ready to say which ones it fails.', AMBER, AMBER_T]
];
work.forEach((r, i) => rowItem(s, 1.9 + i * 1.15, r[0], r[1], r[2], r[3], r[4]));
importantBox(s, 'ON THE THIRD ONE', 'Most of you will find a product that fails at least two of the four. That is not cynicism, it is the exercise working. Bring the specific product, not a general complaint.', { y: 5.5, h: 1.15, size: 14.5 });
s.addNotes('Collect the third one at the start of next session. It takes four minutes and it is the best possible warm up for L2.');

// ---- 42 ----
s = slide('Next session');
s.addShape(pres.ShapeType.roundRect, {
  x: 0.62, y: 1.8, w: 12.1, h: 1.5, fill: { color: INDIGO_T },
  line: { color: 'FFFFFF', width: 0 }, rectRadius: 0.1
});
s.addText('Unit 1, Lecture 2', {
  x: 1.05, y: 1.95, w: 11.2, h: 0.5, fontFace: SANS, fontSize: 13,
  color: INDIGO, bold: true, charSpacing: 1.4, margin: 0
});
s.addText('Intelligent Agent Architectures', {
  x: 1.05, y: 2.4, w: 11.2, h: 0.7, fontFace: SERIF, fontSize: 28,
  color: INK, bold: true, margin: 0
});
body(s, 'Today we built one architecture without naming it. Next time we name the whole family. Reactive, goal based, utility based and learning agents, what each one is actually good for, and which of them your forty lines already is.', { y: 3.7, h: 1.2, size: 16.5 });
activityBox(s, 'COME WITH', 'Practical 1 done, your third tool committed, and one badly marketed agent product to pull apart.', { y: 5.2, h: 1.0 });
s.addNotes('');

pres.writeFile({ fileName: '/home/claude/CSE476_U1_L1.pptx' })
  .then(() => console.log('written'))
  .catch(e => { console.error(e); process.exit(1); });
