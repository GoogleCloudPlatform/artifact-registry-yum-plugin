# Copyright 2021 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

Name: dnf-plugin-artifact-registry
Epoch:   1
Version: %{_version}
Release: g1%{?dist}
Summary: dnf plugin for Artifact Registry
License: ASL 2.0
Url: https://cloud.google.com/artifact-registry
Source0: %{name}_%{version}.orig.tar.gz
Source1: google-auth-1.30.0.tar.gz
Source2: cachetools-4.2.2.tar.gz
Source3: rsa-4.7.2.tar.gz
Patch0: google-auth-imports.patch
Patch1: cachetools-imports.patch
Patch2: rsa-imports.patch

Requires: dnf >= 1.0.0
Requires: python3-requests >= 2.0
Requires: python3-pyasn1
Requires: python3-pyasn1-modules
Requires: python3-six

BuildArch: noarch

%description
Contains a dnf plugin for authenticated access to Artifact Registry repositories.

%prep
%setup
%setup -T -D -a 1
%setup -T -D -a 2
%setup -T -D -a 3
mkdir _vendor
mv google-auth-1.30.0/google _vendor/
rm -rf google-auth-1.30.0
mv cachetools-4.2.2/src/cachetools _vendor/
rm -rf cachetools-4.2.2
mv rsa-4.7.2/rsa _vendor/
rm -rf rsa-4.7.2
%patch0
%patch1
%patch2

%install
%define __python /usr/bin/python3
install -d %{buildroot}%{python_sitelib}/dnf-plugins
install -p -m 0644 dnf/artifact-registry.py %{buildroot}%{python_sitelib}/dnf-plugins/
install -d %{buildroot}/etc/dnf/plugins
install -p -m 0644 artifact-registry.conf %{buildroot}/etc/dnf/plugins/
install -d %{buildroot}%{python_sitelib}/artifact_registry/
mv _vendor %{buildroot}%{python_sitelib}/artifact_registry/

%files
%defattr(-,root,root,-)
%{python_sitelib}/dnf-plugins/artifact-registry.py
%{python_sitelib}/dnf-plugins/__pycache__/artifact-registry*.py*
%{python_sitelib}/artifact_registry/_vendor/google/*.py*
%{python_sitelib}/artifact_registry/_vendor/google/auth/*.py*
%{python_sitelib}/artifact_registry/_vendor/google/auth/compute_engine/*.py*
%{python_sitelib}/artifact_registry/_vendor/google/auth/compute_engine/__pycache__/*.py*
%{python_sitelib}/artifact_registry/_vendor/google/auth/crypt/*.py*
%{python_sitelib}/artifact_registry/_vendor/google/auth/crypt/__pycache__/*.py*
%{python_sitelib}/artifact_registry/_vendor/google/auth/transport/*.py*
%{python_sitelib}/artifact_registry/_vendor/google/auth/transport/__pycache__/*.py*
%{python_sitelib}/artifact_registry/_vendor/google/auth/__pycache__/*.py*
%{python_sitelib}/artifact_registry/_vendor/google/oauth2/*.py*
%{python_sitelib}/artifact_registry/_vendor/google/oauth2/__pycache__/*.py*
%{python_sitelib}/artifact_registry/_vendor/google/__pycache__/*.py*
%{python_sitelib}/artifact_registry/_vendor/cachetools/*.py*
%{python_sitelib}/artifact_registry/_vendor/cachetools/__pycache__/*.py*
%{python_sitelib}/artifact_registry/_vendor/rsa/*.py*
%{python_sitelib}/artifact_registry/_vendor/rsa/__pycache__/*.py*
%config /etc/dnf/plugins/artifact-registry.conf
%doc LICENSE
