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

# Don't build debuginfo packages.
%define debug_package %{nil}

Name: yum-plugin-artifact-registry
Epoch:   1
Version: %{_version}
Release: g1%{?dist}
Summary: Yum plugin for Artifact Registry
License: ASL 2.0
Url: https://cloud.google.com/artifact-registry
Source0: %{name}_%{version}.orig.tar.gz

Requires: yum >= 3.0

BuildArch: %{_arch}

%description
Contains a Yum plugin for authenticated access to Artifact Registry repositories.

%prep
%autosetup

%build
pushd cmd/ar-token
GOPATH=%{_gopath} CGO_ENABLED=0 %{_go} build -ldflags="-s -w" -mod=readonly
popd

%install
install -d %{buildroot}/usr/libexec
install -p -m 0755 cmd/ar-token/ar-token %{buildroot}/usr/libexec/
install -d %{buildroot}/usr/lib/yum-plugins
install -p -m 0644 yum/artifact-registry.py %{buildroot}/usr/lib/yum-plugins/
install -d %{buildroot}/etc/yum/pluginconf.d
install -p -m 0644 artifact-registry.conf %{buildroot}/etc/yum/pluginconf.d/

%files
%defattr(755,root,root,-)
/usr/lib/yum-plugins/artifact-registry.py*
/usr/libexec/ar-token
%config /etc/yum/pluginconf.d/artifact-registry.conf
%doc LICENSE
