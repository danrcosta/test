#!/usr/bin/env python3
"""
Hermes to Claude Code Bridge
Sends images and data from Telegram via Hermes to Claude Code sessions
"""

import json
import requests
import base64
import os
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any
from enum import Enum

class ContentType(Enum):
    TEXT = "text"
    IMAGE = "image"
    CODE = "code"
    FILE = "file"

class HermesClaudeBridge:
    def __init__(self, hermes_url: str = "http://100.86.232.77:8080", timeout: int = 30):
        """
        Initialize the Hermes to Claude Code bridge

        Args:
            hermes_url: URL of Hermes MCP server
            timeout: Request timeout in seconds
        """
        self.hermes_url = hermes_url.rstrip('/')
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'Hermes-Claude-Bridge/1.0'
        })

    def health_check(self) -> bool:
        """Check if Hermes server is reachable"""
        try:
            response = self.session.get(
                f"{self.hermes_url}/health",
                timeout=self.timeout
            )
            return response.status_code == 200
        except Exception as e:
            print(f"❌ Health check failed: {e}")
            return False

    def encode_image(self, image_path: str) -> str:
        """Encode image to base64"""
        try:
            with open(image_path, 'rb') as img_file:
                return base64.b64encode(img_file.read()).decode('utf-8')
        except Exception as e:
            print(f"❌ Error encoding image: {e}")
            return None

    def prepare_payload(
        self,
        content: str,
        content_type: ContentType = ContentType.TEXT,
        image_path: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Prepare payload for Claude Code

        Args:
            content: Main content (text, code, etc.)
            content_type: Type of content
            image_path: Path to image file (optional)
            metadata: Additional metadata

        Returns:
            Prepared payload dictionary
        """
        payload = {
            "timestamp": datetime.now().isoformat(),
            "source": "hermes_telegram",
            "content_type": content_type.value,
            "content": content,
            "metadata": metadata or {}
        }

        # Add image if provided
        if image_path and os.path.exists(image_path):
            image_b64 = self.encode_image(image_path)
            if image_b64:
                payload["image"] = {
                    "data": image_b64,
                    "filename": os.path.basename(image_path)
                }
                payload["metadata"]["image_path"] = image_path

        return payload

    def send_to_claude(
        self,
        content: str,
        content_type: ContentType = ContentType.TEXT,
        image_path: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        endpoint: str = "/claude/send"
    ) -> Dict[str, Any]:
        """
        Send content to Claude Code via Hermes

        Args:
            content: Main content
            content_type: Type of content
            image_path: Optional image path
            metadata: Optional metadata
            endpoint: Hermes endpoint

        Returns:
            Response from server
        """
        try:
            # Check Hermes is available
            if not self.health_check():
                return {
                    "success": False,
                    "error": "Hermes server is not available"
                }

            # Prepare payload
            payload = self.prepare_payload(
                content=content,
                content_type=content_type,
                image_path=image_path,
                metadata=metadata
            )

            # Send to Hermes
            response = self.session.post(
                f"{self.hermes_url}{endpoint}",
                json=payload,
                timeout=self.timeout
            )

            if response.status_code == 200:
                print(f"✅ Successfully sent {content_type.value} to Claude Code")
                return {
                    "success": True,
                    "response": response.json(),
                    "timestamp": datetime.now().isoformat()
                }
            else:
                print(f"❌ Error: {response.status_code} - {response.text}")
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}",
                    "details": response.text
                }

        except requests.exceptions.Timeout:
            return {
                "success": False,
                "error": "Request timeout"
            }
        except Exception as e:
            print(f"❌ Error sending to Claude: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def send_text_prompt(self, prompt: str, metadata: Optional[Dict] = None) -> Dict:
        """Send text prompt to Claude Code"""
        return self.send_to_claude(
            content=prompt,
            content_type=ContentType.TEXT,
            metadata=metadata
        )

    def send_code(self, code: str, language: str = "python", metadata: Optional[Dict] = None) -> Dict:
        """Send code snippet to Claude Code"""
        meta = metadata or {}
        meta["language"] = language
        return self.send_to_claude(
            content=code,
            content_type=ContentType.CODE,
            metadata=meta
        )

    def send_image_analysis(self, image_path: str, description: str = "", metadata: Optional[Dict] = None) -> Dict:
        """Send image for analysis"""
        meta = metadata or {}
        if description:
            meta["description"] = description
        return self.send_to_claude(
            content=description or "Analyze this image",
            content_type=ContentType.IMAGE,
            image_path=image_path,
            metadata=meta
        )

    def send_file(self, file_path: str, content: str, metadata: Optional[Dict] = None) -> Dict:
        """Send file content"""
        meta = metadata or {}
        meta["filename"] = os.path.basename(file_path)
        return self.send_to_claude(
            content=content,
            content_type=ContentType.FILE,
            metadata=meta
        )


def main():
    """Example usage"""
    bridge = HermesClaudeBridge()

    # Example 1: Send text prompt
    print("\n📝 Sending text prompt...")
    result = bridge.send_text_prompt(
        "Analyze this Telegram message and provide insights",
        metadata={
            "source": "telegram",
            "chat_id": "12345",
            "user": "danrcosta"
        }
    )
    print(json.dumps(result, indent=2))

    # Example 2: Send code
    print("\n💻 Sending code snippet...")
    code = """
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)
"""
    result = bridge.send_code(code, language="python")
    print(json.dumps(result, indent=2))

    # Example 3: Send image (if exists)
    print("\n🖼️  Sending image analysis...")
    test_image = "C:\\Users\\SERVER\\AppData\\Local\\hermes\\cache\\images\\img_d654554f7e77.jpg"
    if os.path.exists(test_image):
        result = bridge.send_image_analysis(
            test_image,
            "Analyze this screenshot from Hermes"
        )
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
