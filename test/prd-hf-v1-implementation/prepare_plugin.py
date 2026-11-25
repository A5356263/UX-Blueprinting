from pathlib import Path
import io, json, shutil, subprocess, zipfile

sandbox = Path(__file__).resolve().parent
bundle = sandbox / "plugin-bundle"
plugin = Path(r"E:/AI设计/codex-prd-review-short-evidence-only-plugin")
assert not bundle.exists()
tracked = subprocess.check_output(["git", "archive", "--format=zip", "HEAD"], cwd=plugin)
with zipfile.ZipFile(io.BytesIO(tracked)) as snapshot:
    snapshot.extractall(bundle)
for rel in subprocess.check_output(["git", "diff", "--name-only", "-z", "HEAD"], cwd=plugin).decode("utf8").strip("\0").split("\0"):
    assert rel.startswith((".agents/skills/prd-review/", ".agents/skills/page-spec/", "shared-workflow/skill-graph.json")), rel
    old,new = plugin/rel,bundle/rel
    if old.is_file():
        shutil.copyfile(old,new)
    elif new.is_file():
        new.unlink()
print(bundle)
