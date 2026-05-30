# MayMind CBT Assistant

A Cognitive Behavioural Therapy (CBT) chatbot built with Streamlit and the OpenAI API. May is a supportive AI assistant trained to provide CBT-based emotional support using the UK NHS/IAPT framework.

> **Disclaimer:** This is an AI assistant, not a licensed therapist. For clinical mental health support, please consult a qualified professional.

## Features

- **CBT Chat** — Conversational support with May, a CBT-informed AI therapist
- **PHQ-9 & GAD-7 Assessments** — Validated screening tools for depression and anxiety
- **Thought Journal** — Record and reframe negative thought patterns
- **Activity Planner** — Schedule and track behavioural activation activities
- **Breathing Exercises** — Guided relaxation techniques
- **Progress Tracking** — Visualise mood trends and tool usage over time
- **Export** — Download session reports and chat transcripts as PDF

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/your-username/CBTChatbot.git
cd CBTChatbot
```

### 2. Create a virtual environment

```bash
python -m venv venv
source venv/bin/activate        # macOS/Linux
venv\Scripts\activate           # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure your API key

Copy `.env.example` to `.env` and add your OpenAI API key:

```bash
cp .env.example .env
```

Edit `.env`:

```
OPENAI_API_KEY=your_openai_api_key_here
```

### 5. Run the app

```bash
streamlit run app.py
```

## Project Structure

```
CBTChatbot/
├── app.py                  # Main Streamlit application
├── ai/
│   └── therapist.py        # OpenAI API integration and prompt engineering
├── helpers/
│   ├── assessment.py       # PHQ-9 and GAD-7 assessments
│   ├── safety.py           # Crisis detection and resources
│   ├── ui.py               # Shared UI components
│   └── utils.py            # Session state initialisation
├── tools/
│   ├── thought_journal.py  # CBT thought record tool
│   ├── activity_scheduler.py
│   ├── breathing.py
│   └── mood_tracker.py
├── export/
│   ├── pdf_generator.py    # Full session PDF report
│   └── transcript.py       # Chat transcript PDF
├── styles/
│   └── maymind.css         # Custom pink theme
├── assets/                 # Images and icons
├── tests/                  # Unit, integration, and live API tests
├── .env.example            # Environment variable template
└── requirements.txt
```

## Crisis Support

If you or someone you know is in crisis, please contact:

- **Samaritans**: 116 123 (Free, 24/7)
- **Crisis Text Line**: Text SHOUT to 85258
- **Emergency Services**: 999
- **NHS Direct**: 111
