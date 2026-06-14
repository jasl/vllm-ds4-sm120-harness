# Black-Benediction RTX Public-Stack Baseline

Status: observation
Date: 2026-06-13
Owner/context: external black-benediction endpoint baseline before porting ideas

## Question

Does `local-inference-lab/vllm` `dev/black-benediction` beat the current
SM120 RTX baseline when reproduced with the public dependency stack, and is the
whole B12X/DFlash route worth treating as the next implementation target?

## Profile

- Hardware: dual RTX PRO 6000 / SM120.
- vLLM branch/commit: `local-inference-lab/vllm` `dev/black-benediction`
  `5fcd00c3d797e3e8b132eda5eabf80168b4aca47`.
- Dependency or image identity: `torch==2.11.0+cu130`;
  `triton==3.6.0`; `nvidia-nccl-cu13==2.30.7`;
  `flashinfer-python==0.6.13rc1`;
  `flashinfer-jit-cache==0.6.13rc1+cu130`; `b12x==0.20.0`;
  `ninja==1.13.0`.
- TP / PP / EP: TP=2, PP=1, EP disabled.
- MTP: MTP=2 with `moe_backend=b12x`.
- FP8 KV: enabled.
- Prefix cache: disabled for the comparison run.
- CUDA graph mode: `FULL_AND_PIECEWISE`.
- `max_model_len`: 131072.
- `max_num_seqs`: 2.
- `max_num_batched_tokens`: 8192.
- Other route flags: `--moe-backend b12x`, `--linear-backend b12x`,
  `--attention-backend B12X_MLA_SPARSE`, `--enable-flashinfer-autotune`,
  `--no-enable-prefix-caching`, and the black-benediction B12X env set for
  FlashInfer sampler, B12X MHC, FP8 GEMM, MoE, sparse indexer, V2 model runner,
  and B12X PCIe oneshot allreduce.

The target environment needed two non-repo preparation fixes before this was a
valid reproduction: the vLLM wrapper had to include the target venv `bin` on
`PATH`, and a venv-local PyTorch header compatibility patch was needed so the
B12X PCIe runtime extension could compile under the CUDA 13 / GCC 15 toolchain.
After that, the server reported `B12X_PCIE_ONESHOT` active for TP allreduce.

## Result

The public-stack black-benediction route starts and completes the RTX OSL=128
16K/65K C=1/C=2 matrix, but it does not beat the current local SM120 baseline
on the comparable C=1 no-prefix shape.

| Input tokens | C | Requests | Input tok/s | Output tok/s | Mean TTFT ms | P99 TTFT ms | P99 ITL ms |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 16384 | 1 | 8 | 5407.26 | 42.24 | 2446.82 | 2459.53 | 35.61 |
| 16384 | 2 | 8 | 5696.31 | 44.50 | 3471.63 | 5043.06 | 1200.29 |
| 65536 | 1 | 8 | 5867.14 | 11.46 | 10607.91 | 10706.52 | 21.70 |
| 65536 | 2 | 8 | 5945.66 | 11.61 | 16089.54 | 21570.63 | 1418.34 |

Against the current RTX PR stable preview OSL=128 C=1 evidence, the reproduced
black-benediction stack is slower:

| Input tokens | Current input tok/s | Black input tok/s | Delta | Current mean TTFT ms | Black mean TTFT ms |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 16384 | 6209.00 | 5407.26 | -12.9% | 2030.49 | 2446.82 |
| 65536 | 7049.72 | 5867.14 | -16.8% | 8715.51 | 10607.91 |

The no-prefix measurement had zero prefix hits and zero preemptions. The
same-server warmup absorbed runtime Triton JIT warnings before the measured
rows, and the TP communicator reported `['B12X_PCIE_ONESHOT', 'PYNCCL']`.

## Interpretation

This result argues against porting the black-benediction endpoint stack as a
whole. Under the public dependency stack, its B12X MLA/MoE/linear route is not
an RTX endpoint performance target for our EP-off OSL=128 no-prefix profile,
and the C=2 decode tail is much worse than the current customer baseline.

This does not reject every black-benediction idea. The branch remains valuable
as a mechanism reference, especially the smaller tuned TRITON_MLA decode and
SM120 shared-memory overflow fixes. Those should be isolated and tested
against our current route rather than adopting the full DFlash/B12X endpoint
stack. DFlash/spec-decode remains correctness-sensitive and must stay behind
GSM8K and semantic gates.

Profile sensitivity is explicit: this is RTX / SM120, EP-off, MTP=2, FP8 KV,
prefix-cache-off, OSL=128, random prompt evidence. It does not answer GB10 /
SM121 behavior or user prefix-cache workloads.

This also does not reject the Aiden image/forum route. That route is a bundled
GB10 image/overlay and operational profile, not just the public
`dev/black-benediction` branch reproduced with public dependencies. Treat it as
a separate watchlist item under
`docs/sm120/experiments/2026-06-13-aiden-recipe-forum-watch/README.md`.

## Follow-Up

- Create or update decision:
  `docs/sm120/decisions/watchlist/2026-06-12-backend-parity-roadmap.md`.
- Rerun trigger: black-benediction moves a non-DFlash decode or sparse-prefill
  mechanism; b12x changes the public DS4 route; or GB10 decode evidence shows
  a different bottleneck than RTX.
- Next command or next owner: isolate the lower-risk decode commits from
  black-benediction first, then measure RTX C=1/C=2 decode and GB10 reduced
  decode before touching DFlash/spec-decode.
