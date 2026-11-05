#!/usr/bin/env bash
# Signs the RPMs for one distro directory, builds + signs yum repo metadata,
# and syncs the result to the given GCS bucket path. Intended to be run by
# .github/workflows/build-rpm.yml on a runner with gnupg2, rpm and
# createrepo_c/createrepo-c installed, and gcloud authenticated.
set -euo pipefail

if [[ $# -ne 2 ]]; then
  echo "usage: $0 <local repo dir, e.g. dist/el9> <gcs destination, e.g. gs://bucket/dnf/el9/x86_64>" >&2
  exit 1
fi

RPM_DIR="$1"
BUCKET_PATH="$2"

: "${GPG_KEY_ID:?GPG_KEY_ID env var is required}"
: "${GPG_PASSPHRASE:?GPG_PASSPHRASE env var is required}"

shopt -s nullglob
rpms=("${RPM_DIR}"/*.rpm)
if [[ ${#rpms[@]} -eq 0 ]]; then
  echo "no RPMs found in ${RPM_DIR}" >&2
  exit 1
fi

echo "==> Signing ${#rpms[@]} package(s) in ${RPM_DIR}"
rpm \
  --define "_gpg_name ${GPG_KEY_ID}" \
  --define "__gpg_sign_cmd %{__gpg} gpg --batch --no-armor --pinentry-mode loopback --passphrase-fd 3 --no-secmem-warning -u \"%{_gpg_name}\" -sbo %{__signature_filename} %{__plaintext_filename}" \
  --addsign "${rpms[@]}" 3< <(printf '%s' "${GPG_PASSPHRASE}")

echo "==> Verifying package signatures"
rpm -K "${rpms[@]}"

echo "==> Building repo metadata in ${RPM_DIR}"
createrepo_c --update "${RPM_DIR}"

echo "==> Signing repomd.xml"
gpg --batch --yes --pinentry-mode loopback --passphrase-fd 3 \
  --detach-sign --armor \
  -o "${RPM_DIR}/repodata/repomd.xml.asc" \
  "${RPM_DIR}/repodata/repomd.xml" 3< <(printf '%s' "${GPG_PASSPHRASE}")

echo "==> Syncing ${RPM_DIR} to ${BUCKET_PATH}"
gcloud storage rsync "${RPM_DIR}" "${BUCKET_PATH}" \
  --recursive \
  --delete-unmatched-destination-objects
