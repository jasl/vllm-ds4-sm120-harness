from __future__ import annotations

import argparse
import json
import sys
import time
import urllib.error
from pathlib import Path
from typing import Any

from ds4_harness.bench import run_bench_command
from ds4_harness.cases import SmokeCase, build_cases, select_cases
from ds4_harness.checks import CheckResult, assistant_text, check_chat_response, tool_call_names
from ds4_harness.client import get_json, get_status, post_json
from ds4_harness.gpu_stats import summarize_gpu_csv, write_gpu_json, write_gpu_markdown
from ds4_harness.oracle import (
    attach_prompt_token_ids,
    compare_response,
    load_oracle_cases,
    token_ids_from_tokenize_response,
)
from ds4_harness.oracle_export import export_completion_oracles
from ds4_harness.runtime_stats import (
    summarize_runtime_stats,
    write_runtime_json,
    write_runtime_markdown,
)
from ds4_harness.run_environment import (
    summarize_run_environment,
    write_run_environment_json,
    write_run_environment_markdown,
)
from ds4_harness.toolcall15 import run_suite


DEFAULT_MODEL = "deepseek-ai/DeepSeek-V4-Flash"
DEFAULT_BENCH_DATASET = "hf"
DEFAULT_BENCH_DATASET_PATH = "philschmid/mt-bench"


def _write_jsonl(path: Path | None, row: dict[str, Any]) -> None:
    if path is None:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")


def _content_text(content: Any) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for item in content:
            if isinstance(item, dict) and isinstance(item.get("text"), str):
                parts.append(item["text"])
            else:
                parts.append(json.dumps(item, ensure_ascii=False, indent=2))
        return "\n\n".join(part for part in parts if part)
    if content is None:
        return ""
    return json.dumps(content, ensure_ascii=False, indent=2)


def _fenced_block(text: str, language: str = "text") -> str:
    fence = "```"
    while fence in text:
        fence += "`"
    return f"{fence}{language}\n{text.rstrip()}\n{fence}"


def _write_chat_markdown(path: Path | None, rows: list[dict[str, Any]]) -> None:
    if path is None:
        return

    lines = [
        "# Chat Smoke Report",
        "",
        f"- Cases: {len(rows)}",
        "",
    ]
    for row in rows:
        case = row["case"]
        result = row["result"]
        response = row["response"]
        status = "PASS" if result.ok else "FAIL"

        lines.extend(
            [
                f"## {case.name}",
                "",
                f"- Status: {status}",
                f"- Tags: {', '.join(case.tags)}",
                f"- Check: {result.detail}",
                "",
                "### Prompt",
                "",
            ]
        )
        for message in case.messages:
            role = message.get("role", "unknown")
            lines.extend(
                [
                    f"#### {role}",
                    "",
                    _fenced_block(_content_text(message.get("content"))),
                    "",
                ]
            )

        text = assistant_text(response)
        if text:
            lines.extend(["### Assistant", "", _fenced_block(text), ""])

        names = tool_call_names(response)
        if names:
            lines.extend(["### Tool Calls", ""])
            lines.extend(f"- `{name}`" for name in names)
            lines.append("")

        if "error" in response:
            lines.extend(["### Error", "", _fenced_block(str(response["error"])), ""])

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def _print_case_result(case: SmokeCase, result: CheckResult, response: dict[str, Any]):
    status = "PASS" if result.ok else "FAIL"
    print(f"{status} {case.name}: {result.detail}")
    text = assistant_text(response).replace("\n", " ")[:280]
    if text:
        print(f"  content: {text}")
    names = tool_call_names(response)
    if names:
        print(f"  tool_calls: {names}")


def _cmd_list_cases(args: argparse.Namespace) -> int:
    cases = select_cases(
        build_cases(args.model),
        names=args.case,
        tags=args.tag,
        exclude_tags=args.exclude_tag,
    )
    for case in cases:
        print(f"{case.name}\t{','.join(case.tags)}\tmax_tokens={case.max_tokens}")
    return 0


def _cmd_health(args: argparse.Namespace) -> int:
    health = get_status(args.base_url, "/health", args.timeout)
    print(json.dumps({"path": "/health", "response": health}, ensure_ascii=False))
    if int(health["status_code"]) >= 400:
        return 1

    models = get_json(args.base_url, "/v1/models", args.timeout)
    print(json.dumps({"path": "/v1/models", "response": models}, ensure_ascii=False))
    return 0


def _cmd_chat_smoke(args: argparse.Namespace) -> int:
    cases = select_cases(
        build_cases(args.model),
        names=args.case,
        tags=args.tag,
        exclude_tags=args.exclude_tag,
    )
    if not cases:
        print("No smoke cases selected.", file=sys.stderr)
        return 2

    failures = 0
    markdown_rows: list[dict[str, Any]] = []
    for case in cases:
        payload = case.to_payload(
            default_max_tokens=args.max_tokens,
            default_temperature=args.temperature,
        )
        try:
            response = post_json(
                args.base_url,
                "/v1/chat/completions",
                payload,
                args.timeout,
            )
            result = check_chat_response(case.expectation, response)
        except (
            OSError,
            RuntimeError,
            TimeoutError,
            urllib.error.URLError,
            json.JSONDecodeError,
            ValueError,
        ) as exc:
            response = {"error": repr(exc)}
            result = CheckResult(False, f"request failed: {exc!r}")

        _print_case_result(case, result, response)
        _write_jsonl(
            args.jsonl_output,
            {
                "case": case.name,
                "tags": case.tags,
                "ok": result.ok,
                "detail": result.detail,
                "payload": payload,
                "response": response,
            },
        )
        markdown_rows.append(
            {
                "case": case,
                "result": result,
                "response": response,
            }
        )
        failures += 0 if result.ok else 1
    _write_chat_markdown(args.markdown_output, markdown_rows)
    return 1 if failures else 0


def _cmd_oracle_compare(args: argparse.Namespace) -> int:
    failures = 0
    rows: list[dict[str, Any]] = []
    for case in load_oracle_cases(args.oracle_dir):
        request_payload = dict(case.request)
        if args.model is not None:
            request_payload["model"] = args.model
        if (
            isinstance(request_payload.get("logprobs"), int)
            and request_payload["logprobs"] > args.top_n
        ):
            request_payload["logprobs"] = args.top_n
        try:
            response = post_json(
                args.base_url,
                case.path,
                request_payload,
                args.timeout,
            )
            if args.require_prompt_ids:
                tokenize_payload = {
                    "model": request_payload.get("model"),
                    "prompt": request_payload.get("prompt"),
                }
                tokenize_response = post_json(
                    args.base_url,
                    "/tokenize",
                    tokenize_payload,
                    args.timeout,
                )
                response = attach_prompt_token_ids(
                    response,
                    token_ids_from_tokenize_response(tokenize_response),
                )
            report = compare_response(
                case.name,
                case.response,
                response,
                top_n=args.top_n,
            )
            ok = True
            if args.require_prompt_ids and report["prompt_token_ids_match"] is not True:
                ok = False
            if args.require_token_match and not report["tokens_match"]:
                ok = False
            if (
                args.min_top1_match_rate is not None
                and report["top1_match_rate"] is not None
                and report["top1_match_rate"] < args.min_top1_match_rate
            ):
                ok = False
            report["ok"] = ok
        except (
            OSError,
            RuntimeError,
            TimeoutError,
            urllib.error.URLError,
            json.JSONDecodeError,
            ValueError,
        ) as exc:
            report = {
                "name": case.name,
                "path": case.path,
                "ok": False,
                "error": repr(exc),
            }
        print(json.dumps(report, ensure_ascii=False))
        rows.append(report)
        failures += 0 if report["ok"] else 1

    if args.json_output is not None:
        args.json_output.parent.mkdir(parents=True, exist_ok=True)
        args.json_output.write_text(
            json.dumps(rows, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
    return 1 if failures else 0


def _cmd_oracle_export(args: argparse.Namespace) -> int:
    rows = export_completion_oracles(
        base_url=args.base_url,
        model=args.model,
        output_dir=args.output_dir,
        case_names=args.case,
        timeout=args.timeout,
        logprobs=args.logprobs,
        stop_on_error=args.stop_on_error,
    )
    failures = 0
    for row in rows:
        print(json.dumps(row, ensure_ascii=False))
        failures += 0 if row.get("ok") else 1
    return 1 if failures else 0


def _check_bench_result(result: dict[str, Any], expected_requests: int) -> tuple[bool, str]:
    if result["returncode"] != 0:
        return False, f"vllm bench exited {result['returncode']}"

    successful = result["metrics"].get("successful_requests")
    if successful is None:
        return False, "successful_requests metric missing"
    if successful != expected_requests:
        return (
            False,
            f"successful_requests {successful} != expected {expected_requests}",
        )
    return True, f"successful_requests {successful}/{expected_requests}"


def _server_responding(base_url: str, timeout: float) -> bool:
    try:
        response = get_status(base_url, "/health", timeout)
    except Exception:
        return False
    try:
        return int(response.get("status_code", 599)) < 400
    except (TypeError, ValueError):
        return False


def _generation_responding(base_url: str, model: str, timeout: float) -> bool:
    payload = {
        "model": model,
        "prompt": "Reply with OK.\n",
        "max_tokens": 1,
        "temperature": 0.0,
    }
    try:
        response = post_json(base_url, "/v1/completions", payload, timeout)
    except Exception:
        return False
    return isinstance(response.get("choices"), list)


def _server_responding_after_grace(
    base_url: str,
    *,
    model: str,
    health_timeout: float,
    generation_timeout: float,
    grace_timeout: float,
    grace_interval: float,
) -> bool:
    deadline = time.monotonic() + max(0.0, grace_timeout)
    while True:
        if _server_responding(base_url, health_timeout) and _generation_responding(
            base_url,
            model,
            generation_timeout,
        ):
            return True
        if time.monotonic() >= deadline:
            return False
        remaining = deadline - time.monotonic()
        time.sleep(min(max(0.1, grace_interval), max(0.0, remaining)))


def _cmd_bench_matrix(args: argparse.Namespace) -> int:
    concurrencies = [int(value) for value in args.concurrency.split(",") if value]
    health_base_url = args.base_url or f"http://{args.host}:{args.port}"
    rows: list[dict[str, Any]] = []
    failures = 0
    for concurrency in concurrencies:
        command = [
            args.vllm_bin,
            "bench",
            "serve",
            "--model",
            args.model,
            "--tokenizer-mode",
            args.tokenizer_mode,
            "--dataset-name",
            args.dataset_name,
            "--num-prompts",
            str(args.num_prompts),
            "--max-concurrency",
            str(concurrency),
        ]
        if args.base_url:
            command.extend(["--base-url", args.base_url])
        else:
            command.extend(["--host", args.host, "--port", str(args.port)])
        if args.dataset_name == "random":
            command.extend(
                [
                    "--random-input-len",
                    str(args.random_input_len),
                    "--random-output-len",
                    str(args.random_output_len),
                ]
            )
        elif args.dataset_path:
            command.extend(["--dataset-path", args.dataset_path])
        else:
            print(
                f"--dataset-path is required for dataset {args.dataset_name!r}",
                file=sys.stderr,
            )
            return 2
        if args.ignore_eos:
            command.append("--ignore-eos")
        if args.temperature is not None:
            command.extend(["--temperature", str(args.temperature)])
        command.extend(args.extra_bench_arg or [])

        result = run_bench_command(command, timeout=args.timeout)
        ok, detail = _check_bench_result(result, args.num_prompts)
        row = {
            "concurrency": concurrency,
            "ok": ok,
            "detail": detail,
            "metrics": result["metrics"],
            "command": result["command"],
        }
        rows.append(row)
        failures += 0 if row["ok"] else 1
        print(json.dumps(row, ensure_ascii=False))
        if args.log_dir is not None:
            args.log_dir.mkdir(parents=True, exist_ok=True)
            (args.log_dir / f"bench_c{concurrency}.log").write_text(
                result["stdout"],
                encoding="utf-8",
            )
        if (
            not ok
            and args.stop_on_unresponsive
            and not _server_responding_after_grace(
                health_base_url,
                model=args.model,
                health_timeout=args.health_timeout,
                generation_timeout=args.failure_probe_timeout,
                grace_timeout=args.failure_grace_timeout,
                grace_interval=args.failure_grace_interval,
            )
        ):
            for skipped_concurrency in concurrencies[len(rows) :]:
                skipped = {
                    "concurrency": skipped_concurrency,
                    "ok": False,
                    "skipped": True,
                    "detail": "server unresponsive after previous benchmark; skipped",
                    "metrics": {},
                    "command": None,
                }
                rows.append(skipped)
                print(json.dumps(skipped, ensure_ascii=False))
            failures = 1
            break

    if args.json_output is not None:
        args.json_output.parent.mkdir(parents=True, exist_ok=True)
        args.json_output.write_text(
            json.dumps(rows, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
    return 1 if failures else 0


def _cmd_toolcall15(args: argparse.Namespace) -> int:
    rows = run_suite(
        args.base_url,
        args.model,
        scenario_ids=args.scenario,
        temperature=args.temperature,
        timeout=args.timeout,
        max_turns=args.max_turns,
    )
    failures = 0
    for row in rows:
        ok = row["points"] >= args.min_points
        row["ok"] = ok
        failures += 0 if ok else 1
        print(json.dumps(row, ensure_ascii=False))

    total_points = sum(int(row["points"]) for row in rows)
    max_points = len(rows) * 2
    summary = {
        "cases": len(rows),
        "points": total_points,
        "max_points": max_points,
        "score_percent": round((total_points / max_points) * 100) if max_points else 0,
        "min_points": args.min_points,
        "failures": failures,
    }
    print(json.dumps({"summary": summary}, ensure_ascii=False))

    if args.json_output is not None:
        args.json_output.parent.mkdir(parents=True, exist_ok=True)
        args.json_output.write_text(
            json.dumps({"summary": summary, "results": rows}, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    return 1 if failures else 0


def _cmd_gpu_summary(args: argparse.Namespace) -> int:
    summary = summarize_gpu_csv(args.csv_input)
    print(json.dumps(summary, ensure_ascii=False))
    if args.json_output is not None:
        write_gpu_json(args.json_output, summary)
    if args.markdown_output is not None:
        write_gpu_markdown(args.markdown_output, summary)
    return 0


def _cmd_runtime_summary(args: argparse.Namespace) -> int:
    summary = summarize_runtime_stats(args.metrics_input, args.serve_log)
    print(json.dumps(summary, ensure_ascii=False))
    if args.json_output is not None:
        write_runtime_json(args.json_output, summary)
    if args.markdown_output is not None:
        write_runtime_markdown(args.markdown_output, summary)
    return 0


def _cmd_env_summary(args: argparse.Namespace) -> int:
    summary = summarize_run_environment()
    print(json.dumps(summary, ensure_ascii=False))
    if args.json_output is not None:
        write_run_environment_json(args.json_output, summary)
    if args.markdown_output is not None:
        write_run_environment_markdown(args.markdown_output, summary)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="DeepSeek V4 SM12x correctness and benchmark harness."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    def add_case_filters(p: argparse.ArgumentParser) -> None:
        p.add_argument("--model", default=DEFAULT_MODEL)
        p.add_argument("--case", action="append")
        p.add_argument("--tag", action="append")
        p.add_argument("--exclude-tag", action="append")

    list_cases = subparsers.add_parser("list-cases")
    add_case_filters(list_cases)
    list_cases.set_defaults(func=_cmd_list_cases)

    health = subparsers.add_parser("health")
    health.add_argument("--base-url", default="http://127.0.0.1:8000")
    health.add_argument("--timeout", type=float, default=30.0)
    health.set_defaults(func=_cmd_health)

    smoke = subparsers.add_parser("chat-smoke")
    add_case_filters(smoke)
    smoke.add_argument("--base-url", default="http://127.0.0.1:8000")
    smoke.add_argument("--max-tokens", type=int, default=256)
    smoke.add_argument("--temperature", type=float, default=0.0)
    smoke.add_argument("--timeout", type=float, default=300.0)
    smoke.add_argument("--jsonl-output", type=Path)
    smoke.add_argument("--markdown-output", type=Path)
    smoke.set_defaults(func=_cmd_chat_smoke)

    oracle = subparsers.add_parser("oracle-compare")
    oracle.add_argument("--base-url", default="http://127.0.0.1:8000")
    oracle.add_argument("--oracle-dir", type=Path, required=True)
    oracle.add_argument("--model")
    oracle.add_argument("--top-n", type=int, default=20)
    oracle.add_argument("--timeout", type=float, default=300.0)
    oracle.add_argument("--json-output", type=Path)
    oracle.add_argument("--require-prompt-ids", action="store_true")
    oracle.add_argument("--require-token-match", action="store_true")
    oracle.add_argument("--min-top1-match-rate", type=float)
    oracle.set_defaults(func=_cmd_oracle_compare)

    oracle_export = subparsers.add_parser("oracle-export")
    oracle_export.add_argument("--base-url", default="http://127.0.0.1:8000")
    oracle_export.add_argument("--model", default=DEFAULT_MODEL)
    oracle_export.add_argument("--output-dir", type=Path, required=True)
    oracle_export.add_argument("--case", action="append")
    oracle_export.add_argument("--logprobs", type=int)
    oracle_export.add_argument("--timeout", type=float, default=300.0)
    oracle_export.add_argument("--stop-on-error", action="store_true")
    oracle_export.set_defaults(func=_cmd_oracle_export)

    bench = subparsers.add_parser("bench-matrix")
    bench.add_argument("--vllm-bin", default="vllm")
    bench.add_argument("--model", default=DEFAULT_MODEL)
    bench.add_argument("--tokenizer-mode", default="deepseek_v4")
    bench.add_argument("--host", default="localhost")
    bench.add_argument("--port", type=int, default=8000)
    bench.add_argument("--base-url")
    bench.add_argument("--concurrency", default="1,2,4,8,16,24")
    bench.add_argument("--dataset-name", default=DEFAULT_BENCH_DATASET)
    bench.add_argument("--dataset-path", default=DEFAULT_BENCH_DATASET_PATH)
    bench.add_argument("--random-input-len", type=int, default=1024)
    bench.add_argument("--random-output-len", type=int, default=1024)
    bench.add_argument("--num-prompts", type=int, default=80)
    bench.add_argument("--temperature", type=float)
    bench.add_argument("--ignore-eos", action="store_true")
    bench.add_argument("--timeout", type=float)
    bench.add_argument("--health-timeout", type=float, default=10.0)
    bench.add_argument("--failure-probe-timeout", type=float, default=30.0)
    bench.add_argument("--failure-grace-timeout", type=float, default=0.0)
    bench.add_argument("--failure-grace-interval", type=float, default=10.0)
    bench.add_argument("--stop-on-unresponsive", action="store_true")
    bench.add_argument("--json-output", type=Path)
    bench.add_argument("--log-dir", type=Path)
    bench.add_argument("--extra-bench-arg", action="append")
    bench.set_defaults(func=_cmd_bench_matrix)

    toolcall15 = subparsers.add_parser("toolcall15")
    toolcall15.add_argument("--base-url", default="http://127.0.0.1:8000")
    toolcall15.add_argument("--model", default=DEFAULT_MODEL)
    toolcall15.add_argument("--scenario", action="append")
    toolcall15.add_argument("--temperature", type=float, default=0.0)
    toolcall15.add_argument("--timeout", type=float, default=120.0)
    toolcall15.add_argument("--max-turns", type=int, default=8)
    toolcall15.add_argument("--min-points", type=int, choices=(0, 1, 2), default=2)
    toolcall15.add_argument("--json-output", type=Path)
    toolcall15.set_defaults(func=_cmd_toolcall15)

    gpu_summary = subparsers.add_parser("gpu-summary")
    gpu_summary.add_argument("--csv-input", type=Path, required=True)
    gpu_summary.add_argument("--json-output", type=Path)
    gpu_summary.add_argument("--markdown-output", type=Path)
    gpu_summary.set_defaults(func=_cmd_gpu_summary)

    runtime_summary = subparsers.add_parser("runtime-summary")
    runtime_summary.add_argument("--metrics-input", type=Path)
    runtime_summary.add_argument("--serve-log", type=Path)
    runtime_summary.add_argument("--json-output", type=Path)
    runtime_summary.add_argument("--markdown-output", type=Path)
    runtime_summary.set_defaults(func=_cmd_runtime_summary)

    env_summary = subparsers.add_parser("env-summary")
    env_summary.add_argument("--json-output", type=Path)
    env_summary.add_argument("--markdown-output", type=Path)
    env_summary.set_defaults(func=_cmd_env_summary)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
