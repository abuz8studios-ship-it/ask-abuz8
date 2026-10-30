# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec for the Ask ABUZ8 portable appliance (house pattern:
# one-dir exe + EXTERNAL data). simulator/ and data/ are NOT bundled — they
# ship next to the exe so the ledger stays writable and the feed swappable.
# server.py resolves them via sys.executable when frozen (see ROOT).
#
# Build: pyinstaller appliance/Ask-ABUZ8.spec --distpath dist-appliance --workpath build-appliance
# (normally via appliance/build_appliance.ps1, which also assembles + zips)

from pathlib import Path

ROOT = Path(SPECPATH).parent      # repo root
SERVER = ROOT / "mcp_server"

block_cipher = None

a = Analysis(
    [str(SERVER / "server.py")],
    pathex=[str(SERVER)],
    binaries=[],
    datas=[],
    hiddenimports=[
        # local core (belt-and-braces; also found via pathex)
        "isnad_core",
        # MCP SDK (dynamic bits)
        "mcp",
        "mcp.server",
        "mcp.server.fastmcp",
        "mcp.server.transport_security",
        "mcp.server.streamable_http",
        "mcp.server.streamable_http_manager",
        "mcp.types",
        # uvicorn auto-resolvers (house list)
        "uvicorn",
        "uvicorn.logging",
        "uvicorn.loops",
        "uvicorn.loops.auto",
        "uvicorn.protocols",
        "uvicorn.protocols.http",
        "uvicorn.protocols.http.auto",
        "uvicorn.protocols.websockets",
        "uvicorn.protocols.websockets.auto",
        "uvicorn.lifespan",
        "uvicorn.lifespan.on",
        "uvicorn.supervisors",
        # starlette (string-imported middleware)
        "starlette",
        "starlette.applications",
        "starlette.middleware",
        "starlette.middleware.errors",
        "starlette.responses",
        "starlette.requests",
        "starlette.routing",
        "starlette.datastructures",
        "pydantic",
        "httpx",
        "httpcore",
        "anyio",
        "sse_starlette",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="Ask-ABUZ8",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=True,  # errors stay visible; the launcher starts it minimized
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    name="Ask-ABUZ8",
)
