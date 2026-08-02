#!/usr/bin/env python3
"""
Obsidian Vault Manager
Manages sessions, notes, and interactions between Telegram, Hermes, and Claude Code
"""

import json
import os
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, List, Any
import shutil
from enum import Enum
import logging

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SessionStatus(Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    DISCONNECTED = "disconnected"
    ERROR = "error"


class SessionType(Enum):
    HERMES_OBSIDIAN = "hermes_obsidian"
    FIX_HERMES = "fix_hermes"
    CLAUDE_ANALYSIS = "claude_analysis"
    TELEGRAM_INTERACTION = "telegram_interaction"


class ObsidianVaultManager:
    """Manage Obsidian Vault for session tracking and note organization"""

    def __init__(self, vault_path: str = "./obsidian_vault"):
        """
        Initialize Obsidian Vault Manager

        Args:
            vault_path: Path to Obsidian vault directory
        """
        self.vault_path = Path(vault_path)
        self.vault_path.mkdir(exist_ok=True)

        # Create directory structure
        self.sessions_dir = self.vault_path / "sessions"
        self.interactions_dir = self.vault_path / "interactions"
        self.archive_dir = self.vault_path / "archive"
        self.metadata_dir = self.vault_path / ".metadata"

        for dir_path in [self.sessions_dir, self.interactions_dir, self.archive_dir, self.metadata_dir]:
            dir_path.mkdir(exist_ok=True)

        # Initialize metadata file
        self.metadata_file = self.metadata_dir / "vault_metadata.json"
        self._init_metadata()

        logger.info(f"✅ Obsidian Vault initialized at: {self.vault_path}")

    def _init_metadata(self):
        """Initialize vault metadata"""
        if not self.metadata_file.exists():
            metadata = {
                "vault_name": "Hermes-Claude-Telegram",
                "created_at": datetime.now().isoformat(),
                "version": "1.0",
                "sessions_count": 0,
                "interactions_count": 0
            }
            self._write_json(self.metadata_file, metadata)

    def _write_json(self, file_path: Path, data: Dict) -> bool:
        """Write JSON file"""
        try:
            file_path.parent.mkdir(parents=True, exist_ok=True)
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            logger.error(f"Error writing JSON: {e}")
            return False

    def _read_json(self, file_path: Path) -> Optional[Dict]:
        """Read JSON file"""
        try:
            if not file_path.exists():
                return None
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error reading JSON: {e}")
            return None

    def create_session(
        self,
        session_type: SessionType,
        description: str,
        user: str = "unknown",
        status: SessionStatus = SessionStatus.ACTIVE,
        metadata: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Create a new session

        Args:
            session_type: Type of session
            description: Session description
            user: User who created the session
            status: Initial status
            metadata: Additional metadata

        Returns:
            Session data
        """
        session_id = f"{session_type.value}_{int(datetime.now().timestamp())}"

        session_data = {
            "id": session_id,
            "type": session_type.value,
            "status": status.value,
            "description": description,
            "user": user,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "interactions": [],
            "messages": [],
            "metadata": metadata or {}
        }

        # Create session file
        session_file = self.sessions_dir / f"{session_id}.json"
        self._write_json(session_file, session_data)

        # Create markdown file for notes
        md_file = self.sessions_dir / f"{session_id}.md"
        self._create_session_markdown(md_file, session_data)

        logger.info(f"✅ Session created: {session_id}")
        return session_data

    def _create_session_markdown(self, md_file: Path, session_data: Dict):
        """Create markdown file for session"""
        frontmatter = f"""---
id: {session_data['id']}
type: {session_data['type']}
status: {session_data['status']}
created: {session_data['created_at']}
user: {session_data['user']}
---

# {session_data['description']}

## Status
**{session_data['status']}**

## Information
- **Type**: {session_data['type']}
- **User**: {session_data['user']}
- **Created**: {session_data['created_at']}

## Interactions

## Messages

## Notes
"""
        md_file.write_text(frontmatter, encoding='utf-8')

    def add_interaction(
        self,
        session_id: str,
        interaction_type: str,
        content: str,
        source: str = "telegram",
        metadata: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Add interaction to session

        Args:
            session_id: Session ID
            interaction_type: Type of interaction (text, image, code, file)
            content: Interaction content
            source: Source (telegram, claude, hermes)
            metadata: Additional metadata

        Returns:
            Interaction data
        """
        session_file = self.sessions_dir / f"{session_id}.json"
        session_data = self._read_json(session_file)

        if not session_data:
            logger.error(f"Session not found: {session_id}")
            return None

        interaction_id = f"interaction_{int(datetime.now().timestamp() * 1000)}"

        interaction = {
            "id": interaction_id,
            "type": interaction_type,
            "source": source,
            "content": content[:500],  # Truncate for preview
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {}
        }

        session_data["interactions"].append(interaction)
        session_data["updated_at"] = datetime.now().isoformat()

        # Update JSON file
        self._write_json(session_file, session_data)

        # Update markdown file
        md_file = self.sessions_dir / f"{session_id}.md"
        self._append_to_markdown(md_file, interaction)

        logger.info(f"✅ Interaction added to {session_id}")
        return interaction

    def _append_to_markdown(self, md_file: Path, interaction: Dict):
        """Append interaction to markdown file"""
        try:
            with open(md_file, 'a', encoding='utf-8') as f:
                f.write(f"\n### {interaction['type'].upper()} - {interaction['timestamp']}\n")
                f.write(f"**Source**: {interaction['source']}\n")
                f.write(f"\n{interaction['content']}\n")
        except Exception as e:
            logger.error(f"Error appending to markdown: {e}")

    def add_message(
        self,
        session_id: str,
        role: str,
        content: str,
        source: str = "telegram",
        metadata: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Add message to session

        Args:
            session_id: Session ID
            role: Role (user, assistant, system)
            content: Message content
            source: Source (telegram, claude, hermes)
            metadata: Additional metadata

        Returns:
            Message data
        """
        session_file = self.sessions_dir / f"{session_id}.json"
        session_data = self._read_json(session_file)

        if not session_data:
            logger.error(f"Session not found: {session_id}")
            return None

        message = {
            "id": f"msg_{int(datetime.now().timestamp() * 1000)}",
            "role": role,
            "content": content,
            "source": source,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {}
        }

        session_data["messages"].append(message)
        session_data["updated_at"] = datetime.now().isoformat()

        # Update JSON file
        self._write_json(session_file, session_data)

        logger.info(f"✅ Message added to {session_id}")
        return message

    def get_session(self, session_id: str) -> Optional[Dict]:
        """Get session by ID"""
        session_file = self.sessions_dir / f"{session_id}.json"
        return self._read_json(session_file)

    def list_sessions(self, session_type: Optional[SessionType] = None, status: Optional[SessionStatus] = None) -> List[Dict]:
        """
        List sessions with optional filtering

        Args:
            session_type: Filter by type
            status: Filter by status

        Returns:
            List of sessions
        """
        sessions = []

        for session_file in self.sessions_dir.glob("*.json"):
            session_data = self._read_json(session_file)
            if not session_data:
                continue

            # Apply filters
            if session_type and session_data["type"] != session_type.value:
                continue
            if status and session_data["status"] != status.value:
                continue

            sessions.append(session_data)

        return sorted(sessions, key=lambda x: x["created_at"], reverse=True)

    def update_session_status(self, session_id: str, new_status: SessionStatus) -> bool:
        """Update session status"""
        session_file = self.sessions_dir / f"{session_id}.json"
        session_data = self._read_json(session_file)

        if not session_data:
            return False

        session_data["status"] = new_status.value
        session_data["updated_at"] = datetime.now().isoformat()

        self._write_json(session_file, session_data)
        logger.info(f"✅ Session status updated: {session_id} → {new_status.value}")
        return True

    def export_session(self, session_id: str, export_format: str = "json") -> Optional[str]:
        """
        Export session to file

        Args:
            session_id: Session ID
            export_format: Format (json or markdown)

        Returns:
            Export file path
        """
        session_data = self.get_session(session_id)
        if not session_data:
            return None

        archive_file = self.archive_dir / f"{session_id}_{int(datetime.now().timestamp())}.{export_format}"

        if export_format == "json":
            self._write_json(archive_file, session_data)
        elif export_format == "markdown":
            md_file = self.sessions_dir / f"{session_id}.md"
            if md_file.exists():
                shutil.copy(md_file, archive_file)

        logger.info(f"✅ Session exported: {archive_file}")
        return str(archive_file)

    def create_interaction_index(self) -> Dict[str, List[str]]:
        """Create index of all interactions by type"""
        index = {}

        for session_file in self.sessions_dir.glob("*.json"):
            session_data = self._read_json(session_file)
            if not session_data:
                continue

            for interaction in session_data.get("interactions", []):
                itype = interaction["type"]
                if itype not in index:
                    index[itype] = []
                index[itype].append(interaction["id"])

        return index

    def get_session_summary(self, session_id: str) -> Optional[Dict]:
        """Get session summary for display"""
        session_data = self.get_session(session_id)
        if not session_data:
            return None

        return {
            "id": session_data["id"],
            "type": session_data["type"],
            "status": session_data["status"],
            "description": session_data["description"],
            "user": session_data["user"],
            "created_at": session_data["created_at"],
            "interactions_count": len(session_data.get("interactions", [])),
            "messages_count": len(session_data.get("messages", [])),
            "last_updated": session_data["updated_at"]
        }

    def get_vault_stats(self) -> Dict[str, Any]:
        """Get vault statistics"""
        sessions = self.list_sessions()
        all_interactions = []

        for session in sessions:
            all_interactions.extend(session.get("interactions", []))

        return {
            "total_sessions": len(sessions),
            "active_sessions": len([s for s in sessions if s["status"] == "active"]),
            "total_interactions": len(all_interactions),
            "sessions_by_type": {
                stype: len([s for s in sessions if s["type"] == stype])
                for stype in set(s["type"] for s in sessions)
            },
            "interactions_by_type": {
                itype: len([i for i in all_interactions if i["type"] == itype])
                for itype in set(i["type"] for i in all_interactions)
            }
        }


def main():
    """Example usage"""
    vault = ObsidianVaultManager()

    # Create "Hermes e Obsidian" session
    print("\n📝 Creating 'Hermes e Obsidian' session...")
    session1 = vault.create_session(
        session_type=SessionType.HERMES_OBSIDIAN,
        description="Hermes e Obsidian",
        user="danrcosta",
        metadata={"topic": "Interação Hermes com Vault de notas"}
    )
    print(f"Session ID: {session1['id']}")

    # Add interaction
    vault.add_interaction(
        session_id=session1["id"],
        interaction_type="text",
        content="Solicita mais detalhes sobre a interação entre Hermes e o Vault de notas.",
        source="telegram"
    )

    # Add message
    vault.add_message(
        session_id=session1["id"],
        role="user",
        content="Como integrar Hermes com Obsidian?",
        source="telegram"
    )

    # Create "Fix Hermes" session
    print("\n🔧 Creating 'Fix Hermes' session...")
    session2 = vault.create_session(
        session_type=SessionType.FIX_HERMES,
        description="Fix Hermes",
        user="danrcosta",
        status=SessionStatus.DISCONNECTED,
        metadata={"issue": "Connection timeout"}
    )

    # List sessions
    print("\n📋 Sessions:")
    sessions = vault.list_sessions()
    for session in sessions:
        summary = vault.get_session_summary(session["id"])
        print(f"  - {summary['description']} ({summary['status']}) - {summary['interactions_count']} interactions")

    # Get stats
    print("\n📊 Vault Statistics:")
    stats = vault.get_vault_stats()
    print(json.dumps(stats, indent=2))


if __name__ == "__main__":
    main()
