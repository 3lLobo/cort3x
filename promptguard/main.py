import logging
import time
from typing import Any, Dict, Optional

import httpx
import torch
from fastapi import FastAPI, Request, Response
from fastapi.responses import StreamingResponse
import json
from transformers import (
    AutoModelForSequenceClassification,
    AutoTokenizer,
    BatchEncoding,
)

import os

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
MODEL_ID = os.getenv("MODEL_ID", "meta-llama/Llama-Prompt-Guard-2-86M")

# Optimization: Use GPU if available
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

# Configure logging to track security events and latency
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("PromptGuardProxy")

app = FastAPI(
    title="Prompt-Guard Proxy",
    description="A security layer that intercepts chat completions to detect injections.",
)

# --- Model Initialization ---

logger.info(f"Loading model '{MODEL_ID}' onto device: {DEVICE}")
tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)
model = AutoModelForSequenceClassification.from_pretrained(MODEL_ID).to(DEVICE)
model.eval()

# Global async client for connection pooling
http_client = httpx.AsyncClient(base_url=BACKEND_URL, timeout=60.0)

# --- Core Logic ---


def analyze_text_safety(text: str) -> Dict[str, Any]:
    """
    Analyzes a string using the Prompt-Guard model on the GPU.

    Args:
        text: The user input string to scan.

    Returns:
        A dictionary containing 'is_safe' (bool), 'label' (str), and 'inference_ms' (float).
    """
    start_time = time.perf_counter()

    # Prepare inputs and move to the same device as the model
    inputs: BatchEncoding = tokenizer(text, return_tensors="pt").to(DEVICE)

    with torch.no_grad():
        logits = model(**inputs).logits
        predicted_class_id = logits.argmax().item()

    label = model.config.id2label[predicted_class_id]
    inference_ms = (time.perf_counter() - start_time) * 1000

    return {
        "is_safe": label.upper() == "LABEL_0",
        "label": label,
        "inference_ms": inference_ms,
    }

@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy_gateway(request: Request, path: str):
    method = request.method
    body = await request.body()
    is_streaming_requested = False

    # 1. Security Interception & Stream Check
    if path == "v1/chat/completions" and method == "POST":
        try:
            json_data = json.loads(body)
            # Check if the user requested a stream
            is_streaming_requested = json_data.get("stream", False)
            
            messages = json_data.get("messages", [])
            user_text = messages[-1].get("content", "") if messages else ""

            if user_text:
                result = analyze_text_safety(user_text)
                logger.info(
                    f"SCAN | Path: /{path} | Label: {result['label']} | "
                    f"Inference: {result['inference_ms']:.2f}ms"
                )
                if not result["is_safe"]:
                    logger.warning(f"BLOCK | Detected {result['label']}")
                    return Response(
                        content='{"error": "403 Access denied: Malicious content detected."}',
                        status_code=403,
                        media_type="application/json",
                    )
        except Exception as e:
            logger.error(f"SCAN_ERROR | {e}")

    # 2. Forwarding Logic
    url = f"{BACKEND_URL}/{path}"
    proxy_req = http_client.build_request(
        method=method,
        url=url,
        headers=request.headers.raw,
        content=body,
        params=request.query_params,
    )

    try:
        # Request a streaming response from the backend
        backend_response = await http_client.send(proxy_req, stream=True)
        forward_ms = (time.perf_counter() - start_forward) * 1000

        logger.info(
            f"FORWARD | {method} /{path} -> {backend_response.status_code} | "
            f"Latency: {forward_ms:.2f}ms"
        )
        # Handle Streaming Case
        if is_streaming_requested:
            return StreamingResponse(
                backend_response.aiter_raw(),
                status_code=backend_response.status_code,
                headers=dict(backend_response.headers),
            )
        
        # Handle Standard (Buffered) Case
        else:
            # We must manually read the stream if we aren't returning a StreamingResponse
            full_content = await backend_response.aread()
            return Response(
                content=full_content,
                status_code=backend_response.status_code,
                headers=dict(backend_response.headers),
            )

    except httpx.RequestError as exc:
        logger.error(f"BACKEND_ERROR | {exc}")
        return Response(content="Backend server unreachable", status_code=502)


if __name__ == "__main__":
    import uvicorn

    # Set the PORT the proxy will listen on (e.g., 8080)
    uvicorn.run(app, host="0.0.0.0", port=8001)
