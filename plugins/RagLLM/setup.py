from setuptools import setup, find_packages

setup(
    name="RagLLM",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        'fastapi',
        'pydantic',
        'langchain',
        'langchain-community',
        'langchain-core',
        'langchain-openai',
        'SQLAlchemy',
        'psycopg2-binary',
        'pgvector',
        'tiktoken',
        'semantic-text-splitter',
        'tokenizers'
    ],
    entry_points={
        'my_fastapi_app.plugins': [
            'RagLLM = RagLLM.routes:add_routes',
        ],
    }
)
