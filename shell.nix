{ pkgs ? import <nixpkgs> {} }:

let
  python = pkgs.python313;
  pythonEnv = python.withPackages (ps: [
    ps.hatchling
    ps.humanize
    ps.pysnmp
    ps.rich
    ps.pytest
    ps.pytest-asyncio
  ]);
in
pkgs.mkShell {
  packages = [ pythonEnv pkgs.ruff ];

  shellHook = ''
    export PYTHONPATH="$PWD:$PYTHONPATH"

    find "$HOME/.local/share/hatch/env/.internal/hatch-static-analysis" \
      -path "*/bin/ruff" -type f 2>/dev/null \
      | while read -r f; do
          ln -sf "$(command -v ruff)" "$f"
        done
  '';
}
