# DeepSeek-V4 reasoning effort: what the tiers mean, and what reaches the model

Written 2026-08-10 while making `/v1/responses` behave. Everything here was
measured against the deployed stack or read out of source, not inferred from
documentation.

## The model has three tiers, not four

`vllm/tokenizers/deepseek_v4_encoding.py`:

```python
REASONING_EFFORT_PROMPTS = {
    "low":  "",                                    # no extra prompt at all
    "high": "Reasoning Effort: Absolute maximum with no shortcuts permitted…",
    "max":  "Reasoning Effort: Beyond maximum — exhaustive, relentless…",
}
DEFAULT_REASONING_EFFORT = "low"
```

`none` is not a tier: it means "do not think", and is handled by clearing
`enable_thinking` before a prompt is ever chosen.

## ★ The 0731 checkpoint shifted every tier down one

From smg PR [#2080](https://github.com/smg-project/smg/pull/2080), which adds
per-checkpoint effort detection:

> The 0731 refresh shifted the levels down one: the original's `max` text became
> 0731's `high`, and 0731's `max` is a new, stronger prompt.

```rust
Original => ["high", "max"]
V0731    => ["low", "high", "max"]     // what we serve
```

This is invisible from our own source, which ships only the 0731 table with
nothing to compare against — and it changes how the tiers should be read:

**`high` on 0731 is the original checkpoint's top tier.** Its prompt text still
says "Absolute maximum with no shortcuts permitted", which is the giveaway once
you know to look. Being unable to reach `max` is therefore not a compromise; it
is the ceiling the previous checkpoint had.

It also explains a measurement that looked oddly large: on one prompt, `high`
produced 2337 reasoning characters against `low`'s 1534 (+52%). `low` injects
**no prompt at all**, so the step from `low` to `high` is the whole distance
from "nothing" to the original's maximum.

## What each vocabulary accepts, measured end to end

Three vocabularies meet here and none of them agree:

| | values |
|---|---|
| model (0731) | `low` `high` `max` |
| DeepSeek API | `none` `low` `high` `max` — documented default **high** |
| OpenAI SDK | `none` `minimal` `low` `medium` `high` `xhigh` — **no `max`** |

Measured on the deployment:

| effort | `/v1/chat/completions` direct | `/v1/responses` direct | chat via smg | responses via smg |
|---|---|---|---|---|
| `none` | accepted | accepted, thinking off | accepted | accepted |
| `low` `medium` `high` | accepted | accepted | accepted | accepted |
| `xhigh` | accepted | accepted | accepted | **400** |
| **`max`** | accepted | **accepted** (after our fix) | **accepted** | **400** |

Only smg's **Responses** schema rejects `max` and `xhigh`. Chat completions
passes them through, which is the endpoint nearly every client uses.

Before our fix, `/v1/responses` rejected `max` at schema validation because it
reuses the OpenAI SDK's `Reasoning` type. `/v1/chat/completions` had always
accepted it — the two endpoints disagreed about the same model.

**smg rejects it on `/v1/responses` only.** That schema
(`crates/protocols/src/responses.rs`) declares
`enum ReasoningEffort { Minimal, Low, Medium, High }`. PR #2080 **merged
2026-08-10** without touching it — verified on `main` after the merge — so
upgrading smg does not help. The remaining work is a `Max` variant, and #2080
now argues for it: it added `V0731 => ["low", "high", "max"]`, so smg's own
tokenizer recognises a tier its HTTP schema turns away.

Measured through the gateway on chat completions, three reasoning problems
summed: `low` 9,038 chars, `high` 19,277, `max` 22,050. Monotonic, and the
prompts are genuinely distinct — `high` is "Absolute maximum…", `max` is
"Beyond maximum…".

## The mapping, which upstream already had

`DeepSeekV4Tokenizer.apply_chat_template` folds every spelling onto the model's
three tiers before the encoder ever sees it
(`vllm/tokenizers/deepseek_v4.py`, from upstream #50580):

| in | → | note |
|---|---|---|
| `none` | — | thinking switched off; no tier chosen |
| `max` | `max` | passes through |
| `low`, `minimal`, `medium` | **`low`** | all three collapse to the tier with no prompt at all |
| anything else, incl. `xhigh` | **`high`** | the catch-all, so a typo reasons at `high` rather than erroring |

This is worth reading twice, because two entries are not what the names suggest:
**`medium` is `low`, not something between**, and **`xhigh` is `high`, not
`max`**. The measurements match: on one prompt `low` gave 1534 reasoning
characters, `medium` 1633, `high` 2337.

★ **We add no mapping of our own.** A first draft of the `max` fix added a
second normalisation table in `deepseek_v4_encoding`; it was dropped once this
one was found, rather than left in as a competing source of truth. The trap is
worth naming: `encode_messages` asserts that effort is one of the three tiers,
and it is tempting to read a value that never trips that assert as "silently
swallowed". It is not — it was rewritten one layer up. Follow the value
upstream before concluding anything was lost.


## The default that makes `/v1/responses` behave

Production sets, per replica:

```
--default-chat-template-kwargs '{"thinking":true}'
```

Without it, `/v1/responses` called **without** a `reasoning` object — which is
what a stock OpenAI SDK does, and which is perfectly valid — renders in
non-thinking mode while the model thinks regardless. The reasoning and a bare
`</think>` then land inside `output_text`, looking like a normal answer:

| | `output` | `message` text |
|---|---|---|
| with the flag | `['reasoning', 'message']` | `8` |
| without it | `['message']` | `We need answer Chinese…</think>8` |

`/v1/chat/completions` is unaffected either way; the flag aligns the two paths.

★ Note that a **request-level** `chat_template_kwargs: {"thinking": true}` does
NOT fix it — only the server-level default does. The two reach the response-side
parser by different routes, which is the remaining thread if anyone wants the
root cause rather than the workaround.


## Sampling parameters: what the model card recommends, and what we run

The 0731 card, verified 2026-08-10:

> we recommend setting the sampling parameters to `temperature = 1.0`, with
> `top_p = 0.95` for **agentic scenarios** and `top_p = 1.0` **otherwise**

The recommendation is **conditional**, which is easy to lose when it gets
repeated as "0731 wants top_p 0.95".

| | card | what we serve |
|---|---|---|
| `temperature` | 1.0 | **1.0** |
| `top_p`, general | 1.0 | **1.0** |
| `top_p`, agentic | 0.95 | client passes it per request |

We serve the checkpoint's own `generation_config.json`
(`{"temperature": 1.0, "top_p": 1.0}`), read by
`ModelConfig.get_diff_sampling_param()` — confirmed on the running engine:

```
get_diff_sampling_param() -> {'temperature': 1.0, 'top_p': 1.0}
```

**Do not move the server default to 0.95.** It would match neither the
checkpoint's shipped config nor the card's "otherwise" case, and it would apply
an agentic-only value to ordinary chat. Agentic clients send `top_p: 0.95`
themselves; the two uses then each get the right value instead of one being
made wrong for the other.

Change the server default only if the deployment is *predominantly* agentic —
that is a serving-policy decision, and it should be made explicitly rather than
by reading the card's first clause.

★ `scripts/dgx_spark_start_mp_serve.sh` does contain a `--temperature 1.0`, but
it belongs to the prewarm benchmark, not the serve. It does not set a default.

### Output length at `high` / `max`

The card suggests a maximum output length of **384K tokens** for those tiers.
We run `MAX_MODEL_LEN=262144`, below that, on purpose: the quality knee for this
model is around 400K (64K native window, YaRN 16x, `index_topk: 512` covering
0.128% of a 400K context), and a 384K cold prefill would cost roughly six
minutes. Not a misconfiguration — a known ceiling, recorded so it is not
rediscovered as one.

### When the checkpoint changes

Re-check this section. The values live in the checkpoint, not in our config, so
a new snapshot can move them without anything in this repo changing:

```bash
cat $(find ~/.cache/huggingface/hub/models--deepseek-ai--<CKPT> \
  -name generation_config.json | head -1)
```

## Defaults still disagree, deliberately

vLLM's `DEFAULT_REASONING_EFFORT` is `low`; DeepSeek documents `high`. We did
**not** change it: every request that omits effort would get slower and more
expensive, and that is a serving-policy decision, not a bug fix. Set
`high` explicitly if you want DeepSeek's default.
