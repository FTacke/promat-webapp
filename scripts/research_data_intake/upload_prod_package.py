from __future__ import annotations

import argparse
from pathlib import Path
import shlex
import shutil
import subprocess
import tarfile

INCOMING_ROOT = "/srv/webapps_storage/promat/data/incoming/"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Upload a validated prod package to remote incoming with rsync or tar-over-SSH fallback.")
    parser.add_argument("--package-dir", required=True, help="Local prod package directory path.")
    parser.add_argument("--host", required=True, help="SSH host, for example vhrz2184.")
    parser.add_argument("--remote-dir", required=True, help="Remote target directory under incoming root.")
    parser.add_argument("--ssh-user", default="root", help="SSH user. Default: root.")
    parser.add_argument("--verify-checksums", action="store_true", help="Run remote sha256sum -c checksums.sha256 after upload.")
    return parser.parse_args()


def _run(command: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, capture_output=True, text=True, encoding="utf-8", errors="replace", check=False)


def _require_safe_remote_dir(remote_dir: str) -> None:
    normalized = remote_dir.strip()
    if not normalized.startswith(INCOMING_ROOT):
        raise ValueError(f"remote-dir must stay under {INCOMING_ROOT}")
    if normalized in (INCOMING_ROOT, INCOMING_ROOT.rstrip("/")):
        raise ValueError("remote-dir must include a concrete upload_id directory")
    if "/../" in normalized or normalized.endswith("/.."):
        raise ValueError("remote-dir must not contain parent traversal")
    if "/current" in normalized or "/releases" in normalized:
        raise ValueError("remote-dir must not target current or releases paths")


def _ssh_target(user: str, host: str) -> str:
    return f"{user}@{host}"


def _rsync_upload(package_dir: Path, ssh_user: str, host: str, remote_dir: str) -> None:
    source = package_dir.as_posix().rstrip("/") + "/"
    destination = f"{_ssh_target(ssh_user, host)}:{remote_dir.rstrip('/')}/"
    command = ["rsync", "-avh", "--progress", source, destination]
    process = _run(command)
    if process.returncode != 0:
        raise RuntimeError(process.stderr.strip() or process.stdout.strip() or "rsync upload failed")


def _tar_stream_upload(package_dir: Path, ssh_user: str, host: str, remote_dir: str) -> None:
    ssh_cmd = [
        "ssh",
        _ssh_target(ssh_user, host),
        f"mkdir -p {shlex.quote(remote_dir)} && tar -xf - -C {shlex.quote(remote_dir)}",
    ]
    process = subprocess.Popen(ssh_cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    assert process.stdin is not None
    try:
        with tarfile.open(fileobj=process.stdin, mode="w|") as archive:
            for file_path in sorted(path for path in package_dir.rglob("*") if path.is_file()):
                arcname = file_path.relative_to(package_dir).as_posix()
                archive.add(file_path, arcname=arcname)
    finally:
        process.stdin.close()
    stdout_data, stderr_data = process.communicate()
    if process.returncode != 0:
        stdout_text = stdout_data.decode("utf-8", errors="replace").strip()
        stderr_text = stderr_data.decode("utf-8", errors="replace").strip()
        raise RuntimeError(stderr_text or stdout_text or "tar-over-SSH upload failed")


def _remote_command(ssh_user: str, host: str, command: str) -> str:
    process = _run(["ssh", _ssh_target(ssh_user, host), command])
    if process.returncode != 0:
        raise RuntimeError(process.stderr.strip() or process.stdout.strip() or f"remote command failed: {command}")
    return process.stdout.strip()


def _verify_remote_root(ssh_user: str, host: str, remote_dir: str) -> tuple[int, list[str]]:
    count_output = _remote_command(ssh_user, host, f"find {shlex.quote(remote_dir)} -type f | wc -l")
    count = int((count_output.splitlines()[-1] if count_output else "0").strip())
    root_output = _remote_command(ssh_user, host, f"ls -1 {shlex.quote(remote_dir)}")
    root_entries = [line.strip() for line in root_output.splitlines() if line.strip()]
    required = {"manifest.json", "checksums.sha256", "sessions", "config", "reports"}
    missing = sorted(required - set(root_entries))
    if missing:
        raise RuntimeError("remote root sanity check failed; missing entries: " + ", ".join(missing))
    return count, root_entries


def _verify_remote_checksums(ssh_user: str, host: str, remote_dir: str) -> None:
    _remote_command(ssh_user, host, f"cd {shlex.quote(remote_dir)} && sha256sum -c checksums.sha256")


def main() -> int:
    args = parse_args()
    package_dir = Path(args.package_dir).resolve()
    if not package_dir.exists() or not package_dir.is_dir():
        print(f"error: package-dir is missing or not a directory: {package_dir}")
        return 1

    _require_safe_remote_dir(args.remote_dir)

    strategy: str
    if shutil.which("rsync"):
        strategy = "rsync"
        print("upload strategy: rsync")
        _rsync_upload(package_dir, args.ssh_user, args.host, args.remote_dir)
    else:
        strategy = "tar-over-ssh"
        print("upload strategy: tar-over-ssh (rsync not found)")
        _tar_stream_upload(package_dir, args.ssh_user, args.host, args.remote_dir)

    file_count, root_entries = _verify_remote_root(args.ssh_user, args.host, args.remote_dir)
    print(f"remote file count: {file_count}")
    print("remote root entries: " + ", ".join(root_entries))

    if args.verify_checksums:
        _verify_remote_checksums(args.ssh_user, args.host, args.remote_dir)
        print("remote checksum gate: ok")

    print(f"upload completed: strategy={strategy}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
