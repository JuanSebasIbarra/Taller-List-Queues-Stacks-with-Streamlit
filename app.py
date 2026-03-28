from __future__ import annotations

import streamlit as st

from backend.models import JobStatus
from backend.pipeline import CICDPipeline


st.set_page_config(page_title="Simulador CI/CD", page_icon="🚀", layout="wide")


def get_pipeline() -> CICDPipeline:
    if "pipeline" not in st.session_state:
        st.session_state.pipeline = CICDPipeline()
    return st.session_state.pipeline


pipeline = get_pipeline()

st.title("🚀 Simulador CI/CD")
st.caption("POO + Listas + Pilas + Colas con Python (Backend) y Streamlit (Frontend)")

with st.sidebar:
    st.header("Nuevo trabajo")
    repository = st.text_input("Repositorio", value="mi-organizacion/api")
    branch = st.text_input("Branch", value="main")
    commit_hash = st.text_input("Commit", value="a1b2c3d")
    author = st.text_input("Autor", value="sebastian")
    tests_text = st.text_area(
        "Casos de prueba (uno por línea)",
        value="test_login\ntest_create_user\ntest_checkout",
    )

    if st.button("Encolar trabajo", use_container_width=True):
        test_cases = [line.strip() for line in tests_text.splitlines() if line.strip()]
        created = pipeline.create_job(repository, branch, commit_hash, author, test_cases)
        st.success(f"Trabajo #{created.id} encolado")

st.subheader("Control de ejecución")
col1, col2, col3 = st.columns(3)

with col1:
    compile_ok = st.toggle("Compilación exitosa", value=True)
with col2:
    tests_prob = st.slider("Probabilidad de éxito en pruebas", 0.0, 1.0, 0.8, 0.05)
with col3:
    run_job = st.button("Procesar siguiente trabajo", type="primary", use_container_width=True)

if run_job:
    result = pipeline.process_next_job(compile_ok=compile_ok, tests_ok_probability=tests_prob)
    if result is None:
        st.warning("No hay trabajos en cola")
    elif result.status == JobStatus.SUCCESS:
        st.success(f"Trabajo #{result.id} completado con éxito")
    else:
        st.error(f"Trabajo #{result.id} falló")

if st.button("Rollback último despliegue", use_container_width=True):
    rollback = pipeline.rollback_last_deployment()
    if rollback:
        st.info(rollback)
    else:
        st.warning("No hay despliegues para revertir")

st.divider()
st.subheader("Resumen")
summary = pipeline.summary()
metrics = st.columns(7)
labels = [
    "Total",
    "Pendientes",
    "En ejecución",
    "Exitosos",
    "Fallidos",
    "En cola",
    "Despliegues",
]
keys = [
    "total",
    "pendientes",
    "en_ejecucion",
    "exitosos",
    "fallidos",
    "en_cola",
    "despliegues_activos",
]
for col, label, key in zip(metrics, labels, keys):
    col.metric(label, summary[key])

st.divider()
left, right = st.columns([2, 1])

with left:
    st.subheader("Trabajos")
    if not pipeline.jobs:
        st.caption("Aún no hay trabajos")
    else:
        for job in reversed(pipeline.jobs):
            with st.expander(f"Job #{job.id} - {job.status.value} - {job.repository}@{job.branch}"):
                st.write(f"**Autor:** {job.author}")
                st.write(f"**Commit:** {job.commit_hash}")
                st.write(f"**Creado:** {job.created_at:%Y-%m-%d %H:%M:%S}")
                st.write("**Logs:**")
                st.code("\n".join(job.logs) if job.logs else "Sin logs")
                if job.stage_results:
                    st.write("**Etapas:**")
                    for result in job.stage_results:
                        status_icon = "✅" if result.passed else "❌"
                        st.write(
                            f"{status_icon} {result.stage.value} - {result.message} "
                            f"({result.timestamp:%H:%M:%S})"
                        )

with right:
    st.subheader("Cola actual (FIFO)")
    queued = pipeline.pending_jobs.to_list()
    if not queued:
        st.caption("Cola vacía")
    else:
        for j in queued:
            st.write(f"#{j.id} {j.repository}@{j.branch}")

    st.subheader("Historial despliegues (LIFO)")
    history = pipeline.deployment_history.to_list()
    if not history:
        st.caption("Sin despliegues")
    else:
        for j in reversed(history):
            st.write(f"#{j.id} {j.repository}@{j.branch}")
