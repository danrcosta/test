#!/usr/bin/env python3
"""
Hermes GitHub + Obsidian Bridge
Integrates GitHub automation results with Obsidian Vault
"""

import json
import logging
from datetime import datetime
from hermes_github_automation import (
    HermesGitHubAutomator,
    GitHubAction,
    GitHubAuthError,
)
from obsidian_vault_manager import ObsidianVaultManager, SessionType, SessionStatus

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class HermesGitHubObsidianBridge:
    """Bridge GitHub automation with Obsidian Vault storage"""

    def __init__(self, vault_path: str = "./obsidian_vault", github_token: str = None):
        """
        Initialize bridge.

        Raises:
            GitHubAuthError: if no GitHub token is configured. The bridge
                refuses to start without one rather than logging workflow
                records for calls that never reached GitHub.
        """
        self.automator = HermesGitHubAutomator(github_token=github_token)
        self.vault = ObsidianVaultManager(vault_path=vault_path)
        logger.info("✅ GitHub + Obsidian Bridge initialized")

    def execute_and_log_pr_workflow(
        self,
        owner: str,
        repo: str,
        branch: str,
        title: str,
        description: str = "",
        user: str = "hermes-agent",
        base: str = "main",
        draft: bool = True,
        auto_merge: bool = False
    ) -> dict:
        """
        Execute PR workflow and log to Obsidian

        Args:
            owner: GitHub owner
            repo: Repository name
            branch: Branch name
            title: PR title
            description: PR description
            user: User executing workflow
            base: Base branch to merge into
            draft: Open the PR as a draft
            auto_merge: Merge immediately after creating (off by default)

        Returns:
            Complete workflow result with Obsidian session
        """
        logger.info(f"🚀 Executing PR workflow with Obsidian logging")

        # Create Obsidian session
        session = self.vault.create_session(
            session_type=SessionType.CLAUDE_ANALYSIS,
            description=f"GitHub PR: {title}",
            user=user,
            metadata={
                "workflow_type": "github_pr_automation",
                "repo": f"{owner}/{repo}",
                "branch": branch
            }
        )

        # Log workflow start
        self.vault.add_message(
            session_id=session["id"],
            role="system",
            content=f"Starting GitHub PR workflow automation for {repo}",
            source="hermes-github",
            metadata={
                "event": "workflow_start",
                "repo": f"{owner}/{repo}"
            }
        )

        # Execute workflow
        workflow_result = self.automator.automate_pr_workflow(
            owner=owner,
            repo=repo,
            branch=branch,
            title=title,
            description=description,
            base=base,
            draft=draft,
            auto_merge=auto_merge
        )

        # Log workflow steps to Obsidian
        for step in workflow_result.get("steps", []):
            step_name = step.get("step", "unknown")
            step_result = step.get("result", {})
            succeeded = step_result.get("success", False)

            # Record what GitHub actually returned, success or failure.
            outcome = step_result.get("status") if succeeded else "FAILED"

            self.vault.add_interaction(
                session_id=session["id"],
                interaction_type="github_action",
                content=f"{step_name}: {outcome}",
                source="hermes-github",
                metadata={
                    "action": step_name,
                    "success": succeeded,
                    "status": outcome,
                    "result": step_result
                }
            )

            if succeeded:
                detail = f"✅ {step_name} completed with status: {outcome}"
            else:
                detail = f"❌ {step_name} failed: {step_result.get('error', 'unknown error')}"

            self.vault.add_message(
                session_id=session["id"],
                role="assistant",
                content=detail,
                source="hermes-github",
                metadata=step_result
            )

        # Log workflow completion
        completion_status = "completed" if workflow_result.get("status") == "COMPLETED" else "failed"
        self.vault.add_message(
            session_id=session["id"],
            role="system",
            content=f"Workflow {completion_status}",
            source="hermes-github",
            metadata={
                "event": "workflow_completion",
                "status": workflow_result.get("status")
            }
        )

        # Update session status
        if workflow_result.get("status") == "COMPLETED":
            self.vault.update_session_status(session["id"], SessionStatus.ACTIVE)
        else:
            self.vault.update_session_status(session["id"], SessionStatus.ERROR)

        logger.info(f"✅ Workflow logged to Obsidian session: {session['id']}")

        return {
            "workflow": workflow_result,
            "session": session,
            "session_id": session["id"],
            "obsidian_status": "logged"
        }

    def log_github_action(
        self,
        action: GitHubAction,
        params: dict,
        session_id: str = None,
        user: str = "hermes-agent"
    ) -> dict:
        """
        Log a single GitHub action to Obsidian

        Args:
            action: GitHub action type
            params: Action parameters
            session_id: Existing session ID (optional)
            user: User executing action

        Returns:
            Action result with session
        """
        logger.info(f"📝 Logging GitHub action: {action.value}")

        # Create or get session
        if not session_id:
            session = self.vault.create_session(
                session_type=SessionType.CLAUDE_ANALYSIS,
                description=f"GitHub Action: {action.value}",
                user=user,
                metadata={"action_type": action.value}
            )
            session_id = session["id"]
        else:
            session = self.vault.get_session(session_id)

        # Execute action
        result = self.automator.execute_hermes_command(action, params)
        succeeded = result.get("success", False)
        outcome = result.get("status") if succeeded else "FAILED"

        # Log to Obsidian
        self.vault.add_interaction(
            session_id=session_id,
            interaction_type="github_action",
            content=f"{action.value}: {outcome}",
            source="hermes-github",
            metadata={
                "action": action.value,
                "success": succeeded,
                "status": outcome,
                "result": result
            }
        )

        if succeeded:
            detail = f"✅ {action.value} executed successfully"
        else:
            detail = f"❌ {action.value} failed: {result.get('error', 'unknown error')}"

        self.vault.add_message(
            session_id=session_id,
            role="assistant",
            content=detail,
            source="hermes-github",
            metadata=result
        )

        logger.info(f"✅ Action logged to session: {session_id}")

        return {
            "action": action.value,
            "result": result,
            "session_id": session_id
        }

    def get_workflow_stats(self) -> dict:
        """Get workflow statistics"""
        stats = self.vault.get_vault_stats()
        actions = self.automator.get_action_history()

        return {
            "vault_stats": stats,
            "total_actions": len(actions),
            "actions_by_type": self._group_actions_by_type(actions),
            "recent_actions": actions[-5:] if actions else []
        }

    def _group_actions_by_type(self, actions: list) -> dict:
        """Group actions by type"""
        grouped = {}
        for action in actions:
            action_type = action.get("action", "unknown")
            if action_type not in grouped:
                grouped[action_type] = 0
            grouped[action_type] += 1
        return grouped

    def generate_workflow_report(self) -> dict:
        """Generate comprehensive workflow report"""
        sessions = self.vault.list_sessions()
        github_sessions = [s for s in sessions if s.get("metadata", {}).get("workflow_type") == "github_pr_automation"]

        report = {
            "report_type": "github_automation_report",
            "generated_at": datetime.now().isoformat(),
            "total_workflows": len(github_sessions),
            "workflows": []
        }

        for session in github_sessions:
            summary = self.vault.get_session_summary(session["id"])
            details = self.vault.get_session(session["id"])

            report["workflows"].append({
                "session_id": session["id"],
                "description": session.get("description"),
                "status": session.get("status"),
                "interactions": len(details.get("interactions", [])),
                "messages": len(details.get("messages", [])),
                "created_at": session.get("created_at"),
                "updated_at": session.get("updated_at")
            })

        return report


def main():
    """
    Report on GitHub workflows already recorded in the vault.

    Makes no writes to GitHub: creating a PR is a real, visible action, so
    it belongs in an explicit call rather than in a module's entry point.
    """
    print("\n=== Hermes GitHub + Obsidian Bridge ===\n")

    try:
        bridge = HermesGitHubObsidianBridge()
    except GitHubAuthError as e:
        print(f"❌ {e}")
        return

    check = bridge.automator.verify_token()
    if not check["success"]:
        print(f"❌ {check['error']}")
        return
    print(f"✅ Authenticated as: {check['login']}")

    print("\n📊 Vault statistics:")
    stats = bridge.get_workflow_stats()
    print(f"Total sessions: {stats['vault_stats']['total_sessions']}")
    print(f"Total actions this run: {stats['total_actions']}")
    print(f"Actions by type: {json.dumps(stats['actions_by_type'], indent=2)}")

    print("\n📋 Recorded workflows:")
    report = bridge.generate_workflow_report()
    print(f"Total workflows: {report['total_workflows']}")
    for workflow in report["workflows"]:
        print(f"  • {workflow['description']} ({workflow['status']})")

    print(
        "\nTo run a workflow:\n"
        "  bridge.execute_and_log_pr_workflow(owner=..., repo=..., "
        "branch=..., title=...)\n"
        "Merging requires auto_merge=True and is never implicit."
    )


if __name__ == "__main__":
    main()
