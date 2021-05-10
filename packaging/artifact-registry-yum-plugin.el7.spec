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

Name: yum-plugin-artifact-registry
Epoch:   1
Version: %{_version}
Release: g1%{?dist}
Summary: Yum plugin for Artifact Registry
License: ASL 2.0
Url: https://cloud.google.com/artifact-registry
Source0: %{name}_%{version}.orig.tar.gz
Source1: google-auth-1.21.2.tar.gz
Patch0: google-auth-el7-imports.patch

Requires: yum >= 3.0
Requires: python2-requests >= 2.0
Requires: python2-pyasn1
Requires: python2-pyasn1-modules
Requires: python2-rsa
Requires: python2-six
Requires: python-cachetools

BuildArch: noarch

%description
Contains a Yum plugin for authenticated access to Artifact Registry repositories.

%prep
%setup
%setup -T -D -a 1
mkdir _vendor
touch _vendor/__init__.py
mv google-auth-1.21.2/google _vendor/
rm -rf google-auth-1.21.2
%patch0

%install
install -d %{buildroot}/usr/lib/yum-plugins
install -p -m 0644 yum/artifact-registry.py %{buildroot}/usr/lib/yum-plugins/
install -d %{buildroot}/etc/yum/pluginconf.d
install -p -m 0644 artifact-registry.conf %{buildroot}/etc/yum/pluginconf.d/
install -d %{buildroot}%{python_sitelib}/artifact_registry/
touch %{buildroot}%{python_sitelib}/artifact_registry/__init__.py
cp -a _vendor %{buildroot}%{python_sitelib}/artifact_registry/


%files
%defattr(755,root,root,-)
/usr/lib/yum-plugins/artifact-registry.py*
/usr/lib/python2.7/site-packages/artifact_registry/*.py*
/usr/lib/python2.7/site-packages/artifact_registry/_vendor/*.py*
/usr/lib/python2.7/site-packages/artifact_registry/_vendor/google/*.py*
/usr/lib/python2.7/site-packages/artifact_registry/_vendor/google/auth/*.py*
/usr/lib/python2.7/site-packages/artifact_registry/_vendor/google/auth/compute_engine/*.py*
/usr/lib/python2.7/site-packages/artifact_registry/_vendor/google/auth/crypt/*.py*
/usr/lib/python2.7/site-packages/artifact_registry/_vendor/google/auth/transport/*.py*
/usr/lib/python2.7/site-packages/artifact_registry/_vendor/google/oauth2/*.py*
%config /etc/yum/pluginconf.d/artifact-registry.conf
%doc LICENSE
