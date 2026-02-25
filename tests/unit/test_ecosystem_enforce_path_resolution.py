from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path


def _load_module(module_path: Path, module_name: str):
    spec = spec_from_file_location(module_name, module_path)
    module = module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_root_enforce_prefers_canonical_ecosystem() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    root_enforce = _load_module(repo_root / "ecosystem" / "enforce.py", "root_enforce")

    expected_ecosystem = (
        repo_root
        / "governance"
        / "l3_execution"
        / "boundaries"
        / "namespace-governance-boundary"
        / "implementation"
        / "ecosystem"
    )

    assert root_enforce.ECOSYSTEM_ROOT == expected_ecosystem
    assert root_enforce.WORKSPACE_ROOT == expected_ecosystem.parent
