import itertools
import math
import random
import time
import matplotlib.pyplot as plt
import networkx as nx
import pandas as pd
import streamlit as st

# Configuración inicial de la página
st.set_page_config(
    page_title="TSP • Matemática Computacional",
    page_icon="📐",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -------------------------------------------------------------
# ESTILOS CSS PERSONALIZADOS (DARK SLATE INTERMEDIO / PASTEL)
# -------------------------------------------------------------
st.markdown(
    """
<style>
    /* Fondo Global Slate Intermedio */
    .stApp {
        background-color: #172033;
        color: #f1f5f9 !important;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }

    /* Tipografía y jerarquía */
    h1, h2, h3, h4, p, span, label {
        color: #f1f5f9 !important;
    }
    
    .terminal-kicker {
        font-family: 'Courier New', monospace;
        font-size: 11px;
        letter-spacing: 2px;
        color: #a7f3d0 !important; /* Menta pastel */
        font-weight: 700;
        text-transform: uppercase;
    }
    
    .main-title {
        font-size: 32px;
        font-weight: 800;
        letter-spacing: -0.5px;
        color: #ffffff !important;
        margin-top: 4px;
        margin-bottom: 8px;
    }
    .main-title span {
        color: #c7d2fe !important; /* Lavanda pastel */
    }

    .desc-text {
        color: #cbd5e1 !important;
        font-size: 14px;
        line-height: 1.5;
    }

    /* Insignias matemáticas superiores */
    .stat-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 5px 12px;
        border-radius: 8px;
        font-size: 12px;
        font-weight: 600;
        font-family: 'Courier New', monospace;
    }
    .badge-mint {
        background: rgba(167, 243, 208, 0.16);
        color: #a7f3d0 !important;
        border: 1px solid rgba(167, 243, 208, 0.35);
    }
    .badge-lavender {
        background: rgba(199, 210, 254, 0.16);
        color: #c7d2fe !important;
        border: 1px solid rgba(199, 210, 254, 0.35);
    }
    .badge-rose {
        background: rgba(254, 205, 211, 0.16);
        color: #fecdd3 !important;
        border: 1px solid rgba(254, 205, 211, 0.35);
    }

    /* Métricas */
    div[data-testid="stMetricValue"] {
        color: #ffffff !important;
        font-family: 'Courier New', monospace !important;
        font-size: 26px !important;
        font-weight: 700 !important;
    }
    div[data-testid="stMetricLabel"] p {
        color: #94a3b8 !important;
        font-size: 11px !important;
        letter-spacing: 0.5px !important;
        text-transform: uppercase !important;
    }

    /* Inputs, Sliders y Barra Lateral */
    section[data-testid="stSidebar"] {
        background-color: #121a2b !important;
    }
    div[data-testid="stNumberInput"] input {
        background-color: #243047 !important;
        color: #ffffff !important;
        border: 1px solid #3b4d6e !important;
        border-radius: 8px !important;
        font-family: 'Courier New', monospace !important;
    }
    div[data-testid="stNumberInput"] button {
        background-color: #3b4d6e !important;
        color: #ffffff !important;
    }

    /* Botón de Generación */
    div.stButton > button {
        background: linear-gradient(135deg, #4f46e5 0%, #6366f1 100%) !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 700 !important;
        padding: 8px 16px !important;
        box-shadow: 0 4px 14px rgba(79, 70, 229, 0.3) !important;
        transition: all 0.2s ease !important;
    }
    div.stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 6px 18px rgba(79, 70, 229, 0.4) !important;
    }

    /* Caja de Cálculo Aritmético */
    .calc-box {
        background: #1e293b;
        border: 1px solid #334155;
        border-left: 4px solid #a7f3d0;
        border-radius: 8px;
        padding: 14px 18px;
        font-family: 'Courier New', monospace;
        font-size: 13.5px;
        color: #f1f5f9;
        margin: 10px 0;
    }

    /* Ocultar barra flotante de tabla */
    [data-testid="stElementToolbar"] {
        display: none !important;
    }
</style>
""",
    unsafe_allow_html=True,
)

# -------------------------------------------------------------
# SIDEBAR: PARÁMETROS DEL GRAFO
# -------------------------------------------------------------
with st.sidebar:
  st.markdown(
      '<div class="terminal-kicker">MODELO TOPOLÓGICO G = (V, E)</div>',
      unsafe_allow_html=True,
  )
  st.markdown("### Parámetros del Grafo")

  n = st.slider(
      "Cardinalidad de Vértices |V|",
      min_value=5,
      max_value=9,
      value=6,
      help="Número de nodos del grafo no dirigido.",
  )
  densidad = st.slider(
      "Densidad de Aristas (%)",
      min_value=30,
      max_value=100,
      value=60,
      step=5,
      help="Porcentaje de conectividad entre los pares de vértices.",
  )

  st.write("")
  generar = st.button("🎲 Generar Nueva Topología", use_container_width=True)

  st.markdown("---")
  st.markdown(
      """
    <div style="font-size: 12px; color: #94a3b8; line-height: 1.5;">
        <b>Propiedad Combinatoria:</b><br/>
        Al fijar el nodo origen en <code>A</code> (índice 0), el espacio muestral de trayectorias cerradas se define exactamente por <code>(n - 1)!</code> permutaciones.
    </div>
    """,
      unsafe_allow_html=True,
  )

# -------------------------------------------------------------
# MODELADO MATRICIAL Y GENERACIÓN DEL GRAFO
# -------------------------------------------------------------
if "matriz" not in st.session_state or generar or len(st.session_state.matriz) != n:
  random.seed(int(time.time()) if generar else 42)
  matriz = [[None for _ in range(n)] for _ in range(n)]

  # Ciclo hamiltoniano base garantizado con permutación
  orden_base = list(range(n))
  random.shuffle(orden_base)
  for i in range(n):
    u = orden_base[i]
    v = orden_base[(i + 1) % n]
    peso = random.randint(12, 38)
    matriz[u][v] = peso
    matriz[v][u] = peso

  # Conexiones transversales adicionales
  for i in range(n):
    for j in range(i + 1, n):
      if matriz[i][j] is None and random.random() < (densidad / 100.0):
        peso = random.randint(15, 65)
        matriz[i][j] = peso
        matriz[j][i] = peso

  st.session_state.matriz = matriz

matriz = st.session_state.matriz
nombres = [chr(65 + i) for i in range(n)]

# -------------------------------------------------------------
# ANÁLISIS EXHAUSTIVO DEL ESPACIO MUESTRAL
# -------------------------------------------------------------
evaluaciones = []
mejor_costo = float("inf")
mejor_evaluacion = None

for perm in itertools.permutations(range(1, n)):
  ruta = [0] + list(perm) + [0]
  costo = 0
  valida = True
  desglose_terminos = []

  for k in range(n):
    u, v = ruta[k], ruta[k + 1]
    w = matriz[u][v]
    if w is None:
      valida = False
      desglose_terminos.append(f"w({nombres[u]},{nombres[v]})=—")
      break
    costo += w
    desglose_terminos.append(f"{w}")

  eval_item = {
      "ruta_indices": ruta,
      "ruta_str": " → ".join([nombres[idx] for idx in ruta]),
      "costo": costo if valida else None,
      "valida": valida,
      "desglose": (
          " + ".join(desglose_terminos)
          if valida
          else "Ruta no conexa (aristas faltantes)"
      ),
  }
  evaluaciones.append(eval_item)

  if valida and costo < mejor_costo:
    mejor_costo = costo
    mejor_evaluacion = eval_item

rutas_validas = [r for r in evaluaciones if r["valida"]]
rutas_validas_ordenadas = sorted(rutas_validas, key=lambda x: x["costo"])

# -------------------------------------------------------------
# CABECERA: ENFOQUE EN MATEMÁTICA COMPUTACIONAL
# -------------------------------------------------------------
c_head, c_badges = st.columns([2.6, 1.4])
with c_head:
  st.markdown(
      '<div class="terminal-kicker">MATEMÁTICA COMPUTACIONAL • TEORÍA DE'
      " GRAFOS</div>",
      unsafe_allow_html=True,
  )
  st.markdown(
      '<div class="main-title">Problema del Agente'
      " <span>Viajero</span></div>",
      unsafe_allow_html=True,
  )
  st.markdown(
      '<div class="desc-text">'
      "Optimización discreta sobre grafos ponderados <b>G = (V, E, W)</b>."
      " Búsqueda exhaustiva del ciclo hamiltoniano que minimiza la distancia"
      " acumulada en el espacio muestral factorial."
      "</div>",
      unsafe_allow_html=True,
  )

with c_badges:
  st.write("")
  st.markdown(
      f"""
    <div style="display:flex; flex-direction:column; gap:8px; align-items:flex-end;">
        <span class="stat-badge badge-mint">Topología G = (V, E)</span>
        <span class="stat-badge badge-lavender">Espacio Muestral: {len(evaluaciones):,} rutas</span>
        <span class="stat-badge badge-rose">Ciclos Hamiltonianos: {len(rutas_validas)}</span>
    </div>
    """,
      unsafe_allow_html=True,
  )

st.latex(r"\min_{\pi} \quad C(\pi) = \sum_{i=0}^{n-1} w(v_i, v_{i+1})")

st.write("")

# Métricas
kpi1, kpi2, kpi3, kpi4 = st.columns(4)
with kpi1:
  st.metric("Vértices |V|", f"{n} Nodos")
with kpi2:
  aristas_totales = sum(
      1 for i in range(n) for j in range(i + 1, n) if matriz[i][j] is not None
  )
  st.metric("Aristas Existentes |E|", f"{aristas_totales}")
with kpi3:
  st.metric(
      "Ciclos Factibles",
      f"{len(rutas_validas)} / {len(evaluaciones)}",
  )
with kpi4:
  st.metric(
      "Costo Mínimo Global",
      f"{mejor_costo}" if mejor_costo != float("inf") else "Infactible",
  )

st.write("")

# -------------------------------------------------------------
# PESTAÑAS ANALÍTICAS
# -------------------------------------------------------------
tab_sim, tab_matriz, tab_auditoria = st.tabs([
    "📐 Inspección y Evaluación de Ciclos",
    "🔢 Matriz de Costos / Adyacencia",
    "🛡️ Condición Estructural de Hamiltonicidad",
])

# -------------------------------------------------------------
# PESTAÑA 1: INSPECCIÓN MATEMÁTICA Y GRÁFICA
# -------------------------------------------------------------
with tab_sim:
  col_graf, col_interac = st.columns([1.5, 1])

  with col_interac:
    st.markdown("#### Selección de Trayectoria")
    modo_vista = st.radio(
        "Modo de análisis en el grafo:",
        [
            "⭐ Ciclo Hamiltoniano Óptimo (Mínimo)",
            "🔍 Inspeccionar otra Permutación del Espacio Muestral",
            "🌐 Topología Base Completa",
        ],
        index=0,
    )

    ruta_a_dibujar = None

    if modo_vista == "⭐ Ciclo Hamiltoniano Óptimo (Mínimo)":
      if mejor_evaluacion:
        ruta_a_dibujar = mejor_evaluacion["ruta_indices"]
        st.markdown(
            f"""
                <div class="calc-box">
                    <span style="color:#a7f3d0; font-weight:700;">★ TRAYECTORIA ÓPTIMA:</span><br/>
                    <b>{mejor_evaluacion['ruta_str']}</b><br/><br/>
                    <span style="color:#94a3b8;">Suma analítica de distancias:</span><br/>
                    {mejor_evaluacion['desglose']} = <b style="color:#a7f3d0;">{mejor_costo} unidades</b>
                </div>
                """,
            unsafe_allow_html=True,
        )

    elif modo_vista == "🔍 Inspeccionar otra Permutación del Espacio Muestral":
      if rutas_validas_ordenadas:
        idx_ruta = st.slider(
            "Ciclo ordenado por costo (1 = Menor costo, N = Mayor costo):",
            min_value=1,
            max_value=len(rutas_validas_ordenadas),
            value=min(2, len(rutas_validas_ordenadas)),
        )
        seleccionada = rutas_validas_ordenadas[idx_ruta - 1]
        ruta_a_dibujar = seleccionada["ruta_indices"]

        diferencia = seleccionada["costo"] - mejor_costo
        st.markdown(
            f"""
                <div class="calc-box" style="border-left-color:#fde68a;">
                    <span style="color:#fde68a; font-weight:700;">CICLO #{idx_ruta} EVALUADO:</span><br/>
                    <b>{seleccionada['ruta_str']}</b><br/><br/>
                    <span style="color:#94a3b8;">Suma analítica:</span><br/>
                    {seleccionada['desglose']} = <b style="color:#fde68a;">{seleccionada['costo']} unidades</b><br/>
                    <span style="color:#f87171; font-size:12px;">(+{diferencia} unidades respecto al óptimo)</span>
                </div>
                """,
            unsafe_allow_html=True,
        )
      else:
        st.warning(
            "El grafo actual no posee ciclos hamiltonianos con las conexiones"
            " dadas."
        )

    with st.expander("ℹ️ Detalle de la Función de Costo"):
      st.markdown(
          """
            Para una permutación $\\pi = (v_0, v_1, \\dots, v_{n-1}, v_0)$ con origen fijado en $v_0 = A$:
            """
      )
      st.latex(r"C(\pi) = \sum_{i=0}^{n-1} w(v_i, v_{i+1})")
      st.markdown(
          """
            * Si algún tramo $(v_i, v_{i+1}) \\notin E$, la trayectoria es discontinua y se descarta ($C = \\infty$).
            * La solución corresponde al mínimo global: $\\arg\\min_{\\pi} C(\\pi)$.
            """
      )

  # Representación Gráfica: Polígono Estructurado Asimétrico (Sin superposiciones)
  with col_graf:
    G = nx.Graph()
    for nombre in nombres:
      G.add_node(nombre)
    for i in range(n):
      for j in range(i + 1, n):
        if matriz[i][j] is not None:
          G.add_edge(nombres[i], nombres[j], weight=matriz[i][j])

    # Coordenadas poligonales con ligera variación de radio (polígono orgánico/asimétrico)
    pos = {}
    for i in range(n):
      angulo = (2 * math.pi * i / n) + (math.pi / 2)  # Nodo A en la cima
      # Modulación suave de radio entre 0.92 y 1.05 para que no sea un círculo exacto
      radio = 1.0 + 0.08 * math.sin(i * 1.5)
      pos[nombres[i]] = (radio * math.cos(angulo), radio * math.sin(angulo))

    fig, ax = plt.subplots(figsize=(6.8, 5.2), dpi=140)
    fig.patch.set_facecolor("#1e293b")
    ax.set_facecolor("#1e293b")

    # Aristas del grafo base
    nx.draw_networkx_edges(
        G, pos, ax=ax, edge_color="#475569", width=1.5, alpha=0.75
    )

    # Resaltar trayectoria activa
    if ruta_a_dibujar:
      color_ruta = (
          "#a7f3d0"
          if modo_vista == "⭐ Ciclo Hamiltoniano Óptimo (Mínimo)"
          else "#fde68a"
      )
      aristas_resaltadas = [
          (nombres[ruta_a_dibujar[i]], nombres[ruta_a_dibujar[i + 1]])
          for i in range(n)
      ]
      nx.draw_networkx_edges(
          G,
          pos,
          edgelist=aristas_resaltadas,
          ax=ax,
          edge_color=color_ruta,
          width=3.8,
          alpha=0.98,
      )

    # Vértices (Nodo A menta pastel, resto lavanda suave)
    colores_nodos = ["#a7f3d0" if i == 0 else "#2d3b55" for i in range(n)]
    bordes_nodos = ["#059669" if i == 0 else "#c7d2fe" for i in range(n)]
    textos_nodos = ["#064e3b" if i == 0 else "#f8fafc" for i in range(n)]

    nx.draw_networkx_nodes(
        G,
        pos,
        ax=ax,
        node_color=colores_nodos,
        node_size=90
