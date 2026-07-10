"""V5 cadence probe: same 93-AR graph, cadence controlled by env.

GAP_MODE=none      -> max-rate replays, NO drain gaps (tests pure replay rate)
GAP_MODE=paced     -> 30ms sleep between replays, drain gaps kept (decode-realistic)
GAP_MODE=orig      -> original protocol (back-to-back + 2.5s gap every 100)
INTRA_COMPUTE=1    -> insert a small matmul between ARs inside the graph
REPLAYS=<n>        -> replay count (default 1000)
"""
import os
import time

import torch
import torch.distributed as dist

rank = int(os.environ["RANK"])
gap_mode = os.environ.get("GAP_MODE", "orig")
intra = os.environ.get("INTRA_COMPUTE", "0") == "1"
replays = int(os.environ.get("REPLAYS", "1000"))
hb_every = int(os.environ.get("HB_EVERY", "100"))

dist.init_process_group("nccl")
torch.cuda.set_device(0)
xs = [torch.randn(2560, dtype=torch.bfloat16, device="cuda") for _ in range(93)]
hb = torch.randn(2560, dtype=torch.bfloat16, device="cuda")
a = torch.randn(512, 512, dtype=torch.bfloat16, device="cuda")
b = torch.randn(512, 512, dtype=torch.bfloat16, device="cuda")

for x in xs:
    dist.all_reduce(x)
torch.cuda.synchronize()
dist.barrier()

g = torch.cuda.CUDAGraph()
s = torch.cuda.Stream()
s.wait_stream(torch.cuda.current_stream())
with torch.cuda.stream(s):
    with torch.cuda.graph(g):
        for x in xs:
            dist.all_reduce(x)
            if intra:
                torch.mm(a, b)
torch.cuda.current_stream().wait_stream(s)
torch.cuda.synchronize()
dist.barrier()
if rank == 0:
    print(f"captured OK mode={gap_mode} intra={intra} replays={replays}", flush=True)

t0 = time.perf_counter()
for i in range(replays):
    g.replay()
    if gap_mode == "paced":
        torch.cuda.synchronize()
        time.sleep(0.03)
    if gap_mode == "hb" and i % hb_every == hb_every - 1:
        torch.cuda.synchronize()
        dist.all_reduce(hb)  # eager heartbeat on the SAME comm (vLLM prefill-interleave mimic)
        torch.cuda.synchronize()
    if i % 100 == 99:
        torch.cuda.synchronize()
        if rank == 0:
            print(f"replay {i + 1}/{replays} ok ({(time.perf_counter() - t0) * 1000 / (i + 1):.2f} ms avg)", flush=True)
        if gap_mode in ("orig", "paced"):
            time.sleep(2.5)
torch.cuda.synchronize()
dist.barrier()
if rank == 0:
    print("ALL REPLAYS OK", flush=True)
dist.destroy_process_group()
