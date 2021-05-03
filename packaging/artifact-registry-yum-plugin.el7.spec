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

Requires: yum >= 3.0
Requires: python2-google-auth >= 1.1.1
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
%autosetup

%install
install -d %{buildroot}/usr/lib/yum-plugins
install -p -m 0644 yum/artifact-registry.py %{buildroot}/usr/lib/yum-plugins/
install -d %{buildroot}/etc/yum/pluginconf.d
install -p -m 0644 artifact-registry.conf %{buildroot}/etc/yum/pluginconf.d/
# Setup vendored google-auth package, legacy version with python2.7 support.
install -d %{buildroot}/usr/lib/python2.7/site-packages/artifact_registry/_vendor
touch %{buildroot}/usr/lib/python2.7/site-packages/artifact_registry/_vendor/__init__.py
cp -av vendor/google-auth-1.21.2/google %{buildroot}/usr/lib/python2.7/site-packages/artifact_registry/_vendor
find  %{buildroot}/usr/lib/python2.7/site-packages/artifact_registry/_vendor/ \
  -type f -iname '*.py' -exec sed -i "" \
  -e 's/google\.auth/artifact_registry._vendor.google.auth/g' '{}' \;
find  %{buildroot}/usr/lib/python2.7/site-packages/artifact_registry/_vendor/ \
  -type f -iname '*.py' -exec sed -i "" \
  -e 's/google\.oauth2/artifact_registry._vendor.google.oauth2/g' '{}' \;


%files
%defattr(755,root,root,-)
/usr/lib/yum-plugins/artifact-registry.py*
/usr/lib/python2.7/site-packages/artifact_registry/_vendor/*.py*
/usr/lib/python2.7/site-packages/artifact_registry/_vendor/google/*.py*
/usr/lib/python2.7/site-packages/artifact_registry/_vendor/google/auth/*.py*
/usr/lib/python2.7/site-packages/artifact_registry/_vendor/google/auth/compute_engine/*.py*
/usr/lib/python2.7/site-packages/artifact_registry/_vendor/google/auth/crypt/*.py*
/usr/lib/python2.7/site-packages/artifact_registry/_vendor/google/auth/transport/*.py*
/usr/lib/python2.7/site-packages/artifact_registry/_vendor/google/oauth2/*.py*
%config /etc/yum/pluginconf.d/artifact-registry.conf
%doc LICENSE
