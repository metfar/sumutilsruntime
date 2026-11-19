#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#pylint:disable=W0301
#  
#  Copyright 2018- William Martinez Bas <metfar@gmail.com>
#  
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#  
#
#import warnings;
#warnings.filterwarnings("ignore", category=UserWarning);

"""Portable SUM utility runtime for official Python runtimes.

This module must remain independent of SUM packages.
"""

from __future__ import annotations;

import builtins;
import importlib;
import math;
import os;
from pathlib import Path;
import pickle;
import re;
import subprocess;
import sys;
import zlib;
from types import ModuleType;
from typing import Iterable, Mapping, Sequence;


# Python's native print already has the SUM-style semantics wanted in R.
printR = builtins.print;
print_r = builtins.print;
print = builtins.print;


def load_package(
    pkg: str,
    *,
    pip_name: str | None = None,
    install_missing: bool = True,
) -> dict[str, object]:
    """Load one module, optionally installing its package with pip."""
    try:
        module = importlib.import_module(pkg);
        return {
            "package": pkg,
            "ok": True,
            "reason": None,
            "module": module,
        };
    except ModuleNotFoundError as exc:
        root_name = pkg.split(".", 1)[0];

        if exc.name not in {pkg, root_name}:
            return {
                "package": pkg,
                "ok": False,
                "reason": (
                    f"Module '{pkg}' was found, but dependency "
                    f"'{exc.name}' is missing."
                ),
                "module": None,
            };

        if not install_missing:
            return {
                "package": pkg,
                "ok": False,
                "reason": f"Module '{pkg}' is not installed.",
                "module": None,
            };

    install_name = pip_name or pkg.split(".", 1)[0];

    try:
        subprocess.run(
            [
                sys.executable,
                "-m",
                "pip",
                "install",
                install_name,
            ],
            check=True,
        );
    except subprocess.CalledProcessError as exc:
        return {
            "package": pkg,
            "ok": False,
            "reason": (
                f"Could not install package '{install_name}' "
                f"for module '{pkg}': exit status {exc.returncode}."
            ),
            "module": None,
        };

    try:
        module = importlib.import_module(pkg);
    except Exception as exc:  # pylint:disable=broad-exception-caught
        return {
            "package": pkg,
            "ok": False,
            "reason": (
                f"Package '{install_name}' was installed but module "
                f"'{pkg}' could not be imported: {exc}"
            ),
            "module": None,
        };

    return {
        "package": pkg,
        "ok": True,
        "reason": None,
        "module": module,
    };


def load_packages(
    *module_names: str,
    strict: bool = True,
    pip_names: Mapping[str, str] | None = None,
    install_missing: bool = True,
) -> ModuleType | tuple[ModuleType | None, ...] | None:
    """Load several modules, mirroring sum_utils.R load_packages()."""
    if not module_names:
        return None;

    pip_names = {} if pip_names is None else dict(pip_names);
    width = max(len(name) for name in module_names) + 2;
    results: list[dict[str, object]] = [];

    print("Loading dependencies:");

    for module_name in module_names:
        root_name = module_name.split(".", 1)[0];
        result = load_package(
            module_name,
            pip_name=pip_names.get(
                module_name,
                pip_names.get(root_name),
            ),
            install_missing=install_missing,
        );
        results.append(result);
        status = "OK" if bool(result["ok"]) else "FAILED";
        print(f"  {module_name:<{width}} {status}");

    failed = [result for result in results if not bool(result["ok"])];

    if failed:
        print("");

        for result in failed:
            print(f"Issue: {result['reason']}");

        if strict:
            raise RuntimeError(
                "One or more Python dependencies could not be loaded."
            );

        print("");
        print("Continuing without unavailable dependencies.");

    modules = tuple(
        result["module"] if bool(result["ok"]) else None
        for result in results
    );

    if len(modules) == 1:
        return modules[0];

    return modules;


# Short, declarative alias for scripts.
include = load_packages;


# Division helpers

def intdiv(a, b):
    """Floor/integer division."""
    return a // b;


def moddiv(a, b):
    """Division remainder."""
    return a % b;


def div(a, b) -> dict[str, object]:
    """Return real result, integer quotient, and remainder."""
    return {
        "result": a / b,
        "quotient": intdiv(a, b),
        "remainder": moddiv(a, b),
    };


# ---------------------------------------------------------------------------
# Angular units
# ---------------------------------------------------------------------------

PI = math.pi;
TAU = math.tau if hasattr(math, "tau") else 2.0 * math.pi;

# Historical SUM/BASIC conversion factors: "a radianes" and "a grados".
# AGRAD means "to degrees" here; it is not the abbreviation for gradians.
ARAD = PI / 180.0;
AGRAD = 180.0 / PI;


def deg2rad(value):
    """Convert sexagesimal degrees to radians."""
    return value * PI / 180.0;


def rad2deg(value):
    """Convert radians to sexagesimal degrees."""
    return value * 180.0 / PI;


def gra2rad(value):
    """Convert gradians (gon) to radians."""
    return value * PI / 200.0;


def rad2gra(value):
    """Convert radians to gradians (gon)."""
    return value * 200.0 / PI;


def gra2deg(value):
    """Convert gradians (gon) to sexagesimal degrees."""
    return value * 0.9;


def deg2gra(value):
    """Convert sexagesimal degrees to gradians (gon)."""
    return value * 10.0 / 9.0;


# Surveying/geodesy aliases. A gon and a gradian are the same unit.
gon2rad = gra2rad;
rad2gon = rad2gra;
gon2deg = gra2deg;
deg2gon = deg2gra;

def project_dir() -> Path:
    """Return the directory containing this runtime module."""
    return Path(__file__).resolve().parent;


def project_path(*parts: str | os.PathLike[str]) -> Path:
    """Build a path relative to the directory containing the runtime module."""
    return project_dir().joinpath(*parts);


def ensure_dir(path: str | os.PathLike[str]) -> Path:
    """Create a directory, including parents, when it does not exist."""
    result = Path(path).expanduser().resolve();
    result.mkdir(parents=True, exist_ok=True);
    return result;


def show_file(
    path: str | os.PathLike[str],
    *,
    wait: bool = False,
) -> subprocess.Popen[bytes] | None:
    """
    Open a file with the platform's default desktop application.

    Linux uses xdg-open, macOS uses open, and Windows uses os.startfile().
    """
    file_path = Path(path).expanduser().resolve();

    if not file_path.exists():
        raise FileNotFoundError(file_path);

    if sys.platform.startswith("linux"):
        return subprocess.Popen(
            ["xdg-open", str(file_path)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        ) if not wait else _run_and_return_none(["xdg-open", str(file_path)]);

    if sys.platform == "darwin":
        return subprocess.Popen(
            ["open", str(file_path)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        ) if not wait else _run_and_return_none(["open", str(file_path)]);

    if os.name == "nt":
        os.startfile(str(file_path));  # type: ignore[attr-defined]
        return None;

    raise RuntimeError(f"Unsupported platform: {sys.platform}");


def _run_and_return_none(command: Sequence[str]) -> None:
    """Run a command synchronously and return None."""
    subprocess.run(
        list(command),
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    );
    return None;


def save_plot(
    figure,
    filename: str | os.PathLike[str],
    *,
    width: float = 12.0,
    height: float = 7.0,
    dpi: int = 150,
    show: bool = True,
    tight: bool = False,
) -> Path:
    """Save a Plotnine ggplot or Matplotlib Figure and optionally open it.

    Plotnine is handled directly so Python examples can preserve ggplot-like
    dimensions and composition. Matplotlib output is *not* tight-cropped by
    default because ggplot2::ggsave() also preserves the requested canvas.
    """
    output_path = Path(filename).expanduser().resolve();
    output_path.parent.mkdir(parents=True, exist_ok=True);

    module_name = type(figure).__module__;

    if module_name.startswith("plotnine") and hasattr(figure, "save"):
        figure.save(
            filename=str(output_path),
            width=width,
            height=height,
            dpi=dpi,
            verbose=False,
        );
    elif hasattr(figure, "savefig") and hasattr(figure, "set_size_inches"):
        figure.set_size_inches(width, height);
        save_kwargs = {"dpi": dpi};

        if tight:
            save_kwargs["bbox_inches"] = "tight";

        figure.savefig(
            output_path,
            **save_kwargs,
        );
    else:
        raise TypeError(
            "save_plot() expects a Plotnine ggplot or Matplotlib Figure."
        );

    print(f"[SumUtilsRuntime] Plot saved to: {output_path}");

    if show:
        show_file(output_path);

    return output_path;



# ---------------------------------------------------------------------------
# Copy/paste serialization blocks
# ---------------------------------------------------------------------------

_SUMBLOCK_FORMAT = "SUMBLOCK/1";
_SUMBLOCK_LANGUAGE = "Python";
_SUMBLOCK_ENCODING = "hex";
_SUMBLOCK_COMPRESSION = "zlib";


def _sumblock_lines(blocks: Mapping[str, object]) -> list[str]:
    """Convert a SUMBLOCK mapping into copy/paste-safe text lines."""
    chunks = [str(chunk) for chunk in blocks["chunks"]];
    total = len(chunks);
    lines = [
        f"===== {blocks['format']} =====",
        f"language={blocks['language']}",
        f"serialization={blocks['serialization']}",
        f"compression={blocks['compression']}",
        f"encoding={blocks['encoding']}",
        f"chunk_size={blocks['chunk_size']}",
        f"chunks={total}",
        f"payload_bytes={blocks['payload_bytes']}",
        f"object_bytes={blocks['object_bytes']}",
    ];

    for index, chunk in enumerate(chunks, start=1):
        lines.extend(
            [
                f"===== CHUNK {index}/{total} =====",
                chunk,
                f"===== END CHUNK {index}/{total} =====",
            ]
        );

    lines.append(f"===== END {blocks['format']} =====");
    return lines;


def serializeInBlocks(
    obj,
    chunk_size: int = 12000,
    *,
    emit: bool = False,
) -> dict[str, object]:
    """Serialize any picklable Python object into numbered text blocks.

    The envelope is portable text; the payload intentionally remains native to
    Python. Use SUMTAB (or another interchange format) for cross-language data.
    """
    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than zero.");

    raw_data = pickle.dumps(
        obj,
        protocol=pickle.HIGHEST_PROTOCOL,
    );
    compressed = zlib.compress(raw_data);
    encoded = compressed.hex();
    chunks = [
        encoded[start:start + chunk_size]
        for start in range(0, len(encoded), chunk_size)
    ];

    result: dict[str, object] = {
        "format": _SUMBLOCK_FORMAT,
        "language": _SUMBLOCK_LANGUAGE,
        "serialization": f"pickle-{pickle.HIGHEST_PROTOCOL}",
        "compression": _SUMBLOCK_COMPRESSION,
        "encoding": _SUMBLOCK_ENCODING,
        "chunk_size": chunk_size,
        "payload_bytes": len(compressed),
        "object_bytes": len(raw_data),
        "chunks": chunks,
    };

    if emit:
        printBlocks(result);

    return result;


def _parse_sumblock_text(text_value: str | Sequence[str]) -> dict[str, object]:
    """Parse text produced by printBlocks()."""
    text_blob = text_value if isinstance(text_value, str) else "\n".join(text_value);
    lines = [line.strip() for line in text_blob.splitlines() if line.strip()];

    if not lines or not lines[0].startswith("===== SUMBLOCK/"):
        raise ValueError("Input does not start with a SUMBLOCK header.");

    header_match = re.fullmatch(r"===== (SUMBLOCK/\d+) =====", lines[0]);

    if header_match is None:
        raise ValueError("Malformed SUMBLOCK header.");

    metadata: dict[str, object] = {"format": header_match.group(1)};
    chunks: dict[int, str] = {};
    index = 1;

    while index < len(lines):
        line = lines[index];

        if line == f"===== END {metadata['format']} =====":
            break;

        chunk_match = re.fullmatch(r"===== CHUNK (\d+)/(\d+) =====", line);

        if chunk_match is not None:
            chunk_number = int(chunk_match.group(1));
            total = int(chunk_match.group(2));
            index += 1;
            payload_lines: list[str] = [];
            end_marker = f"===== END CHUNK {chunk_number}/{total} =====";

            while index < len(lines) and lines[index] != end_marker:
                payload_lines.append(lines[index]);
                index += 1;

            if index >= len(lines):
                raise ValueError(f"Missing end marker for chunk {chunk_number}.");

            if chunk_number in chunks:
                raise ValueError(f"Duplicate chunk {chunk_number}.");

            chunks[chunk_number] = "".join(payload_lines);
            metadata.setdefault("declared_chunks", total);
        elif "=" in line:
            key, value = line.split("=", 1);
            metadata[key] = value;

        index += 1;

    total = int(metadata.get("chunks", metadata.get("declared_chunks", 0)));

    if total <= 0:
        raise ValueError("SUMBLOCK metadata does not declare a positive chunk count.");

    missing = [number for number in range(1, total + 1) if number not in chunks];

    if missing:
        raise ValueError(f"Missing SUMBLOCK chunks: {missing}");

    metadata["chunks"] = [chunks[number] for number in range(1, total + 1)];

    for key in ("chunk_size", "payload_bytes", "object_bytes"):
        if key in metadata:
            metadata[key] = int(str(metadata[key]));

    return metadata;


def inspectBlocks(
    blocks: Mapping[str, object] | str | Sequence[str],
) -> dict[str, object]:
    """Validate and summarize a SUMBLOCK payload without deserializing it."""
    parsed = dict(blocks) if isinstance(blocks, Mapping) else _parse_sumblock_text(blocks);
    chunks = [str(chunk) for chunk in parsed.get("chunks", [])];
    encoded = "".join(chunks);

    if str(parsed.get("format")) != _SUMBLOCK_FORMAT:
        raise ValueError(f"Unsupported SUMBLOCK format: {parsed.get('format')}");

    if str(parsed.get("encoding")) != _SUMBLOCK_ENCODING:
        raise ValueError(f"Unsupported encoding: {parsed.get('encoding')}");

    if len(encoded) % 2 != 0 or re.fullmatch(r"[0-9a-fA-F]*", encoded) is None:
        raise ValueError("SUMBLOCK hex payload is malformed.");

    payload = bytes.fromhex(encoded);
    declared_payload_bytes = int(parsed.get("payload_bytes", len(payload)));

    if len(payload) != declared_payload_bytes:
        raise ValueError(
            f"Payload size mismatch: expected {declared_payload_bytes}, got {len(payload)}."
        );

    result = {
        "format": parsed.get("format"),
        "language": parsed.get("language"),
        "serialization": parsed.get("serialization"),
        "compression": parsed.get("compression"),
        "encoding": parsed.get("encoding"),
        "chunks": len(chunks),
        "payload_bytes": len(payload),
        "object_bytes": int(parsed.get("object_bytes", 0)),
        "status": "COMPLETE",
    };
    return result;


def printBlocks(
    blocks: Mapping[str, object],
) -> None:
    """Print SUMBLOCK text exactly as it should be copied from a console."""
    for line in _sumblock_lines(blocks):
        print(line);


def unserializeInBlocks(
    blocks: Mapping[str, object] | str | Sequence[str],
):
    """Restore a Python object from serializeInBlocks()/printBlocks() output."""
    parsed = dict(blocks) if isinstance(blocks, Mapping) else _parse_sumblock_text(blocks);
    inspectBlocks(parsed);

    if str(parsed.get("language")) != _SUMBLOCK_LANGUAGE:
        raise ValueError(
            f"This payload is native to {parsed.get('language')}; Python was expected."
        );

    if str(parsed.get("compression")) != _SUMBLOCK_COMPRESSION:
        raise ValueError(f"Unsupported compression: {parsed.get('compression')}");

    compressed = bytes.fromhex("".join(str(x) for x in parsed["chunks"]));
    raw_data = zlib.decompress(compressed);
    declared_object_bytes = int(parsed.get("object_bytes", len(raw_data)));

    if len(raw_data) != declared_object_bytes:
        raise ValueError(
            f"Object size mismatch: expected {declared_object_bytes}, got {len(raw_data)}."
        );

    return pickle.loads(raw_data);


serialize_in_blocks = serializeInBlocks;
unserialize_in_blocks = unserializeInBlocks;
print_blocks = printBlocks;
inspect_blocks = inspectBlocks;

def section(title: str, width: int = 72) -> None:
    """Print a readable section heading for didactic console output."""
    rule = "=" * width;
    print();
    print(rule);
    print(title);
    print(rule);


def subsection(title: str, width: int = 72) -> None:
    """Print a smaller section heading."""
    print();
    print(title);
    print("-" * min(width, max(len(title), 12)));


def show_values(
    values: Mapping[str, object] | Iterable[tuple[str, object]],
) -> None:
    """Print labelled values in a compact aligned form."""
    items = list(values.items()) if isinstance(values, Mapping) else list(values);

    if not items:
        return;

    label_width = max(len(str(label)) for label, _ in items);

    for label, value in items:
        print(f"{str(label):<{label_width}} : {value}");


def format_p_value(p_value: float) -> str:
    """Format a p-value without hiding very small values."""
    if p_value < 0.0001:
        return f"{p_value:.6e}";

    return f"{p_value:.6f}";


def hypothesis_decision(
    p_value: float,
    alpha: float = 0.05,
    *,
    null_name: str = "H0",
) -> bool:
    """
    Print and return the decision for a classical null-hypothesis test.

    Returns True when H0 is rejected, otherwise False.
    """
    reject = p_value <= alpha;

    show_values(
        {
            "p-value": format_p_value(p_value),
            "alpha": alpha,
        }
    );

    if reject:
        print(f"Decision : REJECT {null_name}");
        print(
            "Reason   : p-value <= alpha, so the observed result is "
            "sufficiently incompatible with the null hypothesis."
        );
    else:
        print(f"Decision : FAIL TO REJECT {null_name}");
        print(
            "Reason   : p-value > alpha, so the sample does not provide "
            "enough evidence to reject the null hypothesis."
        );

    return reject;


def explain(text: str) -> None:
    """Print a didactic explanation paragraph."""
    print();
    print(f"Explanation: {text}");


__all__ = [
    "AGRAD",
    "ARAD",
    "PI",
    "TAU",
    "deg2gon",
    "deg2gra",
    "deg2rad",
    "div",
    "gon2deg",
    "gon2rad",
    "gra2deg",
    "gra2rad",
    "ensure_dir",
    "explain",
    "format_p_value",
    "hypothesis_decision",
    "include",
    "inspectBlocks",
    "inspect_blocks",
    "intdiv",
    "load_package",
    "load_packages",
    "moddiv",
    "print",
    "printBlocks",
    "print_blocks",
    "printR",
    "print_r",
    "project_dir",
    "project_path",
    "rad2deg",
    "rad2gon",
    "rad2gra",
    "save_plot",
    "serializeInBlocks",
    "serialize_in_blocks",
    "section",
    "show_file",
    "show_values",
    "subsection",
    "unserializeInBlocks",
    "unserialize_in_blocks",
];
