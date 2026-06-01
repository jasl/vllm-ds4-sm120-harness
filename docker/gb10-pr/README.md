# GB10 PR Branch Docker Image

This build context packages the DeepSeek V4 SM12x vLLM PR branch for DGX
Spark / GB10 evaluation. Build it on a GB10 host, not on the RTX PRO 6000 test
machine.

The Dockerfile is intentionally self-contained:

- fetches vLLM from the public PR branch by default;
- builds for GB10 / SM121 with `TORCH_CUDA_ARCH_LIST=12.1a`;
- installs the FlashInfer Python, cubin, and JIT cache wheels matching vLLM
  requirements, instead of source-building the large AOT cubin cache;
- installs `flashinfer-python[cu13]` so Blackwell / SM100+ CuTe DSL kernels are
  available;
- builds NCCL `v2.30u1` and redirects the Python NCCL wheel path to that system
  library to avoid the known DGX Spark load-order hang;
- pins CUDA compiler Python wheels to the CUDA 13.0 family used by PyTorch
  `cu130`, preventing the `nvcc` / CCCL header mismatch seen on fresh GB10
  venvs.

## Build

```bash
cd docker/gb10-pr

docker build \
  --progress=plain \
  -t ds4-vllm-gb10:pr \
  --build-arg BUILD_JOBS=8 \
  .
```

To build a different branch or exact commit:

```bash
docker build \
  --progress=plain \
  -t ds4-vllm-gb10:dev \
  --build-arg VLLM_REF=ds4-sm120-preview-dev \
  --build-arg BUILD_JOBS=8 \
  .
```

The default source is:

```text
VLLM_REPO=https://github.com/jasl/vllm.git
VLLM_REF=codex/ds4-sm120-min-enable
```

FlashInfer is intentionally consumed from released wheels by default. The JIT
cache wheel is loaded from the FlashInfer CUDA 13.0 index and requested with the
same public version as the Python and cubin packages. A source build is useful
when developing FlashInfer itself, but it compiles thousands of AOT kernels and
is not a good default for a distribution image.

## Quick Smoke

```bash
docker run --rm --gpus all --ipc=host --network host \
  ds4-vllm-gb10:pr \
  vllm --version

docker run --rm --gpus all --ipc=host --network host \
  ds4-vllm-gb10:pr \
  flashinfer show-config
```

## Two-Node Evaluation

Use the existing `spark-vllm-docker` launcher with this image tag. Keep local
node names, addresses, model cache paths, and credentials outside this repo.

```bash
<spark-vllm-docker-checkout>/launch-cluster.sh \
  -t ds4-vllm-gb10:pr \
  exec vllm serve deepseek-ai/DeepSeek-V4-Flash \
    --host 0.0.0.0 \
    --port 8000 \
    --tensor-parallel-size 2 \
    --distributed-executor-backend mp \
    --max-model-len 131072 \
    --max-num-seqs 2 \
    --max-num-batched-tokens 4176 \
    --gpu-memory-utilization 0.70 \
    --kv-cache-dtype fp8 \
    --enable-expert-parallel \
    --compilation-config '{"cudagraph_mode":"FULL_AND_PIECEWISE","custom_ops":["all"]}'
```

MTP should be evaluated as a separate run:

```bash
--speculative-config '{"method":"mtp","num_speculative_tokens":2}'
```

Keep prefix cache disabled unless the test case is specifically the
prefix-cache lifecycle or reuse gate.

## GB10 Memory Hygiene

GB10 / DGX Spark uses coherent unified memory, so Docker runs can have less
effective KV-cache headroom than a comparable bare-metal run. The GPU is not
virtualized, but container layers, image load/export, overlayfs metadata,
Python packages, FlashInfer/Triton caches, and Linux page cache can reduce the
`MemAvailable` value that vLLM uses during KV profiling.

For any long-context Docker validation:

1. Build or load the image before the measurement window.
2. Reclaim file cache on every node after large image or checkpoint activity:

   ```bash
   sudo sh -c 'sync; echo 3 > /proc/sys/vm/drop_caches'
   ```

3. Avoid `--memory`, `--memory-swap`, and `--non-privileged` limits unless the
   test is explicitly validating constrained-container behavior.
4. Before treating a run as capacity evidence, record:
   - host `MemAvailable`;
   - `docker system df`;
   - vLLM `Available KV cache memory`;
   - vLLM `GPU KV cache size`;
   - current-boot NVIDIA driver health.
5. Run a Docker-specific `max_model_len` ceiling sweep before claiming the same
   64K/128K/long-context support level as bare metal.

Do not promote a Docker long-context number just because the same shape passed
bare metal. Treat Docker and bare metal as separate capacity profiles on GB10.
