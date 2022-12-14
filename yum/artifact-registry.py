#  Copyright 2022 Google LLC
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


from yum.plugins import TYPE_CORE
from subprocess import PIPE, Popen

token_cmd = '/usr/libexec/ar-token'

requires_api_version = '2.3'
plugin_type = (TYPE_CORE,)


def prereposetup_hook(conduit):
  token = _get_token(conduit)
  if not token:
    return
  for repo in conduit.getRepos().listEnabled():
    for url in repo.urls:
      if 'pkg.dev' in url:
        _add_headers(token, repo)
        break  # Stop looking at URLs


def _add_headers(token, repo):
  repo.http_headers.update(
     {'Authorization': 'Bearer %s' % token})


def _get_token(conduit):
  service_account_json = conduit.confString('main', 'service_account_json', '')
  service_account_email = conduit.confString(
      'main', 'service_account_email', '')

  opts = {}
  if service_account_json:
    opts['service_account_json'] = service_account_json
  elif service_account_email:
    opts['service_account_email'] = service_account_email

  return _call_helper(**opts)


def _call_helper(service_account_json=None, service_account_email=None,
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
    stderr = PIPE

  try:
    cmd = Popen([token_cmd] + args, stdout=PIPE, stderr=stderr)
  except OSError as e:
    print('Error trying to obtain Google credentials: %s' % e)
    return

  retcode = cmd.wait()
  if retcode != 0:
    print('Error trying to obtain Google credentials: command returned %d'
          % retcode)
    return

  return cmd.stdout.read()
