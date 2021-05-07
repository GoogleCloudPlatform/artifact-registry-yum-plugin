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

from artifact_registry._vendor.google.auth import compute_engine, default
from artifact_registry._vendor.google.auth.exceptions import DefaultCredentialsError, RefreshError
from artifact_registry._vendor.google.auth.transport import requests
from artifact_registry._vendor.google.oauth2 import service_account

from yum.plugins import TYPE_CORE

requires_api_version = '2.3'
plugin_type = (TYPE_CORE,)


def prereposetup_hook(conduit):
  credentials = _get_creds()
  if not credentials:
    return
  for repo in conduit.getRepos().listEnabled():
    for url in repo.urls:
      if 'pkg.dev' in url:
        _add_headers(credentials, repo)
        break  # Stop looking at URLs


def _get_creds(conduit):
  service_account_json = conduit.confString('main', 'service_account_json', '')
  if service_account_json:
    return service_account.Credentials.from_service_account_file(
        service_account_json)
  service_account_email = conduit.confString(
      'main', 'service_account_email', '')
  if service_account_email:
    return compute_engine.Credentials(service_account_email)

  try:
    creds, _ = default()
  except DefaultCredentialsError:
    return None

  return creds


def _add_headers(credentials, repo):
  token = _get_token(credentials)
  if token:
    repo.http_headers.update(
        {'Authorization': 'Bearer %s' % credentials.token})


def _get_token(credentials):
  if not credentials:
    return None
  if not credentials.valid:
    try:
      credentials.refresh(requests.Request())
    except RefreshError:
      return None
  return credentials.token
