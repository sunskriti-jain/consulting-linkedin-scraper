const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  HeadingLevel, AlignmentType, LevelFormat, BorderStyle, WidthType,
  ShadingType, Header, Footer, PageNumber, ExternalHyperlink,
  TableOfContents,
} = require("docx");
const fs = require("fs");

const BLUE      = "1F4E8C";
const LIGHTBLUE = "D6E4F7";
const GREEN     = "1A6B3C";
const LIGHTGREEN= "DFF2E9";
const ORANGE    = "8B4000";
const LIGHTORANGE="FFF3E0";
const GRAY      = "444444";
const LIGHTGRAY = "F5F5F5";
const BORDER_GRAY = "CCCCCC";
const WHITE     = "FFFFFF";

const border = { style: BorderStyle.SINGLE, size: 1, color: BORDER_GRAY };
const borders = { top: border, bottom: border, left: border, right: border };
const noBorder = { style: BorderStyle.NONE, size: 0, color: WHITE };
const noBorders = { top: noBorder, bottom: noBorder, left: noBorder, right: noBorder };

function h1(text) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_1,
    spacing: { before: 360, after: 120 },
    children: [new TextRun({ text, bold: true, size: 32, color: BLUE, font: "Arial" })],
  });
}

function h2(text) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_2,
    spacing: { before: 240, after: 80 },
    children: [new TextRun({ text, bold: true, size: 26, color: BLUE, font: "Arial" })],
  });
}

function h3(text) {
  return new Paragraph({
    spacing: { before: 180, after: 60 },
    children: [new TextRun({ text, bold: true, size: 22, color: GRAY, font: "Arial" })],
  });
}

function body(text, opts = {}) {
  return new Paragraph({
    spacing: { before: 60, after: 60 },
    children: [new TextRun({ text, size: 22, font: "Arial", color: GRAY, ...opts })],
  });
}

function gap(pts = 120) {
  return new Paragraph({ spacing: { before: pts, after: 0 }, children: [new TextRun("")] });
}

function bullet(text, bold_prefix = null) {
  const runs = [];
  if (bold_prefix) {
    runs.push(new TextRun({ text: bold_prefix + " ", bold: true, size: 22, font: "Arial", color: GRAY }));
    runs.push(new TextRun({ text, size: 22, font: "Arial", color: GRAY }));
  } else {
    runs.push(new TextRun({ text, size: 22, font: "Arial", color: GRAY }));
  }
  return new Paragraph({
    numbering: { reference: "bullets", level: 0 },
    spacing: { before: 40, after: 40 },
    children: runs,
  });
}

function numbered(text, bold_prefix = null) {
  const runs = [];
  if (bold_prefix) {
    runs.push(new TextRun({ text: bold_prefix + " ", bold: true, size: 22, font: "Arial", color: GRAY }));
    runs.push(new TextRun({ text, size: 22, font: "Arial", color: GRAY }));
  } else {
    runs.push(new TextRun({ text, size: 22, font: "Arial", color: GRAY }));
  }
  return new Paragraph({
    numbering: { reference: "numbers", level: 0 },
    spacing: { before: 40, after: 40 },
    children: runs,
  });
}

function subnumbered(text, bold_prefix = null) {
  const runs = [];
  if (bold_prefix) {
    runs.push(new TextRun({ text: bold_prefix + " ", bold: true, size: 22, font: "Arial", color: GRAY }));
    runs.push(new TextRun({ text, size: 22, font: "Arial", color: GRAY }));
  } else {
    runs.push(new TextRun({ text, size: 22, font: "Arial", color: GRAY }));
  }
  return new Paragraph({
    numbering: { reference: "subnumbers", level: 0 },
    spacing: { before: 30, after: 30 },
    children: runs,
  });
}

function codeBlock(lines) {
  const rows = Array.isArray(lines) ? lines : [lines];
  return new Table({
    width: { size: 9360, type: WidthType.DXA },
    columnWidths: [9360],
    rows: [new TableRow({
      children: [new TableCell({
        borders,
        width: { size: 9360, type: WidthType.DXA },
        shading: { fill: "1E1E1E", type: ShadingType.CLEAR },
        margins: { top: 120, bottom: 120, left: 200, right: 200 },
        children: rows.map(line => new Paragraph({
          spacing: { before: 20, after: 20 },
          children: [new TextRun({ text: line, font: "Courier New", size: 20, color: "A8FF60" })],
        })),
      })],
    })],
  });
}

function callout(text, color = LIGHTBLUE, borderColor = BLUE) {
  return new Table({
    width: { size: 9360, type: WidthType.DXA },
    columnWidths: [9360],
    rows: [new TableRow({
      children: [new TableCell({
        borders: {
          top: { style: BorderStyle.NONE },
          right: { style: BorderStyle.NONE },
          bottom: { style: BorderStyle.NONE },
          left: { style: BorderStyle.THICK, size: 24, color: borderColor },
        },
        width: { size: 9360, type: WidthType.DXA },
        shading: { fill: color, type: ShadingType.CLEAR },
        margins: { top: 100, bottom: 100, left: 200, right: 200 },
        children: [new Paragraph({
          children: [new TextRun({ text, size: 22, font: "Arial", color: GRAY })],
        })],
      })],
    })],
  });
}

function warningCallout(text) {
  return new Table({
    width: { size: 9360, type: WidthType.DXA },
    columnWidths: [9360],
    rows: [new TableRow({
      children: [new TableCell({
        borders: {
          top: { style: BorderStyle.NONE },
          right: { style: BorderStyle.NONE },
          bottom: { style: BorderStyle.NONE },
          left: { style: BorderStyle.THICK, size: 24, color: "CC0000" },
        },
        width: { size: 9360, type: WidthType.DXA },
        shading: { fill: "FDE8E8", type: ShadingType.CLEAR },
        margins: { top: 100, bottom: 100, left: 200, right: 200 },
        children: [new Paragraph({
          children: [new TextRun({ text, size: 22, font: "Arial", color: "8B0000" })],
        })],
      })],
    })],
  });
}

function sectionHeader(stepNum, title) {
  return new Table({
    width: { size: 9360, type: WidthType.DXA },
    columnWidths: [9360],
    rows: [new TableRow({
      children: [new TableCell({
        borders: noBorders,
        width: { size: 9360, type: WidthType.DXA },
        shading: { fill: BLUE, type: ShadingType.CLEAR },
        margins: { top: 120, bottom: 120, left: 240, right: 240 },
        children: [new Paragraph({
          children: [
            new TextRun({ text: stepNum ? `Step ${stepNum}  ` : "", size: 24, font: "Arial", color: "AACCFF", bold: true }),
            new TextRun({ text: title, size: 28, font: "Arial", color: WHITE, bold: true }),
          ],
        })],
      })],
    })],
  });
}

function troubleshootRow(error, fix) {
  return new TableRow({
    children: [
      new TableCell({
        borders,
        width: { size: 3200, type: WidthType.DXA },
        shading: { fill: LIGHTORANGE, type: ShadingType.CLEAR },
        margins: { top: 80, bottom: 80, left: 120, right: 120 },
        children: [new Paragraph({
          children: [new TextRun({ text: error, size: 20, font: "Courier New", color: "8B0000" })],
        })],
      }),
      new TableCell({
        borders,
        width: { size: 6160, type: WidthType.DXA },
        margins: { top: 80, bottom: 80, left: 120, right: 120 },
        children: [new Paragraph({
          children: [new TextRun({ text: fix, size: 21, font: "Arial", color: GRAY })],
        })],
      }),
    ],
  });
}

// ── Document ─────────────────────────────────────────────────────────────────
const doc = new Document({
  numbering: {
    config: [
      {
        reference: "bullets",
        levels: [{ level: 0, format: LevelFormat.BULLET, text: "•",
          alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 540, hanging: 360 } } } }],
      },
      {
        reference: "numbers",
        levels: [{ level: 0, format: LevelFormat.DECIMAL, text: "%1.",
          alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 540, hanging: 360 } } } }],
      },
      {
        reference: "subnumbers",
        levels: [{ level: 0, format: LevelFormat.LOWER_LETTER, text: "%1.",
          alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 900, hanging: 360 } } } }],
      },
    ],
  },
  styles: {
    default: { document: { run: { font: "Arial", size: 22, color: GRAY } } },
    paragraphStyles: [
      { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 32, bold: true, font: "Arial", color: BLUE },
        paragraph: { spacing: { before: 360, after: 120 }, outlineLevel: 0 } },
      { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 26, bold: true, font: "Arial", color: BLUE },
        paragraph: { spacing: { before: 240, after: 80 }, outlineLevel: 1 } },
    ],
  },
  sections: [{
    properties: {
      page: {
        size: { width: 12240, height: 15840 },
        margin: { top: 1080, right: 1080, bottom: 1080, left: 1080 },
      },
    },
    headers: {
      default: new Header({
        children: [new Paragraph({
          border: { bottom: { style: BorderStyle.SINGLE, size: 4, color: BLUE, space: 1 } },
          children: [
            new TextRun({ text: "Outreach Engine  ", size: 18, font: "Arial", color: BLUE, bold: true }),
            new TextRun({ text: "Setup Guide for New Users", size: 18, font: "Arial", color: GRAY }),
          ],
        })],
      }),
    },
    footers: {
      default: new Footer({
        children: [new Paragraph({
          border: { top: { style: BorderStyle.SINGLE, size: 4, color: BORDER_GRAY, space: 1 } },
          alignment: AlignmentType.RIGHT,
          children: [
            new TextRun({ text: "Page ", size: 18, font: "Arial", color: GRAY }),
            new TextRun({ children: [PageNumber.CURRENT], size: 18, font: "Arial", color: GRAY }),
            new TextRun({ text: " of ", size: 18, font: "Arial", color: GRAY }),
            new TextRun({ children: [PageNumber.TOTAL_PAGES], size: 18, font: "Arial", color: GRAY }),
          ],
        })],
      }),
    },
    children: [

      // ── Title page ──────────────────────────────────────────────────────
      gap(240),
      new Paragraph({
        alignment: AlignmentType.CENTER,
        spacing: { before: 0, after: 80 },
        children: [new TextRun({ text: "Outreach Engine", size: 64, bold: true, font: "Arial", color: BLUE })],
      }),
      new Paragraph({
        alignment: AlignmentType.CENTER,
        spacing: { before: 0, after: 40 },
        children: [new TextRun({ text: "Setup Guide for New Users", size: 36, font: "Arial", color: GRAY })],
      }),
      new Paragraph({
        alignment: AlignmentType.CENTER,
        spacing: { before: 0, after: 400 },
        children: [new TextRun({ text: "A step-by-step guide to get up and running in 30-45 minutes", size: 22, font: "Arial", color: "888888", italics: true })],
      }),

      // ── Overview callout ────────────────────────────────────────────────
      new Table({
        width: { size: 9360, type: WidthType.DXA },
        columnWidths: [9360],
        rows: [new TableRow({ children: [new TableCell({
          borders: noBorders,
          width: { size: 9360, type: WidthType.DXA },
          shading: { fill: LIGHTBLUE, type: ShadingType.CLEAR },
          margins: { top: 200, bottom: 200, left: 280, right: 280 },
          children: [
            new Paragraph({ spacing: { before: 0, after: 80 }, children: [new TextRun({ text: "What this guide will do", size: 26, bold: true, font: "Arial", color: BLUE })] }),
            new Paragraph({ spacing: { before: 0, after: 40 }, children: [new TextRun({ text: "This guide walks you through setting up the Outreach Engine on your computer — a system that sends personalized cold outreach emails using AI. You don't need any prior coding experience.", size: 22, font: "Arial", color: GRAY })] }),
            new Paragraph({ spacing: { before: 40, after: 0 }, children: [new TextRun({ text: "By the end you will be able to:", size: 22, font: "Arial", color: GRAY })] }),
          ],
        })] })],
      }),
      new Table({
        width: { size: 9360, type: WidthType.DXA },
        columnWidths: [9360],
        rows: [new TableRow({ children: [new TableCell({
          borders: noBorders,
          width: { size: 9360, type: WidthType.DXA },
          shading: { fill: LIGHTBLUE, type: ShadingType.CLEAR },
          margins: { top: 0, bottom: 200, left: 280, right: 280 },
          children: [
            bullet("Run an outreach campaign to a list of companies with one command"),
            bullet("Send AI-personalized emails from your Gmail account"),
            bullet("Track replies and bounces automatically"),
            bullet("Pull the latest campaigns with git pull"),
          ],
        })] })],
      }),

      gap(300),

      // ── Section 1: What You'll Need ──────────────────────────────────────
      sectionHeader(null, "Before You Start — What You'll Need"),
      gap(120),
      body("Make sure you have each of the following ready before starting. Don't worry if you haven't signed up for the API keys yet — we'll guide you through it in Step 5."),
      gap(80),

      new Table({
        width: { size: 9360, type: WidthType.DXA },
        columnWidths: [2400, 6960],
        rows: [
          new TableRow({ children: [
            new TableCell({ borders, width: { size: 2400, type: WidthType.DXA }, shading: { fill: BLUE, type: ShadingType.CLEAR }, margins: { top: 100, bottom: 100, left: 160, right: 160 },
              children: [new Paragraph({ children: [new TextRun({ text: "Requirement", size: 22, bold: true, font: "Arial", color: WHITE })] })] }),
            new TableCell({ borders, width: { size: 6960, type: WidthType.DXA }, shading: { fill: BLUE, type: ShadingType.CLEAR }, margins: { top: 100, bottom: 100, left: 160, right: 160 },
              children: [new Paragraph({ children: [new TextRun({ text: "Details", size: 22, bold: true, font: "Arial", color: WHITE })] })] }),
          ]}),
          ...([
            ["Computer", "Windows 10 or 11, or a Mac (macOS 12+). At least 4 GB of RAM and 2 GB of free disk space."],
            ["Gmail account", "The Gmail address you want to send outreach emails from. This will be connected to the system."],
            ["Anthropic API key", "Powers the AI that personalizes each email. Sign up at console.anthropic.com. You'll need to add $5-20 in credits."],
            ["Perplexity API key", "A cheaper backup AI. Sign up at perplexity.ai/settings/api. The system falls back to this automatically if Anthropic runs out."],
            ["30-45 minutes", "Set aside uninterrupted time for the first setup. Once done, running future campaigns takes under 2 minutes."],
          ].map(([req, detail], i) => new TableRow({ children: [
            new TableCell({ borders, width: { size: 2400, type: WidthType.DXA }, shading: { fill: i % 2 === 0 ? LIGHTGRAY : WHITE, type: ShadingType.CLEAR }, margins: { top: 80, bottom: 80, left: 160, right: 160 },
              children: [new Paragraph({ children: [new TextRun({ text: req, size: 22, bold: true, font: "Arial", color: BLUE })] })] }),
            new TableCell({ borders, width: { size: 6960, type: WidthType.DXA }, shading: { fill: i % 2 === 0 ? LIGHTGRAY : WHITE, type: ShadingType.CLEAR }, margins: { top: 80, bottom: 80, left: 160, right: 160 },
              children: [new Paragraph({ children: [new TextRun({ text: detail, size: 22, font: "Arial", color: GRAY })] })] }),
          ]}))),
        ],
      }),

      gap(300),

      // ── Step 1: Install Python ───────────────────────────────────────────
      sectionHeader(1, "Install Python"),
      gap(100),
      body("Python is the programming language the Outreach Engine runs on. Think of it as the engine's fuel — nothing works without it."),
      gap(80),
      numbered("Go to python.org/downloads in your browser.", "Website:"),
      numbered("Click the big yellow download button for Python 3.11. This is the most stable version."),
      numbered("Run the downloaded installer file."),
      gap(60),
      warningCallout("IMPORTANT: On the very first screen of the installer, check the box that says \"Add Python to PATH\" before clicking Install. If you skip this, nothing will work and you will need to reinstall."),
      gap(60),
      numbered("Click Install Now and wait for it to finish."),
      numbered("Verify Python installed correctly:", "Verify:"),
      gap(60),
      body("Open Command Prompt: press the Windows key + R, type cmd, and press Enter. Then type:"),
      gap(40),
      codeBlock("python --version"),
      gap(60),
      callout("You should see something like:  Python 3.11.9\n\nIf you see \"python is not recognized as an internal or external command\" — go back and reinstall Python, making sure to check the Add Python to PATH box.", LIGHTGREEN, GREEN),

      gap(300),

      // ── Step 2: Install Git ──────────────────────────────────────────────
      sectionHeader(2, "Install Git"),
      gap(100),
      body("Git is what lets you download the Outreach Engine code from the internet and keep it up to date with one command."),
      gap(80),
      numbered("Go to git-scm.com/downloads in your browser."),
      numbered("Click the download for your operating system (Windows or Mac)."),
      numbered("Run the installer. Click Next through all the screens — the defaults are fine."),
      numbered("Verify Git installed:"),
      gap(60),
      codeBlock("git --version"),
      gap(60),
      callout("You should see something like:  git version 2.44.0\n\nIf you don't, close Command Prompt and reopen it, then try again.", LIGHTGREEN, GREEN),

      gap(300),

      // ── Step 3: Download the Code ────────────────────────────────────────
      sectionHeader(3, "Download the Outreach Engine"),
      gap(100),
      body("Now you'll download all the code to your computer. This is called \"cloning\" the repository."),
      gap(80),
      numbered("Open Command Prompt (Win + R, type cmd, Enter)."),
      numbered("Copy and paste the following command exactly and press Enter:"),
      gap(60),
      codeBlock("git clone https://github.com/eleyn-xiong/linkedin-scraper.git"),
      gap(60),
      body("This will download all the files into a new folder called linkedin-scraper. You'll see some download progress text."),
      gap(80),
      numbered("Navigate into the folder by typing:"),
      gap(60),
      codeBlock("cd linkedin-scraper"),
      gap(60),
      callout("You are now inside the project folder. Every command from here on should be run from this folder. You can confirm you're in the right place if your command prompt shows something ending in ...\\linkedin-scraper>", LIGHTBLUE, BLUE),

      gap(300),

      // ── Step 4: Python Environment ───────────────────────────────────────
      sectionHeader(4, "Set Up the Python Environment"),
      gap(100),
      body("A virtual environment (\"venv\") keeps all the required libraries for this project separate from anything else on your computer. This prevents conflicts."),
      gap(80),
      body("Run each of the following commands one at a time, pressing Enter after each:"),
      gap(80),
      h3("Create the environment:"),
      codeBlock("python -m venv venv"),
      gap(100),
      h3("Activate it (Windows):"),
      codeBlock("venv\\Scripts\\activate"),
      gap(60),
      h3("Activate it (Mac):"),
      codeBlock("source venv/bin/activate"),
      gap(60),
      callout("After activating, you should see (venv) appear at the very start of your command prompt line, like this:\n\n(venv) C:\\Users\\YourName\\linkedin-scraper>\n\nThis means the environment is active. You need to activate it every time you open a new Command Prompt window.", LIGHTBLUE, BLUE),
      gap(100),
      h3("Install all required libraries:"),
      codeBlock("pip install -r requirements.txt"),
      gap(60),
      body("This will take 2-3 minutes and show a lot of text scrolling by. That's normal — it's downloading everything needed. Wait for it to finish and return to the prompt."),

      gap(300),

      // ── Step 5: .env file ────────────────────────────────────────────────
      sectionHeader(5, "Create Your Settings File (.env)"),
      gap(100),
      body("The .env file is where you store your private API keys and your name/email. It stays on your computer and is never uploaded anywhere."),
      gap(80),
      h3("Option A — Create the file in File Explorer:"),
      numbered("Open File Explorer and navigate to the linkedin-scraper folder."),
      numbered("Right-click in an empty area > New > Text Document."),
      numbered("Name it exactly:  .env  (just a dot, then env — no .txt at the end)."),
      numbered("Windows may warn \"If you change a file name extension, the file might become unusable\" — click Yes."),
      numbered("Right-click the .env file > Open with > Notepad."),
      gap(80),
      h3("Option B — Create it from Command Prompt:"),
      codeBlock("copy NUL .env"),
      gap(60),
      body("Then open it: right-click .env in File Explorer > Open with > Notepad."),
      gap(100),
      h3("Paste the following into Notepad (fill in your real values):"),
      gap(60),
      codeBlock([
        "ANTHROPIC_API_KEY=your_anthropic_key_here",
        "PERPLEXITY_API_KEY=your_perplexity_key_here",
        "SENDER_NAME=Your Full Name",
        "SENDER_EMAIL=youremail@gmail.com",
        "SENDER_TITLE=Your Title (e.g. Director of Partnerships)",
        "SENDER_COMPANY=Your Organization Name",
      ]),
      gap(100),
      h3("Where to get your API keys:"),
      gap(60),
      new Table({
        width: { size: 9360, type: WidthType.DXA },
        columnWidths: [2200, 7160],
        rows: [
          new TableRow({ children: [
            new TableCell({ borders, width: { size: 2200, type: WidthType.DXA }, shading: { fill: BLUE, type: ShadingType.CLEAR }, margins: { top: 80, bottom: 80, left: 120, right: 120 },
              children: [new Paragraph({ children: [new TextRun({ text: "Key", bold: true, size: 22, font: "Arial", color: WHITE })] })] }),
            new TableCell({ borders, width: { size: 7160, type: WidthType.DXA }, shading: { fill: BLUE, type: ShadingType.CLEAR }, margins: { top: 80, bottom: 80, left: 120, right: 120 },
              children: [new Paragraph({ children: [new TextRun({ text: "How to get it", bold: true, size: 22, font: "Arial", color: WHITE })] })] }),
          ]}),
          new TableRow({ children: [
            new TableCell({ borders, width: { size: 2200, type: WidthType.DXA }, shading: { fill: LIGHTGRAY, type: ShadingType.CLEAR }, margins: { top: 80, bottom: 80, left: 120, right: 120 },
              children: [new Paragraph({ children: [new TextRun({ text: "Anthropic", bold: true, size: 22, font: "Arial", color: BLUE })] })] }),
            new TableCell({ borders, width: { size: 7160, type: WidthType.DXA }, shading: { fill: LIGHTGRAY, type: ShadingType.CLEAR }, margins: { top: 80, bottom: 80, left: 120, right: 120 },
              children: [new Paragraph({ children: [new TextRun({ text: "Go to console.anthropic.com > sign in > API Keys (left sidebar) > Create Key. Copy the key — it starts with sk-ant-... You'll also need to add billing credits (Settings > Billing > Add $5-20).", size: 22, font: "Arial", color: GRAY })] })] }),
          ]}),
          new TableRow({ children: [
            new TableCell({ borders, width: { size: 2200, type: WidthType.DXA }, margins: { top: 80, bottom: 80, left: 120, right: 120 },
              children: [new Paragraph({ children: [new TextRun({ text: "Perplexity", bold: true, size: 22, font: "Arial", color: BLUE })] })] }),
            new TableCell({ borders, width: { size: 7160, type: WidthType.DXA }, margins: { top: 80, bottom: 80, left: 120, right: 120 },
              children: [new Paragraph({ children: [new TextRun({ text: "Go to perplexity.ai/settings/api > sign in > Generate. Copy the key — it starts with pplx-... Add $5 in credits under Billing.", size: 22, font: "Arial", color: GRAY })] })] }),
          ]}),
        ],
      }),
      gap(80),
      body("Save the file in Notepad with Ctrl+S (or File > Save)."),

      gap(300),

      // ── Step 6: Gmail Setup ──────────────────────────────────────────────
      sectionHeader(6, "Connect Your Gmail Account"),
      gap(100),
      body("This is the most involved step, but you only have to do it once. It connects the system to your Gmail so it can send emails on your behalf."),
      gap(60),
      callout("You will need to be signed into the Gmail account you want to send from in your browser during this step.", LIGHTBLUE, BLUE),
      gap(120),

      h2("Part A — Create a Google Cloud Project"),
      gap(60),
      numbered("Go to console.cloud.google.com in your browser. Sign in with the Gmail you want to send from."),
      numbered("At the top of the page, click \"Select a project\" (it might say \"My First Project\" or similar)."),
      numbered("In the popup, click \"New Project\" in the top right."),
      numbered("Name it Outreach Engine, leave the location as-is, and click Create."),
      numbered("Wait a few seconds, then click \"Select a project\" again and select Outreach Engine."),
      gap(120),

      h2("Part B — Enable the Gmail API"),
      gap(60),
      numbered("In the search bar at the very top of the page, type: Gmail API"),
      numbered("Click on \"Gmail API\" in the results."),
      numbered("Click the blue Enable button. Wait for the page to reload."),
      gap(120),

      h2("Part C — Create OAuth Credentials"),
      gap(60),
      numbered("In the left sidebar, click \"APIs & Services\" > \"Credentials\"."),
      numbered("At the top, click \"+ Create Credentials\" > \"OAuth client ID\"."),
      numbered("If it asks you to configure the consent screen first:"),
      subnumbered("Click \"Configure Consent Screen\"."),
      subnumbered("Choose External, click Create."),
      subnumbered("Fill in App name: Outreach Engine, and add your email to the support email field."),
      subnumbered("Click Save and Continue through the remaining screens."),
      subnumbered("On the Test Users screen, click + Add Users, enter your Gmail address, and click Add."),
      subnumbered("Click Save and Continue, then Back to Dashboard."),
      subnumbered("Go back to Credentials in the left sidebar."),
      gap(80),
      numbered("Click \"+ Create Credentials\" > \"OAuth client ID\" again."),
      numbered("Set Application type to Desktop app."),
      numbered("Set Name to Outreach Engine, click Create."),
      numbered("In the popup, click Download JSON. Save the file somewhere you can find it."),
      numbered("Move that downloaded file into your linkedin-scraper folder."),
      numbered("Rename it to exactly: gmail_credentials.json"),
      gap(60),
      callout("The file must be named exactly gmail_credentials.json (all lowercase, no spaces) and be inside the linkedin-scraper folder. Double-check this before the next step.", LIGHTORANGE, ORANGE),
      gap(120),

      h2("Part D — Authorize Your Gmail Account"),
      gap(60),
      body("In Command Prompt (with venv active and inside the linkedin-scraper folder), run:"),
      gap(60),
      codeBlock("python gmail_client.py auth default"),
      gap(60),
      numbered("A browser window will open automatically."),
      numbered("Sign in with the Gmail you want to send outreach from."),
      numbered("You may see a warning: \"Google hasn't verified this app\" — this is expected. Click Advanced, then click \"Go to Outreach Engine (unsafe)\" and proceed."),
      numbered("On the permissions screen, click Allow."),
      numbered("Switch back to Command Prompt — you should see:"),
      gap(60),
      callout("[OK] Token saved to gmail_token.json", LIGHTGREEN, GREEN),

      gap(300),

      // ── Step 7: Test ─────────────────────────────────────────────────────
      sectionHeader(7, "Test That Everything Works"),
      gap(100),
      body("Before running a real campaign, let's make sure all the pieces are connected."),
      gap(80),

      h2("Send a test email to yourself:"),
      gap(60),
      codeBlock("python gmail_client.py test default youremail@gmail.com"),
      gap(60),
      body("(Replace youremail@gmail.com with your actual email address.)"),
      gap(60),
      callout("Check your inbox. A test email should arrive within 30 seconds with the subject \"OutreachEngine test email\". If it arrives, Gmail is fully connected.", LIGHTGREEN, GREEN),
      gap(100),

      h2("Initialize the database:"),
      gap(60),
      codeBlock("python -c \"from db import init_db; init_db(); print('Database ready!')\""),
      gap(60),
      callout("You should see:  Database ready!\n\nThis creates the database file that stores all your contacts, campaigns, and email records.", LIGHTGREEN, GREEN),

      gap(300),

      // ── Step 8: Run a Campaign ───────────────────────────────────────────
      sectionHeader(8, "Run Your First Campaign"),
      gap(100),
      body("You're all set. When you receive a campaign script (a file ending in .py) from your administrator, place it in your linkedin-scraper folder and run it with the command below."),
      gap(80),
      codeBlock([
        "python -u run_your_campaign_name.py > logs\\my_campaign.log 2>&1",
      ]),
      gap(60),
      body("Replace run_your_campaign_name.py with the actual filename given to you (for example: run_bbs_expansion_batch2.py)."),
      gap(80),
      callout("The -u flag is important — it prevents the output from buffering so you can watch progress in real time.", LIGHTBLUE, BLUE),
      gap(100),

      h2("Watch the campaign run live:"),
      body("Open a second Command Prompt window, activate your venv, navigate to the folder, and type:"),
      gap(60),
      codeBlock("type logs\\my_campaign.log"),
      gap(60),
      body("You'll see each email being sent as it goes, along with any errors."),
      gap(100),

      h2("What success looks like:"),
      gap(60),
      codeBlock([
        "[1] Company A - John Smith <john.smith@companya.com>",
        "[2] Company A - Sarah Lee <sarah.lee@companya.com>",
        "...",
        "[ALL DONE] Campaign 'My Campaign - June 2026'",
        "  Sent: 150 | Failed: 0",
      ]),

      gap(300),

      // ── Step 9: Troubleshooting ──────────────────────────────────────────
      sectionHeader(null, "Troubleshooting Common Issues"),
      gap(100),
      body("If something goes wrong, find the error message below and follow the fix:"),
      gap(80),

      new Table({
        width: { size: 9360, type: WidthType.DXA },
        columnWidths: [3200, 6160],
        rows: [
          new TableRow({ children: [
            new TableCell({ borders, width: { size: 3200, type: WidthType.DXA }, shading: { fill: BLUE, type: ShadingType.CLEAR }, margins: { top: 80, bottom: 80, left: 120, right: 120 },
              children: [new Paragraph({ children: [new TextRun({ text: "Error", bold: true, size: 22, font: "Arial", color: WHITE })] })] }),
            new TableCell({ borders, width: { size: 6160, type: WidthType.DXA }, shading: { fill: BLUE, type: ShadingType.CLEAR }, margins: { top: 80, bottom: 80, left: 120, right: 120 },
              children: [new Paragraph({ children: [new TextRun({ text: "Fix", bold: true, size: 22, font: "Arial", color: WHITE })] })] }),
          ]}),
          troubleshootRow("python is not recognized", "Python wasn't added to PATH. Uninstall Python, reinstall it, and check the 'Add Python to PATH' box on the first screen."),
          troubleshootRow("No module named 'X'", "Your virtual environment isn't active. Run:  venv\\Scripts\\activate  (Windows) or  source venv/bin/activate  (Mac), then try again."),
          troubleshootRow("gmail_credentials.json not found", "Make sure the credentials file is in the linkedin-scraper folder and named exactly gmail_credentials.json (lowercase, no spaces)."),
          troubleshootRow("App not verified", "Expected warning. Click 'Advanced' then 'Go to Outreach Engine (unsafe)', then Allow."),
          troubleshootRow("credits exhausted in logs", "Your Anthropic API key ran out of credits. Add more at console.anthropic.com > Billing. The system will auto-use Perplexity as a backup if PERPLEXITY_API_KEY is set in .env."),
          troubleshootRow("Log file is empty", "Add -u to the python command:  python -u run_campaign.py"),
          troubleshootRow("ConnectionResetError 10054", "A network blip interrupted Gmail sending. Run the send-only resume script (ask your admin for it) — it picks up where it left off."),
          troubleshootRow("DB locked", "Another campaign is already running. Wait for it to finish, or check for leftover Python processes in Task Manager and end them."),
        ],
      }),

      gap(300),

      // ── Step 9: Updates ──────────────────────────────────────────────────
      sectionHeader(null, "Getting Updates"),
      gap(100),
      body("When new campaign scripts or features are added to the system, pull them down with one command:"),
      gap(80),
      codeBlock("git pull origin main"),
      gap(60),
      body("Run this from inside the linkedin-scraper folder with your venv active. It downloads any new files added since your last update."),
      gap(80),
      callout("You will NOT lose any of your data, contacts, or campaign history when you update. The database (outreach.db) and your .env file stay on your computer and are never touched by git pull.", LIGHTGREEN, GREEN),

      gap(200),

      // ── Final notes ───────────────────────────────────────────────────────
      new Paragraph({
        border: { top: { style: BorderStyle.SINGLE, size: 4, color: BORDER_GRAY, space: 4 } },
        spacing: { before: 200, after: 80 },
        children: [new TextRun({ text: "You're all set!", bold: true, size: 24, font: "Arial", color: BLUE })],
      }),
      body("If you run into anything not covered here, reach out to your administrator with the exact error message from your log file."),
    ],
  }],
});

Packer.toBuffer(doc).then(buffer => {
  fs.writeFileSync("SETUP_GUIDE.docx", buffer);
  console.log("[OK] SETUP_GUIDE.docx written successfully.");
});
