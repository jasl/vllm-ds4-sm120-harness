from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
from pathlib import Path
from typing import Any

from ds4_harness.baseline_report import build_baseline_report, write_baseline_report
from ds4_harness.bench import run_bench_command
from ds4_harness.cases import SmokeCase, build_cases, select_cases
from ds4_harness.checks import CheckResult, assistant_text, check_chat_response, tool_call_names
from ds4_harness.client import get_json, get_status, post_json, post_json_with_retries
from ds4_harness.generation import (
    DEFAULT_THINKING_MODES,
    evaluate_generation_response,
    generation_result_row,
    load_generation_prompts,
    thinking_extra_body,
    transcript_filename,
    write_generation_transcript,
)
from ds4_harness.gpu_stats import summarize_gpu_csv, write_gpu_json, write_gpu_markdown
from ds4_harness.kv_layout_probe import (
    DEFAULT_BLOCK_SIZE as DEFAULT_KV_LAYOUT_BLOCK_SIZE,
    DEFAULT_CASE_NAME as DEFAULT_KV_LAYOUT_CASE_NAME,
    DEFAULT_HEAD_DIM as DEFAULT_KV_LAYOUT_HEAD_DIM,
    DEFAULT_NUM_BLOCKS as DEFAULT_KV_LAYOUT_NUM_BLOCKS,
    DEFAULT_SCALE_BYTES as DEFAULT_KV_LAYOUT_SCALE_BYTES,
    run_kv_layout_probe,
    write_kv_layout_markdown,
)
from ds4_harness.lm_eval import (
    build_lm_eval_command,
    load_lm_eval_results,
    run_lm_eval_command,
    summarize_lm_eval_results,
)
from ds4_harness.long_context_probe import (
    run_long_context_probe,
    write_long_context_markdown,
)
from ds4_harness.oracle import (
    attach_prompt_token_ids,
    compare_response,
    load_oracle_cases,
    token_ids_from_tokenize_response,
)
from ds4_harness.oracle_export import export_completion_oracles
from ds4_harness.official_baseline import build_official_api_baseline
from ds4_harness.reference_bundle import build_reference_bundle
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

    repeat_count = max((int(row.get("round", 1)) for row in rows), default=1)
    case_count = len({row["case"].name for row in rows})
    lines = [
        "# Chat Smoke Report",
        "",
        f"- Cases: {case_count}",
        f"- Repeat count: {repeat_count}",
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
                f"- Round: {row.get('round', 1)}",
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

        elapsed = row.get("elapsed_seconds")
        if isinstance(elapsed, int | float):
            lines.extend(["### Timing", "", f"- Elapsed seconds: {elapsed:.3f}", ""])

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def _bearer_headers_from_env(env_name: str | None) -> dict[str, str] | None:
    if not env_name:
        return None
    value = os.environ.get(env_name)
    if not value:
        raise RuntimeError(f"{env_name} is not set")
    return {"Authorization": f"Bearer {value}"}


def _apply_max_case_tokens_cap(
    payload: dict[str, Any],
    max_case_tokens: int | None,
) -> None:
    if max_case_tokens is None:
        return
    current = payload.get("max_tokens")
    if isinstance(current, int) and current > max_case_tokens:
        payload["max_tokens"] = max_case_tokens


def _parse_extra_body_json(value: str | None) -> dict[str, Any]:
    if not value:
        return {}
    data = json.loads(value)
    if not isinstance(data, dict):
        raise RuntimeError("--extra-body-json must decode to a JSON object")
    return data


def _validate_request_retries(value: int) -> bool:
    return value >= 0


def _thinking_strength_from_extra_body(extra_body: dict[str, Any]) -> str:
    thinking = extra_body.get("thinking")
    if isinstance(thinking, dict) and thinking.get("type") == "disabled":
        return "disabled"
    effort = extra_body.get("reasoning_effort")
    return str(effort) if effort else "default"


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
    if args.repeat_count < 1:
        print("--repeat-count must be >= 1", file=sys.stderr)
        return 2
    if not _validate_request_retries(args.request_retries):
        print("--request-retries must be >= 0", file=sys.stderr)
        return 2

    cases = select_cases(
        build_cases(args.model),
        names=args.case,
        tags=args.tag,
        exclude_tags=args.exclude_tag,
    )
    if not cases:
        print("No smoke cases selected.", file=sys.stderr)
        return 2

    try:
        headers = _bearer_headers_from_env(args.api_key_env)
        extra_body = _parse_extra_body_json(args.extra_body_json)
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    except json.JSONDecodeError as exc:
        print(f"invalid --extra-body-json: {exc}", file=sys.stderr)
        return 2

    failures = 0
    markdown_rows: list[dict[str, Any]] = []
    for round_index in range(1, args.repeat_count + 1):
        for case in cases:
            payload = case.to_payload(
                default_max_tokens=args.max_tokens,
                default_temperature=args.temperature,
            )
            payload.update(extra_body)
            _apply_max_case_tokens_cap(payload, args.max_case_tokens)
            started = time.monotonic()
            try:
                if headers:
                    response = post_json_with_retries(
                        args.base_url,
                        "/v1/chat/completions",
                        payload,
                        args.timeout,
                        headers=headers,
                        request_retries=args.request_retries,
                        post_func=post_json,
                    )
                else:
                    response = post_json_with_retries(
                        args.base_url,
                        "/v1/chat/completions",
                        payload,
                        args.timeout,
                        request_retries=args.request_retries,
                        post_func=post_json,
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
            elapsed_seconds = round(time.monotonic() - started, 6)

            _print_case_result(case, result, response)
            _write_jsonl(
                args.jsonl_output,
                {
                    "case": case.name,
                    "tags": case.tags,
                    "round": round_index,
                    "ok": result.ok,
                    "detail": result.detail,
                    "elapsed_seconds": elapsed_seconds,
                    "payload": payload,
                    "response": response,
                },
            )
            markdown_rows.append(
                {
                    "case": case,
                    "round": round_index,
                    "result": result,
                    "elapsed_seconds": elapsed_seconds,
                    "response": response,
                }
            )
            failures += 0 if result.ok else 1
    _write_chat_markdown(args.markdown_output, markdown_rows)
    return 1 if failures else 0


def _cmd_generation_matrix(args: argparse.Namespace) -> int:
    if args.repeat_count < 1:
        print("--repeat-count must be >= 1", file=sys.stderr)
        return 2
    if not _validate_request_retries(args.request_retries):
        print("--request-retries must be >= 0", file=sys.stderr)
        return 2

    try:
        headers = _bearer_headers_from_env(args.api_key_env)
        extra_body = _parse_extra_body_json(args.extra_body_json)
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    except json.JSONDecodeError as exc:
        print(f"invalid --extra-body-json: {exc}", file=sys.stderr)
        return 2

    try:
        prompts = load_generation_prompts(
            args.prompt_root,
            languages=args.language,
            names=args.prompt,
            tags=args.tag,
        )
    except OSError as exc:
        print(f"failed to read generation prompts: {exc}", file=sys.stderr)
        return 2

    if not prompts:
        print("No generation prompts selected.", file=sys.stderr)
        return 2

    failures = 0
    thinking_modes = args.thinking_mode or list(DEFAULT_THINKING_MODES)
    for thinking_mode in thinking_modes:
        try:
            mode_extra_body = thinking_extra_body(thinking_mode)
        except KeyError as exc:
            print(str(exc), file=sys.stderr)
            return 2
        for round_index in range(1, args.repeat_count + 1):
            for prompt in prompts:
                payload = prompt.to_payload(
                    model=args.model,
                    default_max_tokens=args.max_tokens,
                    default_temperature=args.temperature,
                    default_top_p=args.top_p,
                    max_case_tokens=args.max_case_tokens,
                )
                payload.update(mode_extra_body)
                payload.update(extra_body)
                started = time.monotonic()
                try:
                    if headers:
                        response = post_json_with_retries(
                            args.base_url,
                            "/v1/chat/completions",
                            payload,
                            args.timeout,
                            headers=headers,
                            request_retries=args.request_retries,
                            post_func=post_json,
                        )
                    else:
                        response = post_json_with_retries(
                            args.base_url,
                            "/v1/chat/completions",
                            payload,
                            args.timeout,
                            request_retries=args.request_retries,
                            post_func=post_json,
                        )
                    result = evaluate_generation_response(
                        prompt,
                        response,
                        skip_expectation_checks=args.skip_expectation_checks,
                    )
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
                elapsed_seconds = time.monotonic() - started
                row = generation_result_row(
                    prompt=prompt,
                    round_index=round_index,
                    thinking_mode=thinking_mode,
                    variant=args.variant,
                    payload=payload,
                    response=response,
                    result=result,
                    elapsed_seconds=elapsed_seconds,
                )
                status = "PASS" if result.ok else "FAIL"
                print(
                    f"{status} {prompt.language}/{prompt.name} "
                    f"round={round_index} thinking={thinking_mode} "
                    f"variant={args.variant}: {result.detail}"
                )
                _write_jsonl(args.jsonl_output, row)
                if args.markdown_output_dir is not None:
                    write_generation_transcript(
                        args.markdown_output_dir
                        / prompt.language
                        / transcript_filename(
                            prompt,
                            round_index=round_index,
                            thinking_mode=thinking_mode,
                            variant=args.variant,
                        ),
                        row,
                    )
                failures += 0 if result.ok else 1

    return 1 if failures else 0


def _cmd_oracle_compare(args: argparse.Namespace) -> int:
    if not _validate_request_retries(args.request_retries):
        print("--request-retries must be >= 0", file=sys.stderr)
        return 2

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
            response = post_json_with_retries(
                args.base_url,
                case.path,
                request_payload,
                args.timeout,
                request_retries=args.request_retries,
                post_func=post_json,
            )
            if args.require_prompt_ids:
                tokenize_payload = {
                    "model": request_payload.get("model"),
                    "prompt": request_payload.get("prompt"),
                }
                tokenize_response = post_json_with_retries(
                    args.base_url,
                    "/tokenize",
                    tokenize_payload,
                    args.timeout,
                    request_retries=args.request_retries,
                    post_func=post_json,
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
    if not _validate_request_retries(args.request_retries):
        print("--request-retries must be >= 0", file=sys.stderr)
        return 2

    rows = export_completion_oracles(
        base_url=args.base_url,
        model=args.model,
        output_dir=args.output_dir,
        case_names=args.case,
        timeout=args.timeout,
        logprobs=args.logprobs,
        stop_on_error=args.stop_on_error,
        request_retries=args.request_retries,
    )
    failures = 0
    for row in rows:
        print(json.dumps(row, ensure_ascii=False))
        failures += 0 if row.get("ok") else 1
    return 1 if failures else 0


def _cmd_long_context_probe(args: argparse.Namespace) -> int:
    if not _validate_request_retries(args.request_retries):
        print("--request-retries must be >= 0", file=sys.stderr)
        return 2

    try:
        headers = _bearer_headers_from_env(args.api_key_env)
        extra_body = _parse_extra_body_json(args.extra_body_json)
        row = run_long_context_probe(
            base_url=args.base_url,
            model=args.model,
            variant=args.variant,
            case_name=args.case_name,
            line_count=args.line_count,
            max_tokens=args.max_tokens,
            temperature=args.temperature,
            top_p=args.top_p,
            thinking_mode=args.thinking_mode,
            timeout=args.timeout,
            request_retries=args.request_retries,
            headers=headers,
            extra_body=extra_body,
        )
    except (KeyError, ValueError, RuntimeError, json.JSONDecodeError) as exc:
        print(str(exc), file=sys.stderr)
        return 2

    if args.json_output is not None:
        args.json_output.parent.mkdir(parents=True, exist_ok=True)
        args.json_output.write_text(
            json.dumps(row, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
    if args.markdown_output is not None:
        write_long_context_markdown(args.markdown_output, row)

    status = "PASS" if row.get("ok") else "FAIL"
    print(f"{status} {row.get('case')} variant={args.variant}: {row.get('detail')}")
    return 0 if row.get("ok") else 1


def _cmd_kv_layout_probe(args: argparse.Namespace) -> int:
    try:
        row = run_kv_layout_probe(
            target_python=args.target_python,
            variant=args.variant,
            case_name=args.case_name,
            num_blocks=args.num_blocks,
            block_size=args.block_size,
            head_dim=args.head_dim,
            scale_bytes=args.scale_bytes,
            raw_output=args.raw_output,
            require_helper_match=args.require_helper_match,
            timeout=args.timeout,
        )
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    if args.json_output is not None:
        args.json_output.parent.mkdir(parents=True, exist_ok=True)
        args.json_output.write_text(
            json.dumps(row, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
    if args.markdown_output is not None:
        write_kv_layout_markdown(args.markdown_output, row)

    status = "PASS" if row.get("ok") else "FAIL"
    print(f"{status} {row.get('case')} variant={args.variant}: {row.get('detail')}")
    return 0 if row.get("ok") else 1


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


def _cmd_lm_eval(args: argparse.Namespace) -> int:
    if not args.task:
        print("at least one --task is required", file=sys.stderr)
        return 2
    if args.num_fewshot < 0:
        print("--num-fewshot must be >= 0", file=sys.stderr)
        return 2
    if args.num_concurrent < 1:
        print("--num-concurrent must be >= 1", file=sys.stderr)
        return 2
    if args.max_retries < 0:
        print("--max-retries must be >= 0", file=sys.stderr)
        return 2

    raw_output_dir = args.output_dir / "raw"
    raw_output_dir.mkdir(parents=True, exist_ok=True)
    command = build_lm_eval_command(
        lm_eval_bin=args.lm_eval_bin,
        model=args.model,
        base_url=args.base_url,
        tasks=args.task,
        num_fewshot=args.num_fewshot,
        num_concurrent=args.num_concurrent,
        max_retries=args.max_retries,
        max_gen_toks=args.max_gen_toks,
        eval_timeout_ms=args.eval_timeout_ms,
        tokenizer_backend=args.tokenizer_backend,
        batch_size=args.batch_size,
        output_path=raw_output_dir,
        extra_args=args.extra_lm_eval_arg,
    )
    command_result = run_lm_eval_command(command, timeout=args.command_timeout)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "stdout.log").write_text(
        command_result.get("stdout", ""),
        encoding="utf-8",
    )
    (args.output_dir / "stderr.log").write_text(
        command_result.get("stderr", ""),
        encoding="utf-8",
    )
    (args.output_dir / "command.json").write_text(
        json.dumps(command, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    raw_results = load_lm_eval_results(raw_output_dir)
    summary = summarize_lm_eval_results(
        raw_results,
        command_result=command_result,
        config={
            "tasks": args.task,
            "num_fewshot": args.num_fewshot,
            "num_concurrent": args.num_concurrent,
            "max_retries": args.max_retries,
            "max_gen_toks": args.max_gen_toks,
            "eval_timeout_ms": args.eval_timeout_ms,
            "tokenizer_backend": args.tokenizer_backend,
            "batch_size": args.batch_size,
        },
    )
    output_path = args.json_output or (args.output_dir / "lm_eval_summary.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(json.dumps(summary, ensure_ascii=False))
    return 0 if summary["ok"] else 1


def _cmd_toolcall15(args: argparse.Namespace) -> int:
    if args.repeat_count < 1:
        print("--repeat-count must be >= 1", file=sys.stderr)
        return 2
    if not _validate_request_retries(args.request_retries):
        print("--request-retries must be >= 0", file=sys.stderr)
        return 2

    try:
        headers = _bearer_headers_from_env(args.api_key_env)
        extra_body = _parse_extra_body_json(args.extra_body_json)
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    except json.JSONDecodeError as exc:
        print(f"invalid --extra-body-json: {exc}", file=sys.stderr)
        return 2

    scenario_sets = (
        ["en", "zh"] if args.scenario_set == "both" else [args.scenario_set]
    )
    rounds: list[dict[str, Any]] = []
    all_rows: list[dict[str, Any]] = []
    total_failures = 0
    thinking_modes = args.thinking_mode or [None]

    for thinking_mode in thinking_modes:
        if thinking_mode is None:
            mode_extra_body: dict[str, Any] = {}
            thinking_label = "default"
        else:
            try:
                mode_extra_body = thinking_extra_body(thinking_mode)
            except KeyError as exc:
                print(str(exc), file=sys.stderr)
                return 2
            thinking_label = thinking_mode
        combined_extra_body = dict(mode_extra_body)
        combined_extra_body.update(extra_body)
        thinking_strength = _thinking_strength_from_extra_body(combined_extra_body)

        for scenario_set in scenario_sets:
            for round_index in range(1, args.repeat_count + 1):
                rows = run_suite(
                    args.base_url,
                    args.model,
                    scenario_ids=args.scenario,
                    scenario_set=scenario_set,
                    temperature=args.temperature,
                    timeout=args.timeout,
                    max_turns=args.max_turns,
                    headers=headers,
                    extra_body=combined_extra_body,
                    preserve_reasoning_content=args.preserve_reasoning_content,
                    request_retries=args.request_retries,
                )
                failures = 0
                for row in rows:
                    ok = row["points"] >= args.min_points
                    row["ok"] = ok
                    row["round"] = round_index
                    row["scenario_set"] = scenario_set
                    row["thinking_mode"] = thinking_label
                    row["thinking_strength"] = thinking_strength
                    failures += 0 if ok else 1
                    print(json.dumps(row, ensure_ascii=False))

                total_points = sum(int(row["points"]) for row in rows)
                max_points = len(rows) * 2
                round_summary = {
                    "scenario_set": scenario_set,
                    "round": round_index,
                    "thinking_mode": thinking_label,
                    "thinking_strength": thinking_strength,
                    "cases": len(rows),
                    "points": total_points,
                    "max_points": max_points,
                    "score_percent": round((total_points / max_points) * 100)
                    if max_points
                    else 0,
                    "min_points": args.min_points,
                    "failures": failures,
                }
                rounds.append(
                    {
                        "scenario_set": scenario_set,
                        "round": round_index,
                        "thinking_mode": thinking_label,
                        "thinking_strength": thinking_strength,
                        "summary": round_summary,
                        "results": rows,
                    }
                )
                all_rows.extend(rows)
                total_failures += failures

    total_points = sum(int(row["points"]) for row in all_rows)
    max_points = len(all_rows) * 2
    cases_per_round = sum(
        len(round_data["results"])
        for round_data in rounds
        if round_data.get("round") == 1
    )
    summary = {
        "scenario_sets": scenario_sets,
        "thinking_modes": [mode or "default" for mode in thinking_modes],
        "rounds": args.repeat_count,
        "cases": cases_per_round,
        "total_cases": len(all_rows),
        "points": total_points,
        "max_points": max_points,
        "score_percent": round((total_points / max_points) * 100) if max_points else 0,
        "min_points": args.min_points,
        "failures": total_failures,
    }
    print(json.dumps({"summary": summary}, ensure_ascii=False))

    if args.json_output is not None:
        payload: dict[str, Any] = {
            "summary": summary,
            "results": all_rows
            if len(scenario_sets) > 1 or len(thinking_modes) > 1
            else rounds[-1]["results"]
            if rounds
            else [],
        }
        if args.repeat_count > 1 or len(scenario_sets) > 1 or len(thinking_modes) > 1:
            payload["rounds"] = rounds
        args.json_output.parent.mkdir(parents=True, exist_ok=True)
        args.json_output.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    return 1 if total_failures else 0


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


def _cmd_baseline_report(args: argparse.Namespace) -> int:
    report = build_baseline_report(
        args.run_dir,
        title=args.title,
        label=args.label,
    )
    if args.output is None:
        print(report, end="")
    else:
        write_baseline_report(args.output, report)
        print(str(args.output))
    return 0


def _cmd_reference_bundle(args: argparse.Namespace) -> int:
    findings = build_reference_bundle(
        run_dir=args.run_dir,
        output_dir=args.output_dir,
        label=args.label,
        date=args.date,
        fail_on_sensitive=False,
    )
    if findings:
        for finding in findings:
            print(finding, file=sys.stderr)
        return 1
    print(str(args.output_dir))
    return 0


def _cmd_official_baseline(args: argparse.Namespace) -> int:
    findings = build_official_api_baseline(
        artifact_dir=args.artifact_dir,
        output_dir=args.output_dir,
        label=args.label,
        date=args.date,
        fail_on_sensitive=False,
    )
    if findings:
        for finding in findings:
            print(finding, file=sys.stderr)
        return 1
    print(str(args.output_dir))
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
    smoke.add_argument("--repeat-count", type=int, default=1)
    smoke.add_argument("--request-retries", type=int, default=1)
    smoke.add_argument("--api-key-env")
    smoke.add_argument("--max-case-tokens", type=int)
    smoke.add_argument("--extra-body-json")
    smoke.add_argument("--jsonl-output", type=Path)
    smoke.add_argument("--markdown-output", type=Path)
    smoke.set_defaults(func=_cmd_chat_smoke)

    generation = subparsers.add_parser("generation-matrix")
    generation.add_argument("--prompt-root", type=Path, default=Path("prompts"))
    generation.add_argument("--language", action="append")
    generation.add_argument("--prompt", action="append")
    generation.add_argument("--tag", action="append")
    generation.add_argument("--thinking-mode", action="append", default=None)
    generation.add_argument("--variant", default=os.environ.get("GENERATION_VARIANT", "manual"))
    generation.add_argument("--base-url", default="http://127.0.0.1:8000")
    generation.add_argument("--model", default=DEFAULT_MODEL)
    generation.add_argument("--max-tokens", type=int, default=2048)
    generation.add_argument("--max-case-tokens", type=int)
    generation.add_argument("--temperature", type=float, default=1.0)
    generation.add_argument("--top-p", type=float, default=1.0)
    generation.add_argument("--timeout", type=float, default=900.0)
    generation.add_argument("--repeat-count", type=int, default=3)
    generation.add_argument("--request-retries", type=int, default=1)
    generation.add_argument("--api-key-env")
    generation.add_argument("--extra-body-json")
    generation.add_argument("--skip-expectation-checks", action="store_true")
    generation.add_argument("--jsonl-output", type=Path)
    generation.add_argument("--markdown-output-dir", type=Path)
    generation.set_defaults(func=_cmd_generation_matrix)

    oracle = subparsers.add_parser("oracle-compare")
    oracle.add_argument("--base-url", default="http://127.0.0.1:8000")
    oracle.add_argument("--oracle-dir", type=Path, required=True)
    oracle.add_argument("--model")
    oracle.add_argument("--top-n", type=int, default=20)
    oracle.add_argument("--timeout", type=float, default=300.0)
    oracle.add_argument("--request-retries", type=int, default=1)
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
    oracle_export.add_argument("--request-retries", type=int, default=1)
    oracle_export.add_argument("--stop-on-error", action="store_true")
    oracle_export.set_defaults(func=_cmd_oracle_export)

    long_context = subparsers.add_parser("long-context-probe")
    long_context.add_argument("--base-url", default="http://127.0.0.1:8000")
    long_context.add_argument("--model", default=DEFAULT_MODEL)
    long_context.add_argument("--variant", default="manual")
    long_context.add_argument("--case-name", default="kv_indexer_long_context")
    long_context.add_argument("--line-count", type=int, default=2400)
    long_context.add_argument("--max-tokens", type=int, default=128)
    long_context.add_argument("--temperature", type=float, default=0.0)
    long_context.add_argument("--top-p", type=float, default=1.0)
    long_context.add_argument("--thinking-mode", default="non-thinking")
    long_context.add_argument("--timeout", type=float, default=1800.0)
    long_context.add_argument("--request-retries", type=int, default=1)
    long_context.add_argument("--api-key-env")
    long_context.add_argument("--extra-body-json")
    long_context.add_argument("--json-output", type=Path)
    long_context.add_argument("--markdown-output", type=Path)
    long_context.set_defaults(func=_cmd_long_context_probe)

    kv_layout = subparsers.add_parser("kv-layout-probe")
    kv_layout.add_argument("--target-python", default=sys.executable)
    kv_layout.add_argument("--variant", default="manual")
    kv_layout.add_argument("--case-name", default=DEFAULT_KV_LAYOUT_CASE_NAME)
    kv_layout.add_argument("--num-blocks", type=int, default=DEFAULT_KV_LAYOUT_NUM_BLOCKS)
    kv_layout.add_argument("--block-size", type=int, default=DEFAULT_KV_LAYOUT_BLOCK_SIZE)
    kv_layout.add_argument("--head-dim", type=int, default=DEFAULT_KV_LAYOUT_HEAD_DIM)
    kv_layout.add_argument("--scale-bytes", type=int, default=DEFAULT_KV_LAYOUT_SCALE_BYTES)
    kv_layout.add_argument(
        "--require-helper-match",
        action=argparse.BooleanOptionalAction,
        default=True,
    )
    kv_layout.add_argument("--timeout", type=float, default=120.0)
    kv_layout.add_argument("--json-output", type=Path)
    kv_layout.add_argument("--markdown-output", type=Path)
    kv_layout.add_argument("--raw-output", type=Path)
    kv_layout.set_defaults(func=_cmd_kv_layout_probe)

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

    lm_eval = subparsers.add_parser("lm-eval")
    lm_eval.add_argument("--lm-eval-bin", default="lm_eval")
    lm_eval.add_argument("--base-url", default="http://127.0.0.1:8000")
    lm_eval.add_argument("--model", default=DEFAULT_MODEL)
    lm_eval.add_argument("--task", action="append", required=True)
    lm_eval.add_argument("--num-fewshot", type=int, default=8)
    lm_eval.add_argument("--num-concurrent", type=int, default=4)
    lm_eval.add_argument("--max-retries", type=int, default=10)
    lm_eval.add_argument("--max-gen-toks", type=int, default=2048)
    lm_eval.add_argument("--eval-timeout-ms", type=int, default=60000)
    lm_eval.add_argument("--tokenizer-backend", default="none")
    lm_eval.add_argument("--batch-size", default="auto")
    lm_eval.add_argument("--command-timeout", type=float, default=7200.0)
    lm_eval.add_argument("--output-dir", type=Path, required=True)
    lm_eval.add_argument("--json-output", type=Path)
    lm_eval.add_argument("--extra-lm-eval-arg", action="append")
    lm_eval.set_defaults(func=_cmd_lm_eval)

    toolcall15 = subparsers.add_parser("toolcall15")
    toolcall15.add_argument("--base-url", default="http://127.0.0.1:8000")
    toolcall15.add_argument("--model", default=DEFAULT_MODEL)
    toolcall15.add_argument("--scenario", action="append")
    toolcall15.add_argument("--scenario-set", choices=("en", "zh", "both"), default="en")
    toolcall15.add_argument("--thinking-mode", action="append", default=None)
    toolcall15.add_argument("--temperature", type=float, default=0.0)
    toolcall15.add_argument("--timeout", type=float, default=120.0)
    toolcall15.add_argument("--max-turns", type=int, default=8)
    toolcall15.add_argument("--repeat-count", type=int, default=1)
    toolcall15.add_argument("--request-retries", type=int, default=1)
    toolcall15.add_argument("--min-points", type=int, choices=(0, 1, 2), default=2)
    toolcall15.add_argument("--api-key-env")
    toolcall15.add_argument("--extra-body-json")
    toolcall15.add_argument(
        "--preserve-reasoning-content",
        action=argparse.BooleanOptionalAction,
        default=True,
    )
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

    baseline_report = subparsers.add_parser("baseline-report")
    baseline_report.add_argument("--run-dir", type=Path, required=True)
    baseline_report.add_argument("--title", default="DeepSeek V4 Baseline Report")
    baseline_report.add_argument("--label")
    baseline_report.add_argument("--output", type=Path)
    baseline_report.set_defaults(func=_cmd_baseline_report)

    reference_bundle = subparsers.add_parser("reference-bundle")
    reference_bundle.add_argument("--run-dir", type=Path, required=True)
    reference_bundle.add_argument("--output-dir", type=Path, required=True)
    reference_bundle.add_argument("--label", required=True)
    reference_bundle.add_argument("--date")
    reference_bundle.set_defaults(func=_cmd_reference_bundle)

    official_baseline = subparsers.add_parser("official-baseline")
    official_baseline.add_argument("--artifact-dir", type=Path, required=True)
    official_baseline.add_argument("--output-dir", type=Path, required=True)
    official_baseline.add_argument("--label", required=True)
    official_baseline.add_argument("--date")
    official_baseline.set_defaults(func=_cmd_official_baseline)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
