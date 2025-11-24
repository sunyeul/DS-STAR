from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class PathsConfig:
    root_dir: Path = Path(__file__).parent.parent
    data_dir: Path = root_dir / "data"


@dataclass
class AnalyzerAgentConfig:
    app_name: str = "analyzer_app"
    agent_name: str = "analyzer_agent"
    user_id: str = "user123"
    gemini_model: str = "gemini-2.5-flash"
    target_file_types: list[str] = field(
        default_factory=lambda: ["csv", "json", "txt", "pdf"]
    )
