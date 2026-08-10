# Engine conformance probes

Behaviour any OpenAI-compatible inference server should get right, checked from
the outside. These are **not** vLLM regression gates — they exist so that a new
implementation (TokenSpeed, or whatever follows) can be held to the same bar
without rediscovering each trap the hard way.

Two rules keep them portable:

- **No engine-specific names in the verdict.** Metrics like
  `vllm:prefix_cache_hits_total` are read when present and printed as
  corroboration, but never decide the result. A probe that keys off them
  reports INCONCLUSIVE on the next engine instead of testing it.
- **Refuse to guess.** Each probe first establishes that the machine can
  demonstrate the effect at all, and exits INCONCLUSIVE if it cannot. A probe
  that passes because nothing happened is worse than no probe.

## `prefix_cache_session_switch.py`

Does a conversation keep its prefix cache while another conversation runs?

```bash
./prefix_cache_session_switch.py --base-url http://HOST:8000 --model MODEL
```

Reported against some vLLM builds in 2026-08: A warm is instant, B runs once,
and A pays the full cold prefill again — with the KV pool nearly empty and no
preemption. The cause is a freed-but-still-cached block being handed to the
next allocation, dropping its hash on the way out.

Upstream fixed it in [#42656](https://github.com/vllm-project/vllm/pull/42656)
(2026-06-16) by splitting the free queue: blocks with no hash are prepended and
consumed first, blocks still carrying a cache entry are appended and touched
only when nothing else remains. **Any engine with an LRU block cache has the
same trap to avoid.**

Measured on this fork at `aa0d513027`, 2026-08-10, at the scale the report
describes (~100 s cold prefill):

```
A cold       121.46s   engine hit   0.0%
A warm         1.82s   engine hit 100.0%
B cold       121.45s   engine hit   0.0%
A after B      1.53s   engine hit 100.0%     <- survives
B after A      1.25s   engine hit 100.0%     <- survives
```

Not reproduced there, nor at ~48 s or ~3 s prefills. What this establishes is
narrow and worth stating as such: **the specific alternating-pair path does not
reproduce here.** It does not cover many-way rotation, genuine capacity
eviction, or a client that reorders turns.

### Exit codes

`0` healthy, `1` the cache did not survive a switch, `2` inconclusive. Verified
both ways: `--tokens 60` returns 2 with "warm is only 0.9x faster than cold",
`--tokens 40000` returns 0.

## Related

`../acceptance/reasoning_effort_matrix.sh` is the same kind of probe for
DeepSeek-V4 thinking and reasoning-effort semantics — silence defaults,
`effort: none`, every spelling on both endpoints, and whether effort actually
moves reasoning depth. It lives under `acceptance/` because it currently gates
our own releases, but it is engine-agnostic in the same way and applies to
anything serving this model.
