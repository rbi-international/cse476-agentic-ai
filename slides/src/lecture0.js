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
pres.title = 'CSE476 Lecture Zero';

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
  s.addText('CSE476  Agentic AI and Intelligent Automation', {
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

function importantBox(s, label, text, o) {
  o = o || {};
  const y = o.y || 5.05;
  const h = o.h || 1.25;
  s.addShape(pres.ShapeType.roundRect, {
    x: 0.62, y, w: o.w || 12.1, h, fill: { color: AMBER_T },
    line: { color: 'FFFFFF', width: 0 }, rectRadius: 0.09
  });
  s.addText(label, {
    x: 0.92, y: y + 0.2, w: 3, h: 0.28, fontFace: SANS, fontSize: 10.5,
    color: AMBER, bold: true, charSpacing: 1.3, margin: 0
  });
  s.addText(text, {
    x: 0.92, y: y + 0.52, w: (o.w || 12.1) - 0.6, h: h - 0.68,
    fontFace: SANS, fontSize: o.size || 15, color: INK, margin: 0, lineSpacing: 21
  });
}

function recallBox(s, text, o) {
  o = o || {};
  const y = o.y || 5.4;
  s.addShape(pres.ShapeType.roundRect, {
    x: 0.62, y, w: o.w || 12.1, h: o.h || 1.0, fill: { color: PANEL },
    line: { color: LINE, width: 1 }, rectRadius: 0.09
  });
  s.addText('HOLD ON TO THIS', {
    x: 0.92, y: y + 0.16, w: 3, h: 0.26, fontFace: SANS, fontSize: 10.5,
    color: TEAL, bold: true, charSpacing: 1.3, margin: 0
  });
  s.addText(text, {
    x: 0.92, y: y + 0.44, w: (o.w || 12.1) - 0.6, h: (o.h || 1.0) - 0.58,
    fontFace: SANS, fontSize: 14.5, color: INK, margin: 0, lineSpacing: 20
  });
}

function activityBox(s, label, text, o) {
  o = o || {};
  const y = o.y || 5.05;
  const h = o.h || 1.3;
  s.addShape(pres.ShapeType.roundRect, {
    x: 0.62, y, w: 12.1, h, fill: { color: TEAL_T },
    line: { color: 'FFFFFF', width: 0 }, rectRadius: 0.09
  });
  s.addText(label, {
    x: 0.92, y: y + 0.2, w: 4, h: 0.28, fontFace: SANS, fontSize: 10.5,
    color: TEAL, bold: true, charSpacing: 1.3, margin: 0
  });
  s.addText(text, {
    x: 0.92, y: y + 0.52, w: 11.5, h: h - 0.68, fontFace: SANS,
    fontSize: o.size || 15, color: INK, margin: 0, lineSpacing: 21
  });
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
   SLIDES
   ============================================================ */

let s;

// ---- 1 title ----
s = titleSlide({
  kicker: 'LOVELY PROFESSIONAL UNIVERSITY,  SCHOOL OF COMPUTER SCIENCE AND ENGINEERING',
  code: 'CSE476',
  title: 'Agentic AI and\nIntelligent Automation',
  sub: 'Lecture Zero. What this course is, why it exists,\nand what you will be able to build by the end of it.',
  foot: 'Rohit Bharti'
});
s.addNotes('TEACHING NOTE (do not say): do not read this slide. Have the glass box demo already open in another window. Say only "give me two minutes before I show you any syllabus" and switch to it.');

// ---- 2 divider ----
s = divider('SECTION 00', 'Let us start with a demo,\nnot a syllabus', 'Two minutes. Then we talk.');
s.addNotes('Switch to the live demo now. Do not narrate while it runs the first time. Let them watch it in silence.');

// ---- 3 ----
s = slide('Watch this before I explain anything');
body(s, 'I am going to give a program a goal. Not a question. A goal.\n\nI will not tell it which steps to take. I will not tell it which tools to use. I will give it the outcome I want and then I will stop typing.');
importantBox(s, 'WHAT TO WATCH FOR', 'Count how many times it stops and thinks between actions. That number is the whole difference between what you have used before and what you are about to learn.', { y: 4.5, h: 1.35 });
s.addNotes('Keep this short. The demo is doing the work, not the slide.');

// ---- 4 ----
s = slide('The goal I gave it');
s.addShape(pres.ShapeType.roundRect, {
  x: 0.62, y: 1.75, w: 12.1, h: 1.15, fill: { color: PANEL },
  line: { color: LINE, width: 1 }, rectRadius: 0.09
});
s.addText('"Find out which of our three suppliers had the worst on time delivery last quarter, then draft the escalation email."', {
  x: 0.95, y: 1.75, w: 11.5, h: 1.15, fontFace: SERIF, fontSize: 19,
  color: INK, italic: true, margin: 0, valign: 'middle', lineSpacing: 26
});
body(s, 'Notice what is missing from that sentence. I did not say where the data lives. I did not say to open the spreadsheet first. I did not say to compare before writing. I did not say what an escalation email looks like.\n\nA search box would return links. A chatbot would ask me to paste the data. This thing went and got it.', { y: 3.2, h: 2.0 });
s.addNotes('The point of this slide is the absence of instructions. Read the goal aloud once, then pause and let them notice what is not in it.');

// ---- 5 ----
s = slide('What it actually did, step by step');
const steps = [
  ['THINK', 'I need delivery records. I do not have them. There is a database tool.'],
  ['ACT', 'Query the supplier delivery table for last quarter.'],
  ['OBSERVE', 'Three suppliers returned. Percentages differ.'],
  ['THINK', 'Rao Logistics is lowest at 71 percent. That is the answer to part one.'],
  ['ACT', 'Draft an escalation email addressed to Rao Logistics.'],
  ['OBSERVE', 'Draft produced. Both parts of the goal are now done. Stop.']
];
steps.forEach((st, i) => {
  const y = 1.72 + i * 0.79;
  const isThink = st[0] === 'THINK';
  const isAct = st[0] === 'ACT';
  const tint = isThink ? INDIGO_T : (isAct ? TEAL_T : PANEL);
  const acc = isThink ? INDIGO : (isAct ? TEAL : MUTED);
  s.addShape(pres.ShapeType.roundRect, {
    x: 0.62, y, w: 12.1, h: 0.66, fill: { color: tint },
    line: { color: 'FFFFFF', width: 0 }, rectRadius: 0.07
  });
  s.addText(st[0], {
    x: 0.88, y, w: 1.35, h: 0.66, fontFace: SANS, fontSize: 12,
    color: acc, bold: true, charSpacing: 1.2, margin: 0, valign: 'middle'
  });
  s.addText(st[1], {
    x: 2.35, y, w: 10.1, h: 0.66, fontFace: SANS, fontSize: 14.5,
    color: INK, margin: 0, valign: 'middle'
  });
});
s.addNotes('Walk down the six rows slowly. The rhythm is the lesson: think, act, observe, think, act, observe. Ask them to say the next word out loud by row four.');

// ---- 6 ----
s = slide('Three words. That is the engine.');
s.addText('a chatbot never gets past this one', {
  x: 0.75, y: 1.72, w: 3.7, h: 0.4, fontFace: SANS, fontSize: 12.5,
  color: RED, bold: true, align: 'center', margin: 0
});
const nodes = [
  { t: 'THINK', sub: 'what should I do now', x: 0.9, fill: INDIGO_T, col: INDIGO },
  { t: 'ACT', sub: 'call a tool', x: 4.95, fill: TEAL_T, col: TEAL },
  { t: 'OBSERVE', sub: 'read what came back', x: 9.0, fill: AMBER_T, col: AMBER }
];
nodes.forEach(nd => {
  s.addShape(pres.ShapeType.roundRect, {
    x: nd.x, y: 2.35, w: 3.4, h: 1.15, fill: { color: nd.fill },
    line: { color: 'FFFFFF', width: 0 }, rectRadius: 0.1
  });
  s.addText(nd.t, {
    x: nd.x, y: 2.5, w: 3.4, h: 0.45, fontFace: SERIF, fontSize: 20,
    color: nd.col, bold: true, align: 'center', margin: 0
  });
  s.addText(nd.sub, {
    x: nd.x, y: 2.97, w: 3.4, h: 0.35, fontFace: SANS, fontSize: 12.5,
    color: MUTED, align: 'center', margin: 0
  });
});
arrow(s, 4.42, 2.92, 0.45);
arrow(s, 8.47, 2.92, 0.45);
// return path
s.addShape(pres.ShapeType.line, { x: 10.7, y: 3.5, w: 0, h: 0.72, line: { color: FAINT, width: 1.5 } });
s.addShape(pres.ShapeType.line, { x: 2.6, y: 4.22, w: 8.1, h: 0, line: { color: FAINT, width: 1.5 } });
s.addShape(pres.ShapeType.line, {
  x: 2.6, y: 3.5, w: 0, h: 0.72,
  line: { color: FAINT, width: 1.5, beginArrowType: 'triangle' }
});
s.addText('and around again, until it decides the goal is met', {
  x: 3.6, y: 4.28, w: 6.1, h: 0.4, fontFace: SANS, fontSize: 12.5,
  color: FAINT, align: 'center', margin: 0, italic: true
});
redBox(s, 0.75, 2.22, 3.7, 1.42);
body(s, 'A chatbot runs this once and stops. An agent runs it again, and again, deciding each time whether it is finished.', { y: 5.1, h: 0.6, size: 17 });
recallBox(s, 'The red box is on THINK, not on ACT. Acting is the part that looks impressive. Reasoning between actions is the part that actually makes it an agent.', { y: 5.8, h: 1.0 });
s.addNotes('The red box is on THINK deliberately. Students expect ACT to be the special part. It is not. Reasoning between actions is the special part.');

// ---- 7 ----
s = slide('So what is the actual difference?');
teachCards(s, [
  { tag: 'WHAT YOU HAVE USED', h: 'A chatbot answers', b: 'One question in, one answer out. It knows things. It cannot do things. If it needs your data, it asks you to paste it.', tint: PANEL, accent: MUTED },
  { tag: 'WHAT WE ARE BUILDING', h: 'An agent finishes', b: 'One goal in, a completed task out. It has tools, it chooses which to use, it reads the result, and it decides on its own when the work is done.', tint: TEAL_T, accent: TEAL }
], { y: 2.0, h: 2.5 });
recallBox(s, 'The difference is not intelligence. Both use the same underlying model. The difference is permission to act and the loop that lets it keep acting.', { y: 4.85, h: 1.05 });
s.addNotes('Emphasise "same underlying model". Students assume agents need a smarter model. They do not. They need tools and a loop.');

// ---- 8 ----
s = slide('That demo is this entire course');
body(s, 'Everything for the next fifty hours sits somewhere inside that loop.\n\nHow the model decides what to do next. How you give it tools safely. How you stop it looping forever. How you know it is telling the truth. How you get it out of your laptop and into something a company can actually run.', { y: 1.7, h: 2.0 });
importantBox(s, 'ONE HONEST WARNING', 'That demo took me about forty lines of code. Getting the same thing to work reliably, for a thousand users, without leaking data or inventing facts, takes considerably more. That gap is where most of this course lives, and it is also where the jobs are.', { y: 4.2, h: 1.6 });
s.addNotes('Set the expectation early that the flashy part is the easy part. This protects you from the mid semester complaint that Unit 5 and Unit 6 are boring.');

// ---- 9 divider ----
s = divider('SECTION 01', 'What actually changed', 'And why this course did not exist three years ago.');
s.addNotes('');

// ---- 10 ----
s = slide('The last four years, compressed');
const tl = [
  ['2022', 'It could talk', 'Fluent text. Impressive. Completely sealed off from the world.'],
  ['2023', 'It could be pointed at your data', 'Retrieval. Now it could answer from documents it had never memorised.'],
  ['2024', 'It could call your functions', 'Tool calling arrives. The model can now trigger real code.'],
  ['2025', 'It could run a loop', 'Frameworks make think, act, observe routine instead of research.'],
  ['2026', 'It has to behave in production', 'The hard questions arrive: cost, safety, identity, audit, governance.']
];
tl.forEach((r, i) => {
  const y = 1.72 + i * 0.94;
  s.addText(r[0], {
    x: 0.66, y, w: 1.1, h: 0.8, fontFace: SERIF, fontSize: 21,
    color: i === 4 ? TEAL : FAINT, bold: true, margin: 0, valign: 'middle'
  });
  s.addShape(pres.ShapeType.rect, { x: 1.95, y: y + 0.05, w: 0.035, h: 0.7, fill: { color: i === 4 ? TEAL : LINE } });
  s.addText(r[1], {
    x: 2.25, y: y - 0.02, w: 4.1, h: 0.42, fontFace: SERIF, fontSize: 16,
    color: INK, bold: true, margin: 0, valign: 'middle'
  });
  s.addText(r[2], {
    x: 6.5, y, w: 6.1, h: 0.8, fontFace: SANS, fontSize: 13.5,
    color: MUTED, margin: 0, valign: 'middle', lineSpacing: 18
  });
});
s.addText('you are here', {
  x: 11.1, y: 6.5, w: 1.6, h: 0.3, fontFace: SANS, fontSize: 11.5,
  color: TEAL, bold: true, align: 'right', margin: 0
});
s.addNotes('The row that matters is 2026. Every previous row was a capability row. This one is an engineering row. That is why the syllabus spends two full units on testing, security and governance.');

// ---- 11 ----
s = slide('The layman version first', 'HOW I WILL TEACH EVERY TOPIC');
body(s, 'Think of hiring someone for your shop.', { y: 1.6, h: 0.4, size: 17, bold: true });
teachCards(s, [
  { tag: 'THE ENCYCLOPEDIA', h: 'You ask, it tells', b: 'A very well read person sitting on a chair. Ask anything, get a good answer. But it will not get up. It will not go to the godown and count the stock for you.', tint: PANEL, accent: MUTED },
  { tag: 'THE EMPLOYEE', h: 'You ask, it goes', b: 'Same knowledge. But this one has the godown keys, the ledger, and the phone. Tell it what you need and it walks off and comes back with the answer.', tint: TEAL_T, accent: TEAL }
], { y: 2.15, h: 2.4 });
importantBox(s, 'NOW THE TECHNICAL PART', 'The keys, the ledger and the phone are called tools. The walking off and coming back is called the agent loop. Everything else in this course is detail on top of those two ideas.', { y: 4.85, h: 1.3 });
s.addNotes('TEACHING NOTE (do not say): this is the layman first pattern they will see in every session. Say the analogy, let it land, then name the technical term. Never the other way round.');

// ---- 12 ----
s = slide('Why suddenly everyone at once');
bullets(s, [
  'Models got reliable enough at following a schema. Tool calling only works if the model returns exactly the structure your code expects, every time. That got solved.',
  'Context windows got long enough to hold a working memory of what the agent has already tried.',
  'Inference got cheap enough that running the loop twenty times instead of once stopped being unaffordable.',
  'Frameworks arrived. What was six months of research code in 2023 is now an import statement.',
  'And crucially, the money arrived. Enterprises stopped experimenting and started budgeting.'
], { y: 1.75, h: 3.6, size: 16 });
recallBox(s, 'None of these five is an intelligence breakthrough. They are engineering breakthroughs. That is a hopeful thing for you, because engineering is learnable.', { y: 5.45, h: 1.0 });
s.addNotes('');

// ---- 13 ----
s = slide('The part the hype does not mention');
body(s, 'Most agent demos on the internet work once, on the demo machine, with the demo question.', { y: 1.65, h: 0.5, size: 18, bold: true });
teachCards(s, [
  { tag: 'FAILURE 1', h: 'It loops forever', b: 'No termination condition. It burns forty API calls deciding it is not done yet. You find out from the bill.', tint: RED_T, accent: RED },
  { tag: 'FAILURE 2', h: 'It confidently lies', b: 'The retrieval pulled the wrong paragraph. The agent does not know that. It answers with total confidence.', tint: RED_T, accent: RED },
  { tag: 'FAILURE 3', h: 'It gets talked into things', b: 'A document it reads contains an instruction. It obeys the document instead of you. This has a name: prompt injection.', tint: RED_T, accent: RED }
], { y: 2.35, h: 2.5, bsize: 13 });
importantBox(s, 'WHICH IS WHY', 'Units 5 and 6, fourteen of our fifty hours, are about exactly these three failures. Not because the syllabus says so, but because this is what separates a student project from something a company will pay for.', { y: 5.15, h: 1.3 });
s.addNotes('These three failures are real ones I have hit. Tell them you will reproduce all three live in class, deliberately, before fixing them.');

// ---- 14 divider ----
s = divider('SECTION 02', 'What this course is,\nand what it is not', 'So nobody is surprised in November.');
s.addNotes('');

// ---- 15 ----
s = slide('The promise, in one sentence');
s.addShape(pres.ShapeType.roundRect, {
  x: 0.62, y: 2.0, w: 12.1, h: 1.9, fill: { color: TEAL_T },
  line: { color: 'FFFFFF', width: 0 }, rectRadius: 0.12
});
s.addText('By December you will have built, secured, instrumented and deployed a working multi agent system, and you will be able to explain every design decision in it to an interviewer.', {
  x: 1.1, y: 2.0, w: 11.1, h: 1.9, fontFace: SERIF, fontSize: 23,
  color: INK, bold: true, margin: 0, valign: 'middle', lineSpacing: 33
});
body(s, 'Read that again and notice the second half. Building it is half the marks. Being able to defend it is the other half, in this room and in every interview after it.', { y: 4.35, h: 0.9, size: 16, color: MUTED });
s.addNotes('');

// ---- 16 ----
s = slide('What this course is');
teachCards(s, [
  { tag: 'HANDS ON', h: 'Code, not slideware', b: 'Twenty one of the fifty hours are you writing and running code. Ten formal practicals plus live builds in almost every session.', tint: TEAL_T, accent: TEAL },
  { tag: 'CURRENT', h: 'Built this month', b: 'Every framework version is verified live before it reaches a slide. This field renames things twice a year and I will tell you when it does.', tint: INDIGO_T, accent: INDIGO },
  { tag: 'ENTERPRISE', h: 'Production shaped', b: 'Microsoft Foundry, Semantic Kernel, AutoGen, real deployment, real observability, real security. Not toy notebooks.', tint: AMBER_T, accent: AMBER }
], { y: 2.0, h: 2.7 });
recallBox(s, 'The whole course is benchmarked against the Microsoft AI Agents professional certificate. If you follow it properly, that credential becomes a short step rather than a fresh start.', { y: 5.0, h: 1.05 });
s.addNotes('');

// ---- 17 ----
s = slide('What this course is not');
teachCards(s, [
  { tag: 'NOT THIS', h: 'Not a prompt writing course', b: 'Prompting is one session, not a semester. If you came for prompt tricks you will be disappointed by week two.', tint: PANEL, accent: MUTED },
  { tag: 'NOT THIS', h: 'Not a model training course', b: 'We do not train or fine tune models here. We orchestrate them. Different skill, different course.', tint: PANEL, accent: MUTED },
  { tag: 'NOT THIS', h: 'Not a copy the notebook course', b: 'I will show you code that is broken, on purpose, before I show you code that works. If you copy without watching, you will not survive the viva.', tint: PANEL, accent: MUTED }
], { y: 2.0, h: 2.7 });
importantBox(s, 'ALSO WORTH SAYING', 'This is not a course where attendance alone produces a grade. The practicals compound. Miss the middle of Unit 3 and Unit 4 will not make sense, because Unit 4 builds directly on it.', { y: 5.0, h: 1.25 });
s.addNotes('');

// ---- 18 ----
s = slide('What I need from you, and what you get from me');
teachCards(s, [
  { tag: 'FROM YOU', h: 'Bring the laptop, open the editor', b: 'Every session has code. A session where you only watch is a session you will not remember. Also: tell me when something breaks. I would rather fix it in class than read about it in a viva.', tint: INDIGO_T, accent: INDIGO },
  { tag: 'FROM ME', h: 'Nothing untested reaches you', b: 'Every code cell I hand you has been run against the installed package version, not written from documentation memory. When something is deprecated I will say so and tell you the replacement.', tint: TEAL_T, accent: TEAL }
], { y: 2.0, h: 2.7 });
recallBox(s, 'I am learning parts of this stack alongside you. Semantic Kernel and the enterprise governance material are new ground for me too. You will see me check things live. That is the job, not a weakness in it.', { y: 5.0, h: 1.15 });
s.addNotes('Say this one honestly and out loud. It buys enormous goodwill and it models exactly the behaviour you want from them, which is checking rather than assuming.');

// ---- 19 divider ----
s = divider('SECTION 03', 'The map', 'Six units, fifty hours, one system at the end.');
s.addNotes('');

// ---- 20 ----
s = slide('The whole course on one slide');
const units = [
  ['U1', 'Foundations', 'What an agent is. Microsoft Foundry.', 8, TEAL, TEAL_T],
  ['U2', 'Workflows', 'Tool calling, orchestration, automation.', 7, TEAL, TEAL_T],
  ['U3', 'Frameworks', 'Python, Semantic Kernel, AutoGen, memory, RAG.', 10, INDIGO, INDIGO_T],
  ['U4', 'Multi agent', 'Collaboration, delegation, MCP and A2A.', 9, INDIGO, INDIGO_T],
  ['U5', 'Ship it', 'Testing, observability, deployment, CI/CD.', 7, AMBER, AMBER_T],
  ['U6', 'Trust it', 'Responsible AI, security, governance.', 7, AMBER, AMBER_T]
];
units.forEach((u, i) => {
  const y = 1.68 + i * 0.85;
  s.addShape(pres.ShapeType.roundRect, {
    x: 0.62, y, w: 12.1, h: 0.72, fill: { color: u[5] },
    line: { color: 'FFFFFF', width: 0 }, rectRadius: 0.08
  });
  s.addText(u[0], {
    x: 0.9, y, w: 0.9, h: 0.72, fontFace: SERIF, fontSize: 17,
    color: u[4], bold: true, margin: 0, valign: 'middle'
  });
  s.addText(u[1], {
    x: 1.85, y, w: 2.7, h: 0.72, fontFace: SERIF, fontSize: 16,
    color: INK, bold: true, margin: 0, valign: 'middle'
  });
  s.addText(u[2], {
    x: 4.6, y, w: 6.6, h: 0.72, fontFace: SANS, fontSize: 13.5,
    color: MUTED, margin: 0, valign: 'middle'
  });
  s.addText(u[3] + ' hrs', {
    x: 11.3, y, w: 1.15, h: 0.72, fontFace: SANS, fontSize: 13.5,
    color: u[4], bold: true, align: 'right', margin: 0, valign: 'middle'
  });
});
s.addText('Fifty hours total. Twenty one of them are hands on code.', {
  x: 0.62, y: 6.75, w: 12.1, h: 0.3, fontFace: SANS, fontSize: 13,
  color: MUTED, margin: 0
});
s.addNotes('Give them thirty seconds to just look at this. Then point out that Units 5 and 6 together are fourteen hours, more than Unit 3, and ask them to remember that when we get there.');

// ---- 21 ----
s = slide('Unit 1, Foundations of AI Agents and Microsoft Foundry', 'EIGHT HOURS');
bullets(s, [
  'What an agent actually is, and the honest boundary between a chatbot and an agent.',
  'Agent architectures: reactive, goal based, utility based. Perception and action models.',
  'Planning and reasoning. The ReAct pattern, which you will use for the rest of your career.',
  'Microsoft Foundry, first contact. Projects, model catalogue, playground, deployments.',
  'Prompt engineering, specifically for agents rather than for chat.',
  'A map of the Microsoft AI ecosystem, including which parts are already deprecated.'
], { y: 1.85, h: 3.1, size: 16 });
activityBox(s, 'YOU WILL BUILD', 'Practical 1: your full development environment across all four access lanes. Practical 2: a conversational hotel information agent, your first working agent.', { y: 5.15, h: 1.2 });
s.addNotes('');

// ---- 22 ----
s = slide('Unit 2, Building Intelligent Agent Workflows', 'SEVEN HOURS');
bullets(s, [
  'Workflow versus agency. When a plain deterministic pipeline is the better engineering choice, and how to tell.',
  'Tool calling mechanics in depth. Schemas, how the model chooses, the execution loop, what happens when a tool fails.',
  'API integration and connecting an agent to real services.',
  'Workflow chaining and event driven agent systems.',
  'Context aware agents that carry state across turns.',
  'First look at testing and deployment, which Unit 5 then takes seriously.'
], { y: 1.85, h: 3.1, size: 16 });
activityBox(s, 'YOU WILL BUILD', 'Practical 3: an intelligent workflow automation agent that takes a messy real input and produces a structured, actioned output.', { y: 5.15, h: 1.2 });
s.addNotes('Block 2.1 is the one that matters most here. Students over apply agents. Teaching them when not to use one is a genuine professional skill.');

// ---- 23 ----
s = slide('Unit 3, Agent Development with Python and Frameworks', 'TEN HOURS, THE HEAVIEST UNIT');
bullets(s, [
  'Python for agents: async, typing, Pydantic. I will assume gaps here and fill them rather than pretend.',
  'Semantic Kernel, the mental model. This is genuinely new thinking, not a renamed version of something you know.',
  'AutoGen and AG2, conversational agent patterns.',
  'Memory and state. Short term, long term, session scoped. Why an agent that forgets is nearly useless.',
  'Prompt templates and structured output you can actually rely on in code.',
  'Retrieval augmented generation, so the agent can answer from your documents.',
  'Connecting an agent to a conversational channel using the Microsoft 365 Agents SDK.'
], { y: 1.82, h: 3.4, size: 15.5 });
activityBox(s, 'YOU WILL BUILD', 'Practical 4: tool calling and API integration with Semantic Kernel. Practical 5: an agent with working memory and context management.', { y: 5.4, h: 1.15 });
s.addNotes('Warn them here: this unit is where people fall behind. Ten hours, most new material, and everything after it depends on it.');

// ---- 24 ----
s = slide('Unit 4, Multi Agent Systems and Collaboration', 'NINE HOURS');
bullets(s, [
  'Why use several agents at all, including the honest cases where one agent is simply better.',
  'Planner and executor architectures. One agent decides, others do.',
  'Inter agent communication and task delegation.',
  'Orchestration patterns: sequential, concurrent, group chat, handoff.',
  'Role based agents, where each agent gets a job description rather than a prompt.',
  'Open protocols. MCP and A2A. Why the industry needed a standard and what it changed.',
  'Microsoft Agent Framework 1.0 and where Semantic Kernel and AutoGen are heading.'
], { y: 1.82, h: 3.4, size: 15.5 });
activityBox(s, 'YOU WILL BUILD', 'Practical 6: a medical information agent with responsible AI safeguards. Practical 7: a multi agent collaborative workflow system.', { y: 5.4, h: 1.15 });
s.addNotes('');

// ---- 25 ----
s = slide('Unit 5, Testing, Monitoring and Deployment', 'SEVEN HOURS, HALF OF IT HANDS ON');
bullets(s, [
  'Why agents are hard to test. The same input gives a different output. So what exactly do you assert?',
  'Debugging an agent trace, which is a genuinely different skill from debugging a stack trace.',
  'Observability and telemetry. OpenTelemetry, Azure Monitor, Prometheus and Grafana.',
  'Hallucination detection and validation. Making the system check its own work.',
  'Deployment: containers, Azure Container Apps, hosted agents, scale to zero.',
  'CI/CD and performance optimisation.'
], { y: 1.85, h: 3.1, size: 16 });
activityBox(s, 'YOU WILL BUILD', 'Practical 8: retrieval augmented generation workflows. Practical 9: monitoring and observability for a running agent.', { y: 5.15, h: 1.2 });
s.addNotes('');

// ---- 26 ----
s = slide('Unit 6, Responsible AI, Security and Governance', 'SEVEN HOURS. THE ONE NOBODY ELSE TEACHES.');
bullets(s, [
  'Responsible AI principles, applied specifically to agents that can take actions.',
  'Prompt injection, direct and indirect. We will run a successful attack in class before defending against it.',
  'Authentication and authorisation. Managed identity, least privilege, and the confused deputy problem.',
  'Content safety, filters and guardrails.',
  'Compliance, auditing and data residency.',
  'Enterprise governance models and secure multi agent architecture.'
], { y: 1.85, h: 3.1, size: 16 });
importantBox(s, 'WHY THIS UNIT IS WORTH YOUR ATTENTION', 'Almost every course and tutorial online stops at Unit 4. An agent that works is now a commodity. An agent somebody trusts with real permissions is not. This unit is your differentiator.', { y: 5.15, h: 1.25 });
s.addNotes('Schedule this unit as early as your timetable allows. It sits at the end of the semester where it is most at risk of being cut, and it is the most valuable thing here.');

// ---- 27 ----
s = slide('Why this order and not another');
body(s, 'The order is not arbitrary. It follows the shape of a real project.', { y: 1.6, h: 0.4, size: 17, bold: true });
const flow = [
  ['Understand', 'U1'], ['Connect', 'U2'], ['Build', 'U3'],
  ['Scale up', 'U4'], ['Prove it works', 'U5'], ['Make it trustworthy', 'U6']
];
let fx = 0.72;
flow.forEach((f, i) => {
  s.addShape(pres.ShapeType.roundRect, {
    x: fx, y: 2.35, w: 1.72, h: 1.15, fill: { color: i < 2 ? TEAL_T : (i < 4 ? INDIGO_T : AMBER_T) },
    line: { color: 'FFFFFF', width: 0 }, rectRadius: 0.1
  });
  s.addText(f[1], {
    x: fx, y: 2.5, w: 1.72, h: 0.35, fontFace: SANS, fontSize: 11.5,
    color: i < 2 ? TEAL : (i < 4 ? INDIGO : AMBER), bold: true, align: 'center', margin: 0
  });
  s.addText(f[0], {
    x: fx + 0.08, y: 2.83, w: 1.56, h: 0.55, fontFace: SERIF, fontSize: 14.5,
    color: INK, bold: true, align: 'center', margin: 0, lineSpacing: 18
  });
  if (i < 5) arrow(s, fx + 1.78, 2.93, 0.36);
  fx += 2.14;
});
body(s, 'A team in industry does exactly this. They understand the problem, connect to the data, build the thing, split it across specialists when it grows, prove it works, and only then are they allowed to give it real permissions on real systems.\n\nYou are not learning topics in a syllabus order. You are walking a project lifecycle.', { y: 4.0, h: 2.0, size: 16 });
s.addNotes('');

// ---- 28 divider ----
s = divider('SECTION 04', 'What you will actually build', 'Ten practicals, and one system that survives to the end.');
s.addNotes('');

// ---- 29 ----
s = slide('The ten practicals');
const pr = [
  ['01', 'Development environment, Foundry and VS Code'],
  ['02', 'Conversational hotel information agent'],
  ['03', 'Intelligent workflow automation agent'],
  ['04', 'Tool calling and API integration, Semantic Kernel'],
  ['05', 'Agent with memory and context management'],
  ['06', 'Medical information agent with responsible AI'],
  ['07', 'Multi agent collaborative workflow system'],
  ['08', 'Retrieval augmented generation workflows'],
  ['09', 'Monitoring and observability for agents'],
  ['10', 'Secure deployment and governance']
];
pr.forEach((p, i) => {
  const col = i < 5 ? 0 : 1;
  const row = i % 5;
  const x = 0.62 + col * 6.25;
  const y = 1.8 + row * 0.86;
  const spine = i >= 7;
  s.addShape(pres.ShapeType.roundRect, {
    x, y, w: 5.85, h: 0.72, fill: { color: spine ? AMBER_T : PANEL },
    line: { color: spine ? 'FFFFFF' : LINE, width: spine ? 0 : 1 }, rectRadius: 0.08
  });
  s.addText(p[0], {
    x: x + 0.22, y, w: 0.6, h: 0.72, fontFace: SERIF, fontSize: 16,
    color: spine ? AMBER : FAINT, bold: true, margin: 0, valign: 'middle'
  });
  s.addText(p[1], {
    x: x + 0.85, y, w: 4.85, h: 0.72, fontFace: SANS, fontSize: 13.5,
    color: INK, margin: 0, valign: 'middle', lineSpacing: 17
  });
});
s.addText('The last three are highlighted for a reason. Next slide.', {
  x: 0.62, y: 6.45, w: 12.1, h: 0.3, fontFace: SANS, fontSize: 13.5,
  color: AMBER, bold: true, margin: 0
});
s.addNotes('');

// ---- 30 ----
s = slide('Practicals 8, 9 and 10 are one system, not three');
body(s, 'Most courses hand you ten disconnected notebooks. You finish with ten things that each work once. That is not what a portfolio looks like.', { y: 1.6, h: 0.75, size: 16.5 });
const spine = [
  ['P8', 'Build it', 'A retrieval agent that answers from a real document set.', TEAL, TEAL_T],
  ['P9', 'Watch it', 'Instrument that same agent. Traces, metrics, a live dashboard.', INDIGO, INDIGO_T],
  ['P10', 'Trust it', 'Secure and deploy that same agent. Identity, filters, governance.', AMBER, AMBER_T]
];
let sy = 2.55;
spine.forEach((sp, i) => {
  s.addShape(pres.ShapeType.roundRect, {
    x: 0.62 + i * 4.18, y: sy, w: 3.85, h: 2.0, fill: { color: sp[4] },
    line: { color: 'FFFFFF', width: 0 }, rectRadius: 0.1
  });
  s.addText(sp[0], {
    x: 0.85 + i * 4.18, y: sy + 0.2, w: 3.4, h: 0.35, fontFace: SANS, fontSize: 12,
    color: sp[3], bold: true, charSpacing: 1.2, margin: 0
  });
  s.addText(sp[1], {
    x: 0.85 + i * 4.18, y: sy + 0.55, w: 3.4, h: 0.45, fontFace: SERIF, fontSize: 19,
    color: INK, bold: true, margin: 0
  });
  s.addText(sp[2], {
    x: 0.85 + i * 4.18, y: sy + 1.05, w: 3.4, h: 0.85, fontFace: SANS, fontSize: 13.5,
    color: MUTED, margin: 0, lineSpacing: 19
  });
  if (i < 2) arrow(s, 4.55 + i * 4.18, sy + 1.0, 0.3);
});
importantBox(s, 'THE POINT', 'You leave this course with one deployed, observable, secured system you can put a link to on your resume, and defend line by line. Not ten notebooks nobody will open.', { y: 5.0, h: 1.25 });
s.addNotes('');

// ---- 31 ----
s = slide('How the practicals are taught', 'THE FAILURE FIRST METHOD');
body(s, 'I am not going to hand you working code and explain why it works. That produces students who can run my code and cannot write their own.', { y: 1.6, h: 0.75, size: 16.5 });
teachCards(s, [
  { tag: 'STEP 1', h: 'The naive version', b: 'We write the obvious solution together. It looks correct. We run it.', tint: PANEL, accent: MUTED },
  { tag: 'STEP 2', h: 'It breaks, live', b: 'It fails in front of you, in a specific way, for a specific reason. Nobody is protected from this.', tint: RED_T, accent: RED },
  { tag: 'STEP 3', h: 'We fix the actual cause', b: 'Not a workaround. The real reason. And then you remember it, because you watched it hurt.', tint: TEAL_T, accent: TEAL }
], { y: 2.55, h: 2.35, bsize: 13 });
recallBox(s, 'Every failure I show you is a real one from a real build. A tool that tried to do two jobs and broke on a compound instruction. A loop with no exit condition. A retrieval that answered confidently from the wrong paragraph.', { y: 5.2, h: 1.15 });
s.addNotes('');

// ---- 32 divider ----
s = divider('SECTION 05', 'Where this leads', 'The honest version, including the caveats.');
s.addNotes('');

// ---- 33 ----
s = slide('The roles this maps to');
teachCards(s, [
  { tag: 'CLOSEST FIT', h: 'AI Agent Developer', b: 'Builds and ships agent systems. The role this syllabus is literally benchmarked against.', tint: TEAL_T, accent: TEAL },
  { tag: 'ADJACENT', h: 'AI Engineer', b: 'Broader remit. Agents are one part of a larger applied AI surface.', tint: INDIGO_T, accent: INDIGO },
  { tag: 'ADJACENT', h: 'Automation Engineer', b: 'Enterprise workflow automation, increasingly with an agent layer on top.', tint: INDIGO_T, accent: INDIGO },
  { tag: 'LATER', h: 'Solutions Architect', b: 'Designs the system rather than writing it. Needs the governance half of this course badly.', tint: PANEL, accent: MUTED }
], { y: 2.05, h: 2.6, hsize: 16, bsize: 12.5 });
body(s, 'These are not aspirational titles I invented. They are the roles the current Microsoft certification tracks are explicitly written for.', { y: 4.95, h: 0.6, size: 15, color: MUTED });
s.addNotes('If you have placement data from your own students, add it here as a slide of its own. Real numbers from people they know beat any national average.');

// ---- 34 ----
s = slide('What an interviewer will actually test');
bullets(s, [
  'Can you explain why you chose an agent instead of a plain script for this problem?',
  'What stops your loop? Show me the termination condition.',
  'How do you know the answer it gave was grounded and not invented?',
  'What happens when the tool call fails halfway through?',
  'What permissions does this agent run with, and why those and not more?',
  'Show me a trace of one real request going through your system.'
], { y: 1.8, h: 3.3, size: 16 });
importantBox(s, 'NOTICE WHAT IS ABSENT', 'Not one of those questions is about prompt wording. Every one of them is about engineering judgement. That is the thing this course is actually trying to build in you.', { y: 5.3, h: 1.15 });
s.addNotes('Read these six aloud. Then tell them the practical viva questions will be drawn from exactly this list, which makes the list a study guide rather than a scare.');

// ---- 35 ----
s = slide('The durable skills and the perishable ones');
teachCards(s, [
  { tag: 'WILL OUTLAST THE TOOLS', h: 'Durable', b: 'The agent loop. Tool design. When not to use an agent. How to test something non deterministic. Least privilege. Grounding and citation. Failure modes.', tint: TEAL_T, accent: TEAL },
  { tag: 'WILL CHANGE UNDER YOU', h: 'Perishable', b: 'Exact SDK names. Import paths. Portal layouts. Which framework is fashionable. Product names, which Microsoft changes roughly once a year.', tint: PANEL, accent: MUTED }
], { y: 2.05, h: 2.6 });
importantBox(s, 'A REAL EXAMPLE, FROM THIS YEAR', 'Bot Framework SDK was the standard way to connect an agent to a chat channel. Its support ended in December 2025 and its repository is now archived. The skill of connecting an agent to a channel did not expire. The SDK did. Learn the first, expect to relearn the second.', { y: 4.95, h: 1.45 });
s.addNotes('This is the single most useful mindset slide in the deck. It also pre justifies the moments later in the semester when you tell them something in the syllabus has changed.');

// ---- 36 divider ----
s = divider('SECTION 06', 'Setup, and the money question', 'Because none of this matters if you cannot run it.');
s.addNotes('');

// ---- 37 ----
s = slide('Let us deal with the obvious problem first');
body(s, 'This is a cloud course. Cloud costs money. Most of you do not have a credit card, and I am not going to pretend that is not a real obstacle.', { y: 1.65, h: 0.85, size: 17 });
s.addShape(pres.ShapeType.roundRect, {
  x: 0.62, y: 2.75, w: 12.1, h: 1.35, fill: { color: TEAL_T },
  line: { color: 'FFFFFF', width: 0 }, rectRadius: 0.1
});
s.addText('Nobody in this room will be blocked from any practical for lack of money. Every single one runs on a free path, and the code is identical either way.', {
  x: 1.05, y: 2.75, w: 11.25, h: 1.35, fontFace: SERIF, fontSize: 20,
  color: INK, bold: true, margin: 0, valign: 'middle', lineSpacing: 28
});
body(s, 'That is a design decision, not a concession. It required writing every notebook a particular way, and understanding why is itself worth a few minutes.', { y: 4.4, h: 0.7, size: 16, color: MUTED });
s.addNotes('Say this early and clearly. In a class of this size some students will silently drop out of the practicals over exactly this worry.');

// ---- 38 ----
s = slide('The layman version', 'HOW WE MAKE THE CODE PROVIDER PROOF');
body(s, 'Think of the model as electricity and your code as an appliance.', { y: 1.6, h: 0.4, size: 17, bold: true });
body(s, 'Your mixer does not care whether the electricity came from a coal plant, a solar panel, or your neighbour\'s inverter. It cares about one thing: does the plug fit the socket.\n\nAlmost every model provider now offers the same socket shape. So we write every practical against that one socket, and change nothing but which plug is in the wall.', { y: 2.15, h: 1.8, size: 16.5 });
importantBox(s, 'THE TECHNICAL CORRELATE', 'That common socket is an OpenAI compatible API. Every notebook in this course has one PROVIDER constant at the top. Change that one line and the entire notebook runs somewhere else. No other cell changes.', { y: 4.3, h: 1.4 });
s.addNotes('');

// ---- 39 ----
s = slide('What that looks like in code');
const cb = codeBox(s, [
  { t: '# the only line you change all semester', c: '7E93A8' },
  { t: 'PROVIDER = "github"      # foundry | github | local', c: 'FFD479' },
  { t: '', c: 'D6E2EE' },
  { t: 'client = make_client(PROVIDER)', c: 'D6E2EE' },
  { t: '', c: 'D6E2EE' },
  { t: '# everything below is identical on every lane', c: '7E93A8' },
  { t: 'reply = client.complete(', c: 'D6E2EE' },
  { t: '    model=MODEL,', c: 'D6E2EE' },
  { t: '    messages=[...],', c: 'D6E2EE' },
  { t: '    tools=[get_delivery_records],', c: 'D6E2EE' },
  { t: ')', c: 'D6E2EE' }
], { x: 0.62, y: 1.9, w: 7.5, size: 13.5 });
const rbY = cb.y + 0.25 + cb.lh - 0.03;
redBox(s, cb.x + 0.15, rbY, cb.w - 0.35, cb.lh + 0.06);
s.addShape(pres.ShapeType.line, {
  x: 8.32, y: rbY + 0.19, w: 0.42, h: 0,
  line: { color: RED, width: 1.75, endArrowType: 'triangle' }
});
s.addText('change this,\nnothing else', {
  x: 8.78, y: rbY - 0.24, w: 3.4, h: 0.85, fontFace: SANS, fontSize: 13,
  color: RED, bold: true, margin: 0, valign: 'middle', lineSpacing: 18
});
s.addShape(pres.ShapeType.roundRect, {
  x: 8.45, y: 3.35, w: 4.27, h: cb.y + cb.h - 3.35, fill: { color: PANEL },
  line: { color: LINE, width: 1 }, rectRadius: 0.09
});
s.addText('Why this matters', {
  x: 8.75, y: 3.55, w: 3.7, h: 0.4, fontFace: SERIF, fontSize: 17, color: INK, bold: true, margin: 0
});
s.addText('I will demonstrate on the paid enterprise platform, because you should see the real thing.\n\nYou will run the exact same notebook on a free endpoint.\n\nNeither of us edits the code. Same file, different socket.', {
  x: 8.75, y: 4.05, w: 3.7, h: 1.85, fontFace: SANS, fontSize: 13,
  color: MUTED, margin: 0, lineSpacing: 18
});
s.addNotes('This is the one code slide in Lecture Zero and it earns its red box. Point at the highlighted line while you speak.');

// ---- 40 ----
s = slide('The four lanes');
const lanes = [
  ['LANE A', 'Microsoft Foundry', 'The real enterprise platform. I demonstrate on this. You watch. My account, my cost.', TEAL, TEAL_T],
  ['LANE B', 'GitHub Models', 'Free, for every one of you, and still Microsoft infrastructure. This is your default lane.', INDIGO, INDIGO_T],
  ['LANE C', 'Azure for Students', 'Optional. 100 USD of credit, no credit card, verified with your university email.', AMBER, AMBER_T],
  ['LANE D', 'Fully local', 'Ollama on your own laptop. Slow and weak. Free forever. The lane that never fails.', MUTED, PANEL]
];
lanes.forEach((l, i) => {
  rowItem(s, 1.85 + i * 1.05, l[0], l[1], l[2], l[3], l[4]);
});
recallBox(s, 'Lane B is the one to remember. You all already need a GitHub account for the course repository, so you already have the key.', { y: 6.15, h: 0.75 });
s.addNotes('');

// ---- 41 ----
s = slide('Lane B, in detail', 'YOUR DEFAULT LANE, AND THE MOST IMPORTANT SLIDE IN THIS SECTION');
bullets(s, [
  'Free API access to GPT class models, Llama, Mistral, DeepSeek and others, with a GitHub account.',
  'It runs on Microsoft infrastructure and speaks the OpenAI compatible protocol, so the SDK patterns match what we use on Foundry.',
  'No credit card. No Azure signup. No waiting on an approval from anybody.',
  'Endpoint: https://models.github.ai/inference'
], { y: 1.9, h: 2.2, size: 16 });
importantBox(s, 'THE LIMITATION, STATED HONESTLY', 'Requests are capped at roughly 8K tokens in and 4K out, and the rate limits are modest. That is comfortable for learning and wrong for production. Knowing exactly where a free tier stops being adequate is itself a professional skill, so we will measure it rather than guess.', { y: 4.4, h: 1.6 });
s.addNotes('If a student asks why we do not just use this for everything: the answer is the token cap and the rate limit under concurrent load. That is a real production constraint and a good five minute discussion.');

// ---- 42 ----
s = slide('Lane C, Azure for Students');
bullets(s, [
  '100 USD in Azure credits, valid for twelve months, renewable each year while you remain a student.',
  'No credit card needed. You verify with your institutional email address.',
  'You must be eighteen or older and a full time student at an accredited degree granting institution.',
  'Comes with a set of always free services alongside the credit.'
], { y: 1.85, h: 2.1, size: 16 });
importantBox(s, 'TWO THINGS TO KNOW BEFORE YOU ACTIVATE', 'When the 100 USD runs out the subscription is disabled rather than billed to you, which is protective, but it also means an idle resource you forgot to delete can quietly consume your whole year. The credit does not top up early. So deleting your deployed resources after every lab is a habit I will keep nagging you about.', { y: 4.25, h: 1.7 });
s.addNotes('Tell them to activate this at the start of the semester rather than the end, because the twelve month clock starts on activation and their project work is in the back half.');

// ---- 43 ----
s = slide('Before next session', 'YOUR SETUP CHECKLIST');
const chk = [
  'A GitHub account. You need it for the repository and for Lane B.',
  'Python 3.12 and VS Code installed, with the Python and Jupyter extensions.',
  'Git installed and configured with your name and email.',
  'Clone the course repository. The link is on the last slide.',
  'Run the setup verification script in the repo root. It checks all four lanes and prints exactly what is missing.',
  'Optional but recommended: activate Azure for Students now, not in October.'
];
chk.forEach((c, i) => {
  const y = 1.72 + i * 0.68;
  s.addShape(pres.ShapeType.roundRect, {
    x: 0.62, y, w: 0.42, h: 0.42, fill: { color: 'FFFFFF' },
    line: { color: TEAL, width: 1.5 }, rectRadius: 0.06
  });
  s.addText(c, {
    x: 1.2, y: y - 0.06, w: 11.4, h: 0.55, fontFace: SANS, fontSize: 15.5,
    color: INK, margin: 0, valign: 'middle'
  });
});
activityBox(s, 'IF SOMETHING BREAKS', 'Do not spend three hours on it alone. Post the exact error text in the course channel. Half the class will hit the same error and one thread solves it for everyone.', { y: 5.72, h: 1.05, size: 14.5 });
s.addNotes('');

// ---- 44 ----
s = slide('One naming warning, so you are not confused later');
teachCards(s, [
  { tag: 'YOU WILL SEE THIS NAME', h: 'Azure AI Foundry', b: 'In tutorials, in videos, in blog posts, and in a great deal of documentation written before 2026. Also in our own approved syllabus text.', tint: PANEL, accent: MUTED },
  { tag: 'THE CURRENT NAME', h: 'Microsoft Foundry', b: 'Renamed at Ignite in November 2025 and formalised in the January 2026 product terms. Same platform. Same resource type. Same keys.', tint: TEAL_T, accent: TEAL }
], { y: 2.0, h: 2.5 });
importantBox(s, 'AND ONE MORE, FOR CONTEXT', 'This is the second rename in twelve months. Azure AI Studio became Azure AI Foundry, then Azure AI Foundry became Microsoft Foundry. When you search for help, search both names. This is not a mistake in the syllabus, it is the pace of the field.', { y: 4.8, h: 1.5 });
s.addNotes('Small slide, disproportionate payoff. It stops a dozen confused questions across the semester and it reinforces the durable versus perishable idea from earlier.');

// ---- 45 divider ----
s = divider('SECTION 07', 'How this course runs', 'Sessions, marks, rules, and how to get help.');
s.addNotes('');

// ---- 46 ----
s = slide('The shape of a typical session');
const shape = [
  ['OPEN', 'Recall', 'Five minutes on what we did last time. Not a lecture, a few questions to you.', TEAL, TEAL_T],
  ['CORE', 'Concept', 'The layman frame first, then the technical mechanism, then a worked example.', INDIGO, INDIGO_T],
  ['CORE', 'Live build', 'We write code together. It breaks. We fix it. Your editor should be open.', INDIGO, INDIGO_T],
  ['CLOSE', 'Hold on to this', 'One idea from today, stated in a single sentence, that you will need again later.', AMBER, AMBER_T]
];
shape.forEach((r, i) => rowItem(s, 1.9 + i * 1.08, r[0], r[1], r[2], r[3], r[4]));
recallBox(s, 'Every session is written to stand on its own. If you miss one you will not be lost in the next, though you will have to catch up on the code.', { y: 6.25, h: 0.7 });
s.addNotes('');

// ---- 47 ----
s = slide('Assessment');
teachCards(s, [
  { tag: 'CONTINUOUS', h: 'CA', b: 'Assessed through the practicals and short in class checks. The practicals are the assessment, not homework attached to it.', tint: TEAL_T, accent: TEAL },
  { tag: 'MID TERM', h: 'MTE', b: 'Covers the first half of the course. Concept and judgement questions, not definition recall.', tint: INDIGO_T, accent: INDIGO },
  { tag: 'END TERM', h: 'ETE', b: 'Full syllabus, with weight on the design decisions behind a system rather than framework trivia.', tint: AMBER_T, accent: AMBER },
  { tag: 'PRACTICALS', h: 'File and viva', b: 'Ten practicals, submitted and defended. The viva questions come from the list you saw earlier.', tint: PANEL, accent: MUTED }
], { y: 2.05, h: 2.7, hsize: 17, bsize: 12.5 });
importantBox(s, 'THE ONE RULE THAT MATTERS', 'You may use AI assistance to write your code. You may not use it to replace your understanding. The viva is where that distinction becomes visible, and it becomes visible very quickly.', { y: 5.05, h: 1.3 });
s.addNotes('TEACHING NOTE (do not say): insert your actual CA count, MTE and ETE weightings and practical marks before delivering. The card structure holds whatever numbers your scheme uses.');

// ---- 48 ----
s = slide('Ground rules');
bullets(s, [
  'Ask the question. If you are confused, four other people are too, and one of them will thank you.',
  'Tell me when my code breaks on your machine. Environment differences are real and I want to know.',
  'Never commit an API key. We will cover this properly, but start the habit now.',
  'Delete your cloud resources after every lab. An idle deployment costs money while you sleep.',
  'Bring the laptop charged. Sessions with code are most of them.',
  'If you fall behind, say so early. Falling behind in Unit 3 is recoverable in week nine and painful in week thirteen.'
], { y: 1.85, h: 3.6, size: 16 });
recallBox(s, 'And one more. This field moves fast enough that I will occasionally be wrong or out of date. When you find that, tell me. Being corrected by a student is a good day, not a bad one.', { y: 5.6, h: 1.0 });
s.addNotes('');

// ---- 49 ----
s = slide('Where everything lives');
teachCards(s, [
  { tag: 'CODE', h: 'The repository', b: 'Every notebook, every practical, the setup script, and the requirements file. Cloned once, pulled before each session.', tint: TEAL_T, accent: TEAL },
  { tag: 'SLIDES', h: 'Decks and handouts', b: 'Each session ships a deck and a collapsed handout you can read without the slides.', tint: INDIGO_T, accent: INDIGO },
  { tag: 'HELP', h: 'The course channel', b: 'Post the exact error, not "it is not working". Screenshot the full traceback. Somebody will have hit it already.', tint: AMBER_T, accent: AMBER }
], { y: 2.05, h: 2.7 });
activityBox(s, 'RIGHT NOW, BEFORE YOU LEAVE', 'Take out your phone and note the repository link on the next slide. Do the clone tonight, not on the morning of the first practical.', { y: 5.05, h: 1.1 });
s.addNotes('');

// ---- 50 ----
s = slide('What you will be able to say in December');
body(s, 'Not "I did a course on AI agents." Anybody can say that.', { y: 1.7, h: 0.5, size: 17, color: MUTED });
s.addShape(pres.ShapeType.roundRect, {
  x: 0.62, y: 2.4, w: 12.1, h: 2.5, fill: { color: TEAL_T },
  line: { color: 'FFFFFF', width: 0 }, rectRadius: 0.12
});
s.addText('"I built a multi agent system. Here is the live link. It is instrumented, so here is a trace of a real request. It runs with least privilege, so here is what it is not allowed to touch. It caught a prompt injection during testing, and here is the fix I wrote for it."', {
  x: 1.15, y: 2.4, w: 11.05, h: 2.5, fontFace: SERIF, fontSize: 21,
  color: INK, bold: true, margin: 0, valign: 'middle', lineSpacing: 32
});
body(s, 'That sentence is the entire point of the next fifty hours. Everything in the syllabus exists to make it true for you.', { y: 5.3, h: 0.7, size: 17 });
s.addNotes('End here. Do not add a thank you slide. Move straight into the setup checklist and start helping people install things, because that is the highest value use of the remaining time.');

// ---- 51 ----
s = slide('Next session');
s.addShape(pres.ShapeType.roundRect, {
  x: 0.62, y: 1.8, w: 12.1, h: 1.5, fill: { color: INDIGO_T },
  line: { color: 'FFFFFF', width: 0 }, rectRadius: 0.1
});
s.addText('Unit 1, Lecture 1', {
  x: 1.05, y: 1.95, w: 11.2, h: 0.5, fontFace: SANS, fontSize: 13,
  color: INDIGO, bold: true, charSpacing: 1.4, margin: 0
});
s.addText('What an Agent Actually Is', {
  x: 1.05, y: 2.4, w: 11.2, h: 0.7, fontFace: SERIF, fontSize: 28,
  color: INK, bold: true, margin: 0
});
body(s, 'We take the loop you saw today apart properly. Where the boundary between a chatbot and an agent actually sits, why that boundary is blurrier than most people claim, and the four things a system needs before the word agent is honest.', { y: 3.7, h: 1.3, size: 16.5 });
activityBox(s, 'COME WITH', 'Your environment set up and the repository cloned. We start writing code in the second half of that session.', { y: 5.3, h: 1.0 });
s.addNotes('');

// ---- write ----
for (let i = 0; i < 0; i++) {} // no op

pres.writeFile({ fileName: '/home/claude/CSE476_Lecture_Zero.pptx' })
  .then(() => console.log('written'))
  .catch(e => { console.error(e); process.exit(1); });
