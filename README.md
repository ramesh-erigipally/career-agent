---
title: career_agent
app_file: app.py
sdk: gradio
sdk_version: 5.37.0
---

# Career Agent

An AI-powered resume chatbot that answers questions about a person's background using their resume and LinkedIn summary. Built with Gradio, OpenAI, and Python.

## Features
- Conversational AI that answers questions about Ramesh Erigipally’s professional background
- Uses resume (PDF) and LinkedIn summary as context
- Records user interactions and unknown questions
- Sends notifications via Pushover when users provide contact details or ask unknown questions
- Gradio web interface for easy interaction

## Demo
Launch the app locally and interact with the chatbot in your browser.

## Setup & Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/ramesh-erigipally/career-agent.git
   cd career-agent
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Prepare data:**
   - Place your resume PDF as `data/resume.pdf`
   - Place your LinkedIn/professional summary as `data/summary.txt`

4. **Set up environment variables:**
   Create a `.env` file in the project root with the following (see `.env.example` if available):
   ```env
   OPENAI_API_KEY=your_openai_api_key
   PUSHOVER_USER=your_pushover_user_key   # (optional, for notifications)
   PUSHOVER_TOKEN=your_pushover_app_token # (optional, for notifications)
   ```

## Usage

Run the app:
```bash
python app.py
```

This will launch a Gradio web interface. Open the provided local URL in your browser to chat with the AI.

## File Structure
- `app.py` — Main application code
- `requirements.txt` — Python dependencies
- `data/resume.pdf` — Resume file (user-provided)
- `data/summary.txt` — LinkedIn/professional summary (user-provided)
- `test.py` — Example/test Gradio chat interface

## Credits
- Developed by Ramesh Erigipally
- Powered by [OpenAI](https://openai.com/), [Gradio](https://gradio.app/), and [Pushover](https://pushover.net/)

## License
MIT
