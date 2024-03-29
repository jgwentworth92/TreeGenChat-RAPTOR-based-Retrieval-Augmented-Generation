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
