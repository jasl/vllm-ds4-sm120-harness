# jasl/vllm#19 — DeepSeek-V4 instruction-following regression (preview-dev vs full)

Status: fix committed + validated (no regression on standard metrics)
Date: 2026-06-17

## ⚠️ Correction (2026-06-17, after reading the full issue thread)

This fix does **NOT** close #19. The full thread shows:
- **aqua001** (reporter) tests with explicit `chat_template_kwargs:{enable_thinking:false}`
  and says the issue persists on the latest head — a path our `a8746555ef` restore
  does **not** change (verified: explicit-false → still prose).
- **v1b3coder** (second reporter) gave a same-line bisection: preview-dev
  `5dd7b972f` (06-04) **clean** → `5be22eb` (06-16) **regressed** — pinning the
  real regression to the 06-14 upstream-rebase window, *within* the preview-dev
  line. So the `full`-vs-preview `a8746555ef` difference does not explain it.

So the `a8746555ef` restore = a real **bare-request** default improvement (parity
with `full`), fast-forwarded onto the PR branch `codex/ds4-sm120-min-enable`
**locally (not pushed; backup ref `backup/min-enable-pre-api-semantics-20260617`
@ `73e99c165`)**. It is **not** the #19 fix. #19's actual cause is under
investigation via the `5dd7b972f`→`5be22eb` bisection. The "bare-request
prepending prose" framing in the sections below was *my* reproduction, not
aqua001's reported case — kept for the record, but read it with this correction.

## Report

`ds4-sm120-preview-dev` (= the PR line, `codex/ds4-sm120-min-enable`) adds an
explanatory prose preamble when the system prompt says "Output ONLY a JSON
array, no explanation"; `ds4-sm120-full` follows it (JSON-only). Reporter:
aqua001. Persists on PR head `73e99c165`, `temperature:0` (greedy), and with
`chat_template_kwargs:{enable_thinking:false}`.

## Root cause (workflow + reproduced on RTX, greedy)

Reproduced on the PR-line default serve:
- bare request (no thinking key) → thinking **OFF** → prose preamble + JSON;
- explicit `enable_thinking:false` → thinking OFF → prose preamble + JSON;
- thinking **ON** → reasons cleanly, then complies.

Ruled out (4-dimension analysis, both adversarial verifiers concur): MTP /
spec-decode (greedy-verify is output-neutral at temp=0; kernel byte-identical
to upstream), prompt rendering for *explicit* false (byte-identical both
branches), the D512 split/chunked prefill (gated ≥8192 tokens — #19's prompt is
~1.2k), and the reasoning parser (post-split only). The full-vs-preview-dev
comparison is also **confounded** by a ~1454-commit / 6-week rebase gap.

**The real, grep-confirmed divergence**: the PR line dropped full's
"Align DeepSeek-V4 API semantics" commit `a8746555ef` — the top-level `thinking`
request field, `apply_chat_template_kwargs` (bare DSv4 requests default thinking
**ON**), the `deepseek_v4_sampling_override`, the `reasoning_content` alias,
prefix/wo_eos messages, and DSv4 tokenizer tool-arg robustness. For **bare**
requests (the common API path) `full` defaults thinking ON (reasons → complies)
while preview-dev defaults OFF (answers directly → preamble). This is the
real-world regression. The reporter's **explicit** `enable_thinking:false` case
renders an identical prompt on both branches, so it is a *separate* residual
generation-quality softness (the documented PR-line GSM8K-strict ~0.92 /
toolcall-15 ~70% vs the ~0.965 fork), not fixed by this change.

## Fix

Ported `a8746555ef` onto the PR head → branch
`codex/ds4-sm120-dsv4-api-semantics-20260617`, commit `6aade4d75`, pushed.
Cherry-pick, 4 conflicts resolved by keeping the June PR's evolved code
(`build_chat_params` reasoning_effort handling; the dedicated
`DeepSeekV4ReasoningParser`) and layering the DSv4 semantics on top
(`serving._effective_chat_template_kwargs` applies `apply_chat_template_kwargs`
after `build_chat_params`). Pure-Python entrypoint; import-clean on RTX.

**Behavior validated** (source-shadow onto the built worktree, greedy):
| request | thinking engaged | content |
|---|---|---|
| bare (no thinking key) | YES (reasoning ~7.6k) | `["vLLM","CUDA","NVIDIA","Blackwell"]` — clean ✅ |
| top-level `thinking:{disabled}` | no | prose + JSON (field honored) ✅ |
| top-level `thinking:{enabled}` | YES | clean JSON ✅ |
| explicit `enable_thinking:false` | no | prose + JSON (residual softness, unchanged) |

So the fix repairs the **bare-request** path + honors the top-level `thinking`
field; the explicit-false residual softness is separate (tracked as the broader
PR-line quality gap).

**Scope**: this changes the *default* for bare DSv4 requests (→ thinking ON +
sampling override), matching `full` / DeepSeek-official. Right for the fork; a
design decision for the upstream minimal PR (land in #41834 vs a follow-up).

**Not related to prefill**: #19 is a single short request (D512-inert, no
concurrency) — it does not touch the (shelved) prefill concurrency bug; fixing
it does not affect prefill. The only shared theme is the broader sparse-MLA
generation softness (a separate quality track).

## Validation matrix (complete)

Same-setup A/B on RTX (TP=2, fp8 KV, MTP2). Each config source-shadows the 7
entrypoint files (baseline = HEAD `present=0`; fix = the branch `present=1`),
starts a fresh server (verified distinct pids, `serve UP ~75s` on warm page
cache), runs toolcall-15 (temp=1.0, repeat=3 → 45 case-runs/mode, scenario-set
en) + GSM8K-200 (5-shot, raw `/v1/completions`).

| config | toolcall-15 non-thinking | toolcall-15 think-high | GSM8K flex | GSM8K strict |
|---|---|---|---|---|
| baseline (no fix) | 70% (63/90) | 84% (76/90) | 0.940 | 0.915 |
| fix               | 67% (60/90) | 89% (80/90) | 0.950 | 0.935 |

**Verdict: no regression; no explicit-mode improvement either — all deltas are
temp=1.0 noise.** Per-case decomposition (passes/3 per case, baseline→fix):
- non-thinking: 7 cases flipped **bidirectionally** (+1,−1,−1,−2,+2,−1,+1), net ≈ 0.
- think-high: 6 cases flipped bidirectionally (3 up, 3 down), net ≈ +1 — the
  +5pp is scattered run-to-run variance, not a concentrated gain.
- GSM8K: 0.915→0.935 is within 1 stderr (~0.018) and fix-inert (raw completions).

This is the **expected** result: both harness modes set `thinking` *explicitly*,
so they bypass the fix's actual lever — the **bare-request** thinking default
(no thinking key → ON). In explicit non-thinking the fix is a near-no-op (only
DSv4 tool-arg robustness applies); in explicit think-high the sampling-override
fires but produced no consistent quality shift here. The fix's real value (the
bare-request instruction-following repair) is validated separately in the table
above (bare → thinking-ON → clean JSON), not by these explicit-mode metrics.

So the matrix confirms the fix is **safe to keep** (no standard-metric
regression), and the #19 repair itself is the bare-request behavior change.
(`rc=1` on the toolcall-15 runs = some cases below min-points, normal; all four
runs produced valid 45-case summaries.)

## Real-regression localization (32-agent offline workflow + window mining, 2026-06-17)

Adversarial diff-analysis of the local bracket `f32247a5a` (06-12, clean-side) →
`5be22eb0e` (06-16, regressed), 5 generation clusters, every finding refuted:
- **0 survivors / 26 refuted.** The 06-12→06-16 window is byte-equivalent for
  generation: MLA/attention kernel diffs are re-layout/whitespace; spec-decode
  changes are dynamic-SD-only (inert at static MTP2); the V2-runner sampler is
  unreachable (disabled for quantized DSv4); reasoning/EOS/stop/render path
  **unchanged**. So the regression is **not** in this window and **not** a
  06-12→06-16 kernel/build change.

**Methodological hole found:** v1b3coder's clean commit is `5dd7b972f` (**06-04**);
my clean-side proxy `f32247a5a` is **06-12** — so the diff is blind to anything
that entered **06-04→06-12**. `5dd7b972f` is gone from origin (force-pushed by the
06-14 rebase) and unfetchable. Mining `f32247a5a`'s own ancestry for that hidden
window shows it is **dominated by the SM12x sparse-MLA *decode* kernel
introduction + wiring + tuning** ("Add SM12x sparse MLA direct decode kernels",
"Wire SM12x sparse MLA into DeepSeek V4", MQA/topk retunes) — i.e. **compute**.
The only pure-Python generation commits there (reasoning-parser lint, "defensive
implicit `</think>`", tool-marker buffering) are **post-generation parsing** and
inert for aqua001's non-streaming, thinking-OFF request. No entrypoints / render /
protocol change in-window, and the workflow verified `build_chat_params` renders
an explicit `enable_thinking:false` payload byte-identically → **the prompt the
model sees did not change.**

**Leading hypothesis (by elimination, NOT yet confirmed):** the SM12x sparse-MLA
**decode kernel** (introduced 06-04→06-12) is numerically *softer* than the prior
path, degrading **greedy** generation quality → the #19 thinking-OFF
instruction-following regression. This would **unify** with the documented
sparse-MLA generation softness (GSM8K-strict ~0.92 / toolcall-15 ~70% vs the fork
~0.965) and the "ctx0 decode gap" note. The decode kernel that *leads the fork on
perf* may be a perf-win / quality-regression tradeoff.

**This revises the workflow's "pure-Python, no build-bisect" verdict** — that was
scoped to the only window it could see (06-12→06-16). The HIDDEN window contains
the kernel work, so a **build-bisect (or decode-path A/B) IS the confirmation
path** — GPU + builds. Elimination ≠ proof; do not claim confirmed.

Confirmation options (decision pending, GPU/build cost):
1. (free) Ask v1b3coder for the exact `5dd7b972f` (or a patch) to tighten the
   window before building.
2. (moderate) Direct `full`-vs-preview-dev greedy A/B on aqua001's exact request,
   if they use different decode paths — isolates the kernel without a bisect.
3. (expensive) Build-bisect across the 06-04→06-12 sparse-MLA-decode commits.

## full-vs-preview A/B on aqua001's EXACT request (RTX, 2026-06-17)

Both pre-built on RTX; aqua001's exact repro (explicit `enable_thinking:false`,
temp 0, the tagging prompt):

| build | output | tokens |
|---|---|---|
| `full` `a76b1a9be` (05-06, older/different MLA) | `["vLLM","NVIDIA","CUDA","Blackwell","NVFP4"]` clean | 23 |
| `preview` `ee1a079e6` (06-16, SM12x sparse-MLA decode) OFF | `好的，这是根据您提供的笔记内容生成的分类标签。` + ```` ```json ```` fenced array — **prose preamble + Chinese drift** | 44 |
| `preview` thinking-**ON** | reasons (1757 chars) → `["vLLM","Blackwell","NVFP4","LLM Inference"]` clean | 511 |

**CONFIRMED**: the regression reproduces on our HW with aqua001's exact request
(full complies; preview adds a prose preamble + markdown fence + drifts to
Chinese). **Trigger = thinking-OFF** (thinking-ON rescues on the *same* preview
build → the decode kernel is identical for both modes, so the thinking-OFF
direct-answer path is the fragile one).

**Still confounded** (full=05-06 vs preview=06-16 spans the whole 6-week gap), so
this confirms *existence + direction*, not the decode kernel specifically.
`a8746555ef` is ruled out for this case: full has it, but for explicit
`enable_thinking:false` its thinking-default branch is bypassed and its
sampling-override only applies when thinking is ON — so it does not explain the
explicit-off divergence (consistent with our ported fix being inert here).

**Leading hypothesis (unproven)**: the SM12x sparse-MLA **decode kernel** (new in
06-04→06-12; `full` uses a totally different older MLA) is numerically *softer*,
degrading thinking-OFF greedy instruction-following → #19. This plausibly
**unifies** with the broader sparse-MLA generation softness (GSM8K-strict ~0.92 /
toolcall-15 ~70% vs the fork ~0.965): the decode kernel that leads on perf may be
a perf-win / quality-regression tradeoff. **Proof requires the within-line
build-bisect** (build the commit before vs after "Wire SM12x sparse MLA into
DeepSeek V4", A/B aqua001's request) — GPU + builds, pending authorization. The
"fix" may then be decode-kernel numerics work (not a simple revert).

Serve gotchas hit + fixed (recorded for reuse): preview needs `gpu-mem 0.95` +
modest `max-model-len` (model eats 75.74 GiB/GPU → only ~3.2 GiB KV at 0.90, just
under the threshold); `full`'s serve needs the venv `bin` on PATH for ninja
(flashinfer JIT).

## Build-free bisect — VERDICT: sparse-MLA decode kernel (2026-06-17)

No genuinely pre-sparse-MLA build exists except `full` (the 06-07 and 06-12
worktrees already carry the decode kernel via a rebased SHA). So I served the
**old-MLA `full`** vs the **two earliest sparse-MLA builds** (both **pre-06-14-
rebase**), matched config (no-MTP — output-neutral at greedy + sidesteps
spec-config drift; `gpu-mem 0.95`, `max-len 8192`), aqua001's exact request:

| build | MLA | output |
|---|---|---|
| `full` `a76b1a9be` (05-06) | **old MLA** | `["vLLM","NVIDIA","CUDA","Blackwell","NVFP4"]` clean |
| `49910eea6` (06-07) | **sparse-MLA** | `好的，这是根据您提供的笔记内容生成的分类标签。` + ```` ```json ```` + `"LLM推理"` — prose |
| `591b71bed09` (06-12) | **sparse-MLA** | `好的，这是根据笔记内容生成的分类标签。` + ```` ```json ```` — prose |
| `preview` `ee1a079e6` (06-16, prior A/B) | sparse-MLA | prose |

**The regression flips exactly at old-MLA → sparse-MLA, present from the earliest
sparse-MLA build.** This **rules out**: the 06-14 upstream rebase (06-07/06-12 are
pre-rebase), **MTP** (reproduces with MTP off → greedy-neutral confirmed),
`a8746555ef`, and all post-06-07 upstream churn. Chinese drift (`好的…`) +
markdown-fence is a robust signature across every sparse-MLA build.

**VERDICT (confirmed to achievable granularity): the SM12x sparse-MLA *decode*
kernel is #19's root cause.** The decode kernel that leads the fork on perf
(shipped to the PR) is numerically *softer* → degrades thinking-OFF greedy
instruction-following. This **unifies #19 with the broader sparse-MLA generation
softness** (GSM8K-strict ~0.92 / toolcall-15 ~70% vs the fork ~0.965) — one root,
two symptoms.

Residual confound (honest): the 05-06→06-07 span (~1 month) isn't *purely* the
decode kernel; perfect isolation would need building the exact pre/post-sparse-
MLA commit (`ecc6a2468^` vs `4456c54e2`). But the sparse-MLA decode is the
dominant attention change *and* the component that generates the output tokens,
so it is the overwhelmingly likely cause — a build-bisect would tighten, not
overturn.

**Implication for the fix**: improve the sparse-MLA **decode numerics** (a real
kernel effort) — NOT a revert (that loses the perf win + SM120 decode enablement).
#19 is now the same track as the broader decode-quality gap. The `a8746555ef`
bare-request fix (on the PR branch, local) remains a separate, valid improvement
that does not touch this.

## Fixability — decode-variant + fork A/B (RTX, 2026-06-17): YES, achievable

Same-build gate A/B (rebased-dev, no-MTP, gpu-mem 0.95) + fork existence check,
aqua001's exact request:

| decode path | output |
|---|---|
| `full` old MLA (05-06) | clean |
| our **Triton sparse decode** (gate-off) | prose (Chinese drift) |
| our **FlashInfer SM120 runner** (gate-on, engaged @ `flashinfer_sm120_decode.py:156`) | prose (English preamble — no drift, still non-compliant) |
| **fork `FLASHINFER_MLA_SPARSE`** sparse-sm120 decode | **clean** |

**Two decisive conclusions:**
1. The decode-*kernel choice* (Triton vs our FlashInfer runner) is NOT the lever —
   **both of ours are soft**. So the cheap "just default the runner on" fix is out,
   and the culprit is **shared** between our two decode kernels → the **indexer
   (DSA top-k selection)** or the fp8-KV path, not the attention kernel itself.
2. **The fork's sparse-sm120 decode is CLEAN** → a clean sparse decode *exists*;
   the softness is **specific to our implementation**, NOT inherent to sparsity.

**VERDICT: fixable.** There is a concrete reference (the fork) and a narrowed
suspect (our shared sparse indexer/KV path). The fix = localize what our sparse
path does differently from the fork's (offline diff: indexer top-k, metadata,
fp8-KV layout), port it, validate (aqua001 + GSM8K + toolcall + no perf regression).
Real multi-step work with GPU validation, but tractable with a concrete target —
and it would close BOTH #19 and the broader generation-softness gap. Caveat: the
fork is a different codebase (the fork→clean is confounded by its whole stack),
so the diff narrows the lever rather than proving a single line; final proof is
the ported fix passing on our stack.

## Localization — cheap levers EXHAUSTED (RTX, 2026-06-17)

Indexer diff (ours 803 vs fork 774 lines) surfaced two SM12x-specific differences
ours introduced; both tested on aqua001's request, **both ruled out**:
- **`VLLM_SPARSE_INDEXER_MAX_LOGITS_MB`** (ours caps SM12x at 256 MB vs fork 512):
  override to **1024 → still prose** (flipped the preamble Chinese→English, core
  instruction-violation unchanged).
- **deep-gemm indexer-scheduler disabled on SM120** (ours adds `and not
  is_device_capability_family(120)`): enable it (pure-Python edit, deep_gemm
  import OK) → **still prose** (identical English-preamble output). Indexer
  restored (git-clean).

So the softness is **robust to indexer configuration** and persists across **all
three of our decode kernels** (Triton, FlashInfer runner, default) while the fork
is clean. The remaining structural difference is **the fork's dedicated
`flashinfer_mla_sparse_sm120.py` decode backend, which ours LACKS** (ours has only
the generic `flashinfer_mla_sparse.py` + Triton/runner). The lever is the **sparse
attention compute itself** (the fork's SM120 kernel is more accurate), not a
config/scheduler knob.

**Honest verdict on "can you fix it?": fixable in principle, but the cheap fixes
are exhausted.** The remaining path is a **substantial kernel effort** — port/adapt
the fork's `flashinfer_mla_sparse_sm120` decode (it depends on the fork's
flashinfer 0.6.12 `run_sparse_mla` kernel, *dropped* from flashinfer main), or a
deeper numerical-precision fix in our sparse attention (fp8-KV dequant /
accumulation / top-k selection precision). This is a dedicated multi-step project
with its own validation, NOT a one-line change. Recommended: tackle as a focused
follow-up, or accept the decode-quality tradeoff for now (the `a8746555ef`
bare-request fix is already banked on the PR branch; #19's explicit-thinking-off
softness stays a tracked quality-gap item, same root as GSM8K-strict/toolcall).

## "fallback-before-replacement" tag test — squash hypothesis REFUTED (2026-06-17)

User suspected the softness was introduced by the PR commit-squash/minimization,
and pointed at the believed-good tag `sm120-pr-41834-fallback-before-replacement-
20260612053720` (target commit `5d1584e2`, **06-10**). Built it (worktree +
editable build, arch 12.0a, ~10 min warm-ccache; the only "ERROR" was a harmless
`b12x torch>=2.12` pip warning), served it (gpu-mem 0.95, max-len 8192, no-MTP),
aqua001's exact request:

- **tag (06-10) → PROSE** (`Based on the note content, the primary subjects are…`
  + JSON) — the **same #19 softness** as current.

So the squash did **not** introduce it — the softness **predates** the tag. The
tag carries the sparse-MLA decode + 4 *extra* decode-kernel variants + a
`dequantize_combined_sparse_mla_decode_kv` step that current dropped, **and it's
still soft** → those dropped pieces are **not** the quality lever either. This
confirms the bisect: the softness is intrinsic to **our** sparse-MLA decode from
its introduction (~06-07/06-10), independent of squash/rebase/decode-kernel-
choice/indexer-config. The only clean sparse decode remains the **fork's**
`flashinfer_mla_sparse_sm120`. (The tag's "effective-good" reputation was likely
perf or a thinking-ON / different-prompt test; this explicit-thinking-OFF
instruction-following case is soft on the tag too.)

Build side effect (noted for cleanup): the editable build repointed the lucifer
venv's vllm to the tag worktree + downgraded its nccl 2.30.7→2.28.9 — harmless for
PYTHONPATH-override serves (2.28.9 served fine), restore with a `pip -e` of the
rebased-dev worktree if a no-PYTHONPATH import is ever needed.

**Net: cheap-fix avenues are fully exhausted** (decode-kernel choice, indexer
max-logits, deep-gemm scheduler, squash-restore — all ruled out). The remaining
fix is the substantial kernel effort: port/match the fork's `flashinfer_mla_
sparse_sm120` sparse decode, or a deeper precision fix in our sparse attention.

## Decode-code archaeology vs trusted tag — CONFIRMS upstream-shared root (2026-06-18)

Concern raised: a past context-compression event may have *corrupted* the decode
kernel ("kernel 崩坏"), making the current code an untrustworthy artifact. Tested
by diffing the **entire decode path** between the trusted tag `5d1584e2de2`
(`sm120-pr-41834-fallback-before-replacement-20260612`) and HEAD `ee1a079e633`:

| component | tag→HEAD |
|---|---|
| `flashmla.py` `_forward_decode` | **byte-identical** |
| `flashmla.py` `_forward_sparse_mla_compressed_decode_triton` | **byte-identical** |
| `flashmla.py` `_forward_sparse_mla_swa_decode_triton` | **byte-identical** |
| `cache_utils.py` (`compute_global_topk_indices_and_lens`) | **byte-identical** |
| `sparse_mla_kernels.py` (matmul/finish/accumulate/build-mask) | **semantically identical** (only black/ruff reflow) |

So the decode dispatch **and** the Triton attention kernels are unchanged since
the trusted tag (the 16 KB `flashmla.py` shrink is pure stats-instrumentation
removal). **The "kernel got corrupted during context loss" worry is disproven** —
the decode kernel was never the lever, and since the tag is *itself soft* (prior
section), the softness is **not a post-tag regression of any kind**.

`use_flattening` (indexer.py) **did** change in the rebase
(`use_fp4_indexer_cache AND next_n∉{1,2}` → `NOT is_device_capability_family(100)
AND next_n∉{1,2}`), flipping SM120+MTP from the native to the flattening indexer
decode path. **Exonerated**: the softness reproduces at **no-MTP** (next_n=1),
where both tag and HEAD compute `use_flattening=False` (no divergence).

**Sharpened root-cause hypothesis (the shared upstream component):** the **DSA
indexer top-k is scored on fp8-quantized KV** (indexer cache = block-fp8, "128 fp8
+ 4 scale bytes", `indexer.py:243`; `use_fp4_indexer_cache` is *disallowed* on
SM120 → always fp8). The **DeepSeek reference scores on bf16** and its code
explicitly flags fp8 as a quality tradeoff it declined: `# kv could also use fp8
format, though current implementation uses bf16` (`reference_inference/model.py`
Indexer.forward). fp8 top-k scoring → slightly-wrong position selection → subtle
thinking-OFF instruction softness; **shared by both our decode kernels** (they
consume the same top-k), matching "culprit shared between our two kernels."

**Honest caveat:** the fp8 indexer cache is *upstream vLLM's* DSA design
(`NOTE(Chen)`, "DeepSeek-V3.2"), so it is likely shared with the fork too → it is
a real gap **vs the bf16 reference** but may not be the **ours-vs-fork**
differentiator. Resolving that is exactly the user's chosen **走2**: a numerical
A/B against the reference ground truth (`reference_inference`), which *quantifies*
where our top-k / attention output diverges instead of guessing.

**Next: numerical localization (走2).** Reference indexer scoring is pure-torch
(`einsum("bshd,btd->bsht").relu_() * weights).sum(dim=2) → topk(512)`); reference
`sparse_attn` is an fp32 online-softmax with attn_sink (tilelang, trivially
re-expressible in torch). Plan: (1) measure top-k selection fidelity — our
fp8-indexer top-k vs the reference bf16 top-k on matched inputs (recall/overlap);
if high → indexer precision exonerated, gap is in attention fp8 dequant/accum; if
low → indexer precision confirmed. (2) localize the attention-output divergence
similarly. Fixing the shared indexer/KV path corrects **both** decode routes at
once (Triton default + FlashInfer runner), satisfying "Triton 路线也保持正常".

## 走2 Measurement 1 — attention KERNEL is FAITHFUL (RTX, 2026-06-18)

Sizing reframe first: `sliding_window=128`, aqua001 prompt ~1180 tok → ~295 (ratio-4)
/ ~9 (ratio-128) compressed positions, **both < `index_topk=512` → top-k SELECTION
is INACTIVE** (all positions selected) → selection, `index_topk` count, and fp8-KV
*value* precision (the clean `full` baseline ran on the same fp8 KV) are all
**exonerated** for this prompt. ~89% of context flows through the compressed path.

Instrumented the matmul sparse-MLA decode (`flashmla.py`, env-gated dump hook, 35-line
diff, git-revertible) and served HEAD **no-MTP, enforce-eager** (so the cpu/save dump
doesn't break CG capture), **matmul path forced** (`VLLM_TRITON_MLA_SPARSE_TOPK_CHUNK_SIZE=2048`),
aqua001's exact request. **Soft path reproduced in eager** (`好的，根据你的要求…` + JSON,
`reasoning_len:0`) → eager is not a confound; dumps are of the real soft run.

Dumped `(q, combined_kv, valid_tokens, attn_sink, scale, output)` for 159 real-decode
layer-calls (+41 warmup `valid=0` dumps, ignored). Offline fp32 recompute with the
EXACT reference semantics (full-576 QK·PV, denominator-only sink — verified vs both the
reference `sparse_attn` and our finish-kernel):

| | ratio-4 | ratio-128 |
|---|---|---|
| cosine (min/med/max) | —/**0.99998**/1.0 | —/**0.99999**/1.0 |
| rel-L2 (med) | 0.0053 | 0.0036 |

**VERDICT: our sparse-MLA attention kernel is numerically faithful to fp32** (rel-L2
~0.5% = pure bf16 rounding). The score/softmax/sink/value-reduction compute is **NOT**
#19's bug — closes that branch with a hard number (was prior-session indirect inference).
Selection complete (valid=428 = all ~295 compressed + 128 window) + kernel faithful →
the softness is in the kernel's **INPUTS**: `q` (query path) or `combined_kv` (compressor
output + fp8 dequant). `q` is the standard MLA query shared with the clean dense `full`
path → prime suspect is **`combined_kv` (the compressor's downsampled KV)**, which carries
89% of aqua001's context and is the thing that distinguishes our soft sparse path from the
clean dense baseline. → Measurement 2: validate the compressed-KV values vs the reference
compressor. Driver `.local-tmp/run_issue19_capture.sh`; analyzer
`/tmp/issue19_archaeology/analyze_decode_faithfulness.py`.

## 走2 M2+M3 — compressor + RoPE + scale ALL FAITHFUL (RTX, 2026-06-18)

Captured the compressor's prefill `kv_score` + the decode `combined_kv`/slot order
(`.local-tmp/run_issue19_capture2.sh`; instrumented `compressor.py` + `flashmla.py`,
git-revertible). **Methodology note**: the first M2 run was INVALID (caught the 8192-token
startup-warmup prefill, not aqua001's ~1180-tok real prefill; + slot-order misalignment) —
red flags (cos≈0 random, nRef=2048, slotAsc=False) flagged it; NOT reported as a finding.
Fixed: `<4096`-tok filter skips warmup; **alignment-free** best-cosine matching (our
compressed candidates are in block-structured cache-slot order with -1 sentinels, not
position order — match each reference token to its nearest twin in our set instead).

| Measurement | metric | verdict |
|---|---|---|
| M2 compressor pool/overlap/APE/norm (nope, pre-RoPE) | bestRef cosine **0.99965** med (all 41 layers, nValid==nRef) | FAITHFUL |
| M3 compressed-KV RoPE (reference YaRN θ=160000, pos i·ratio) | ropeCos **1.00000** all layers | FAITHFUL |
| softmax scale | ref `head_dim**-0.5`=0.04419 == our `layer.scale` | FAITHFUL |

Code-confirmed: `build_deepseek_v4_rope` uses `compress_rope_theta=160000`+`deepseek_yarn`
+`is_neox_style=False` for compress layers — matches reference. Analyzers:
`/tmp/issue19_archaeology/analyze_compressor_faithfulness.py` + `analyze_compressor_rope.py`.

**PARADOX (the real state):** kernel ✓ (M1, 0.99998) + compressor ✓ (M2) + RoPE ✓ (M3) +
scale ✓ + selection ✓ — the entire measurable sparse-decode pipeline is faithful to the
reference, yet output is soft. The attention-kernel inputs still **unverified vs the
reference** (M1 took them as given → a shared error wouldn't surface): (1) the **query `q`
values** (wq_b/q_norm/q-RoPE); (2) the **SWA window KV** part of `combined_kv` (recent-128 raw
KV from the separate `swa_cache_layer` — the two-cache decomposition that most differs from
the reference's single cat([window,compressed]) tensor); (3) the **window `valid_tokens`**
(swa_lens/decode_swa_indices); (4) **attn_sink loading** (TP head mapping). Next: an
end-to-end reference-attention recompute on captured per-layer hidden states (pure torch +
checkpoint weights + the verified fp32 sparse_attn) validates all of q/window/sink at once.
GPU-hygiene: eager-serve teardown can orphan a spinning kernel on a TP worker (saw GPU1
@128W/no-process); `sudo nvidia-smi --gpu-reset -i 1` clears it.

## 走2 DECIDER — reference is CLEAN → it's a BUG, NOT inherent (RTX, 2026-06-18)

Ran the **DeepSeek reference implementation end-to-end on SM120** (the user's ground truth)
on aqua001's EXACT request (system+user, `thinking_mode="chat"`=thinking-off, greedy temp=0):

```
REFERENCE VERDICT: JSON-ONLY (clean)
["vLLM", "NVIDIA", "CUDA", "Blackwell", "NVFP4"]
```

**The reference — which IS sparse (compressed + window + sparse_attn / DSA) — produces CLEAN
JSON-only**, identical to the clean `full` dense baseline. Our sparse-MLA is SOFT (prose).
**⟹ #19's thinking-off softness is NOT inherent to DSA; it is a BUG in OUR implementation.**

Reconciles the M1/M2/M3 paradox: the components I verified faithful (compressed-KV values,
attention-kernel math, RoPE, scale) are **not** where the bug is. The bug is in the inputs I
did NOT verify vs the reference: **`q`, the SWA window KV, the window `valid_tokens`, or the
window+compressed COMBINATION** — i.e. exactly the **two-cache decomposition** (our separate
`swa_cache_layer` raw-window + compressed cache, two-pass) vs the reference's single
`kv = cat([window_raw, compressed])` + single `topk_idxs = cat([window_idxs, compress_topk])`
+ ONE `sparse_attn`. Prime suspect: the window handling / a window↔compressed double-count or
disjointness bug (reference keeps them disjoint by construction; ours may not).

Setup that made the reference run on SM120 (reusable):
- tilelang 0.1.9 works on SM120 with the **system CUDA 13.3** toolkit (`CUDA_HOME=/usr/local/cuda`,
  `PATH=/usr/local/cuda/bin:...`); the venv's bundled cu13 nvcc is mismatched ("CUDA compiler and
  toolkit headers incompatible").
- `sparse_attn_kernel` shared mem (q+kv+o+acc with h=32 @ MP=2) exceeds SM120's ~99KB opt-in;
  reduce `kernel.py` `num_stages 2→1` + `block 64→32` (numerically identical; block≥32 required —
  `warp_col_tiles≥8`). Writable code copy at `/home/jasl/tmp/ds4_ref/{inference,encoding}` (HF
  snapshot files are blob symlinks → `cp -rL`).
- `fast_hadamard_transform` sdist build is broken (missing csrc); pure-torch FWHT shim
  (`/home/jasl/tmp/ds4_ref/fast_hadamard_transform.py`) suffices — it only feeds the indexer's
  top-k *selection*, inactive for aqua001's all-selected short prompt.
- `convert.py` MP=2 fp4 → 2×81GB shards `/home/jasl/tmp/dsv4_ref_ckpt/`; driver
  `/home/jasl/tmp/ds4_ref/ds4_ref_run.py` + `run.sh` (torchrun 2-proc). Reference encodes
  aqua001 to 1200 tokens, fits 81GB/GPU.

NEXT: localize within {q, SWA window KV, window valid_tokens, combination}. Capture the
reference's per-layer attention OUTPUT (the reference run can dump it) vs ours on the same
hidden states; or instrument our SWA window path + compare to the reference's window handling.

## 走2 PER-LAYER LOCALIZATION — bug is the C4A (ratio-4) PREFILL attention (RTX, 2026-06-18)

Dumped the **per-layer attention-block output** (post-o_proj, last prompt position) for BOTH
the reference (patched `model.py` `_ref_dump_x`, refdump/) and ours (patched `attention.py`
`_our_attn_dump`, our_attn_dump/) on aqua001's identical prompt, compared by layer order
(`compare_layers.py`). Layer-0 cosine 0.998 confirms prompts match → comparison valid.

| layer | type | cosine(ref,ours) |
|---|---|---|
| 0,1 | SWA (ratio 0) | 0.998, 0.997 ✓ |
| **2** | **compress ratio-4 (C4A)** | **0.769 ← FIRST sharp drop** |
| 3 | ratio-128 (C128A) | 0.872 |
| 4,6,8,… | ratio-4 | 0.61/0.49/0.51… (worst) |

**VERDICT: the bug is in the C4A (compress-ratio-4) PREFILL sparse-MLA attention.** Layer 2
(first C4A) diverges hard (0.769) with MATCHED input (layers 0,1 SWA faithful 0.998); ratio-4
layers are worst, SWA clean. Key: M1 verified the **decode** matmul kernel, but PREFILL uses a
DIFFERENT path (`_forward_sparse_mla_prefill_triton` / indexed-D512) — unverified until now, and
it's what processes the prompt → determines the first (divergent) token. So the prior M1/M2/M3
"faithful" results stand (decode kernel, compressor values, RoPE, scale, q) — the bug is the
**prefill C4A attention compute** (kernel / window / combination), NOT decode. C4A-specific:
indexer + overlap-compressor + ~300 compressed positions (selection still inactive: 299<512).
NEXT: instrument the C4A prefill attention (its q/kv/topk inputs + output) vs the reference's
single `sparse_attn(q, cat([raw,compressed]), topk_idxs)` at layer 2 to pinpoint kernel-vs-
window-vs-combination, then fix. GPU-hygiene: eager teardown orphaned a kernel again (GPU@100%/
no-proc); `sudo nvidia-smi --gpu-reset` clears.

## 走2 ROOT CAUSE — C4A prefill DROPS the compressed positions (RTX, 2026-06-18)

M1-style prefill-kernel faithfulness check (`analyze_prefill_faithfulness.py` on dumped C4A
prefill inputs+output): **prefill KERNEL is FAITHFUL** — cosine **1.00000** layers 2-40 (our
output == fp32 attention over its inputs). So the bug is in the kernel's INPUTS. Captured the
reference's layer-2 `kv`+`topk_idxs` (`refkv_*.pt`) and compared:

- Reference layer-2 attends **428** positions = window(128, raw recent) + **compressed(300)**.
- OURS: `combined_lens=427` but `combined_indices` has only **128 valid (≥0)**; the ~299
  compressed slots are **-1 sentinels**.
- By-VALUE NN match (layouts differ so index-compare is invalid): our 128 attended-KV match the
  reference's **WINDOW at cosine 0.9988**, the reference's **COMPRESSED at only 0.1456**.

**ROOT CAUSE: our C4A PREFILL `combined_indices` populates the 128 window positions but leaves the
~300 compressed (indexer-selected) slots as -1 → the prefill attends to ONLY the recent-128 raw
window, DROPPING all distant downsampled context** (incl. the early "output ONLY JSON" instruction).
→ corrupted prompt representation → ignores the instruction (#19) + degrades all long-context
generation (same root as GSM8K/toolcall softness). Decode (M1-faithful) then generates faithfully
from the corrupted cache. **Definitively a BUG, fixable** (populate the compressed indices in the
C4A prefill combined-index construction). Confirmed rigorous: kernel-faithful + combined_lens(427)
vs valid(128) inconsistency + 0.9988-window/0.146-compressed value match.

## 走2 MECHANISM — DSA indexer doesn't populate the PREFILL top-k (RTX, 2026-06-18)

Dumped the C4A prefill `topk_indices` (the indexer output fed to `combine_topk_swa_indices`):
**ALL -1, n_valid=0, width=512, across all 21 C4A layers.** So `combine_topk_swa_indices` is
CORRECT (faithfully merges window + all-(-1) compressed). **The DSA INDEXER is not writing the
PREFILL top-k into `topk_indices_buffer`** (it stays at the -1 init).

Traced: C4A reads `topk_indices_buffer[num_decode_tokens:][:num_prefill_tokens]`; the indexer
(`DeepseekV4Indexer`→`SparseAttnIndexer`→`sparse_attn_indexer()` in
`vllm/model_executor/layers/sparse_attn_indexer.py`) inits `topk_indices_buffer[:n]=-1` (line 230)
then `if has_prefill:` writes `topk_indices_buffer[chunk.token_start:token_end,:topk]` via the fused
`fp8_fp4_mqa_topk_indices` (SM120: only when q_scale is None) or the fallback `fp8_fp4_mqa_logits`+
`ops.top_k_per_row_prefill` (lines 276-316). Decode path (`if has_decode`) works (M1).

A 16-token dummy-batch dump showed the indexer **builds prefill chunks correctly** (`n_chunks=1`,
`chunk.token_start=7=num_decode_tokens` — right coordinate) → candidates (a) empty-chunks and (b)
mis-targeted-write are unlikely. **Prime suspect (c): the SM120 prefill-topk write silently no-ops**
(the prefill uses the SM12x `fp8_fp4_mqa_logits`+`top_k_per_row_prefill` fallback — exactly the
SM100-family-tuned path the rebase's `use_flattening` change flagged as SM120-limited; cf. indexer.py
"the FP8 paged MQA logits kernel only supports next_n∈(1,2) outside SM100"). This is **upstream-shared**
code (deepseek_v2 / V3.2-on-B200 works), so the bug is SM120-specific.

**STATUS: root cause + mechanism rigorously confirmed; #19 is a fixable SM120 indexer-prefill bug.**

## 走2 ROOT CAUSE NAILED + FIXED + VALIDATED (RTX, 2026-06-18)

**Exact bug (non-contiguous output stride):** `sm12x_deep_gemm_fallbacks.py::_fp8_mqa_logits_topk_triton`
calls the custom op `top_k_per_row_prefill`, which writes its output **as a contiguous `[M, select_k]`
buffer** (it is given the *logits* strides, not the output's). But `selected = out[:, :select_k]` is
**non-contiguous whenever `select_k = min(topk_tokens, N) < topk_tokens`** — i.e. when the compressed-KV
count `N < index_topk (512)`. Standalone proof: non-contig `out[M,512][:, :300]` → nvalid 776/1200,
**last row 0**; contiguous `out[M,300]` → 1200/1200, last row 300. So the op silently corrupts the later
rows → those queries get all-(-1) top-k → C4A prefill drops the compressed/distant context → the model
attends only the recent-128 raw window → ignores the early instruction (#19) and garbles long-context
output (arthur's GB10 mixed-script report). Triggers for SHORT prompts (aqua001: N≈300<512, all queries)
and the EARLY/short-context queries of LONG prompts (arthur). The 8192-tok warmup used N=2048→select_k=512
=width→contiguous→looked fine (why it wasn't caught). This is the "accidentally dropped" contiguous
handling.

**Fix:** hand `top_k_per_row_prefill` a contiguous work buffer (`selected.contiguous()`) and copy back;
no-op when already contiguous (select_k==topk_tokens), so zero behavior change outside the buggy case.
The chunked long-context variant (`_fp8_mqa_logits_topk_triton_chunked`) was already safe (stride-aware
`torch.topk(out=)`/`torch.gather(out=)`). Corrects the prompt representation for BOTH decode routes at once.

**VALIDATED (RTX SM120, aqua001 exact request, thinking-off greedy):** `VERDICT: JSON-ONLY (clean)` →
`["vLLM","NVIDIA","CUDA","Blackwell","NVFP4"]` — matches the DeepSeek reference + full-MLA baseline; the
prose preamble is gone. One-spot fix in `vllm/models/deepseek_v4/nvidia/ops/sm12x_deep_gemm_fallbacks.py`
(uncommitted in the rebased-dev worktree). Likely also fixes arthur's GB10 (SM121) long-context gibberish
(same root) and the broader GSM8K-strict/toolcall generation-softness. PENDING: broader validation
(GSM8K + toolcall-15 + no perf regression) before promoting to PR#41834.

Box instrumentation reverted (git-clean except the fix); reference run env at `/home/jasl/tmp/ds4_ref/`;
analyzers preserved. NOTE: eager+TP teardown orphaned a spinning kernel 3× this session — `sudo nvidia-smi
--gpu-reset -i N` clears.
