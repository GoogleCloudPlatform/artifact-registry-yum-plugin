import google.auth
import google.auth.transport.requests
from google.auth.exceptions import DefaultCredentialsError, RefreshError

from yum.plugins import TYPE_CORE

requires_api_version = '2.3'
plugin_type = (TYPE_CORE,)


def prereposetup_hook(conduit):
  conduit.info(2, 'Enabling Artifact Registry authentication')
  for repo in conduit.getRepos().listEnabled():
    for url in repo.urls:
      if 'pkg.dev' in url:
        _add_headers(repo)
        break  # Stop looking at URLs


def _add_headers(repo):
  try:
    credentials, _ = google.auth.default()
  except DefaultCredentialsError:
    return None

  try:
    credentials.refresh(google.auth.transport.requests.Request())
  except RefreshError:
    return None

  if credentials.valid:
    repo.http_headers.update(
        {'Authorization': 'Bearer %s' % credentials.token})
