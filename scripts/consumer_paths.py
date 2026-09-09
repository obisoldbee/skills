#!/usr/bin/env python3
"""Filesystem-identity boundary checks and handle-bound consumer links."""

from __future__ import annotations

import argparse
import ctypes as c
from ctypes import wintypes as w
import struct
import json
import os
from pathlib import Path
import re
import stat
import sys


def identity(path: Path) -> tuple[int, int]:
    observed = path.stat()
    return observed.st_dev, observed.st_ino


def consumer_boundary(repo: Path) -> Path:
    parent = repo.parent
    declaration = parent / "AGENTS.md"
    control = parent / "skills/AGENTS.md"
    conventional_repo = parent / "GitHub"
    # samefile honors the actual volume's case behavior. Merely naming a
    # standalone checkout GitHub does not make its parent a collection.
    if (conventional_repo.is_dir() and repo.samefile(conventional_repo)
            and declaration.is_file() and control.is_file()):
        text = declaration.read_text(encoding="utf-8")
        if ("Project Collection" in text and "obisoldbee/skills" in text
                and "collection-control" in control.read_text(encoding="utf-8")):
            return parent
    return repo


def inspect_target(repo: Path, target: Path) -> tuple[Path, str]:
    repo = repo.resolve(strict=True)
    if not target.is_absolute():
        raise ValueError("target-must-be-absolute")
    resolved = target.resolve(strict=True)
    if not resolved.is_dir():
        raise ValueError("target-parent-missing")
    boundary = consumer_boundary(repo)
    boundary_id = identity(boundary)
    # Both sides matter: an internal outward alias is still not a consumer,
    # while an external inward alias must not hide its physical ancestry.
    for path in (target, resolved):
        for ancestor in (path, *path.parents):
            if identity(ancestor) == boundary_id:
                kind = "repository" if boundary_id == identity(repo) else "collection"
                raise ValueError(f"target-inside-{kind}: {target}")
    token = json.dumps([identity(repo), boundary_id, identity(resolved)], separators=(",", ":"))
    return resolved, token


# Windows uses NtCreateFile RootDirectory + FILE_CREATE followed by
# handle-bound FSCTL_SET/GET_REPARSE_POINT. See Microsoft Learn:
# winternl/nf-winternl-ntcreatefile; winioctl/ni-winioctl-fsctl_set_reparse_point.
class UnicodeString(c.Structure):
    _fields_ = [("Length", w.USHORT), ("MaximumLength", w.USHORT), ("Buffer", w.LPWSTR)]


class ObjectAttributes(c.Structure):
    _fields_ = [("Length", w.ULONG), ("RootDirectory", w.HANDLE),
                ("ObjectName", c.POINTER(UnicodeString)), ("Attributes", w.ULONG),
                ("SecurityDescriptor", w.LPVOID), ("SecurityQualityOfService", w.LPVOID)]


class IoStatus(c.Structure):
    _fields_ = [("Status", c.c_void_p), ("Information", c.c_size_t)]


class FileInfo(c.Structure):
    _fields_ = [("Attributes", w.DWORD), ("Creation", w.FILETIME),
                ("Access", w.FILETIME), ("Write", w.FILETIME),
                ("Volume", w.DWORD), ("SizeHigh", w.DWORD), ("SizeLow", w.DWORD),
                ("Links", w.DWORD), ("IndexHigh", w.DWORD), ("IndexLow", w.DWORD)]


def windows_api():
    kernel = c.WinDLL("kernel32", use_last_error=True)
    nt = c.WinDLL("ntdll")
    kernel.CreateFileW.argtypes = [w.LPCWSTR, w.DWORD, w.DWORD, w.LPVOID, w.DWORD, w.DWORD, w.HANDLE]
    kernel.CreateFileW.restype = w.HANDLE
    kernel.CloseHandle.argtypes = [w.HANDLE]
    kernel.GetFileInformationByHandle.argtypes = [w.HANDLE, c.POINTER(FileInfo)]
    kernel.DeviceIoControl.argtypes = [w.HANDLE, w.DWORD, w.LPVOID, w.DWORD, w.LPVOID, w.DWORD, c.POINTER(w.DWORD), w.LPVOID]
    kernel.SetFileInformationByHandle.argtypes = [w.HANDLE, c.c_int, w.LPVOID, w.DWORD]
    nt.NtCreateFile.argtypes = [c.POINTER(w.HANDLE), w.DWORD, c.POINTER(ObjectAttributes), c.POINTER(IoStatus), w.LPVOID, w.DWORD, w.DWORD, w.DWORD, w.DWORD, w.LPVOID, w.DWORD]
    nt.NtCreateFile.restype = c.c_int32
    nt.RtlNtStatusToDosError.argtypes = [c.c_int32]
    nt.RtlNtStatusToDosError.restype = w.ULONG
    return kernel, nt


def create_child(nt, parent, name):
    """Final syscall, isolated for real Windows race-injection tests."""
    buffer = c.create_unicode_buffer(name)
    length = len(name.encode("utf-16-le"))
    text = UnicodeString(length, length + 2, c.cast(buffer, w.LPWSTR))
    attrs = ObjectAttributes(c.sizeof(ObjectAttributes), parent, c.pointer(text), 0x40, None, None)
    handle, status = w.HANDLE(), IoStatus()
    # GENERIC_WRITE | DELETE | SYNCHRONIZE; share READ only; FILE_CREATE;
    # DIRECTORY_FILE | SYNCHRONOUS_IO_NONALERT | OPEN_REPARSE_POINT.
    result = nt.NtCreateFile(c.byref(handle), 0x40110000, c.byref(attrs), c.byref(status),
                            None, 0x10, 1, 2, 0x200021, None, 0)
    if result < 0:
        raise c.WinError(nt.RtlNtStatusToDosError(result))
    return handle


def create_junction(parent_path: Path, name: str, source: Path, expected_id, validate):
    kernel, nt = windows_api()
    # Pin the verified directory object without following a final reparse point.
    # Share DELETE permits renames, but creation remains bound to this object.
    parent = kernel.CreateFileW(str(parent_path), 0x80, 7, None, 3, 0x02200000, None)
    if parent == w.HANDLE(-1).value:
        raise c.WinError(c.get_last_error())
    child = None
    try:
        info = FileInfo()
        if not kernel.GetFileInformationByHandle(parent, c.byref(info)):
            raise c.WinError(c.get_last_error())
        if (info.Attributes & 0x400 or
                (info.Volume, (info.IndexHigh << 32) | info.IndexLow) != tuple(expected_id)):
            raise ValueError("consumer-target-or-boundary-changed")
        validate()
        child = create_child(nt, parent, name)
        printed = str(source)
        if printed.startswith("\\\\") or not source.drive:
            raise ValueError("junction-source-must-be-local-drive")
        substitute = ("\\??\\" + printed).encode("utf-16-le")
        display = printed.encode("utf-16-le")
        paths = substitute + b"\0\0" + display + b"\0\0"
        payload = struct.pack("<IHHHHHH", 0xA0000003, 8 + len(paths), 0,
                              0, len(substitute), len(substitute) + 2, len(display)) + paths
        returned = w.DWORD()
        data = c.create_string_buffer(payload)
        if not kernel.DeviceIoControl(child, 0x900A4, data, len(payload), None, 0, c.byref(returned), None):
            raise c.WinError(c.get_last_error())
        observed = c.create_string_buffer(16384)
        if not kernel.DeviceIoControl(child, 0x900A8, None, 0, observed, len(observed), c.byref(returned), None):
            raise c.WinError(c.get_last_error())
        if observed.raw[:returned.value] != payload:
            raise ValueError("apply-verification-failed")
        validate()
    except BaseException:
        if child is not None:
            # Delete only our exclusive object by handle, never by pathname.
            # If deletion fails, leave it for inspection instead of a fallback.
            delete = c.c_ubyte(1)
            kernel.SetFileInformationByHandle(child, 4, c.byref(delete), c.sizeof(delete))
        raise
    finally:
        if child is not None:
            kernel.CloseHandle(child)
        kernel.CloseHandle(parent)


def require_safe_create() -> None:
    if os.name == "nt":
        windows_api()
        return
    if (os.name != "posix" or not hasattr(os, "O_DIRECTORY")
            or not hasattr(os, "O_NOFOLLOW")
            or os.stat not in os.supports_follow_symlinks
            or any(operation not in os.supports_dir_fd
                   for operation in (os.symlink, os.stat, os.readlink))):
        raise ValueError("safe-consumer-create-unsupported: requires Unix directory-fd symlink creation")


def create_link(repo: Path, target: Path, name: str, source: Path, expected: str) -> None:
    require_safe_create()
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", name):
        raise ValueError("invalid-skill")
    repo = repo.resolve(strict=True)
    source = source.resolve(strict=True)
    if not source.is_relative_to(repo) or source == repo or not (source / "SKILL.md").is_file():
        raise ValueError("source-outside-repository-or-invalid")
    resolved, token = inspect_target(repo, target)
    if token != expected:
        raise ValueError("consumer-target-or-boundary-changed")
    if os.name == "nt":
        def validate():
            if inspect_target(repo, target)[1] != expected:
                raise ValueError("consumer-target-or-boundary-changed")

        create_junction(resolved, name, source, json.loads(expected)[2], validate)
        return
    descriptor = os.open(resolved, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        opened = os.fstat(descriptor)
        parent_id = (opened.st_dev, opened.st_ino)
        if parent_id != tuple(json.loads(expected)[2]) or inspect_target(repo, target)[1] != expected:
            raise ValueError("consumer-target-or-boundary-changed")
        # symlinkat is exclusive and never treats an existing leaf as a
        # container. The fd binds creation to the verified parent even if its
        # pathname is replaced after the last check.
        os.symlink(str(source), name, dir_fd=descriptor)
        created = os.stat(name, dir_fd=descriptor, follow_symlinks=False)
        if not stat.S_ISLNK(created.st_mode) or os.readlink(name, dir_fd=descriptor) != str(source):
            raise ValueError("apply-verification-failed")
        if inspect_target(repo, target)[1] != expected:
            # Do not remove a concurrent actor's replacement or follow the new
            # path to roll back. Our link may remain in the original directory.
            raise ValueError("consumer-target-or-boundary-changed-after-create")
    finally:
        os.close(descriptor)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("operation", choices=("check", "create", "check-create-support"))
    parser.add_argument("--repository", type=Path)
    parser.add_argument("--target", type=Path)
    parser.add_argument("--name")
    parser.add_argument("--source", type=Path)
    parser.add_argument("--expected")
    parser.add_argument("--expected-env", action="store_true")
    args = parser.parse_args()
    if args.expected_env:
        args.expected = os.environ.get("SKILLS_CONSUMER_EXPECTED")
    try:
        if args.operation == "check-create-support":
            require_safe_create()
        elif args.repository is None or args.target is None:
            parser.error("--repository and --target are required")
        elif args.operation == "check":
            print(inspect_target(args.repository, args.target)[1])
        elif args.name is None or args.source is None or args.expected is None:
            parser.error("create requires --name, --source and --expected")
        else:
            create_link(args.repository, args.target, args.name, args.source, args.expected)
    except (OSError, ValueError, UnicodeError, RuntimeError) as exc:
        print(f"error {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
