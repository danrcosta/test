#!/usr/bin/env python3
"""
Hermes + Claude Code GitHub Automation
Real GitHub REST API client for PR workflow automation.

Every method here performs an actual HTTP call against api.github.com.
Failures are surfaced, not swallowed: a returned dict with success=False
means the API rejected the call, and the "error" field carries the reason.
"""

import logging
import json
import os
import requests
from datetime import datetime
from typing import Optional, Dict, Any, List
from enum import Enum

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

GITHUB_API = "https://api.github.com"


class GitHubAction(Enum):
    CREATE_PR = "create_pr"
    REVIEW_PR = "review_pr"
    MERGE_PR = "merge_pr"
    CLOSE_PR = "close_pr"
    UPDATE_PR = "update_pr"


class GitHubAuthError(RuntimeError):
    """Raised when no usable GitHub credential is configured."""


class HermesGitHubAutomator:
    """
    Drives GitHub PR workflows through the REST API.

    Requires a token with `repo` scope in GITHUB_ACCESS_TOKEN (or passed
    explicitly). Without one, construction fails loudly rather than
    producing results that look real but are not.
    """

    def __init__(self, github_token: str = None, timeout: int = 30):
        """
        Args:
            github_token: GitHub token with `repo` scope. Falls back to the
                GITHUB_ACCESS_TOKEN or GITHUB_TOKEN environment variables.
            timeout: Per-request timeout in seconds.

        Raises:
            GitHubAuthError: if no token is available.
        """
        self.github_token = (
            github_token
            or os.getenv("GITHUB_ACCESS_TOKEN")
            or os.getenv("GITHUB_TOKEN")
        )
        if not self.github_token:
            raise GitHubAuthError(
                "No GitHub token configured. Set GITHUB_ACCESS_TOKEN (or "
                "GITHUB_TOKEN) to a token with `repo` scope, or pass "
                "github_token= explicitly."
            )

        self.timeout = timeout
        self.action_history: List[Dict[str, Any]] = []

        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {self.github_token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "Hermes-GitHub-Automator/2.0",
        })

        logger.info("✅ Hermes GitHub Automator initialized")

    # ------------------------------------------------------------------
    # HTTP plumbing
    # ------------------------------------------------------------------

    def _request(self, method: str, path: str, **kwargs) -> Dict[str, Any]:
        """
        Perform an authenticated GitHub API call.

        Returns a dict with success=True and the parsed body under "data",
        or success=False with the API's error message.
        """
        url = f"{GITHUB_API}{path}"
        try:
            response = self.session.request(
                method, url, timeout=self.timeout, **kwargs
            )
        except requests.exceptions.Timeout:
            return {"success": False, "error": f"Timeout calling {method} {path}"}
        except requests.exceptions.RequestException as e:
            return {"success": False, "error": f"Request failed: {e}"}

        if response.status_code == 401:
            return {
                "success": False,
                "error": "GitHub rejected the token (401). Check that it is "
                         "valid and has `repo` scope.",
                "status_code": 401,
            }

        if not response.ok:
            detail = response.text
            try:
                body = response.json()
                detail = body.get("message", detail)
                if body.get("errors"):
                    detail = f"{detail} — {json.dumps(body['errors'])}"
            except ValueError:
                pass
            return {
                "success": False,
                "error": f"HTTP {response.status_code}: {detail}",
                "status_code": response.status_code,
            }

        try:
            data = response.json()
        except ValueError:
            data = {}

        return {"success": True, "data": data, "status_code": response.status_code}

    def _record(self, action: GitHubAction, params: Dict, result: Dict) -> None:
        """Append an action to the in-memory history."""
        self.action_history.append({
            "action": action.value,
            "params": params,
            "result": result,
            "timestamp": datetime.now().isoformat(),
        })

    # ------------------------------------------------------------------
    # Dispatch
    # ------------------------------------------------------------------

    def execute_hermes_command(
        self, action: GitHubAction, params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute a GitHub action.

        Args:
            action: Which action to run.
            params: Action parameters (see each handler for required keys).

        Returns:
            Result dict. success=False carries an "error" describing what
            GitHub rejected.
        """
        command_map = {
            GitHubAction.CREATE_PR: self._create_pr,
            GitHubAction.REVIEW_PR: self._review_pr,
            GitHubAction.MERGE_PR: self._merge_pr,
            GitHubAction.CLOSE_PR: self._close_pr,
            GitHubAction.UPDATE_PR: self._update_pr,
        }

        handler = command_map.get(action)
        if handler is None:
            return {"success": False, "error": f"Unknown action: {action}"}

        try:
            result = handler(params)
        except KeyError as e:
            result = {"success": False, "error": f"Missing required param: {e}"}
        except Exception as e:
            logger.error(f"❌ Error executing {action.value}: {e}")
            result = {"success": False, "error": str(e)}

        self._record(action, params, result)
        return result

    # ------------------------------------------------------------------
    # Actions
    # ------------------------------------------------------------------

    def _create_pr(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a pull request.

        Required params: owner, repo, branch (head), title.
        Optional: base (default "main"), description, draft (default True).
        """
        owner = params["owner"]
        repo = params["repo"]
        title = params["title"]

        logger.info(f"📝 Creating PR on {owner}/{repo}: {title}")

        result = self._request(
            "POST",
            f"/repos/{owner}/{repo}/pulls",
            json={
                "title": title,
                "head": params["branch"],
                "base": params.get("base", "main"),
                "body": params.get("description", ""),
                "draft": params.get("draft", True),
            },
        )

        if not result["success"]:
            logger.error(f"❌ PR creation failed: {result['error']}")
            return result

        pr = result["data"]
        logger.info(f"✅ PR created: #{pr['number']} — {pr['html_url']}")
        return {
            "success": True,
            "action": "create_pr",
            "pr_number": pr["number"],
            "pr_url": pr["html_url"],
            "status": pr["state"].upper(),
            "draft": pr.get("draft", False),
            "timestamp": datetime.now().isoformat(),
        }

    def _review_pr(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Submit a review on a pull request.

        Required params: owner, repo, pr_number.
        Optional: event (COMMENT | APPROVE | REQUEST_CHANGES, default COMMENT),
                  body, comments (list of inline review comments).

        Note: GitHub rejects APPROVE on your own PR with a 422. That is the
        API enforcing review integrity, not a bug here.
        """
        owner = params["owner"]
        repo = params["repo"]
        pr_number = params["pr_number"]
        event = params.get("event", "COMMENT")

        logger.info(f"🔍 Reviewing PR #{pr_number} on {owner}/{repo} ({event})")

        payload: Dict[str, Any] = {"event": event}
        if params.get("body"):
            payload["body"] = params["body"]
        if params.get("comments"):
            payload["comments"] = params["comments"]

        result = self._request(
            "POST", f"/repos/{owner}/{repo}/pulls/{pr_number}/reviews", json=payload
        )

        if not result["success"]:
            logger.error(f"❌ Review failed: {result['error']}")
            return result

        review = result["data"]
        logger.info(f"✅ PR #{pr_number} reviewed: {review.get('state')}")
        return {
            "success": True,
            "action": "review_pr",
            "pr_number": pr_number,
            "review_id": review.get("id"),
            "review_status": review.get("state"),
            "reviewed_at": datetime.now().isoformat(),
        }

    def _merge_pr(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Merge a pull request.

        Required params: owner, repo, pr_number.
        Optional: merge_method (merge | squash | rebase, default "squash"),
                  commit_title, commit_message.
        """
        owner = params["owner"]
        repo = params["repo"]
        pr_number = params["pr_number"]

        logger.info(f"🔀 Merging PR #{pr_number} on {owner}/{repo}")

        payload: Dict[str, Any] = {
            "merge_method": params.get("merge_method", "squash")
        }
        if params.get("commit_title"):
            payload["commit_title"] = params["commit_title"]
        if params.get("commit_message"):
            payload["commit_message"] = params["commit_message"]

        result = self._request(
            "PUT", f"/repos/{owner}/{repo}/pulls/{pr_number}/merge", json=payload
        )

        if not result["success"]:
            logger.error(f"❌ Merge failed: {result['error']}")
            return result

        merge = result["data"]
        logger.info(f"✅ PR #{pr_number} merged: {merge.get('sha')}")
        return {
            "success": True,
            "action": "merge_pr",
            "pr_number": pr_number,
            "merge_method": payload["merge_method"],
            "sha": merge.get("sha"),
            "merged_at": datetime.now().isoformat(),
            "status": "MERGED",
        }

    def _close_pr(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Close a pull request without merging.

        Required params: owner, repo, pr_number.
        """
        owner = params["owner"]
        repo = params["repo"]
        pr_number = params["pr_number"]

        logger.info(f"❌ Closing PR #{pr_number} on {owner}/{repo}")

        result = self._request(
            "PATCH", f"/repos/{owner}/{repo}/pulls/{pr_number}", json={"state": "closed"}
        )

        if not result["success"]:
            logger.error(f"❌ Close failed: {result['error']}")
            return result

        logger.info(f"✅ PR #{pr_number} closed")
        return {
            "success": True,
            "action": "close_pr",
            "pr_number": pr_number,
            "closed_at": datetime.now().isoformat(),
            "status": "CLOSED",
        }

    def _update_pr(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update a pull request's title, body, base, or state.

        Required params: owner, repo, pr_number.
        Optional: title, body, base, state.
        """
        owner = params["owner"]
        repo = params["repo"]
        pr_number = params["pr_number"]

        payload = {
            key: params[key]
            for key in ("title", "body", "base", "state")
            if key in params
        }
        if not payload:
            return {
                "success": False,
                "error": "Nothing to update: pass at least one of "
                         "title, body, base, state.",
            }

        logger.info(f"✏️  Updating PR #{pr_number} on {owner}/{repo}")

        result = self._request(
            "PATCH", f"/repos/{owner}/{repo}/pulls/{pr_number}", json=payload
        )

        if not result["success"]:
            logger.error(f"❌ Update failed: {result['error']}")
            return result

        logger.info(f"✅ PR #{pr_number} updated")
        return {
            "success": True,
            "action": "update_pr",
            "pr_number": pr_number,
            "updated_fields": list(payload.keys()),
            "updated_at": datetime.now().isoformat(),
        }

    # ------------------------------------------------------------------
    # Read helpers
    # ------------------------------------------------------------------

    def get_pr(self, owner: str, repo: str, pr_number: int) -> Dict[str, Any]:
        """Fetch a pull request's current state."""
        return self._request("GET", f"/repos/{owner}/{repo}/pulls/{pr_number}")

    def verify_token(self) -> Dict[str, Any]:
        """
        Confirm the configured token authenticates.

        Returns success=True plus the authenticated login, so callers can
        check credentials before running a workflow.
        """
        result = self._request("GET", "/user")
        if result["success"]:
            login = result["data"].get("login")
            logger.info(f"✅ Token valid, authenticated as {login}")
            return {"success": True, "login": login}
        return result

    # ------------------------------------------------------------------
    # Workflow
    # ------------------------------------------------------------------

    def automate_pr_workflow(
        self,
        owner: str,
        repo: str,
        branch: str,
        title: str,
        description: str = "",
        base: str = "main",
        draft: bool = True,
        auto_merge: bool = False,
        merge_method: str = "squash",
    ) -> Dict[str, Any]:
        """
        Create a PR, and optionally merge it.

        Merging is opt-in (auto_merge=False by default): a workflow that
        creates and immediately merges its own PR defeats the point of
        review, so the caller has to ask for it explicitly.

        Args:
            owner: Repository owner.
            repo: Repository name.
            branch: Head branch to open the PR from.
            title: PR title.
            description: PR body.
            base: Base branch to merge into.
            draft: Open as a draft PR.
            auto_merge: Merge immediately after creating.
            merge_method: merge | squash | rebase.

        Returns:
            Workflow result with a step-by-step trace.
        """
        logger.info(f"🚀 Starting PR workflow on {owner}/{repo}")

        workflow_result: Dict[str, Any] = {
            "workflow": "pr_automation",
            "repo": f"{owner}/{repo}",
            "branch": branch,
            "steps": [],
            "status": "RUNNING",
        }

        create_result = self.execute_hermes_command(
            GitHubAction.CREATE_PR,
            {
                "owner": owner,
                "repo": repo,
                "branch": branch,
                "base": base,
                "title": title,
                "description": description,
                "draft": draft,
            },
        )
        workflow_result["steps"].append({"step": "create_pr", "result": create_result})

        if not create_result["success"]:
            workflow_result["status"] = "FAILED"
            logger.error("❌ Workflow aborted: PR creation failed")
            return workflow_result

        pr_number = create_result["pr_number"]
        workflow_result["pr_number"] = pr_number
        workflow_result["pr_url"] = create_result["pr_url"]

        if auto_merge:
            merge_result = self.execute_hermes_command(
                GitHubAction.MERGE_PR,
                {
                    "owner": owner,
                    "repo": repo,
                    "pr_number": pr_number,
                    "merge_method": merge_method,
                },
            )
            workflow_result["steps"].append({"step": "merge_pr", "result": merge_result})

            if not merge_result["success"]:
                workflow_result["status"] = "PARTIAL"
                logger.warning(
                    f"⚠️  PR #{pr_number} created but not merged: "
                    f"{merge_result['error']}"
                )
                return workflow_result

        workflow_result["status"] = "COMPLETED"
        logger.info(f"✅ PR workflow completed: #{pr_number}")
        return workflow_result

    # ------------------------------------------------------------------
    # History
    # ------------------------------------------------------------------

    def get_action_history(self) -> List[Dict[str, Any]]:
        """Get the in-memory action history for this instance."""
        return self.action_history

    def export_workflow_log(self, filename: str = "github_workflow.json") -> bool:
        """Write the action history to a JSON file."""
        try:
            with open(filename, 'w') as f:
                json.dump(self.action_history, f, indent=2)
            logger.info(f"✅ Workflow log exported: {filename}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to export log: {e}")
            return False


def main():
    """Verify credentials and report repository state. Makes no writes."""
    print("\n=== Hermes GitHub Automation ===\n")

    try:
        automator = HermesGitHubAutomator()
    except GitHubAuthError as e:
        print(f"❌ {e}")
        return

    print("1️⃣  Verifying token...")
    check = automator.verify_token()
    if not check["success"]:
        print(f"❌ {check['error']}")
        return
    print(f"✅ Authenticated as: {check['login']}")

    print(
        "\nThis entry point performs no writes. To create a PR, call\n"
        "  automator.automate_pr_workflow(owner=..., repo=..., branch=..., title=...)\n"
        "Merging requires auto_merge=True and is never implicit."
    )


if __name__ == "__main__":
    main()
