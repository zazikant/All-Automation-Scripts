# Mailster Vision Pipeline

This pipeline automatically converts skeleton layout images into pixel-perfect Mailster HTML templates using a Human-In-The-Loop AI workflow.

---

## 🚀 Getting Started (Agent Initialization)
To start this project as the acting agent:
1. **Environment:** Ensure Python 3.x is installed with `opencv-python` and `numpy`.
2. **Analysis:** Run `python worker.py --analyze --input Skeleton.png` to generate the geometric blueprint of the layout.
3. **Execution:** Run `python runner.py` to begin the interactive generation loop.

---

Here is exactly how the overarching pipeline will behave from start to finish when you decide to feed it a brand new skeleton image:

### Phase 1: The Vision Engine (`worker.py`)
* **Image Input:** You kick off the script pointing it to a new skeleton layout (e.g., `new_skeleton.png`).
* **OpenCV Parsing:** `worker.py` consumes the image and uses pixel thresholding to aggressively scan for horizontal section borders.
* **Element Extraction:** Within each detected section, it runs color-space detection to locate grey bounding boxes (images), black bounding boxes (text), and yellow boxes (buttons). It measures their exact widths and sizes based on pixel coordinates.
* **JSON Blueprint Export:** It compiles all of this geometric data and exports it as a JSON payload, mapping out exactly how many sections exist and what proportions/elements belong in each.

### Phase 2: The Action Orchestrator and HITL (`runner.py`)
* **Prompt Generation:** `runner.py` wraps the JSON data from `worker.py` and the strict Mailster instruction rules from `CLAUDE.md` into highly specified prompts for your AI agent (MiniMax 2.5).
* **Section-by-Section Loop:** Instead of generating the entire email at once (which is highly prone to hallucination), `runner.py` initiates a loop. It tells the active MiniMax agent, *"Look at Section 1 of the image. Here are the dimensions OpenCV found. Print the strict layout HTML for this specific section using dummy.mailster.co placeholders."*
* **Human-In-The-Loop Verification:**
  * MiniMax outputs the HTML chunk back to the CLI and signifies it is done using the `EOF` token.
  * The script pauses and presents the slice to you (the human).
  * You press **[Y]** to approve it, **[R]** to reject it and force the agent to try again if it made a structural mistake, or **[S]** to skip it.
  * *This ensures code quality stays relentlessly high and perfectly tuned before moving forward.*

### Phase 3: GEM Engserv Boilerplate Assembly
* **Packaging:** Once you have approved the slice of HTML for every section in the skeleton image, `runner.py` takes all the approved chunks and groups them together.
* **Final Wrapper Injection:** It injects those raw layout chunks securely between the `<modules>` parameters of the heavily refined GEM Engserv `600px` boilerplate template that we just perfected.
* **Output:** It writes out `mailster_template.html` locally into your folder. You now have a complete, responsive, pixel-perfect digital twin of your skeleton mockup that is guaranteed to be 100% compliant with Mailster!

---

## 🤖 AI Agent Operating Protocol

When you are acting as the agent in the generation loop, follow this refined **Flow of Thoughts**:

### 1. The 0.25x Scaling Rule
The source skeleton is **2400px wide**, but the final template is **600px wide**.
- **Calculation:** Multiply every width, height, and coordinate from the `worker.py` output by **0.25**.
- **Example:** A 1000px wide box in the skeleton becomes a `250px` wide column in HTML.

### 2. The 24/12/8 Spacing Hierarchy
To maintain the premium aesthetic, strictly follow these spacers:
- **Module separator:** Always use `height="24"` between major blocks.
- **Section separator:** Use `height="12"` for internal section headers.
- **Element separator:** Use `height="8"` between images, title, description, and buttons.

### 3. Image Placeholder Standards
- **Format:** Always use `https://dummy.mailster.co/WIDTHxHEIGHT.jpg`.
- **Attributes:** All `<img>` tags must have `width="..."`, `height="auto"`, and `editable=""`.

### 4. The "Zero Margin" CSS Reset
- **Critical Requirement:** Browser default margins add unwanted padding.
- **Rule:** Always ensure the CSS block includes:
  ```css
  h1, h2, h3, h4, h5, h6, p, li { 
      margin: 0 !important; 
  }
  ```
- **Control:** Vertical spacing must be managed EXCLUSIVELY via table cell heights, never via text margins.

### 5. HITL Iteration Strategy
- Generate one Mailster section at a time.
- If the human requests a retry, analyze the specific alignment or spacing feedback and adjust your 0.25x scaling calculations accordingly.
