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


## Configuration and usage

These plugins enable authenticated access to
repositories. After installing the appropriate yum
or dnf plugin, add the definition for your
repository following the `official instructions`.

By default, the plugin will attempt to detect and
use application default credentials as documented
`here`. Practically this usually means using the
default service account associated with your GCE
instance at launch. Otherwise there are two options
which can be set in the appropriate plugin
configuration file.

#### Configuration options

The `service\_account\_json` option

Since it is impractical to set the
GOOGLE\_APPLICATION\_CREDENTIALS variable in all
contexts where yum or dnf may be invoked, this
option can be used to provide an absolute path to a
JSON file containing service account or application
default credentials. This option takes precedence, if
both are set, this one will be used.

The `service\_account\_email` option

By default on GCE instances the plugin will use the
"default" service account, typically the compute
service service account for the project. If the
instance is launched with custom service accounts or
multiple service accounts, this option may be used to
specify which one should be used.
