from flask import request, Response

import logging
from .. import app
from .. import csrf

from ..handlers import BitBucketWebHook, PushHookBitBucket, CodeShipWebHook, GitLabWebHook, PushHookGitLab, \
    PipelineHookGitLab, MergeRequestHookGitLab, MergeRequestHookBitBucket

logger = logging.getLogger()


@app.route('/webhook/', methods=['POST'])
@csrf.exempt
def webhook():
    if request.headers.get('X-Gitlab-Event'):
        git_lab = GitLabWebHook()
        git_lab.add_evens('Pipeline Hook', PipelineHookGitLab)
        git_lab.add_evens('Push Hook', PushHookGitLab)
        git_lab.add_evens('Merge Request Hook', MergeRequestHookGitLab)
        git_lab.get_event(request)

    if request.headers.get('User-Agent') == 'Codeship Webhook':
        code_ship = CodeShipWebHook(request.get_data())
        code_ship.init()
    elif request.headers.get('User-Agent') == 'Bitbucket-Webhooks/2.0':
        bit_bucket = BitBucketWebHook()
        bit_bucket.add_evens('repo:push', PushHookBitBucket)
        bit_bucket.add_evens('pullrequest:created', MergeRequestHookBitBucket)
        bit_bucket.get_event(request)
    else:
        pass
    # print(request
    #       )
    # print(request.get_data()
    #       )
    # print(request.headers
    #       )
    return Response(status=200)
