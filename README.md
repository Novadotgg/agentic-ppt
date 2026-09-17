# Nova PPT Gen 🚀

> **Agentic AI PowerPoint Generator** powered by LangGraph, Groq (Llama 3.3 70B), and `python-pptx`. Create professionally styled, content-rich PowerPoint decks in seconds.

[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688?style=flat&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![LangGraph](https://img.shields.io/badge/LangGraph-0.2+-blue?style=flat)](https://github.com/langchain-ai/langgraph)
[![Groq](https://img.shields.io/badge/Groq-Llama_3.3_70B-f55036?style=flat)](https://groq.com)
[![Python PPTX](https://img.shields.io/badge/python--pptx-1.0+-d9381e?style=flat)](https://python-pptx.readthedocs.io)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## ✨ Overview

**Nova PPT Gen** is a full-stack presentation generator that transforms any topic or brief into a structured, design-forward PowerPoint presentation (`.pptx`).

Unlike standard presentation tools that generate superficial bullet points or plain white slides, Nova PPT Gen pairs an intelligent planning workflow with an enterprise-grade PPTX rendering engine. It selects deliberate slide archetypes, pairs typography, applies WCAG AA/AAA contrast-verified color palettes, and writes detailed speaker notes.

---

## 🌟 Key Features

- **⚡ Blazing Fast Generation**: Powered by Groq's high-speed inference running `llama-3.3-70b-versatile`.
- **🧠 Agentic Structure & Narrative Architecture**: LangGraph orchestrates slide planning to ensure every slide has a clear takeaway headline and concrete data-driven insights.
- **🎨 Curated Design Palettes**:
  - `Obsidian Emerald`: High-tech dark mode with emerald neon accents.
  - `Midnight Executive`: Deep navy with gold accents for corporate and board meetings.
  - `Ivory Linen`: Warm, sophisticated editorial style with bronze and charcoal tones.
  - `Arctic Blueprint`: Clean SaaS / tech-deck style with electric blue accents on crisp slate.
  - `Crimson Authority`: High-contrast black and crimson for punchy, decisive pitches.
- **📐 Purpose-Built Slide Layout Archetypes**:
  - **Hero Title**: Bold presentation opener with subtitle and speaker credentials.
  - **Split Screen**: Side-by-side comparison (problem vs. solution, before vs. after).
  - **Metrics Callout**: 3–4 prominent KPI blocks with values and contextual labels.
  - **Process Timeline**: Sequential steps or development roadmaps.
  - **Feature Grid**: Modular 3–4 card highlights for capabilities or value propositions.
  - **Quote Focus**: Impactful editorial statement or client testimonial.
- **🎙️ Comprehensive Speaker Notes**: Generates natural, slide-by-slide talking points for presenters.
- **🔒 Privacy First & Stateless**: User-provided Groq API keys are request-scoped and never stored on disk or logged. Generated files are streamed and cleaned up automatically via background tasks.
- **🖥️ Built-In Web Interface**: Clean, dark-mode frontend built with Space Mono and emerald tokens—no heavy setup required.

---

## 🏗️ Architecture

```
User Input (Topic, Theme, Slides, Notes)
                  │
                  ▼
         FastAPI REST API
                  │
                  ▼
         LangGraph Agent
      (Groq / Llama 3.3 70B)
                  │
                  ▼
       Structured Slide JSON
                  │
                  ▼
      python-pptx Layout Engine
   (Card shapes, Palettes, Typography)
                  │
                  ▼
         Downloadable .pptx
```

---

## 🚀 Quick Start

### 1. Prerequisites

- **Python 3.10+** installed
- A **Groq API Key** ([Get one for free at Groq Console](https://console.groq.com/keys))

### 2. Clone the Repository

```bash
git clone https://github.com/Novadotgg/agentic-ppt.git
cd agentic-ppt
```

### 3. Create a Virtual Environment & Install Dependencies

```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate

# Install requirements
pip install -r requirements.txt
```

### 4. Configure Environment (Optional)

Copy the example environment file:

```bash
cp .env.example .env
```

Default contents of `.env.example`:
```env
# Optional Development Configuration
# In production, users provide their own Groq API key in the UI.
GROQ_MODEL=llama-3.3-70b-versatile
```

### 5. Run the Server

```bash
python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

- **Frontend App**: Open [http://localhost:8000](http://localhost:8000) in your browser.
- **Interactive API Docs (Swagger)**: Open [http://localhost:8000/docs](http://localhost:8000/docs).

---

## 📂 Project Structure

```text
agentic-ppt/
├── backend/
│   ├── agent/
│   │   ├── graph.py        # LangGraph workflow definition
│   │   ├── groq_node.py    # LLM execution node with structured JSON parser
│   │   ├── prompt.py       # Domain-specific prompt generator & theme definitions
│   │   └── state.py        # TypedDict state schemas
│   ├── api/
│   │   └── routes.py       # FastAPI route handlers (/health, /generate-ppt)
│   ├── ppt/
│   │   └── generator.py    # python-pptx rendering engine (layouts, colors, fonts)
│   ├── main.py             # FastAPI app initialization, CORS, static file serving
│   └── schemas.py          # Pydantic request and response models
├── frontend/
│   ├── DESIGN.md           # Visual design tokens and design principles
│   ├── theme.css           # Design system stylesheets
│   ├── tokens.json         # Raw design tokens
│   └── variables.css       # CSS custom properties
├── index.html              # Standalone web app interface (served at root)
├── requirements.txt        # Python package dependencies
├── .env.example            # Environment configuration template
├── vercel.json             # Deployment configuration
└── README.md
```

---

## 📡 API Reference

### 1. Health Check

```http
GET /api/health
```

**Response:**
```json
{
  "status": "ok",
  "service": "Nova PPT Gen"
}
```

---

### 2. Generate Presentation

```http
POST /api/generate-ppt
Content-Type: application/json
```

#### Request Body

| Field | Type | Required | Default | Description |
| :--- | :--- | :--- | :--- | :--- |
| `groq_api_key` | `string` | **Yes** | — | Groq API key for inference (request-scoped) |
| `topic` | `string` | **Yes** | — | Presentation topic or core subject |
| `description` | `string` | No | `null` | Optional context, requirements, or focus areas |
| `number_of_slides` | `integer`| No | `6` | Number of slides to create (`3` to `10`) |
| `theme_selection` | `string` | No | `"Obsidian Emerald"` | Theme palette name |
| `font_style` | `string` | No | `"Modern Sans-Serif"` | Typography pairing direction |
| `notes` | `boolean`| No | `true` | Generate speaker notes for each slide |
| `images` | `boolean`| No | `false` | Generate visual asset prompts |
| `logo` | `boolean`| No | `false` | Include branding placement markers |

#### Example cURL

```bash
curl -X POST "http://localhost:8000/api/generate-ppt" \
  -H "Content-Type: application/json" \
  -d '{
    "groq_api_key": "gsk_...",
    "topic": "Future of Autonomous Agents in 2026",
    "description": "Cover multi-agent coordination, benchmarks, and enterprise adoption",
    "number_of_slides": 6,
    "theme_selection": "Obsidian Emerald",
    "font_style": "Modern Sans-Serif",
    "notes": true
  }' \
  --output presentation.pptx
```

#### Response

- Returns the binary PowerPoint presentation file (`application/vnd.openxmlformats-officedocument.presentationml.presentation`).
- Attachment filename is automatically formatted as `<sanitized_topic>.pptx`.

---

## 🛡️ Security & Privacy

1. **No Stored Keys**: Groq API keys are provided on each request and used only within that request's execution scope. They are never written to disk, saved in databases, or included in logs.
2. **Ephemeral File Storage**: PowerPoint presentations are compiled to temporary files, streamed to the client, and immediately removed via background cleanup tasks.

---

## 🤝 Contributing

Contributions are welcome! If you'd like to add new slide archetypes, new color themes, or improve layout rendering:

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/cool-new-layout`)
3. Commit your changes (`git commit -m "Add comparison matrix layout"`)
4. Push to the branch (`git push origin feature/cool-new-layout`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).
