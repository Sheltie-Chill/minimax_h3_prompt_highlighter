# MiniMax H3 Prompt Highlighter (WanGP Plugin)

Live syntax highlighting for [Wan2GP (WanGP)](https://github.com/deepbeepmeep/Wan2GP) prompt boxes when using **MiniMax H3** models. Structure your prompts visually: sections, subjects, shots, timestamps, dialogue blocks and commands are all color-coded as you type.

<img width="802" height="629" alt="image" src="https://github.com/user-attachments/assets/45f61b89-9bea-482d-86c7-de13098d4fad" />

## Features

- **Live highlighting** — real-time color coding of the MiniMax H3 prompt structure in the main prompt textarea *and* the wizard:
  - Section titles (`summary:`, `subject_definitions:`, `detailed_description:`, …)
  - `# Title` navigation headers
  - Sliding-window commands (`[/...]`)
  - Task tags (`[reference generation]`, `[video editing]`, …)
  - Per-number `<Subject N>` markers with a dedicated color per subject
  - `<Picture N>` / `<Video N>` / `<Audio N>` references
  - `[Shot N]` markers
  - Timestamps (`At MM:SS.mmm`)
  - Dialogue blocks (`<d>…</d>`) including `(Sx)` speakers
  - `<scenetrans>` / `<cutoff>` tags
  - Retention modes
- **Opt-in toggle + color customization** — a controls bar under the prompt with an enable checkbox and a *Customize colors* button; the palette is persisted in the browser
- **Model-aware** — highlighting is active only for MiniMax H3 models; the controls bar hides itself otherwise

## Installation

### Option A — WanGP Plugin Manager (recommended)

1. Open Wan2GP and go to the **Plugin Manager** tab (under User Support)
2. Use the install-from-URL field and paste:
   ```
   https://github.com/<your-github-username>/minimax_h3_prompt_highlighter
   ```
3. Restart WanGP.

### Option B — Manual

1. Download this repository (Code → Download ZIP, then extract) or `git clone` it
2. Copy the folder into your WanGP installation under `plugins/` so that `plugin.py` sits directly inside:
   ```
   Wan2GP/plugins/minimax_h3_prompt_highlighter/plugin.py
   ```
3. Restart WanGP.

## Usage

- In the Generate tab, a bar appears under the prompt: *Highlight MiniMax H3 prompt syntax* (checkbox) and **Customize colors**
- Toggle highlighting on/off at any time; the checkbox spans the whole label text
- Use **Customize colors** to re-theme any token type — the background chips re-derive automatically from your text colors

## Requirements

- Wan2GP with the plugin system enabled (shared/plugins support)

## License

[MIT](LICENSE)
