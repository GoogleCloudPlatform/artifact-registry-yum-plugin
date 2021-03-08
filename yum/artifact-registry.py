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
