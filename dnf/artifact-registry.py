#  Copyright 2021 Google LLC
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import dnf

from artifact_registry._vendor.google.auth import compute_engine, default
from artifact_registry._vendor.google.auth.exceptions import DefaultCredentialsError, RefreshError
from artifact_registry._vendor.google.auth.transport import requests
from artifact_registry._vendor.google.oauth2 import service_account


class ArtifactRegistry(dnf.Plugin):
  """DNF Plugin for authenticated access to Google Artifact Registry."""

  name = 'artifact-registry'

  def __init__(self, base, cli):
    super(ArtifactRegistry, self).__init__(base, cli)
    self.base = base
    self.credentials = self._get_creds()

  def config(self):
    for repo in self.base.repos.iter_enabled():
      opts = dict(repo.cfg.items(repo.id))
      if 'pkg.dev' in opts.get('baseurl', ''):
        self._add_headers(repo)

  def _get_creds(self):
    config = self.read_config(self.base.conf)
    if config.has_section('main'):
      if config.has_option('main', 'service_account_json'):
        service_account_json = config.get('main', 'service_account_json')
        return service_account.Credentials.from_service_account_file(
            service_account_json)
      if config.has_option('main', 'service_account_email'):
        service_account_email = config.get('main', 'service_account_email')
        return compute_engine.Credentials(service_account_email)

    try:
      creds, _ = default()
    except DefaultCredentialsError:
      return None

    return creds

  def _add_headers(self, repo):
    token = self._get_token()
    if token:
      headers = repo.get_http_headers()
      new_headers = ('Authorization: Bearer %s' % token,) + headers
      repo.set_http_headers(new_headers)

  def _get_token(self):
    if not self.credentials:
      return None
    if not self.credentials.valid:
      try:
        self.credentials.refresh(requests.Request())
      except RefreshError:
        return None
    return self.credentials.token
