#!/usr/bin/env python3
"""
Telegram + Hermes + Obsidian Integrator
Complete integration of all three components
"""

import logging
from datetime import datetime
from typing import Optional, Dict, Any
from hermes_claude_bridge import HermesClaudeBridge, ContentType
from obsidian_vault_manager import ObsidianVaultManager, SessionType, SessionStatus

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class TelegramHermesObsidianIntegrator:
    """Integrate Telegram, Hermes Bridge, and Obsidian Vault"""

    def __init__(
        self,
        hermes_url: str = "http://100.86.232.77:8080",
        vault_path: str = "./obsidian_vault"
    ):
        """
        Initialize integrator

        Args:
            hermes_url: Hermes MCP server URL
            vault_path: Obsidian vault path
        """
        self.hermes_bridge = HermesClaudeBridge(hermes_url=hermes_url)
        self.vault_manager = ObsidianVaultManager(vault_path=vault_path)
        self.active_sessions = {}

        logger.info("✅ Telegram-Hermes-Obsidian Integrator initialized")

    def process_telegram_message(
        self,
        user: str,
        message_text: str,
        chat_id: int,
        session_id: Optional[str] = None,
        image_path: Optional[str] = None,
        metadata: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Process incoming Telegram message through entire pipeline

        Args:
            user: Telegram username
            message_text: Message content
            chat_id: Telegram chat ID
            session_id: Optional existing session ID
            image_path: Optional image path for analysis
            metadata: Additional metadata

        Returns:
            Processing result
        """
        logger.info(f"📨 Processing message from @{user}: {message_text[:50]}...")

        try:
            # Create or get session
            if not session_id:
                session_id = self._get_or_create_session(user, message_text)

            session = self.vault_manager.get_session(session_id)
            if not session:
                return {
                    "success": False,
                    "error": "Session not found"
                }

            # Build metadata
            msg_metadata = metadata or {}
            msg_metadata.update({
                "source": "telegram",
                "user": user,
                "chat_id": chat_id,
                "session_id": session_id
            })

            # Add message to Obsidian vault
            vault_msg = self.vault_manager.add_message(
                session_id=session_id,
                role="user",
                content=message_text,
                source="telegram",
                metadata=msg_metadata
            )

            # Send to Claude Code via Hermes
            if image_path:
                hermes_result = self.hermes_bridge.send_image_analysis(
                    image_path=image_path,
                    description=message_text or "Analyze this image",
                    metadata=msg_metadata
                )
            else:
                hermes_result = self.hermes_bridge.send_text_prompt(
                    prompt=message_text,
                    metadata=msg_metadata
                )

            # Add interaction to vault
            self.vault_manager.add_interaction(
                session_id=session_id,
                interaction_type="image" if image_path else "text",
                content=message_text,
                source="telegram",
                metadata=msg_metadata
            )

            return {
                "success": True,
                "session_id": session_id,
                "vault_message": vault_msg,
                "hermes_result": hermes_result,
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"❌ Error processing message: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def _get_or_create_session(self, user: str, message_text: str) -> str:
        """Get existing or create new session for user"""
        # Check for active sessions
        for session in self.vault_manager.list_sessions():
            if session["user"] == user and session["status"] == "active":
                logger.info(f"✅ Using existing session: {session['id']}")
                return session["id"]

        # Create new session
        logger.info(f"📝 Creating new session for @{user}")
        description = message_text[:50] + ("..." if len(message_text) > 50 else "")

        session = self.vault_manager.create_session(
            session_type=SessionType.TELEGRAM_INTERACTION,
            description=description,
            user=user,
            metadata={
                "started_by": "telegram",
                "auto_created": True
            }
        )

        return session["id"]

    def process_code_snippet(
        self,
        user: str,
        code: str,
        language: str = "python",
        session_id: Optional[str] = None,
        metadata: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Process code snippet through pipeline

        Args:
            user: Telegram username
            code: Code content
            language: Programming language
            session_id: Optional session ID
            metadata: Additional metadata

        Returns:
            Processing result
        """
        logger.info(f"💻 Processing code snippet from @{user}")

        try:
            # Get or create session
            if not session_id:
                session = self.vault_manager.create_session(
                    session_type=SessionType.CLAUDE_ANALYSIS,
                    description=f"Code Analysis - {language}",
                    user=user,
                    metadata={"language": language}
                )
                session_id = session["id"]

            msg_metadata = metadata or {}
            msg_metadata.update({
                "source": "telegram",
                "user": user,
                "language": language,
                "session_id": session_id
            })

            # Add to vault
            self.vault_manager.add_message(
                session_id=session_id,
                role="user",
                content=f"Analyze this {language} code",
                source="telegram",
                metadata=msg_metadata
            )

            # Send to Claude via Hermes
            hermes_result = self.hermes_bridge.send_code(
                code=code,
                language=language,
                metadata=msg_metadata
            )

            # Add interaction
            self.vault_manager.add_interaction(
                session_id=session_id,
                interaction_type="code",
                content=code[:500],
                source="telegram",
                metadata=msg_metadata
            )

            return {
                "success": True,
                "session_id": session_id,
                "hermes_result": hermes_result,
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"❌ Error processing code: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def get_user_sessions(self, user: str) -> Dict[str, Any]:
        """Get all sessions for a user"""
        sessions = self.vault_manager.list_sessions()
        user_sessions = [s for s in sessions if s["user"] == user]

        return {
            "user": user,
            "total_sessions": len(user_sessions),
            "sessions": [
                self.vault_manager.get_session_summary(s["id"])
                for s in user_sessions
            ]
        }

    def get_session_details(self, session_id: str) -> Optional[Dict]:
        """Get detailed session information"""
        session = self.vault_manager.get_session(session_id)
        if not session:
            return None

        return {
            "summary": self.vault_manager.get_session_summary(session_id),
            "messages": session.get("messages", []),
            "interactions": session.get("interactions", []),
            "metadata": session.get("metadata", {})
        }

    def close_session(self, session_id: str) -> bool:
        """Close a session"""
        return self.vault_manager.update_session_status(
            session_id,
            SessionStatus.INACTIVE
        )

    def get_vault_stats(self) -> Dict[str, Any]:
        """Get vault statistics"""
        return self.vault_manager.get_vault_stats()

    def export_session_to_obsidian(self, session_id: str) -> Optional[str]:
        """Export session to Obsidian markdown"""
        return self.vault_manager.export_session(session_id, export_format="markdown")


def main():
    """Example usage"""
    integrator = TelegramHermesObsidianIntegrator()

    print("\n=== Telegram + Hermes + Obsidian Integration Demo ===\n")

    # Example 1: Process text message
    print("1️⃣  Processing text message...")
    result = integrator.process_telegram_message(
        user="danrcosta",
        message_text="Analise a interação entre Hermes e o Vault de notas",
        chat_id=12345
    )
    print(f"Session ID: {result['session_id']}")

    # Example 2: Process code
    print("\n2️⃣  Processing code snippet...")
    code = """
def hello_world():
    print("Hello from Telegram!")
    return True
"""
    result = integrator.process_code_snippet(
        user="danrcosta",
        code=code,
        language="python"
    )
    print(f"Session ID: {result['session_id']}")

    # Example 3: Get user sessions
    print("\n3️⃣  Fetching user sessions...")
    sessions = integrator.get_user_sessions("danrcosta")
    print(f"Total sessions for @danrcosta: {sessions['total_sessions']}")
    for session in sessions['sessions']:
        print(f"  - {session['description']} ({session['status']})")

    # Example 4: Get vault stats
    print("\n4️⃣  Vault statistics:")
    stats = integrator.get_vault_stats()
    print(f"Total sessions: {stats['total_sessions']}")
    print(f"Active sessions: {stats['active_sessions']}")
    print(f"Total interactions: {stats['total_interactions']}")


if __name__ == "__main__":
    main()
