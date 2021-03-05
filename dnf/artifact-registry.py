#   manpage for plugin(s)
#   config file

import dnf

import google.auth
import google.auth.transport.requests
from google.auth import compute_engine
from google.auth.exceptions import DefaultCredentialsError, RefreshError
from google.oauth2 import service_account


class ArtifactRegistry(dnf.Plugin):
  """DNF Plugin for authenticated access to Google Artifact Registry"""

  name = "artifact-registry"

  def __init__(self, base, cli):
    super(ArtifactRegistry, self).__init__(base, cli)
    self.base = base
    self.credentials = self._get_creds()

  def _get_creds(self):
    cp = self.read_config(self.base.conf)
    if cp.has_section('main'):
      if cp.has_option('main', 'service_account_json'):
        service_account_json = cp.get('main', 'service_account_json')
        return service_account.Credentials.from_service_account_file(
            service_account_json)
      if cp.has_option('main', 'service_account_email'):
        service_account_email = cp.get('main', 'service_account_email')
        return compute_engine.Credentials(service_account_email)
    try:
      creds, _ = google.auth.default()
      return creds
    except DefaultCredentialsError:
      return None

  def config(self):
    for repo in self.base.repos.iter_enabled():
      opts = dict(repo.cfg.items(repo.id))
      if 'pkg.dev' in opts.get('baseurl', ''):
        self._add_headers(repo)

  def _add_headers(self, repo):
    token = self._get_token()
    if token:
      headers = repo.get_http_headers()
      new_headers = ("Authorization: Bearer %s" % token,) + headers
      repo.set_http_headers(new_headers)

  def _get_token(self):
    if not self.credentials:
      return None
    if not self.credentials.valid:
      try:
        self.credentials.refresh(google.auth.transport.requests.Request())
      except RefreshError:
        return None
    return self.credentials.token
