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
Summary: dnf plugin for Google Artifact Registry
License: ASL 2.0
Url: https://cloud.google.com/artifact-registry
Source0: %{name}_%{version}.orig.tar.gz

Requires: dnf >= 1.0.0
Requires: python3-google-auth >= 1.1.1
BuildArch: %{_arch}

%description
Contains a dnf plugin for authenticated access to Google Artifact Registry repositories.

%prep
%autosetup

%install
install -d %{buildroot}%{python_sitelib}/dnf-plugins
install -p -m 0644 dnf/artifact-registry.py %{buildroot}%{python_sitelib}/dnf-plugins/
install -d %{buildroot}/etc/dnf/plugins
install -p -m 0644 dnf/artifact-registry.conf %{buildroot}/etc/dnf/plugins/

%files
%defattr(-,root,root,-)
%{python_sitelib}/dnf-plugins/artifact-registry.py*
%config /etc/dnf/plugins/artifact-registry.conf
%doc LICENSE
