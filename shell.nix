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
  packages = [ pythonEnv ];

  shellHook = ''
    export PYTHONPATH="$PWD:$PYTHONPATH"
  '';
}
