#!/bin/bash
# Multi-platform release driver.
#
# Bumps the version, commits, pushes to all four remotes (origin / mac /
# graviton4 / loongson), kicks off the local x86 build and three remote
# builds in parallel, pulls every wheel back, sanity-checks them, and
# uploads to PyPI under [pypi] from ~/.pypirc.
#
#     scripts/deploy.sh 0.1.3
#
# Targets — one wheel each unless noted:
#   x86_64 linux (local)       manylinux_2_34_x86_64  via cibuildwheel + podman
#   arm64 mac (`mac` host)     macosx_15_0_arm64      via /tmp/build_mac.sh
#   aarch64 linux (`graviton4`) manylinux_2_34_aarch64 via /tmp/build_graviton.sh
#   loongarch64 linux (`loongson`)    TWO wheels:
#       - old world: linux_loongarch64                via gcc 15.2.0
#       - new world: manylinux_2_38_loongarch64       via gcc 16.1.0
#
# Preconditions (set up once per host):
#   - Build scripts at /tmp/build_<host>.sh on mac, graviton4, loongson.
#   - SSH config with hosts mac, graviton4, loongson.
#   - receive.denyCurrentBranch=updateInstead on each remote checkout
#     (lets `git push <remote> main` update the working tree).
#   - ~/.pypirc [pypi] entry with an API token.
#   - podman installed locally; loongson cmake at /opt/loongson-cmake-4.3.2.
#
# The script doesn't ship a wheel without your sign-off — after pulling
# wheels back and running `twine check`, it waits for an Enter press
# before uploading and tagging.

set -euo pipefail

NEW_VERSION="${1?usage: $0 <new-version>   (e.g. 0.1.3)}"
REPO="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO"

# Reach twine in the user's general-env. Falls back to the PATH lookup.
TWINE="${TWINE:-/home/adam/general-env/bin/twine}"
command -v "$TWINE" >/dev/null || TWINE=twine

# ───────────────────────── version bump ──────────────────────────────────────
echo "[1/9] Bumping to ${NEW_VERSION}"
sed -i "s/^version = .*/version = \"${NEW_VERSION}\"/" pyproject.toml
sed -i "s/^__version__ = .*/__version__ = \"${NEW_VERSION}\"/" \
    src/witty_for_python/__init__.py

# ───────────────────────── commit + push ─────────────────────────────────────
echo "[2/9] Committing + pushing to origin/mac/graviton4/loongson"
git add pyproject.toml src/witty_for_python/__init__.py
if ! git diff --cached --quiet; then
    git commit -m "Release ${NEW_VERSION}"
fi
git push origin main
# --no-verify skips the git-lfs pre-push hook (the remote checkouts have no
# LFS server). The favicon under examples/ is the only LFS object and it's
# unused by the builds, so this is safe.
for r in mac graviton4 loongson; do
    echo "  push → $r"
    git push --no-verify "$r" main
done

# ─────────────────── pre-build TinyMCE → loongson ────────────────────────────
echo "[3/9] Staging pre-built TinyMCE dist on loongson"
# loongson's Node is 12.x — too old for TinyMCE's yarn build. Ship the dist
# we already have in our submodule tree so loongson can skip yarn entirely
# (build script reads /tmp/tinymce_dist.tar.gz when present).
TINYMCE_TARBALL=/tmp/tinymce_dist.tar.gz
if [[ -f "${REPO}/extern/tinymce/modules/tinymce/js/tinymce/tinymce.min.js" ]]; then
    tar czf "${TINYMCE_TARBALL}" \
        -C "${REPO}/extern/tinymce/modules/tinymce/js" tinymce/
    scp -q "${TINYMCE_TARBALL}" loongson:/tmp/tinymce_dist.tar.gz
else
    echo "  WARN: no pre-built TinyMCE under extern/tinymce — loongson will fail" >&2
fi

# ─────────────────── kick off all builds in parallel ─────────────────────────
echo "[4/9] Launching builds (local x86 + 3 remotes detached)"
rm -rf wheelhouse build dist
mkdir -p wheelhouse

# Local x86 — cibuildwheel inside a podman manylinux_2_34_x86_64 container.
( CIBW_CONTAINER_ENGINE=podman /home/adam/general-env/bin/cibuildwheel \
      --platform linux --output-dir wheelhouse \
      > /tmp/deploy_x86.log 2>&1 \
      && echo "  ✓ x86_64" \
      || { echo "  ✗ x86_64 (see /tmp/deploy_x86.log)"; false; } ) &
LOCAL_X86_PID=$!

# Remote builds — nohup-detached so the build survives ssh disconnects.
# (mac is zsh and doesn't have setsid; nohup alone is enough on macOS.)
launch_remote() {
    local host="$1" script="$2"
    ssh "$host" "
        cd ~/dev/witty_for_python &&
        rm -rf build dist wheelhouse 2>/dev/null
        rm -f /tmp/build_${host}.log
        nohup bash ${script} > /tmp/build_${host}.log 2>&1 < /dev/null &
        disown
        sleep 2
        pgrep -f ${script} >/dev/null && echo '  ✓ ${host} launched' || echo '  ✗ ${host} did not launch'
    "
}
launch_remote mac        /tmp/build_mac.sh
launch_remote graviton4  /tmp/build_graviton.sh
launch_remote loongson   /tmp/build_loongson.sh

# ──────────────────────── wait for completions ───────────────────────────────
echo "[5/9] Waiting for builds (local x86 in foreground; remotes polled)"
wait "$LOCAL_X86_PID" || true   # nonzero only if cibuildwheel actually errored

# Poll each remote until the build script is no longer running.
poll_until_done() {
    local host="$1" script="$2"
    echo "  polling $host…"
    while ssh -o ConnectTimeout=5 "$host" \
              "pgrep -f ${script} >/dev/null" 2>/dev/null; do
        sleep 60
    done
    echo "  ✓ $host build process exited"
}
poll_until_done mac        /tmp/build_mac.sh
poll_until_done graviton4  /tmp/build_graviton.sh
poll_until_done loongson   /tmp/build_loongson.sh

# ────────────────────────── pull wheels back ─────────────────────────────────
echo "[6/9] Collecting wheels from remotes"
for host in mac graviton4 loongson; do
    if ! scp -q "${host}:dev/witty_for_python/wheelhouse/witty_for_python-${NEW_VERSION}-*.whl" \
                wheelhouse/; then
        echo "  ✗ $host: no wheel — check /tmp/build_${host}.log on the host" >&2
        false
    fi
done
ls -la wheelhouse/

# ──────────────────────────── twine check ────────────────────────────────────
echo "[7/9] twine check"
"$TWINE" check wheelhouse/witty_for_python-"${NEW_VERSION}"-*.whl

# ───────────────────────── upload (with prompt) ──────────────────────────────
echo
echo "[8/9] About to upload to PyPI. Wheels:"
ls -1 wheelhouse/witty_for_python-"${NEW_VERSION}"-*.whl
echo
read -r -p "Hit Enter to upload, Ctrl-C to abort. " _
"$TWINE" upload --repository pypi \
    wheelhouse/witty_for_python-"${NEW_VERSION}"-*.whl

# ───────────────────────────── tag + push ────────────────────────────────────
echo "[9/9] Tagging v${NEW_VERSION}"
git tag "v${NEW_VERSION}"
git push origin "v${NEW_VERSION}"

echo
echo "🟢 Released v${NEW_VERSION}"
