"""Windows junctions: NtCreateFile RootDirectory + FILE_CREATE, then handle IO.

Microsoft Learn: winternl/nf-winternl-ntcreatefile and
winioctl/ni-winioctl-fsctl_set_reparse_point. No symlink privilege required.
"""
from __future__ import annotations

import ctypes as c
from ctypes import wintypes as w
from pathlib import Path
import struct


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


def api():
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
    kernel, nt = api()
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
