from dataclasses import dataclass
from pathlib import Path


@dataclass
class PathsConfig:
    root_dir: Path = Path(__file__).parent.parent
    data_dir: Path = root_dir / "data"
