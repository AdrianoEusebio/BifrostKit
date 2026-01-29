from __future__ import annotations

import json
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

from bifrostkit.providers.mcp.types import McpActionConfig, McpServerConfig


@dataclass(frozen=True)
class McpRunResult:
    ok: bool
    stdout: str
    stderr: str
    response: Dict[str, Any]


class McpRunner:
    def run_action(
        self,
        mcp: McpServerConfig,
        action: McpActionConfig,
        file_path: Optional[Path] = None,
        timeout_seconds: int = 60,
    ) -> McpRunResult:
        if mcp.transport.transport_type != "docker-stdio":
            raise ValueError(f"Unsupported transport: {mcp.transport.transport_type}")

        if not mcp.transport.image:
            raise ValueError("MCP transport image is required for docker-stdio.")

        input_payload = self._build_payload(action=action, file_path=file_path)

        stdout, stderr, response = self._run_docker_stdio(
            image=mcp.transport.image,
            command=mcp.transport.command,
            env=mcp.transport.env,
            payload=input_payload,
            timeout_seconds=timeout_seconds,
        )

        ok = bool(response.get("ok", False))
        return McpRunResult(ok=ok, stdout=stdout, stderr=stderr, response=response)

    def apply_output(
        self,
        action: McpActionConfig,
        result: McpRunResult,
        input_file_path: Optional[Path],
    ) -> Optional[Path]:
        """
        Applies action output rules (e.g., overwrite_input).
        Returns the path modified (if any).
        """
        if not result.ok:
            return None

        if action.output is None:
            return None

        if action.output.output_type != "markdown":
            return None

        markdown = _extract_markdown(result.response)
        if markdown is None:
            return None

        if action.output.target == "sobrescrever_entrada":
            if input_file_path is None:
                return None
            input_file_path.write_text(markdown, encoding="utf-8")
            return input_file_path

        return None

    def _build_payload(self, action: McpActionConfig, file_path: Optional[Path]) -> Dict[str, Any]:
        inputs: Dict[str, Any] = {}

        # Minimal MVP: if a file is provided, send its content (avoids mounts).
        if file_path is not None:
            content = file_path.read_text(encoding="utf-8")
            inputs["file"] = {
                "path": str(file_path),
                "name": file_path.name,
                "content": content,
            }

        return {
            "action": action.key,
            "inputs": inputs,
        }

    def _run_docker_stdio(
        self,
        image: str,
        command: list[str],
        env: Dict[str, str],
        payload: Dict[str, Any],
        timeout_seconds: int,
    ) -> Tuple[str, str, Dict[str, Any]]:
        docker_cmd = ["docker", "run", "--rm", "-i"]

        for k, v in env.items():
            docker_cmd.extend(["-e", f"{k}={v}"])

        docker_cmd.append(image)

        if command:
            docker_cmd.extend(command)

        request_str = json.dumps(payload, ensure_ascii=False) + "\n"

        start = time.time()
        proc = subprocess.Popen(
            docker_cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        try:
            assert proc.stdin is not None
            assert proc.stdout is not None
            assert proc.stderr is not None

            proc.stdin.write(request_str)
            proc.stdin.flush()
            proc.stdin.close()

            stdout, stderr = _communicate_with_timeout(proc, timeout_seconds=timeout_seconds)
            response = _parse_first_json(stdout)

            if response is None:
                response = {"ok": False, "error": "No valid JSON response from MCP."}

            return stdout, stderr, response

        finally:
            # Ensure process is not left hanging
            if proc.poll() is None and (time.time() - start) > timeout_seconds:
                proc.kill()


def _communicate_with_timeout(proc: subprocess.Popen[str], timeout_seconds: int) -> Tuple[str, str]:
    try:
        stdout, stderr = proc.communicate(timeout=timeout_seconds)
        return stdout or "", stderr or ""
    except subprocess.TimeoutExpired:
        proc.kill()
        stdout, stderr = proc.communicate()
        return (stdout or "") + "\n", (stderr or "") + "\n[timeout]"


def _parse_first_json(stdout: str) -> Optional[Dict[str, Any]]:
    """
    Tries to find and parse the first JSON object in stdout.
    MCP servers often print logs before JSON; we try line-by-line first, then fallback.
    """
    lines = [ln.strip() for ln in stdout.splitlines() if ln.strip()]
    for ln in lines:
        try:
            obj = json.loads(ln)
            if isinstance(obj, dict):
                return obj
        except json.JSONDecodeError:
            continue

    # Fallback: attempt to parse the full stdout if it's a JSON dict
    try:
        obj = json.loads(stdout)
        if isinstance(obj, dict):
            return obj
    except json.JSONDecodeError:
        return None

    return None


def _extract_markdown(response: Dict[str, Any]) -> Optional[str]:
    if "markdown" in response and isinstance(response["markdown"], str):
        return response["markdown"]

    outputs = response.get("outputs")
    if isinstance(outputs, dict):
        md = outputs.get("markdown")
        if isinstance(md, str):
            return md

    return None
