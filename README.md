# YUM and DNF plugins for Artifact Registry

This repository contains plugins for the YUM and DNF
package tools which add support for accessing
authenticated Artifact Registry repositories.

These plugins are supported on Enterprise Linux-based
Linux distributions including Red Hat Enterprise
Linux (RHEL) and CentOS.

## Installation

#### Configuring the repository

These plugins are available as installable RPM
packages in Google managed package repositories.
These repositories and therefore the packages are
available by default on Google Compute Engine
instances running Google managed GCE Images.
Otherwise, you can configure the repository on your
system by following these steps.

Create a file
`/etc/yum.repos.d/artifact-registry-plugin.repo`
with the following contents:

    [ar-plugin]
    name=Artifact Registry Plugin
    baseurl=https://packages.cloud.google.com/yum/repos/$YUM-plugin-artifact-registry-stable
    enabled=1
    gpgcheck=1
    repo_gpgcheck=0
    gpgkey=https://packages.cloud.google.com/yum/doc/yum-key.gpg
           https://packages.cloud.google.com/yum/doc/rpm-package-key.gpg

where $YUM should be "yum" if your operating
system is version 7 or earlier, "dnf" otherwise.

The plugin can then be installed by:

    $ yum install $YUM-plugin-artifact-registry

#### Flowplay-built packages (Rocky Linux 9 / 10)

This fork also builds and publishes `dnf-plugin-artifact-registry` RPMs for
Rocky Linux 9 and 10 to a Flowplay-managed, GPG-signed yum repository hosted
in `gs://flowplay-public-repo`. See [Releasing](#releasing) below for how
builds are produced.

Create `/etc/yum.repos.d/flowplay-ar-plugin.repo` with the contents matching
your OS major version (`el9` or `el10`):

    [flowplay-ar-plugin]
    name=Flowplay Artifact Registry Plugin
    baseurl=https://storage.googleapis.com/flowplay-public-repo/dnf/el9/x86_64
    enabled=1
    gpgcheck=1
    repo_gpgcheck=1
    gpgkey=https://storage.googleapis.com/flowplay-public-repo/dnf/doc/RPM-GPG-KEY-flowplay-public-repo

Then install with:

    $ dnf install dnf-plugin-artifact-registry

## Releasing

RPMs are built and published via
[`.github/workflows/build-rpm.yml`](.github/workflows/build-rpm.yml), which
builds natively inside `rockylinux/rockylinux:9` and `:10` containers, then
GPG-signs the packages and repo metadata before syncing to
`gs://flowplay-public-repo/dnf/{el9,el10}/x86_64`. It can be triggered in a
few ways, all restricted to the approvers listed in [OWNERS](OWNERS):

* Push a tag like `v1.2.3` on the default branch to build, sign, and publish
  both distros.
* Run the workflow manually (`workflow_dispatch`) to build only, or to
  build+publish by supplying a version and checking "publish".
* Comment on a pull request:
  * `/build-rpm [version]` — builds el9 + el10 RPMs from the PR head and
    uploads them as workflow run artifacts only (no signing, no publish).
  * `/publish-rpm <version>` — builds, signs, and publishes from the PR head.

One-time setup required before the publish path will work (not needed for
`/build-rpm`):

* `secrets.GPG_PRIVATE_KEY_B64` — a base64-encoded, armored GPG private key
  used to sign packages and repo metadata.
* `secrets.GPG_PASSPHRASE` — the passphrase for that key.
* `secrets.GCP_SA_KEY` — a JSON key for a service account in `operations-167722`
  granted `roles/storage.objectAdmin` on `gs://flowplay-public-repo` (scope
  the grant to the bucket, not the project).
* The bucket should grant `roles/storage.objectViewer` to `allUsers` (or
  equivalent) so `https://storage.googleapis.com/flowplay-public-repo/...`
  is publicly readable, matching the `baseurl`/`gpgkey` above.


## Configuration and usage

These plugins enable authenticated access to
repositories. After installing the appropriate yum
or dnf plugin, add the definition for your
repository following the
[official instructions](https://cloud.google.com/artifact-registry/docs/os-packages/rpm/configure).

By default, the plugin will attempt to detect and
use application default credentials as documented
[here](https://cloud.google.com/docs/authentication/application-default-credentials).
Practically this usually means using the
default service account associated with your GCE
instance at launch. Otherwise there are two options
which can be set in the appropriate plugin
configuration file.

#### Configuration options

The `service_account_json` option

Since it is impractical to set the
GOOGLE_APPLICATION_CREDENTIALS variable in all
contexts where yum or dnf may be invoked, this
option can be used to provide an absolute path to a
JSON file containing service account or application
default credentials. This option takes precedence, if
both are set, this one will be used.

The `service_account_email` option

By default on GCE instances the plugin will use the
"default" service account, typically the compute
service service account for the project. If the
instance is launched with custom service accounts or
multiple service accounts, this option may be used to
specify which one should be used.
