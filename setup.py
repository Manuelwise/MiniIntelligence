from setuptools import setup, find_packages

setup(
    name="miniintelligence",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        # Core FastAPI
        "fastapi>=0.105.0,<0.106.0",
        "uvicorn[standard]>=0.24.0,<0.25.0",

        # Auth
        "python-jose[cryptography]==3.3.0",
        "passlib[bcrypt]==1.7.4",

        # Pydantic & Config
        "pydantic>=2.7.4,<3.0.0",
        "pydantic-settings>=2.0.3,<3.0.0",
        "python-dotenv==1.0.0",
        "python-multipart==0.0.6",

        # LangChain + Groq
        "langchain>=0.2.11,<0.3.0",
        "langchain-core>=0.2.35,<0.3.0",
        "langchain-community>=0.2.11,<0.3.0",
        "langchain-groq>=0.1.10,<0.2.0",
        "groq>=0.4.1,<1.0.0",

        # Redis / Rate Limiting
        "redis==5.0.1",
        "aioredis==2.0.1",
        "slowapi==0.1.8",

        # HTTP client
        "httpx==0.26.0",

        # Testing
        "pytest==7.4.3",
        "pytest-asyncio==0.21.1",
    ],
)
