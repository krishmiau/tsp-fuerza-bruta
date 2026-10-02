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
# ESTILOS CSS PERSONALIZADOS (TEMA CLARO EDITORIAL DE ALTO CONTRASTE)
# -------------------------------------------------------------
st.markdown(
    """
<style>
    /* Fondo Global Claro y Tipografía */
    .stApp {
        background-color: #f8fafc;
        color: #0f172a !important;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }

    /* Jerarquía de textos oscuros legibles */
    p, span, label, div, h1, h2, h3, h4 {
        color: #0f172a !important;
    }
    
    .terminal-kicker {
        font-family: 'Courier New', monospace;
        font-size: 13px;
        letter-spacing: 2.5px;
        color: #4f46e5 !important; /* Índigo */
        font-weight: 800;
        text-transform: uppercase;
        margin-bottom: 4px;
    }
    
    .main-title {
        font-size: 42px;
        font-weight: 800;
        letter-spacing: -0.5px;
        color: #0f172a !important;
        margin-top: 0px;
        margin-bottom: 12px;
    }
    .main-title span {
        color: #4f46e5 !important;
    }

    .desc-text {
        color: #334155 !important;
        font-size: 16px;
        line-height: 1.6;
        margin-bottom: 14px;
    }

    /* Insignias superiores claras */
    .stat-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 6px 14px;
        border-radius: 8px;
        font-size: 13px;
        font-weight: 700;
        font-family: 'Courier New', monospace;
    }
    .badge-mint {
        background: #ecfdf5;
        color: #047857 !important;
        border: 1px solid #a7f3d0;
    }
    .badge-lavender {
        background: #eef2ff;
        color: #4338ca !important;
        border: 1px solid #c7d2fe;
    }
    .badge-rose {
        background: #fff1f2;
        color: #be123c !important;
        border: 1px solid #fecdd3;
    }

    /* Métricas destacadas */
    div[data-testid="stMetricValue"] {
        color: #0f172a !important;
        font-family: 'Courier New', monospace !important;
        font-size: 32px !important;
        font-weight: 800 !important;
    }
    div[data-testid="stMetricLabel"] p {
        color: #64748b !important;
        font-size: 13px !important;
        font-weight: 700 !important;
        letter-spacing: 0.5px !important;
        text-transform: uppercase !important;
    }

    /* Caja de Cálculo Aritmético en fondo claro */
    .calc-box {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-left: 5px solid #059669;
        border-radius: 10px;
        padding: 16px 20px;
        font-family: 'Courier New', monospace;
        font-size: 15px;
        color: #0f172a;
        margin: 14px 0;
        line-height: 1.6;
        box-shadow: 0 4px 12px -2px rgba(15, 23, 42, 0.05);
    }

    /* Inputs y Sliders claros */
    div[data-testid="stNumberInput"] input {
        background-color: #ffffff !important;
        color: #0f172a !important;
        font-size: 16px !important;
        border: 1.5px solid #cbd5e1 !important;
        border-radius: 8px !important;
    }

    /* Botón interactivo */
    div.stButton > button {
        background: linear-gradient(135deg, #4f46e5 0%, #6366f1 100%) !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 800 !important;
        font-size: 15px !important;
        padding: 10px 18px !important;
        box-shadow: 0 4px 14px rgba(79, 70, 229, 0.25) !important;
        transition: all 0.2s ease !important;
    }
    div.stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 6px 20px rgba(79, 70, 229, 0.35) !important;
    }
    div.stButton > button p {
        color: #ffffff !important;
    }

    /* Botón de descarga CSV */
    div.stDownloadButton > button {
        border-radius: 8px !important;
        border: 1px solid #cbd5e1 !important;
        background-color: #ffffff !important;
        color: #1e293b !important;
        font-weight: 700 !important;
        font-size: 13px !important;
        padding: 6px 14px !important;
        transition: all 0.2s ease !important;
    }
    div.stDownloadButton > button:hover {
        border-color: #4f46e5 !important;
        color: #4f46e5 !important;
    }
    div.stDownloadButton > button p {
        color: #1e293b !important;
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
    <div style="font-size: 13px; color: #64748b; line-height: 1.6;">
        <b>Propiedad Combinatoria:</b><br/>
        Al fijar el nodo origen en <code>A</code>, el espacio muestral de trayectorias cerradas se define exactamente por <code>(n - 1)!</code> permutaciones.
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

  # Conexiones transversales
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
# EVALUACIÓN FACTORIAL DEL ESPACIO MUESTRAL
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
# CABECERA Y FÓRMULAS MATEMÁTICAS FORMALES
# -------------------------------------------------------------
c_head, c_badges = st.columns([2.5, 1.5])
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
      """
    <div class="desc-text">
        Optimización discreta sobre grafos ponderados <b>G = (V, E, W)</b>. Búsqueda exhaustiva del ciclo hamiltoniano que minimiza la distancia acumulada en el espacio muestral factorial.
    </div>
    """,
      unsafe_allow_html=True,
  )

with c_badges:
  st.write("")
  st.markdown(
      f"""
    <div style="display:flex; flex-direction:column; gap:10px; align-items:flex-end;">
        <span class="stat-badge badge-mint">Topología G = (V, E)</span>
        <span class="stat-badge badge-lavender">Espacio Muestral: {len(evaluaciones):,} rutas</span>
        <span class="stat-badge badge-rose">Ciclos Hamiltonianos: {len(rutas_validas)}</span>
    </div>
    """,
      unsafe_allow_html=True,
  )

st.latex(r"\min_{\pi} \quad C(\pi) = \sum_{i=0}^{n-1} w(v_i, v_{i+1})")

st.write("")

# Métricas grandes
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
# PESTAÑAS DE ANÁLISIS
# -------------------------------------------------------------
tab_sim, tab_matriz, tab_auditoria = st.tabs([
    "📐 Inspección y Evaluación de Ciclos",
    "🔢 Matriz de Costos / Adyacencia",
    "🛡️ Condición Estructural de Hamiltonicidad",
])

# -------------------------------------------------------------
# PESTAÑA 1: INSPECCIÓN MATEMÁTICA Y GRÁFICO
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
                    <span style="color:#059669; font-weight:800; font-size:16px;">★ TRAYECTORIA ÓPTIMA:</span><br/>
                    <b style="font-size:17px; color:#0f172a;">{mejor_evaluacion['ruta_str']}</b><br/><br/>
                    <span style="color:#64748b; font-size:13px;">Suma aritmética de distancias:</span><br/>
                    <span style="font-size:15px; color:#1e293b;">{mejor_evaluacion['desglose']} = <b style="color:#059669;">{mejor_costo} unidades</b></span>
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
                <div class="calc-box" style="border-left-color:#d97706;">
                    <span style="color:#d97706; font-weight:800; font-size:16px;">CICLO #{idx_ruta} EVALUADO:</span><br/>
                    <b style="font-size:17px; color:#0f172a;">{seleccionada['ruta_str']}</b><br/><br/>
                    <span style="color:#64748b; font-size:13px;">Suma aritmética:</span><br/>
                    <span style="font-size:15px; color:#1e293b;">{seleccionada['desglose']} = <b style="color:#d97706;">{seleccionada['costo']} unidades</b></span><br/>
                    <span style="color:#dc2626; font-size:12px; font-weight:bold;">(+{diferencia} unidades respecto al óptimo)</span>
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
            * Si algún tramo $(v_i, v_{i+1}) \notin E$, la trayectoria es discontinua y se descarta ($C = \infty$).
            * La solución corresponde al mínimo global: $\\arg\min_{\\pi} C(\\pi)$.
            """
      )

  # Representación Gráfica con NetworkX y Matplotlib (Tema Claro Nítido)
  with col_graf:
    G = nx.Graph()
    for nombre in nombres:
      G.add_node(nombre)
    for i in range(n):
      for j in range(i + 1, n):
        if matriz[i][j] is not None:
          G.add_edge(nombres[i], nombres[j], weight=matriz[i][j])

    pos = nx.spring_layout(G, seed=42, k=2.0 / (n**0.5), iterations=60)

    fig, ax = plt.subplots(figsize=(7.2, 5.4), dpi=140)
    fig.patch.set_facecolor("#ffffff")
    ax.set_facecolor("#ffffff")

    # 1. Aristas base tenues
    nx.draw_networkx_edges(
        G, pos, ax=ax, edge_color="#e2e8f0", width=1.6, alpha=0.9
    )

    # 2. Resaltar trayectoria activa
    if ruta_a_dibujar:
      color_ruta = (
          "#059669"
          if modo_vista == "⭐ Ciclo Hamiltoniano Óptimo (Mínimo)"
          else "#d97706"
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
          alpha=0.95,
      )

    # 3. Vértices con doble aro y alto contraste
    colores_nodos = ["#4f46e5" if i == 0 else "#ffffff" for i in range(n)]
    bordes_nodos = ["#3730a3" if i == 0 else "#64748b" for i in range(n)]
    textos_nodos = ["#ffffff" if i == 0 else "#0f172a" for i in range(n)]

    nx.draw_networkx_nodes(
        G,
        pos,
        ax=ax,
        node_color=colores_nodos,
        node_size=950,
        edgecolors=bordes_nodos,
        linewidths=2.4,
    )

    for idx, nombre in enumerate(nombres):
      ax.text(
          pos[nombre][0],
          pos[nombre][1],
          nombre,
          fontsize=12,
          fontweight="bold",
          color=textos_nodos[idx],
          ha="center",
          va="center",
      )

    # 4. Pesos de las aristas en cápsulas claras
    edge_labels = nx.get_edge_attributes(G, "weight")
    nx.draw_networkx_edge_labels(
        G,
        pos,
        edge_labels=edge_labels,
        ax=ax,
        font_size=9,
        font_color="#334155",
        font_family="monospace",
        font_weight="bold",
        bbox=dict(
            boxstyle="round,pad=0.25",
            facecolor="#ffffff",
            edgecolor="#cbd5e1",
            linewidth=1.0,
            alpha=0.98,
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
      """
    <div style="font-size:15px; color:#334155; margin-bottom:14px;">
        Matriz de adyacencia ponderada simétrica correspondiente al grafo <b>G = (V, E, W)</b>. El símbolo '—' denota ausencia de conexión directa.
    </div>
    """,
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
      """
    <div style="font-size:15px; color:#334155; margin-bottom:16px;">
        En teoría de grafos, una condición necesaria para la existencia de un ciclo hamiltoniano es que cada vértice satisfaga la condición de grado <b>deg(v) ≥ 2</b> (permitiendo una arista de entrada y una de salida sin repetir vértices).
    </div>
    """,
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
