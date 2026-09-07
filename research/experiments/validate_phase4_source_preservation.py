"""Check the complete inherited tree and original Phase-IV contract by identity."""

import hashlib
import json
import subprocess
from pathlib import Path

BASE_COMMIT = "a853d5d3f2d6c93a3483a0126ab3475b02960bfc"
BASE_TREE = "fae65d7457225dff1601eaf43fb0ef2b2d4b2c19"
CONTRACT_SHA256 = "1ec55a67aaa89289e7f167564fb9788fde136f6decc8f5dbfebc54e7d6009f03"
ROOT = Path(__file__).resolve().parents[2]


def check_preservation(root: Path = ROOT) -> dict[str, object]:
    tree = subprocess.check_output(
        ["git", "rev-parse", f"{BASE_COMMIT}^{{tree}}"], cwd=root, text=True,
    ).strip()
    if tree != BASE_TREE:
        raise ValueError("inherited tree identity mismatch")
    entries = subprocess.check_output(["git", "ls-tree", "-rz", BASE_COMMIT], cwd=root)
    changed: list[str] = []
    count = 0
    for entry in entries.split(b"\0"):
        if not entry:
            continue
        metadata, raw_path = entry.split(b"\t", 1)
        mode, kind, expected_blob = metadata.decode().split()
        relative = raw_path.decode("utf-8")
        path = root / relative
        count += 1
        if kind != "blob" or not path.is_file() or path.is_symlink():
            changed.append(relative)
            continue
        data = path.read_bytes()
        blob = hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
        executable = bool(path.stat().st_mode & 0o111)
        if blob != expected_blob or executable != (mode == "100755"):
            changed.append(relative)
    if changed:
        raise ValueError(f"inherited files changed: {changed}")
    contract = root / "research/contracts/DTRM_PHASE_IV_TEMPORAL_STATE_CONTRACT_v0.1.md"
    if hashlib.sha256(contract.read_bytes()).hexdigest() != CONTRACT_SHA256:
        raise ValueError("original Phase-IV v0.1 contract changed")
    binding = json.loads((root / "research/contracts/DTRM_PHASE4_SOURCE_BINDING_V0.json").read_text())
    if (binding["inherited_commit"] != BASE_COMMIT or binding["inherited_tree"] != BASE_TREE
            or binding["stage0_contract_sha256"] != CONTRACT_SHA256):
        raise ValueError("source binding does not match authoritative identities")
    return {"status": "PASS_SOURCE_PRESERVATION", "inherited_commit": BASE_COMMIT,
            "inherited_tree": BASE_TREE, "verified_inherited_files": count,
            "stage0_contract_sha256": CONTRACT_SHA256}


if __name__ == "__main__":
    print(json.dumps(check_preservation(), sort_keys=True))
