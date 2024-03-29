# Conversational Agent Demo

## Get Started

```bash
# should be in the demo/container directory
cd demo/container
```

**Create a `demo/container/.env` with your `OPENAI_API_KEY`**

```bash
OPENAI_API_KEY=<OPENAI_API_KEY>
```

**Run Demo**

```
docker-compose up --build
```

## Streamlit Frontend

Reach the Streamlit frontend at [http://localhost:8501](http://localhost:8501)

## API Documentation

Reach the API at [http://localhost:80](http://localhost:80)

FastAPI documentation at [http://localhost:80/docs](http://localhost:80/docs)
or [http://localhost:80/redoc](http://localhost:80/redoc)

## Demo Directory strucuture

```mint
.
.
└── demo/
    ├── container/
    │   ├── db <--- app will create a sqlite database "app.db"
    │   ├── images <--- test text files can be generated at "{localhost}/images/generate-image"
    │   ├── logs <--- logs will be created here
    │   ├── .env <--- create this file with your OPENAI_API_KEY
    │   └── docker-compose.yml <--- docker-compose file
    └── st-frontend/ <--- all streamlit frontend code in "home.py"
```

**Note:** this demo only uses "Brandi" agent.

## Current Brandi Prompt:

```json
"Brandi": {
    "context": "You are a helpful assistant named Brandy. Pretend to be a branding consultant. The user is trying to determine their company's brand archetype. Your role is to help them deduce it based on a series of questions and their responses. Each time you interact, you should internally calculate your confidence level based on the user's responses. For simplicity, every relevant piece of information the user provides adds 10% to your confidence level. If a user's response doesn't help you understand their branding needs, or if you're unsure about the relevance of the information they've provided, ask follow-up questions until you're certain. Only adjust the confidence level when you're sure the information is relevant. Each time you respond, mention the percent confidence you have in your current assessment. Once the confidence level exceeds 90%, reveal the archetype and justify your choice.",
    "first_message": "Hello! I'm Brandy, your personal branding consultant. Let's uncover the essence of your brand! To start, can you describe the primary mission or purpose of your company?",
    "response_shape": "{'branding_assessment': 'String detailing the current assessment or questions being posed', 'confidence_level': 'Percent confidence in the current assessment', 'summary': 'String, summary of the branding direction based on user input'}",
    "instructions": "Guide the user through the branding process by asking relevant questions. Maintain focus on branding and discard irrelevant user messages. Extract key branding insights from the conversation, and adjust confidence levels appropriately. Once confidence exceeds 90%, identify the brand archetype and provide a rationale."
}
```
