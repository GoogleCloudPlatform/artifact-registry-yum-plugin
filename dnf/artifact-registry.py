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

import os
import dnf

from subprocess import CalledProcessError, DEVNULL, PIPE, run
from urllib.parse import urlparse

token_cmd = '/usr/libexec/ar-token'


class ArtifactRegistry(dnf.Plugin):
  """DNF Plugin for authenticated access to Google Artifact Registry."""

  name = 'artifact-registry'

  def __init__(self, base, cli):
    super(ArtifactRegistry, self).__init__(base, cli)
    self.base = base
    self.token = None
    self.error = False

  def config(self):
    """ Setup http headers to repos with baseurl option containing pkg.dev. """
    for repo in self.base.repos.iter_enabled():
      # Check if the 'artifact_registry_oauth' option is set in the repository's config.
      if repo.cfg.has_option(repo.id, 'artifact_registry_oauth') and repo.cfg.getboolean(repo.id, 'artifact_registry_oauth'):
        self._add_headers(repo)
        break  # Don't add more than one Authorization header.
      # We don't have baseurl option so skip it earlier.
      if not hasattr(repo, 'baseurl'):
        continue
      # Check if any repo urls are for Artifact Registry.
      for baseurl in repo.baseurl:
        if not self.error:  # Check error flag first for efficiency
          parsed_url = urlparse(baseurl)
          if parsed_url.scheme == 'https' and parsed_url.netloc.endswith('-yum.pkg.dev'):
            self._add_headers(repo)
            break  # Don't add more than one Authorization header.

  def _add_headers(self, repo):
    token = self._get_token()
    if token:
      headers = repo.get_http_headers()
      new_headers = ('Authorization: Bearer %s' % token,) + headers
      repo.set_http_headers(new_headers)

  def _get_token(self):
    if self.token:
      return self.token

    config = self.read_config(self.base.conf)
    opts = {}
    if config.has_section('main'):
      # JSON has priority over email.
      if config.has_option('main', 'service_account_json'):
        opts['service_account_json'] = config.get(
            'main', 'service_account_json')
      elif config.has_option('main', 'service_account_email'):
        opts['service_account_email'] = config.get(
            'main', 'service_account_email')

      if config.has_option('main', 'debug'):
        opts['debug'] = config.getboolean('main', 'debug')

    self.token = self._call_helper(**opts)
    return self.token

  def _call_helper(self, service_account_json=None, service_account_email=None,
                   debug=False):
    args = []
    # JSON has priority over email.
    if service_account_json:
      args.append('--service_account_json=' + service_account_json)
    elif service_account_email:
      args.append('--service_account_email=' + service_account_email)

    if debug:
      # Inherit stderr to see debug statements
      stderr = None
    else:
      stderr = DEVNULL

    try:
      cmd_result = run([token_cmd] + args,
                       check=True, stdout=PIPE, stderr=stderr, env=os.environ.copy())
    except CalledProcessError as e:
      self.error = True
      print('Error trying to obtain Google credentials:', e)
      return

    return cmd_result.stdout.decode('utf-8')
