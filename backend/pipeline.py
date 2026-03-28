from __future__ import annotations

import random
from datetime import datetime
from typing import Dict, List, Optional

from .data_structures import Queue, Stack
from .models import Job, JobStatus, PipelineStage, StageResult


class CICDPipeline:
    """Orquesta el flujo de integración y despliegue usando POO."""

    def __init__(self) -> None:
        self.pending_jobs: Queue[Job] = Queue()
        self.deployment_history: Stack[Job] = Stack()
        self.jobs: List[Job] = []
        self.global_logs: List[str] = []
        self._next_id: int = 1

    def create_job(
        self,
        repository: str,
        branch: str,
        commit_hash: str,
        author: str,
        test_cases: Optional[List[str]] = None,
    ) -> Job:
        """Crea y encola un nuevo trabajo."""
        job = Job(
            id=self._next_id,
            repository=repository,
            branch=branch,
            commit_hash=commit_hash,
            author=author,
            test_cases=test_cases or [],
        )
        self._next_id += 1
        self.jobs.append(job)
        self.pending_jobs.enqueue(job)

        msg = f"Job #{job.id} encolado para {job.repository}@{job.branch}"
        self.global_logs.append(msg)
        job.add_log(msg)
        return job

    def process_next_job(self, compile_ok: bool, tests_ok_probability: float) -> Optional[Job]:
        """Procesa el siguiente trabajo de la cola."""
        if self.pending_jobs.is_empty():
            return None

        job = self.pending_jobs.dequeue()
        job.status = JobStatus.RUNNING
        job.add_log("Inicio de ejecución")

        compile_result = self._run_compile(job, compile_ok)
        if not compile_result.passed:
            job.status = JobStatus.FAILED
            return job

        tests_result = self._run_tests(job, tests_ok_probability)
        if not tests_result.passed:
            job.status = JobStatus.FAILED
            return job

        deploy_result = self._run_deploy(job)
        if not deploy_result.passed:
            job.status = JobStatus.FAILED
            return job

        job.status = JobStatus.SUCCESS
        self.deployment_history.push(job)
        job.add_log("Pipeline finalizado con éxito")
        self.global_logs.append(f"Job #{job.id} desplegado correctamente")
        return job

    def rollback_last_deployment(self) -> Optional[str]:
        """Revierte el último despliegue exitoso usando una pila."""
        if self.deployment_history.is_empty():
            return None

        last_job = self.deployment_history.pop()
        message = (
            f"Rollback aplicado al Job #{last_job.id} "
            f"({last_job.repository}@{last_job.branch})"
        )
        last_job.add_log(message)
        self.global_logs.append(message)
        return message

    def summary(self) -> Dict[str, int]:
        """Resumen estadístico del pipeline."""
        return {
            "total": len(self.jobs),
            "pendientes": sum(1 for j in self.jobs if j.status == JobStatus.PENDING),
            "en_ejecucion": sum(1 for j in self.jobs if j.status == JobStatus.RUNNING),
            "exitosos": sum(1 for j in self.jobs if j.status == JobStatus.SUCCESS),
            "fallidos": sum(1 for j in self.jobs if j.status == JobStatus.FAILED),
            "en_cola": self.pending_jobs.size(),
            "despliegues_activos": self.deployment_history.size(),
        }

    def _run_compile(self, job: Job, compile_ok: bool) -> StageResult:
        passed = compile_ok
        message = "Compilación completada" if passed else "Error de compilación"
        result = StageResult(stage=PipelineStage.COMPILE, passed=passed, message=message)
        job.add_stage_result(result)
        job.add_log(f"[{result.timestamp:%H:%M:%S}] {message}")
        return result

    def _run_tests(self, job: Job, tests_ok_probability: float) -> StageResult:
        chance = max(0.0, min(1.0, tests_ok_probability))
        passed = random.random() <= chance
        total_tests = len(job.test_cases)
        executed = total_tests if total_tests > 0 else 1

        message = (
            f"Pruebas exitosas ({executed}/{executed})"
            if passed
            else f"Pruebas fallidas ({max(0, executed - 1)}/{executed})"
        )

        result = StageResult(stage=PipelineStage.TEST, passed=passed, message=message)
        job.add_stage_result(result)
        job.add_log(f"[{result.timestamp:%H:%M:%S}] {message}")
        return result

    def _run_deploy(self, job: Job) -> StageResult:
        passed = True
        message = f"Despliegue en entorno de staging - {datetime.now():%Y-%m-%d %H:%M:%S}"
        result = StageResult(stage=PipelineStage.DEPLOY, passed=passed, message=message)
        job.add_stage_result(result)
        job.add_log(f"[{result.timestamp:%H:%M:%S}] {message}")
        return result
