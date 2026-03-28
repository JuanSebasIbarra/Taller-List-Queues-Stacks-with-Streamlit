from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List


class JobStatus(str, Enum):
    """Estados posibles de un trabajo en el pipeline."""

    PENDING = "Pendiente"
    RUNNING = "En ejecución"
    SUCCESS = "Exitoso"
    FAILED = "Fallido"


class PipelineStage(str, Enum):
    """Etapas del proceso CI/CD."""

    COMPILE = "Compilar"
    TEST = "Probar"
    DEPLOY = "Desplegar"


@dataclass
class StageResult:
    """Resultado de una etapa específica."""

    stage: PipelineStage
    passed: bool
    message: str
    timestamp: datetime = field(default_factory=datetime.now)
    duration_ms: int = 0


@dataclass
class Job:
    """Representa un trabajo del pipeline."""

    id: int
    repository: str
    branch: str
    commit_hash: str
    author: str
    created_at: datetime = field(default_factory=datetime.now)
    status: JobStatus = JobStatus.PENDING
    test_cases: List[str] = field(default_factory=list)
    stage_results: List[StageResult] = field(default_factory=list)
    logs: List[str] = field(default_factory=list)

    def add_log(self, message: str) -> None:
        self.logs.append(message)

    def add_stage_result(self, result: StageResult) -> None:
        self.stage_results.append(result)
