docker run --gpus all --env HF_TOKEN=$(cat ~/.cache/huggingface/token) -v ~/.cache/huggingface:/root/.cache/huggingface \
    -p 8000:8000 \
    -p 8001:8001 \
    -v ./supervisord.conf:/etc/supervisor/conf.d/supervisord.conf \
    -v ./guard_proxy.py:/vllm-workspace/guard_proxy.py \
    -v ./entrypoint.sh:/vllm-workspace/entrypoint.sh \
    -d --rm \
    --net=vllm \
    --ipc=host \
    --name vllm-openai \
    --entrypoint "./entrypoint.sh" \
    vllm/vllm-openai:latest \
    "casperhansen/deepseek-r1-distill-qwen-7b-awq"  --quantization awq  --dtype half --gpu-memory-utilization 0.70  --max-model-len 8096  --reasoning-parser deepseek_r1 --enable-auto-tool-choice --tool-call-parser hermes
    #--model meta-llama/Llama-Guard-4-12B casperhansen/deepseek-r1-distill-qwen-7b-awq 
    # "casperhansen/deepseek-r1-distill-qwen-7b-awq" 
