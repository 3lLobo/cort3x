import json
import logging
import torch
from mitmproxy import http
from transformers import AutoModelForSequenceClassification, AutoTokenizer

# --- Configuration ---
MODEL_ID = "meta-llama/Llama-Prompt-Guard-2-86M"
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("PromptGuardMitm")

class PromptGuardPlugin:
    def __init__(self):
        logger.info(f"Initializing Prompt-Guard on {DEVICE}...")
        self.tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)
        self.model = AutoModelForSequenceClassification.from_pretrained(MODEL_ID).to(DEVICE)
        self.model.eval()
        logger.info("Model loaded and ready.")

    def request(self, flow: http.HTTPFlow):
        """
        Intercepts the request to scan for injections.
        """
        # Only target the chat completions endpoint
        if "/v1/chat/completions" in flow.request.path and flow.request.method == "POST":
            try:
                data = json.loads(flow.request.content)
                messages = data.get("messages", [])
                user_text = messages[-1].get("content", "") if messages else ""

                if user_text:
                    if not self._is_safe(user_text):
                        logger.warning(f"BLOCKING REQUEST: Malicious content detected.")
                        flow.response = http.Response.make(
                            403,
                            json.dumps({"error": "Access denied: Malicious content detected."}),
                            {"Content-Type": "application/json"}
                        )
            except Exception as e:
                logger.error(f"Error processing request: {e}")

    def responseheaders(self, flow: http.HTTPFlow):
        """
        Decides whether to stream the response based on the request body.
        """
        if "/v1/chat/completions" in flow.request.path:
            try:
                # We peek at the request body to see if 'stream' was requested
                req_data = json.loads(flow.request.content)
                if req_data.get("stream") is True:
                    # mitmproxy toggle for streaming mode
                    flow.response.stream = True
                    logger.info("Streaming enabled for this response.")
            except Exception:
                pass

    def _is_safe(self, text: str) -> bool:
        """Internal helper for model inference."""
        inputs = self.tokenizer(text, return_tensors="pt").to(DEVICE)
        with torch.no_grad():
            logits = self.model(**inputs).logits
            predicted_class_id = logits.argmax().item()
        
        label = self.model.config.id2label[predicted_class_id]
        return label.upper() == "LABEL_0"

# Register the plugin
addons = [PromptGuardPlugin()]
