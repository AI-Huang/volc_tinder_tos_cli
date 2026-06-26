#!/usr/bin/env python3
"""Upload a fake file to TOS, measure speed, then delete the object."""

from __future__ import annotations

import argparse
import os
import sys
import tempfile
import time
import uuid
from pathlib import Path

_SRC_DIR = Path(__file__).resolve().parent.parent / "src"
if str(_SRC_DIR) not in sys.path:
    sys.path.insert(0, str(_SRC_DIR))

from volc_tinder_tos_cli.settings import tos_settings  # noqa: E402
from volc_tinder_tos_cli.storage.tos_service import TosService  # noqa: E402

DEFAULT_SIZE_MB = 100
_WRITE_CHUNK_SIZE = 8 * 1024 * 1024


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="上传假数据到 TOS 测速，并在结束后删除桶内测试文件",
    )
    parser.add_argument(
        "--bucket-name",
        default=tos_settings.bucket_name,
        help="目标桶名，默认读取 TOS_BUCKET_NAME",
    )
    parser.add_argument(
        "--object-key",
        default="",
        help="桶内对象 key；默认自动生成唯一值",
    )
    parser.add_argument(
        "--size-mb",
        type=int,
        default=DEFAULT_SIZE_MB,
        help=f"假数据文件大小，默认 {DEFAULT_SIZE_MB} MB",
    )
    return parser


def _require_tos_settings(bucket_name: str) -> None:
    missing = []
    if not tos_settings.access_key:
        missing.append("TOS_ACCESS_KEY")
    if not tos_settings.secret_access_key:
        missing.append("TOS_SECRET_ACCESS_KEY")
    if not tos_settings.endpoint:
        missing.append("TOS_ENDPOINT")
    if not tos_settings.region:
        missing.append("TOS_REGION")
    if not bucket_name:
        missing.append("TOS_BUCKET_NAME or --bucket-name")

    if missing:
        raise SystemExit("Missing required TOS settings: " + ", ".join(missing))


def _create_fake_file(size_bytes: int) -> Path:
    fd, file_path = tempfile.mkstemp(prefix="tos-speed-test-", suffix=".bin")
    path = Path(file_path)
    chunk = b"0" * _WRITE_CHUNK_SIZE
    remaining = size_bytes

    try:
        with os.fdopen(fd, "wb") as handle:
            while remaining > 0:
                block = chunk if remaining >= len(chunk) else chunk[:remaining]
                handle.write(block)
                remaining -= len(block)
    except Exception:
        path.unlink(missing_ok=True)
        raise

    return path


def _format_mib_per_second(size_bytes: int, duration_seconds: float) -> float:
    if duration_seconds <= 0:
        return 0.0
    return (size_bytes / (1024 * 1024)) / duration_seconds


def main() -> int:
    args = _build_parser().parse_args()
    if args.size_mb <= 0:
        raise SystemExit("--size-mb must be greater than 0")

    bucket_name = args.bucket_name.strip()
    _require_tos_settings(bucket_name)

    size_bytes = args.size_mb * 1024 * 1024
    object_key = args.object_key.strip() or (
        f"benchmarks/tos-speed-test-{args.size_mb}mb-{uuid.uuid4().hex}.bin"
    )

    fake_file = _create_fake_file(size_bytes)
    client = TosService(
        tos_settings.access_key,
        tos_settings.secret_access_key,
        tos_settings.endpoint,
        tos_settings.region,
    )

    upload_started = None
    upload_finished = None
    upload_ok = False

    try:
        print(f"bucket_name={bucket_name}")
        print(f"object_key={object_key}")
        print(f"local_file={fake_file}")
        print(f"file_size_bytes={size_bytes}")
        print(f"file_size_mb={args.size_mb}")

        with fake_file.open("rb") as handle:
            upload_started = time.perf_counter()
            upload_ok = client.put_object(bucket_name, object_key, handle)
            upload_finished = time.perf_counter()

        if not upload_ok:
            print("upload_status=failed")
            return 1

        duration_seconds = upload_finished - upload_started
        speed_mib_per_second = _format_mib_per_second(size_bytes, duration_seconds)
        print("upload_status=success")
        print(f"upload_duration_seconds={duration_seconds:.3f}")
        print(f"upload_speed_mib_per_second={speed_mib_per_second:.3f}")
        return 0
    finally:
        try:
            if upload_ok:
                deleted = client.delete_object(bucket_name, object_key)
                print(f"remote_delete_status={'success' if deleted else 'failed'}")
            else:
                print("remote_delete_status=skipped")
        finally:
            fake_file.unlink(missing_ok=True)
            print("local_file_deleted=true")


if __name__ == "__main__":
    raise SystemExit(main())
