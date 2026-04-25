FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install --no-cache-dir uv && \
    uv pip install --system --no-cache streamlit openai openai-agents python-dotenv
EXPOSE 8000
CMD ["streamlit", "run", "main.py", "--server.port=8000", "--server.address=0.0.0.0"]