FROM vllm/vllm-openai:latest

WORKDIR /app

COPY main.py .

EXPOSE 8001

ENTRYPOINT ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]