import itertools
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
# ESTILOS CSS PERSONALIZADOS (DARK MODE PASTEL Y ALTO CONTRASTE)
# -------------------------------------------------------------
st.markdown(
    """
<style>
    /* Fondo Global Dark Slate */
    .stApp {
        background-color: #0b0f19;
        color: #e2e8f0 !important;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }

    /* Tipografía y colores pastel */
    h1, h2, h3, h4, p, span, label {
        color: #e2e8f0 !important;
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
        color: #f8fafc !important;
        margin-top: 4px;
        margin-bottom: 8px;
    }
    .main-title span {
        color: #c7d2fe !important; /* Lavanda pastel */
    }

    .desc-text {
        color: #94a3b8 !important;
        font-size: 14px;
        line-height: 1.5;
    }

    /* Insignias matemáticas superiores */
    .stat-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 4px 10px;
        border-radius: 8px;
        font-size: 12px;
        font-weight: 600;
        font-family: 'Courier New', monospace;
    }
    .badge-mint {
        background: rgba(167, 243, 208, 0.12);
        color: #a7f3d0 !important;
        border: 1px solid rgba(167, 243, 208, 0.25);
    }
    .badge-lavender {
        background: rgba(199, 210, 254, 0.12);
        color: #c7d2fe !important;
        border: 1px solid rgba(199, 210, 254, 0.25);
    }
    .badge-rose {
        background: rgba(254, 205, 211, 0.12);
        color: #fecdd3 !important;
        border: 1px solid rgba(254, 205, 211, 0.25);
    }

    /* Métricas */
    div[data-testid="stMetricValue"] {
        color: #f8fafc !important;
        font-family: 'Courier New', monospace !important;
        font-size: 24px !important;
        font-weight: 700 !important;
    }
    div[data-testid="stMetricLabel"] p {
        color: #94a3b8 !important;
        font-size: 11px !important;
        letter-spacing: 0.5px !important;
        text-transform: uppercase !important;
    }

    /* Inputs y Sliders */
    div[data-testid="stNumberInput"] input {
        background-color: #1e293b !important;
        color: #f8fafc !important;
        border: 1px solid #334155 !important;
        border-radius: 8px !important;
        font-family: 'Courier New', monospace !important;
    }
    div[data-testid="stNumberInput"] button {
        background-color: #334155 !important;
        color: #f8fafc !important;
    }

    /* Botón de Generación */
    div.stButton > button {
        background: linear-gradient(135deg, #4f46e5 0%, #6366f1 100%) !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 700 !important;
        padding: 8px 16px !important;
        box-shadow: 0 4px 14px rgba(79, 70, 229, 0.35) !important;
        transition: all 0.2s ease !important;
    }
    div.stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 6px 18px rgba(79, 70, 229, 0.45) !important;
    }

    /* Caja de Cálculo Aritmético */
    .calc-box {
        background: #1e293b;
        border-left: 4px solid #a7f3d0;
        border-radius: 6px;
        padding: 12px 16px;
        font-family: 'Courier New', monospace;
        font-size: 13px;
        color: #e2e8f0;
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

  # Ciclo hamiltoniano base garantizado con permutación espacial
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
      "Optimización discreta sobre grafos ponderados $G = (V, E, W)$. Búsqueda"
      " del ciclo hamiltoniano que minimiza la función objetivo $C(\\pi) = \\sum"
      " w(v_i, v_{i+1})$ en el espacio muestral factorial."
      "</div>",
      unsafe_allow_html=True,
  )

with c_badges:
  st.write("")
  st.markdown(
      f"""
    <div style="display:flex; flex-direction:column; gap:8px; align-items:flex-end;">
        <span class="stat-badge badge-mint">Grafo Ponderado G = (V, E)</span>
        <span class="stat-badge badge-lavender">Espacio Muestral: {len(evaluaciones):,} rutas</span>
        <span class="stat-badge badge-rose">Ciclos Hamiltonianos: {len(rutas_validas)}</span>
    </div>
    """,
      unsafe_allow_html=True,
  )

st.write("")

# Métricas topológicas y analíticas
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
                    <span style="color:#a7f3d0; font-weight:700;">Trayectoria Óptima:</span><br/>
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
                <div class="calc-box">
                    <span style="color:#fde68a; font-weight:700;">Ciclo Hamiltoniano #{idx_ruta}:</span><br/>
                    <b>{seleccionada['ruta_str']}</b><br/><br/>
                    <span style="color:#94a3b8;">Suma analítica:</span><br/>
                    {seleccionada['desglose']} = <b style="color:#fde68a;">{seleccionada['costo']} unidades</b><br/>
                    <span style="color:#f87171; font-size:11px;">(Diferencia con el óptimo: +{diferencia} unidades)</span>
                </div>
                """,
            unsafe_allow_html=True,
        )
      else:
        st.warning(
            "El grafo actual no posee ciclos hamiltonianos con las conexiones"
            " dadas."
        )

    with st.expander("ℹ️ Formulación Matemática del Costo"):
      st.markdown(
          """
            Para una permutación $\\pi = (v_0, v_1, \\dots, v_{n-1}, v_0)$ con $v_0 = A$:
            
            $$C(\\pi) = \\sum_{i=0}^{n-1} w(v_i, v_{i+1})$$
            
            * Si algún tramo $(v_i, v_{i+1}) \\notin E$, la trayectoria es discontinua y se descarta del conjunto de soluciones válidas.
            * La solución corresponde a $\\arg\\min_{\\pi} C(\\pi)$.
            """
      )

  # Representación Gráfica con NetworkX y Matplotlib
  with col_graf:
    G = nx.Graph()
    for nombre in nombres:
      G.add_node(nombre)
    for i in range(n):
      for j in range(i + 1, n):
        if matriz[i][j] is not None:
          G.add_edge(nombres[i], nombres[j], weight=matriz[i][j])

    pos = nx.spring_layout(G, seed=42, k=2.0 / (n**0.5), iterations=60)

    fig, ax = plt.subplots(figsize=(6.8, 5.2), dpi=140)
    fig.patch.set_facecolor("#111827")
    ax.set_facecolor("#111827")

    # Aristas del grafo
    nx.draw_networkx_edges(
        G, pos, ax=ax, edge_color="#334155", width=1.5, alpha=0.7
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
          width=3.6,
          alpha=0.95,
      )

    # Vértices (Nodo A distinguido)
    colores_nodos = ["#a7f3d0" if i == 0 else "#1e293b" for i in range(n)]
    bordes_nodos = ["#059669" if i == 0 else "#c7d2fe" for i in range(n)]
    textos_nodos = ["#064e3b" if i == 0 else "#f8fafc" for i in range(n)]

    nx.draw_networkx_nodes(
        G,
        pos,
        ax=ax,
        node_color=colores_nodos,
        node_size=880,
        edgecolors=bordes_nodos,
        linewidths=2.2,
    )

    for idx, nombre in enumerate(nombres):
      ax.text(
          pos[nombre][0],
          pos[nombre][1],
          nombre,
          fontsize=11,
          fontweight="bold",
          color=textos_nodos[idx],
          ha="center",
          va="center",
      )

    # Pesos de las aristas
    edge_labels = nx.get_edge_attributes(G, "weight")
    nx.draw_networkx_edge_labels(
        G,
        pos,
        edge_labels=edge_labels,
        ax=ax,
        font_size=7.5,
        font_color="#cbd5e1",
        font_family="monospace",
        bbox=dict(
            boxstyle="round,pad=0.22",
            facecolor="#0b0f19",
            edgecolor="#334155",
            linewidth=0.8,
            alpha=0.92,
        ),
    )

    ax.axis("off")
    plt.tight_layout()
    st.pyplot(fig)

# -------------------------------------------------------------
# PESTAÑA 2: MATRIZ DE COSTOS
# -------------------------------------------------------------
with tab_matriz:
  st.markdown(
      '<div style="font-size:13px; color:#94a3b8; margin-bottom:12px;">Matriz'
      " de adyacencia ponderada simétrica correspondiente al grafo $G = (V, E,"
      " W)$. El símbolo '—' denota ausencia de arista directa ($w = \\infty$)."
      "</div>",
      unsafe_allow_html=True,
  )

  df_matriz = pd.DataFrame(
      [
          [val if val is not None else "—" for val in fila]
          for fila in matriz
      ],
      index=nombres,
      columns=nombres,
  )
  st.dataframe(df_matriz, use_container_width=True)

  csv = df_matriz.to_csv().encode("utf-8")
  st.download_button(
      label="📥 Exportar Matriz a CSV",
      data=csv,
      file_name="matriz_adyacencia_ponderada.csv",
      mime="text/csv",
  )

# -------------------------------------------------------------
# PESTAÑA 3: AUDITORÍA DE HAMILTONICIDAD
# -------------------------------------------------------------
with tab_auditoria:
  st.markdown("#### Condición Necesaria de Grado Mínimo")
  st.markdown(
      '<div style="font-size:13px; color:#94a3b8; margin-bottom:14px;">En'
      " teoría de grafos, una condición fundamental para que un ciclo"
      " hamiltoniano exista es que cada vértice posea al menos dos aristas"
      " incidentes: $deg(v) \\ge 2$ (una para entrar y otra para salir sin"
      " repetir vértices).</div>",
      unsafe_allow_html=True,
  )

  grados_data = []
  for i in range(n):
    g = sum(1 for j in range(n) if matriz[i][j] is not None)
    cumple = g >= 2
    grados_data.append({
        "Vértice": nombres[i],
        "Grado deg(v)": g,
        "Condición deg(v) ≥ 2": (
            "✅ Satisfecho" if cumple else "❌ No cumple (deg < 2)"
        ),
    })

  st.table(pd.DataFrame(grados_data))
