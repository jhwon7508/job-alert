import yaml
import os
from dataclasses import dataclass, field
from typing import List

@dataclass
class SourceConfig:
    name: str
    url: str

@dataclass
class KeywordsConfig:
    include: List[str] = field(default_factory=list)
    exclude: List[str] = field(default_factory=list)

@dataclass
class ScoringConfig:
    title_hit: int
    body_hit: int
    exclude_penalty: int

@dataclass
class DigestConfig:
    min_score: int
    max_items: int

@dataclass
class Config:
    sources: List[SourceConfig]
    keywords: KeywordsConfig
    scoring: ScoringConfig
    digest: DigestConfig
    db_path: str
    discord_webhook_url: str

def load_config(path: str = "sources.yaml") -> Config:
    if not os.path.exists(path):
        raise FileNotFoundError(f"Config file not found: {path}")

    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    sources = [SourceConfig(**s) for s in data.get("sources", [])]
    keywords = KeywordsConfig(**data.get("keywords", {}))
    scoring = ScoringConfig(**data.get("scoring", {}))
    digest = DigestConfig(**data.get("digest", {}))
    
    db_path = os.getenv("DB_PATH", "jobs.db")
    discord_webhook_url = os.getenv("DISCORD_WEBHOOK_URL", "")

    return Config(
        sources=sources,
        keywords=keywords,
        scoring=scoring,
        digest=digest,
        db_path=db_path,
        discord_webhook_url=discord_webhook_url
    )
