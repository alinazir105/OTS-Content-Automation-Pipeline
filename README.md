# EdTech HTML Pipeline

Automated pipeline that reads lesson PDFs and generates **immersive, fully
interactive HTML lesson pages** — one per PDF. Pages include:

- Animated 3D Three.js scene (content-specific objects)
- Sort / drag-and-drop game
- Knowledge quiz
- True or False game
- Extra game (memory cards, fill-in-the-blanks, or word scramble)
- Subject-matched colour theme
- Mobile-responsive layout

---

## Folder Structure

```
edtech-pipeline/
├── generate.py            ← main entry point
├── requirements.txt
├── .env.example           ← copy to .env and add your key
│
├── utils/
│   ├── class_config.py    ← per-class language / difficulty settings
│   ├── html_builder.py    ← assembles the full HTML page
│   ├── theme_selector.py  ← subject → colour theme mapping
│   ├── game_selector.py   ← deterministic extra-game picker
│   └── pdf_reader.py      ← fallback PDF text extractor
│
├── classes/               ← PUT YOUR PDFs HERE
│   ├── class 1/
│   │   └── computer/
│   │       ├── lesson_1.pdf
│   │       └── lesson_2.pdf
│   ├── class 2/
│   │   ├── math/
│   │   └── science/
│   └── ...
│
└── output/                ← generated HTML pages appear here
    ├── class 1/
    │   └── computer/
    │       ├── lesson_1.html
    │       └── lesson_2.html
    └── pipeline.log
```

---

## Quick Start

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Set up API key

```bash
cp .env.example .env
# Edit .env and set GEMINI_API_KEY=your_key_here
```

Get a free Gemini API key at: https://aistudio.google.com/app/apikey

### 3. Add your PDFs

Place PDFs under `classes/` following the structure above:
```
classes/<class name>/<subject>/<lesson>.pdf
```

### 4. Run the pipeline

```bash
# Process all PDFs
python generate.py

# Process a single PDF
python generate.py --file "classes/class 1/computer/lesson_1.pdf"

# Process only Class 3
python generate.py --class-filter "class 3"

# Preview what would be generated (no API calls)
python generate.py --dry-run

# Force regenerate even if cached
python generate.py --force
```

---

## Scaling to More Classes & Subjects

The pipeline is fully scalable. To add new classes or subjects:

1. **Create the folder** under `classes/`:
   ```
   classes/class 5/science/
   classes/class 10/math/
   ```

2. **Drop PDFs in** — the pipeline discovers them automatically.

3. **Run `generate.py`** — new PDFs generate, existing unchanged ones skip (cached).

### Supported class levels

Classes 1–12 are all configured in `utils/class_config.py`. Each class has:
- Age-appropriate language instructions for Gemini
- Adjusted quiz question count (5 for Class 1 → 25 for Class 12)
- Difficulty style description
- Definition complexity

### Adding new subjects

Subjects are detected from folder names. To get a custom colour theme for a
new subject, add an entry to `utils/theme_selector.py`:

```python
SUBJECT_THEMES = {
    ...
    "biology": {
        "name": "Nature Green",
        "primary": "#16a34a",
        ...
    },
}
```

If no match is found, the `"default"` Vibrant Indigo theme is used.

---

## Cache & Incremental Updates

The pipeline writes `.pipeline_cache.json` to the output folder. On subsequent
runs, PDFs whose content hasn't changed (same MD5 hash) are skipped. This
means you can add new lessons and re-run without re-processing existing ones.

Use `--force` to regenerate everything regardless of cache.

---

## Output

Each generated `.html` file is **fully self-contained** — no server needed.
Just open in a browser. All CSS, JS, and content are embedded inline.

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `No PDFs found` | Check folder depth: must be `classes/<class>/<subject>/<file>.pdf` |
| `JSON parse error` | Gemini returned malformed JSON — pipeline retries 3× automatically |
| `No GEMINI_API_KEY` | Add key to `.env` or set environment variable |
| Page is blank | Open browser DevTools console for JS errors |
| Wrong theme | Check subject folder name matches a key in `theme_selector.py` |
