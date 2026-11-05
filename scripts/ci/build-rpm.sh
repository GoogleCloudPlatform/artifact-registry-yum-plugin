#!/usr/bin/env bash
# Builds the dnf-plugin-artifact-registry RPM natively inside a Rocky Linux
# container (el9 or el10). Intended to be run by .github/workflows/build-rpm.yml
# from the root of a checked-out source tree.
set -euo pipefail

if [[ $# -ne 2 ]]; then
  echo "usage: $0 <dist: el9|el10> <version>" >&2
  exit 1
fi

DIST="$1"
VERSION="$2"
NAME="dnf-plugin-artifact-registry"
GO_BOOTSTRAP_VERSION="1.23.4"

case "$(uname -m)" in
  x86_64) GOARCH=amd64 ;;
  aarch64) GOARCH=arm64 ;;
  *) echo "unsupported arch: $(uname -m)" >&2; exit 1 ;;
esac

echo "==> Installing build dependencies"
# Rocky's minimal images ship curl-minimal, which conflicts with the full
# curl package but already provides a working /usr/bin/curl, so it's
# intentionally left off this list.
dnf install -y rpm-build rpmdevtools python3-devel git tar gzip which make

# The repo's go.mod pins a toolchain (go1.26.x) newer than what Rocky's dnf
# repos may ship. Any Go >=1.21 understands the go.mod "toolchain" directive
# and will transparently download the exact required toolchain on first use
# (GOTOOLCHAIN=auto, the default), so we only need a modern-enough bootstrap.
echo "==> Bootstrapping Go ${GO_BOOTSTRAP_VERSION} (bootstrap only; go.mod toolchain directive upgrades as needed)"
curl -fsSL "https://go.dev/dl/go${GO_BOOTSTRAP_VERSION}.linux-${GOARCH}.tar.gz" -o /tmp/go.tar.gz
tar -C /usr/local -xzf /tmp/go.tar.gz
export PATH="/usr/local/go/bin:${PATH}"
export GOPATH="${HOME}/go"
export GOTOOLCHAIN=auto
go version

echo "==> Preparing rpmbuild tree"
rpmdev-setuptree

SOURCE_DIR="${HOME}/rpmbuild/SOURCES"
TARBALL="${SOURCE_DIR}/${NAME}_${VERSION}.orig.tar.gz"

echo "==> Building source tarball ${TARBALL}"
tar --exclude-vcs \
    --transform "s,^,${NAME}-${VERSION}/," \
    -czf "${TARBALL}" .

echo "==> Building RPM (dist=.${DIST}, version=${VERSION})"
rpmbuild -ba packaging/artifact-registry-yum-plugin.spec \
  --define "_version ${VERSION}" \
  --define "_go /usr/local/go/bin/go" \
  --define "_gopath ${GOPATH}" \
  --define "dist .${DIST}"

OUT_DIR="dist/${DIST}"
mkdir -p "${OUT_DIR}"
find "${HOME}/rpmbuild/RPMS" -name '*.rpm' -exec cp -v {} "${OUT_DIR}/" \;

echo "==> Built packages:"
find "${OUT_DIR}" -name '*.rpm'
