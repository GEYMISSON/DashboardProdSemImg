import streamlit as st


def aplicar_estilo():
    st.markdown("""
    <style>
    .main { background-color: #f5f7fa; }
    .block-container { padding-top: 1.4rem; padding-bottom: 2rem; }
    .titulo { font-size: 32px; font-weight: 750; color: #111827; margin-top: 18px; margin-bottom: 4px; padding-top: 8px; line-height: 1.25; }
    .subtitulo { font-size: 15px; color: #6b7280; margin-bottom: 18px; }
    .card { background:#fff; border:1px solid #e5e7eb; border-radius:12px; padding:16px; min-height:105px; box-shadow:0 2px 8px rgba(0,0,0,.05); }
    .card-title { color:#6b7280; font-size:12px; font-weight:700; text-transform:uppercase; }
    .card-value { color:#111827; font-size:27px; font-weight:750; margin-top:7px; }
    .blue { border-left:5px solid #2563eb; } .green { border-left:5px solid #16a34a; } .red { border-left:5px solid #dc2626; } .orange { border-left:5px solid #f59e0b; }
    .info-box { background:#fff; border:1px solid #e5e7eb; border-radius:10px; padding:12px 16px; margin-bottom:12px; }
    .badge { display:inline-block; padding:4px 9px; border-radius:999px; font-size:12px; font-weight:800; }
    .badge-green { background:#dcfce7; color:#166534; } .badge-yellow { background:#fef3c7; color:#92400e; } .badge-red { background:#fee2e2; color:#991b1b; }
    </style>
    """, unsafe_allow_html=True)


def metric_card(col, titulo, valor, classe="blue", percentual=False):
    texto = f"{valor:.2f}%" if percentual else f"{int(valor):,}".replace(",", ".")
    with col:
        st.markdown(f'<div class="card {classe}"><div class="card-title">{titulo}</div><div class="card-value">{texto}</div></div>', unsafe_allow_html=True)


def status_badge(status):
    cls = {"EXCELENTE":"badge-green", "ATENÇÃO":"badge-yellow", "CRÍTICO":"badge-red"}.get(status, "badge-yellow")
    return f'<span class="badge {cls}">{status}</span>'
