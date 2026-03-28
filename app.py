"""Frontend Streamlit - Simulador CI/CD estilo Jenkins."""

from __future__ import annotations

from typing import Optional

import streamlit as st

from backend.models import JobStatus, PipelineStage
from backend.pipeline import CICDPipeline

# ── Configuración de página ────────────────────────────────────────
st.set_page_config(
    page_title="CI/CD Pipeline Simulator",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ── Helpers ────────────────────────────────────────────────────────
def get_pipeline() -> CICDPipeline:
    if "pipeline" not in st.session_state:
        st.session_state.pipeline = CICDPipeline()
    return st.session_state.pipeline


def navigate(view: str, job_id: Optional[int] = None) -> None:
    st.session_state.view = view
    if job_id is not None:
        st.session_state.selected_job_id = job_id


def fmt_dur(ms: int) -> str:
    """Formatea milisegundos en cadena legible estilo Jenkins."""
    if ms <= 0:
        return "-"
    if ms < 1_000:
        return f"{ms}ms"
    s = ms // 1_000
    if s < 60:
        return f"{s}s"
    m, s = divmod(s, 60)
    return f"{m}min {s}s"


pipeline = get_pipeline()

_defaults: dict = {
    "view": "status",
    "selected_job_id": None,
    "flash_msg": None,
    "flash_type": "info",
}
for _k, _v in _defaults.items():
    if _k not in st.session_state:
        st.session_state[_k] = _v


# ── CSS global estilo Jenkins ──────────────────────────────────────
st.markdown(
    """
<style>
#MainMenu, footer, .stDeployButton { visibility: hidden; display: none; }

.block-container {
    padding-top: 0 !important;
    padding-left: 1.2rem !important;
    padding-right: 1.2rem !important;
    max-width: 100% !important;
}

:root {
    --jk-dark:      #1a1a1a;
    --jk-red:       #D33833;
    --jk-blue:      #335061;
    --jk-border:    #d4d4d4;
    --jk-stage-hdr: #d7e9f7;
    --ok-bg:        #e8f5e9;  --ok-txt:   #1b5e20;
    --fail-bg:      #ffebee;  --fail-txt: #b71c1c;
    --run-bg:       #fff8e1;  --run-txt:  #e65100;
    --pend-bg:      #f5f5f5;  --pend-txt: #9e9e9e;
}

/* Header */
.jk-header {
    background: var(--jk-dark);
    color: white;
    padding: 9px 20px;
    display: flex;
    align-items: center;
    gap: 20px;
    border-bottom: 3px solid var(--jk-red);
    margin-bottom: 6px;
}
.jk-logo { font-size: 18px; font-weight: bold; }
.jk-slash { color: var(--jk-red); }
.jk-header-right { margin-left: auto; font-size: 12px; color: #999; }

/* Breadcrumb */
.jk-breadcrumb {
    background: white;
    padding: 5px 14px;
    border-bottom: 1px solid var(--jk-border);
    font-size: 12px;
    color: #555;
    margin-bottom: 10px;
}

/* Titulo de sección */
.jk-title {
    font-size: 21px;
    font-weight: bold;
    color: #1a1a1a;
    border-bottom: 2px solid var(--jk-border);
    padding-bottom: 5px;
    margin: 4px 0 14px 0;
}

/* Tabla Stage View */
.jk-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 13px;
    background: white;
    box-shadow: 0 1px 4px rgba(0,0,0,.07);
}
.jk-table th {
    background: var(--jk-stage-hdr);
    border: 1px solid #c8d8e8;
    padding: 9px 14px;
    text-align: center;
    font-weight: bold;
    color: var(--jk-blue);
    white-space: nowrap;
}
.jk-table td {
    border: 1px solid var(--jk-border);
    padding: 9px 14px;
    text-align: center;
    vertical-align: middle;
    min-width: 100px;
}
.jk-avg td { background: #f0f7ff; font-size: 11px; color: #555; font-style: italic; }
.jk-cell-ok   { background: var(--ok-bg);   color: var(--ok-txt);   font-weight: 600; }
.jk-cell-fail { background: var(--fail-bg);  color: var(--fail-txt); font-weight: 600; }
.jk-cell-run  { background: var(--run-bg);   color: var(--run-txt);  }
.jk-cell-pend { background: var(--pend-bg);  color: var(--pend-txt); font-style: italic; }

/* Badges */
.jk-badge {
    display: inline-block;
    width: 28px; height: 28px;
    border-radius: 50%;
    line-height: 28px;
    text-align: center;
    font-size: 11px;
    font-weight: bold;
    color: white;
}
.jk-b-ok   { background: #2da44e; }
.jk-b-fail { background: #cf222e; }
.jk-b-run  { background: #e6a817; }
.jk-b-pend { background: #9e9e9e; }

/* Metricas */
.jk-metrics { display: flex; gap: 10px; margin-bottom: 14px; flex-wrap: wrap; }
.jk-metric {
    background: white;
    border: 1px solid var(--jk-border);
    border-radius: 4px;
    padding: 10px 18px;
    flex: 1; min-width: 80px;
    text-align: center;
    box-shadow: 0 1px 2px rgba(0,0,0,.04);
}
.jk-metric-val { font-size: 26px; font-weight: bold; color: var(--jk-blue); }
.jk-metric-lbl { font-size: 10px; color: #777; text-transform: uppercase; letter-spacing: .5px; margin-top: 2px; }

/* Consola */
.jk-console {
    background: #1e1e1e;
    color: #d4d4d4;
    font-family: 'Courier New', Courier, monospace;
    font-size: 12px;
    padding: 14px;
    border-radius: 4px;
    max-height: 360px;
    overflow-y: auto;
    white-space: pre-wrap;
    line-height: 1.7;
}

/* Banners */
.jk-banner { padding: 10px 14px; margin: 8px 0; border-radius: 0 4px 4px 0; font-size: 13px; }
.jk-info    { background: #e3f2fd; border-left: 4px solid #1976d2; }
.jk-success { background: #e8f5e9; border-left: 4px solid #388e3c; }
.jk-warning { background: #fff3e0; border-left: 4px solid #f57c00; }
.jk-error   { background: #ffebee; border-left: 4px solid #d32f2f; }

/* Etiquetas de estado inline */
.jk-lbl-ok   { background:#2da44e; color:white; padding:2px 9px; border-radius:3px; font-size:12px; font-weight:bold; }
.jk-lbl-fail { background:#cf222e; color:white; padding:2px 9px; border-radius:3px; font-size:12px; font-weight:bold; }
.jk-lbl-run  { background:#e6a817; color:white; padding:2px 9px; border-radius:3px; font-size:12px; font-weight:bold; }
.jk-lbl-pend { background:#9e9e9e; color:white; padding:2px 9px; border-radius:3px; font-size:12px; font-weight:bold; }

/* Nav activo en sidebar */
.jk-nav-active {
    background: #d7e9f7;
    border-left: 3px solid var(--jk-blue);
    padding: 4px 8px;
    font-weight: bold;
    font-size: 13px;
    color: var(--jk-blue);
    margin-bottom: 2px;
    border-radius: 0 3px 3px 0;
}
.jk-nav-inactive { padding: 4px 8px; font-size: 13px; color: #333; margin-bottom: 2px; }

/* Botones Jenkins */
div[data-testid="stButton"] button {
    background: var(--jk-blue) !important;
    color: white !important;
    border: none !important;
    border-radius: 3px !important;
    font-size: 13px !important;
}
div[data-testid="stButton"] button:hover { background: #2a4050 !important; }
</style>
""",
    unsafe_allow_html=True,
)

# ── Header Jenkins ─────────────────────────────────────────────────
st.markdown(
    """
<div class="jk-header">
    <div class="jk-logo">CI<span class="jk-slash">/</span>CD Pipeline Simulator</div>
    <div style="font-size:12px; color:#666; border-left:1px solid #444; padding-left:14px;">
        Integracion y Despliegue Continuo
    </div>
    <div class="jk-header-right">Admin &nbsp;|&nbsp; Cerrar sesion</div>
</div>
<div class="jk-breadcrumb">
    Dashboard &rsaquo; mi-organizacion/pipeline &rsaquo; <strong>main</strong>
</div>
""",
    unsafe_allow_html=True,
)

# ── Flash messages ─────────────────────────────────────────────────
if st.session_state.flash_msg:
    css_cls = {"success": "jk-success", "error": "jk-error", "warning": "jk-warning"}.get(
        st.session_state.flash_type, "jk-info"
    )
    st.markdown(
        f'<div class="jk-banner {css_cls}">{st.session_state.flash_msg}</div>',
        unsafe_allow_html=True,
    )
    st.session_state.flash_msg = None

# ── Sidebar estilo Jenkins ─────────────────────────────────────────
with st.sidebar:
    current_view = st.session_state.view

    st.markdown(
        "<div style='font-size:12px; font-weight:bold; color:#555; margin-bottom:4px;'>"
        "MENU PRINCIPAL</div>",
        unsafe_allow_html=True,
    )

    nav_items = [
        ("status",    "Estado / Vista de Etapas"),
        ("build_now", "Construir Ahora"),
        ("rollback",  "Revertir Despliegue"),
        ("logs",      "Registro de Actividad"),
    ]

    for view_key, label in nav_items:
        is_active = current_view == view_key
        css = "jk-nav-active" if is_active else "jk-nav-inactive"
        prefix = "▶ " if is_active else "   "
        st.markdown(f'<div class="{css}">{prefix}{label}</div>', unsafe_allow_html=True)
        if st.button(label, key=f"nav_{view_key}", use_container_width=True):
            navigate(view_key)
            st.rerun()

    st.divider()

    st.markdown(
        "<div style='font-size:12px; font-weight:bold; color:#555; margin-bottom:4px;'>"
        "HISTORIAL DE CONSTRUCCIONES</div>",
        unsafe_allow_html=True,
    )
    filter_text = st.text_input(
        "Filtrar",
        placeholder="Filtrar construcciones...",
        label_visibility="collapsed",
        key="hist_filter",
    )

    all_jobs = list(reversed(pipeline.jobs))
    if filter_text:
        all_jobs = [
            j for j in all_jobs
            if filter_text.lower() in f"#{j.id} {j.repository} {j.branch} {j.author}".lower()
        ]

    if not all_jobs:
        st.caption("Sin construcciones aun.")
    else:
        for job in all_jobs[:20]:
            icon = {"SUCCESS": "[OK]  ", "Exitoso": "[OK]  "}.get(
                job.status.value,
                "[FAIL]" if job.status == JobStatus.FAILED else "[...] ",
            )
            lbl = f"{icon} #{job.id}  {job.branch}"
            if st.button(lbl, key=f"hist_{job.id}", use_container_width=True):
                navigate("build_detail", job.id)
                st.rerun()


# ── Vista actual ───────────────────────────────────────────────────
view = st.session_state.view


# ═══════════════════════════════════════════════════════════════════
# VISTA: STATUS / STAGE VIEW
# ═══════════════════════════════════════════════════════════════════
if view == "status":
    summary = pipeline.summary()
    st.markdown('<div class="jk-title">Vista de Etapas del Pipeline</div>', unsafe_allow_html=True)

    # Tarjetas de metricas
    st.markdown(
        f"""
        <div class="jk-metrics">
            <div class="jk-metric">
                <div class="jk-metric-val">{summary['total']}</div>
                <div class="jk-metric-lbl">Total</div>
            </div>
            <div class="jk-metric">
                <div class="jk-metric-val" style="color:#9e9e9e;">{summary['en_cola']}</div>
                <div class="jk-metric-lbl">En Cola</div>
            </div>
            <div class="jk-metric">
                <div class="jk-metric-val" style="color:#e6a817;">{summary['en_ejecucion']}</div>
                <div class="jk-metric-lbl">En Ejecucion</div>
            </div>
            <div class="jk-metric">
                <div class="jk-metric-val" style="color:#2da44e;">{summary['exitosos']}</div>
                <div class="jk-metric-lbl">Exitosos</div>
            </div>
            <div class="jk-metric">
                <div class="jk-metric-val" style="color:#cf222e;">{summary['fallidos']}</div>
                <div class="jk-metric-lbl">Fallidos</div>
            </div>
            <div class="jk-metric">
                <div class="jk-metric-val" style="color:#335061;">{summary['despliegues_activos']}</div>
                <div class="jk-metric-lbl">Despliegues</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    jobs = list(reversed(pipeline.jobs))

    if not jobs:
        st.markdown(
            '<div class="jk-banner jk-info">No hay construcciones registradas. '
            'Use <strong>Construir Ahora</strong> en el menu lateral para iniciar el primer pipeline.</div>',
            unsafe_allow_html=True,
        )
    else:
        stages = list(PipelineStage)

        # Tiempos promedio por etapa (builds exitosos)
        avg: dict = {s: [] for s in stages}
        for j in jobs:
            for r in j.stage_results:
                if r.passed and r.duration_ms > 0:
                    avg[r.stage].append(r.duration_ms)
        avg_str = {
            s: fmt_dur(int(sum(v) / len(v))) if v else "-"
            for s, v in avg.items()
        }

        html = '<table class="jk-table"><thead><tr>'
        html += '<th style="min-width:170px; text-align:left;">Construccion</th><th>Cambios</th>'
        for s in stages:
            html += f"<th>{s.value}</th>"
        html += "</tr></thead><tbody>"

        # Fila de promedios
        html += '<tr class="jk-avg">'
        html += '<td style="text-align:left;">Tiempo promedio por etapa</td><td>-</td>'
        for s in stages:
            html += f"<td>{avg_str[s]}</td>"
        html += "</tr>"

        # Filas de builds
        for job in jobs:
            row_bg = "background:#fff8f8;" if job.status == JobStatus.FAILED else ""
            html += f'<tr style="{row_bg}">'

            badge_cls = {
                JobStatus.SUCCESS: "jk-b-ok",
                JobStatus.FAILED:  "jk-b-fail",
                JobStatus.RUNNING: "jk-b-run",
                JobStatus.PENDING: "jk-b-pend",
            }.get(job.status, "jk-b-pend")

            html += f"""
            <td style="text-align:left; background:white;">
                <span class="jk-badge {badge_cls}">#{job.id}</span>
                &nbsp;
                <span style="font-size:11px; color:#555; line-height:1.6;">
                    {job.created_at:%b %d, %H:%M}<br>
                    <span style="color:#999;">{job.author}</span>
                </span>
            </td>"""

            html += (
                f'<td style="font-size:11px; color:#888; background:white; white-space:nowrap;">'
                f'{job.commit_hash[:7]}<br><em>{job.branch}</em></td>'
            )

            for s in stages:
                result = next((r for r in job.stage_results if r.stage == s), None)
                if result is None:
                    html += '<td class="jk-cell-pend">-</td>'
                elif result.passed:
                    html += f'<td class="jk-cell-ok">{fmt_dur(result.duration_ms)}</td>'
                else:
                    html += '<td class="jk-cell-fail">Error</td>'

            html += "</tr>"

        html += "</tbody></table>"
        st.markdown(html, unsafe_allow_html=True)

    # Permalinks
    if jobs:
        st.markdown("<br>**Permalinks**", unsafe_allow_html=True)
        last_ok = next((j for j in jobs if j.status == JobStatus.SUCCESS), None)
        last_fail = next((j for j in jobs if j.status == JobStatus.FAILED), None)
        st.write(f"Ultima construccion: #{jobs[0].id}")
        if last_ok:
            st.write(f"Ultima construccion exitosa: #{last_ok.id}")
        if last_fail:
            st.write(f"Ultima construccion fallida: #{last_fail.id}")


# ═══════════════════════════════════════════════════════════════════
# VISTA: CONSTRUIR AHORA
# ═══════════════════════════════════════════════════════════════════
elif view == "build_now":
    st.markdown('<div class="jk-title">Construir Ahora</div>', unsafe_allow_html=True)

    with st.form("build_form", clear_on_submit=False):
        col_l, col_r = st.columns(2)

        with col_l:
            st.markdown("**Informacion del repositorio**")
            repository  = st.text_input("Repositorio", value="mi-organizacion/api")
            branch      = st.text_input("Branch", value="main")
            commit_hash = st.text_input("Hash del commit", value="a1b2c3d")
            author      = st.text_input("Autor", value="sebastian")

        with col_r:
            st.markdown("**Casos de prueba** (uno por linea)")
            tests_text = st.text_area(
                "Casos de prueba",
                value="test_login\ntest_create_user\ntest_checkout",
                height=130,
                label_visibility="collapsed",
            )
            st.markdown("**Configuracion de ejecucion**")
            compile_ok = st.toggle("Compilacion exitosa", value=True)
            tests_pct  = st.slider(
                "Probabilidad de exito en pruebas (%)",
                min_value=0, max_value=100, value=80, step=5, format="%d%%",
            )

        submitted = st.form_submit_button("Iniciar construccion", use_container_width=True)

    if submitted:
        test_cases = [ln.strip() for ln in tests_text.splitlines() if ln.strip()]
        pipeline.create_job(repository, branch, commit_hash, author, test_cases)
        result = pipeline.process_next_job(
            compile_ok=compile_ok,
            tests_ok_probability=tests_pct / 100,
        )
        if result:
            if result.status == JobStatus.SUCCESS:
                st.session_state.flash_msg = (
                    f"Construccion <strong>#{result.id}</strong> finalizada con exito. "
                    f"Repositorio: {result.repository} | Branch: {result.branch}"
                )
                st.session_state.flash_type = "success"
            else:
                failed_stage = next(
                    (r.stage.value for r in result.stage_results if not r.passed),
                    "desconocida",
                )
                st.session_state.flash_msg = (
                    f"Construccion <strong>#{result.id}</strong> fallo en la etapa "
                    f"<strong>{failed_stage}</strong>."
                )
                st.session_state.flash_type = "error"
            navigate("build_detail", result.id)
            st.rerun()


# ═══════════════════════════════════════════════════════════════════
# VISTA: DETALLE DE CONSTRUCCION
# ═══════════════════════════════════════════════════════════════════
elif view == "build_detail":
    job_id = st.session_state.selected_job_id
    job = next((j for j in pipeline.jobs if j.id == job_id), None)

    if job is None:
        st.markdown(
            '<div class="jk-banner jk-warning">Construccion no encontrada. '
            'Seleccione una del historial en el menu lateral.</div>',
            unsafe_allow_html=True,
        )
    else:
        status_lbl = {
            JobStatus.SUCCESS: '<span class="jk-lbl-ok">EXITOSO</span>',
            JobStatus.FAILED:  '<span class="jk-lbl-fail">FALLIDO</span>',
            JobStatus.RUNNING: '<span class="jk-lbl-run">EN EJECUCION</span>',
            JobStatus.PENDING: '<span class="jk-lbl-pend">PENDIENTE</span>',
        }.get(job.status, "")

        st.markdown(
            f'<div class="jk-title">Construccion #{job.id} &nbsp; {status_lbl}</div>',
            unsafe_allow_html=True,
        )

        col_main, col_info = st.columns([3, 1])

        with col_main:
            banner_cls = {
                JobStatus.SUCCESS: "jk-success",
                JobStatus.FAILED:  "jk-error",
                JobStatus.RUNNING: "jk-warning",
                JobStatus.PENDING: "jk-info",
            }.get(job.status, "jk-info")

            st.markdown(
                f'<div class="jk-banner {banner_cls}">'
                f'<strong>Repositorio:</strong> {job.repository} &nbsp;|&nbsp; '
                f'<strong>Branch:</strong> {job.branch} &nbsp;|&nbsp; '
                f'<strong>Commit:</strong> {job.commit_hash} &nbsp;|&nbsp; '
                f'<strong>Autor:</strong> {job.author}'
                f'</div>',
                unsafe_allow_html=True,
            )

            if job.stage_results:
                st.markdown("**Etapas del pipeline:**")
                for r in job.stage_results:
                    badge = (
                        '<span class="jk-lbl-ok">OK</span>'
                        if r.passed
                        else '<span class="jk-lbl-fail">ERROR</span>'
                    )
                    st.markdown(
                        f"{badge} &nbsp; <strong>{r.stage.value}</strong> "
                        f"&mdash; {r.message} "
                        f'<span style="color:#999; font-size:12px;">'
                        f"({fmt_dur(r.duration_ms)})</span>",
                        unsafe_allow_html=True,
                    )
                st.markdown("<br>", unsafe_allow_html=True)

            st.markdown("**Salida de consola:**")
            log_html = "\n".join(job.logs) if job.logs else "Sin logs disponibles."
            st.markdown(f'<div class="jk-console">{log_html}</div>', unsafe_allow_html=True)

        with col_info:
            st.markdown("**Informacion**")
            st.write(f"ID: #{job.id}")
            st.write(f"Estado: {job.status.value}")
            st.write(f"Repositorio: {job.repository}")
            st.write(f"Branch: {job.branch}")
            st.write(f"Commit: {job.commit_hash}")
            st.write(f"Autor: {job.author}")
            st.write(f"Fecha: {job.created_at:%Y-%m-%d %H:%M:%S}")

            if job.test_cases:
                st.divider()
                st.markdown("**Casos de prueba:**")
                for tc in job.test_cases:
                    st.write(f"- {tc}")

            if job.stage_results:
                st.divider()
                st.markdown("**Duracion por etapa:**")
                for r in job.stage_results:
                    st.write(f"{r.stage.value}: {fmt_dur(r.duration_ms)}")

            st.divider()
            st.markdown("**Permalinks**")
            st.write(f"Esta construccion: #{job.id}")


# ═══════════════════════════════════════════════════════════════════
# VISTA: REVERTIR DESPLIEGUE
# ═══════════════════════════════════════════════════════════════════
elif view == "rollback":
    st.markdown('<div class="jk-title">Revertir Despliegue (Rollback)</div>', unsafe_allow_html=True)

    history = pipeline.deployment_history.to_list()

    if not history:
        st.markdown(
            '<div class="jk-banner jk-warning">'
            'No hay despliegues exitosos en la pila. '
            'Ejecute al menos un pipeline exitoso para poder revertir.'
            '</div>',
            unsafe_allow_html=True,
        )
    else:
        last = history[-1]
        st.markdown(
            f'<div class="jk-banner jk-info">'
            f'Se revertira el ultimo despliegue: '
            f'<strong>Construccion #{last.id}</strong> &nbsp;|&nbsp; '
            f'{last.repository} &nbsp;|&nbsp; {last.branch} &nbsp;|&nbsp; '
            f'{last.created_at:%Y-%m-%d %H:%M}'
            f'</div>',
            unsafe_allow_html=True,
        )

        st.markdown("**Pila de despliegues activos (LIFO — el primero sera revertido):**")
        for i, j in enumerate(reversed(history)):
            top = " &larr; siguiente rollback" if i == 0 else ""
            st.markdown(
                f'<span style="font-size:13px;"><strong>#{i + 1}</strong> &nbsp; '
                f'Construccion #{j.id} &nbsp;|&nbsp; {j.repository} &nbsp;|&nbsp; '
                f'{j.branch} &nbsp;|&nbsp; {j.created_at:%Y-%m-%d %H:%M}{top}</span>',
                unsafe_allow_html=True,
            )

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Aplicar rollback al ultimo despliegue", use_container_width=True):
            msg = pipeline.rollback_last_deployment()
            if msg:
                st.session_state.flash_msg = msg
                st.session_state.flash_type = "info"
            navigate("status")
            st.rerun()


# ═══════════════════════════════════════════════════════════════════
# VISTA: REGISTRO DE ACTIVIDAD
# ═══════════════════════════════════════════════════════════════════
elif view == "logs":
    st.markdown('<div class="jk-title">Registro de Actividad Global</div>', unsafe_allow_html=True)

    global_logs = pipeline.global_logs

    if not global_logs:
        st.markdown(
            '<div class="jk-banner jk-info">No hay actividad registrada aun.</div>',
            unsafe_allow_html=True,
        )
    else:
        log_text = "\n".join(f"[{i + 1:03d}] {line}" for i, line in enumerate(global_logs))
        st.markdown(f'<div class="jk-console">{log_text}</div>', unsafe_allow_html=True)
        st.caption(f"Total de eventos registrados: {len(global_logs)}")
