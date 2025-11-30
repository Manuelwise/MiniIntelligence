from setuptools import setup, find_packages

setup(
    name="miniintelligence",
    version="0.1.0",
    packages=find_packages(),  # auto-discovers only actual Python packages
    install_requires=[
        "fastapi>=0.105.0,<0.106",
        "uvicorn>=0.24.0,<0.25",
        "python-jose[cryptography]==3.3.0",
        "passlib[bcrypt]==1.7.4",
        "pydantic>=2.7.4,<3.0.0",
        "pydantic-settings>=2.0.3",
        "python-dotenv==1.0.0",
        "python-multipart==0.0.6",
        "langchain>=1.0.0,<2.0.0",
        "openai>=0.28.1",
        "tenacity==8.2.3",
        "redis==5.0.1",
        "slowapi==0.1.8",
        "httpx==0.26.0",
        "aioredis==2.0.1",
        "langchain-openai>=0.0.1",
        "langchain-core>=1.0.0",
        "langchain-community>=0.0.10"
    ],
)
