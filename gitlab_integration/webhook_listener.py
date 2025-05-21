import json
import threading

from flask import request, jsonify

from gitlab_integration.gitlab_fetcher import GitlabMergeRequestFetcher,GitlabPushEventFetcher, GitlabRepoManager
from response_module.response_controller import ReviewResponse
from review_engine.review_engine import ReviewEngine
from utils.logger import log
from gitlab_integration.gitlab_fetcher import is_merge_request_opened
from config.config import *
class WebhookListener:
    def __init__(self):
        pass

    def handle_webhook(self):
        """
        处理webhook的请求
        :return:
        """
        gitlab_payload = request.data.decode('utf-8')
        gitlab_payload = json.loads(gitlab_payload)
        log.info(f"本次gitlab webhook: \n{gitlab_payload}\n")
        event_type = gitlab_payload.get('object_kind')
        return self.call_handle(gitlab_payload, event_type)

    def call_handle(self, gitlab_payload, event_type):
        if event_type == 'merge_request':
            config = {
                'type': 'merge_request',
                'project_id': gitlab_payload.get('project')['id'],
                'merge_request_iid': gitlab_payload.get('object_attributes')['iid']
            }
            reply = ReviewResponse(config)
            return self.handle_merge_request(gitlab_payload, reply)
        elif event_type == 'push':

            commits = gitlab_payload.get('commits', [])
            if not commits:
                log.warning("未找到 commit 列表，忽略本次 push")
                return jsonify({'status': 'no commits'}), 200
            toEmail = gitlab_payload.get('commits')[0].get('author').get('email')
            
            email_list = list(TO_EMAIL_ADDR)
            if toEmail and isinstance(toEmail, str) and toEmail not in email_list:
                email_list.append(toEmail)
            log.info(f"🚀 本次push的作者邮箱: {toEmail}\n")
            
            config = {
                'type': 'push',
                'project_id': gitlab_payload.get('project')['id'],
                'smtp_server': SMTP_SERVER,
                'smtp_port': SMTP_PORT,
                'smtp_user': SMTP_USER,
                'smtp_password': SMTP_PASSWORD,
                'from_addr': SMTP_FROM_ADDR,
                'to_addrs': email_list
            }
            reply = ReviewResponse(config)

            return self.handle_push(gitlab_payload, reply)
        else:
            config = {
                'type': 'other',
                'project_id': gitlab_payload.get('project')['id']
            }
            reply = ReviewResponse(config)
            return self.handle_other(gitlab_payload, reply)

    def handle_merge_request(self, gitlab_payload, reply):
        """
        处理合并请求事件
        """
        if is_merge_request_opened(gitlab_payload):
            log.info("首次merge_request ", gitlab_payload)
            project_id = gitlab_payload.get('project')['id']
            merge_request_iid = gitlab_payload.get("object_attributes")["iid"]
            review_engine = ReviewEngine(reply)
            gitlabMergeRequestFetcher = GitlabMergeRequestFetcher(project_id, merge_request_iid)
            gitlabRepoManager = GitlabRepoManager(project_id)
            thread = threading.Thread(target=review_engine.handle_merge, args=(gitlabMergeRequestFetcher, gitlabRepoManager, gitlab_payload))
            thread.start()

            return jsonify({'status': 'success'}), 200
        return jsonify({'status': 'do not need check'}), 200

    def handle_push(self, gitlab_payload, reply):
        """
        处理推送事件
        """
        try:
            project_id = gitlab_payload.get('project', {}).get('id')
            commits = gitlab_payload.get('commits', [])

            if not commits:
                log.warning("未找到 commit 列表，忽略本次 push")
                return jsonify({'status': 'no commits'}), 200

            for commit in commits:
                commit_id = commit.get('id')
                log.info(f"本次gitlab提交的commit_id: {commit_id}\n")

                # 为每个 commit 启动一个线程
                review_engine = ReviewEngine(reply)
                gitlabPushEventFetcher = GitlabPushEventFetcher(project_id, commit_id)
                gitlabRepoManager = GitlabRepoManager(project_id)

                thread = threading.Thread(
                    target=review_engine.handle_push,
                    args=(gitlabPushEventFetcher, gitlabRepoManager, gitlab_payload)
                )
                thread.start()

            return jsonify({'status': 'success', 'commits_handled': len(commits)}), 200

            # commit_info = push_fetcher.get_commit_info()
            # commit_diffs = push_fetcher.get_commit_diff()

            # log.info(f"🔍 最新提交信息: {commit_info.get('title')}")
            # for diff in commit_diffs:
            #     log.info(f"📄 文件变动: {diff['new_path']}")

            # # 审查结果打印到本地
            # for diff in commit_diffs:
            #     log.info(f"提交变动的文件: {diff['new_path']}")

            # return jsonify({'status': 'success'}), 200

        except Exception as e:
            log.error(f"处理 push 请求失败: {e}")
            return jsonify({'status': 'failed', 'error': str(e)}), 500

    def handle_other(self, gitlab_payload, reply):
        """
        处理其他事件
        """
        event_type = gitlab_payload.get('object_kind')
        log.info(f"Unhandled event type: {event_type}")
        return jsonify({'status': 'unhandled event type'}), 200

webhook_listener = WebhookListener()