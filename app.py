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
    page_title="TSP • Neutral Elegance",
    page_icon="⚜️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -------------------------------------------------------------
# PALETA NEUTRAL ELEGANCE (APLICADA A TODA LA PÁGINA)
# #FFDBBB | #CCBEB1 | #997E67 | #664930
# -------------------------------------------------------------
st.markdown(
    """
<style>
    /* 1. Fondo Global y Tipografía Base */
    .stApp {
        background-color: #FFDBBB !important; /* Melocotón/Crema claro */
        color: #664930 !important;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }

    /* 2. Textos en General */
    p, span, label, div, h1, h2, h3, h4 {
        color: #664930 !important; /* Marrón profundo */
    }

    .editorial-kicker {
        font-family: 'Courier New', monospace;
        font-size: 11px;
        letter-spacing: 2px;
        color: #997E67 !important; /* Marrón medio */
        font-weight: 700;
        text-transform: uppercase;
        margin-bottom: 2px;
    }

    .main-title {
        font-family: 'Georgia', serif;
        font-size: 34px;
        font-weight: 800;
        letter-spacing: -0.5px;
        color: #664930 !important;
        margin-top: 4px;
        margin-bottom: 8px;
    }
    .main-title span {
        color: #997E67 !important;
    }

    .desc-text {
        color: #664930 !important;
        font-size: 14px;
        line-height: 1.5;
        opacity: 0.9;
    }

    /* 3. Insignias superiores */
    .stat-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 5px 12px;
        border-radius: 6px;
        font-size: 12px;
        font-weight: 700;
        font-family: 'Courier New', monospace;
    }
    .badge-primary {
        background: #CCBEB1;
        color: #664930 !important;
        border: 1px solid #997E67;
    }
    .badge-accent {
        background: #997E67;
        color: #FFDBBB !important;
        border: 1px solid #664930;
    }

    /* 4. Métricas / KPIs */
    div[data-testid="stMetricValue"] {
        color: #664930 !important;
        font-family: 'Courier New', monospace !important;
        font-size: 26px !important;
        font-weight: 800 !important;
    }
    div[data-testid="stMetricLabel"] p {
        color: #997E67 !important;
        font-size: 11px !important;
        letter-spacing: 0.5px !important;
        text-transform: uppercase !important;
        font-weight: 700 !important;
    }

    /* 5. Barra Lateral (Sidebar) */
    section[data-testid="stSidebar"] {
        background-color: #CCBEB1 !important; /* Gris cálido */
        border-right: 1px solid #997E67 !important;
    }
    section[data-testid="stSidebar"] * {
        color: #664930 !important;
    }

    /* Inputs y Sliders */
    div[data-testid="stNumberInput"] input {
        background-color: #FFDBBB !important;
        color: #664930 !important;
        border: 1px solid #997E67 !important;
        border-radius: 6px !important;
        font-weight: 700 !important;
    }
    div[data-testid="stNumberInput"] button {
        background-color: #997E67 !important;
        color: #FFDBBB !important;
    }

    /* 6. Botones (Marrón profundo y detalles crema) */
    div.stButton > button {
        background-color: #664930 !important;
        color: #FFDBBB !important;
        border: 1px solid #664930 !important;
        border-radius: 6px !important;
        font-weight: 700 !important;
        padding: 8px 16px !important;
        box-shadow: 0 2px 6px rgba(102, 73, 48, 0.2) !important;
        transition: all 0.2s ease !important;
    }
    div.stButton > button:hover {
        background-color: #997E67 !important;
        color: #FFDBBB !important;
        border-color: #997E67 !important;
        transform: translateY(-1px);
    }
    div.stButton > button p {
        color: #FFDBBB !important;
    }

    /* Botón de descarga CSV */
    div.stDownloadButton > button {
        background-color: #997E67 !important;
        color: #FFDBBB !important;
        border: 1px solid #664930 !important;
        border-radius: 6px !important;
        font-weight: 700 !important;
    }
    div.stDownloadButton > button:hover {
        background-color: #664930 !important;
    }
    div.stDownloadButton > button p {
        color: #FFDBBB !important;
    }

    /* 7. Caja de Desglose de Cálculo */
    .calc-box {
        background: #CCBEB1;
        border: 1px solid #997E67;
        border-left: 5px solid #664930;
        border-radius: 8px;
        padding: 14px 18px;
        font-family: 'Courier New', monospace;
        font-size: 13.5px;
        color: #664930;
        margin: 10px 0;
        box-shadow: 0 2px 5px rgba(102, 73, 48, 0.08);
    }

    /* Pestañas (Tabs) */
    button[data-baseweb="tab"] {
        color: #997E67 !important;
        font-weight: 700 !important;
    }
    button[data-baseweb="tab"][aria-selected="true"] {
        color: #664930 !important;
        border-bottom-color: #664930 !important;
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
      '<div class="editorial-kicker">MODELO TOPOLÓGICO G = (V, E)</div>',
      unsafe_allow_html=True,
  )
  st.markdown("### Configuración")

  n = st.slider(
      "Ciudades / Vértices (n)",
      min_value=5,
      max_value=9,
      value=7,
      help="Número de vértices del grafo ponderado.",
  )
  densidad = st.slider(
      "Densidad de Caminos (%)",
      min_value=30,
      max_value=100,
      value=60,
      step=5,
      help="Porcentaje de conexiones entre las ciudades.",
  )

  st.write("")
  generar = st.button("⚜️ Construir / Regenerar", use_container_width=True)

  st.markdown("---")
  st.markdown(
      """
    <div style="font-size: 12px; color: #664930; line-height: 1.5;">
        <b>Propiedad Combinatoria:</b><br/>
        Fijando el vértice origen en <code>A</code>, el espacio factorial examinado es exactamente de <code>(n - 1)!</code> permutaciones.
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

  # Ciclo base garantizado con permutación
  orden_base = list(range(n))
  random.shuffle(orden_base)
  for i in range(n):
    u = orden_base[i]
    v = orden_base[(i + 1) % n]
    peso = random.randint(7, 35)
    matriz[u][v] = peso
    matriz[v][u] = peso

  # Conexiones adicionales según densidad
  for i in range(n):
    for j in range(i + 1, n):
      if matriz[i][j] is None and random.random() < (densidad / 100.0):
        peso = random.randint(15, 60)
        matriz[i][j] = peso
        matriz[j][i] = peso

  st.session_state.matriz = matriz

matriz = st.session_state.matriz
nombres = [chr(65 + i) for i in range(n)]

# -------------------------------------------------------------
# ANÁLISIS DEL ESPACIO MUESTRAL
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
          else "Ruta no conexa (sin arista)"
      ),
  }
  evaluaciones.append(eval_item)

  if valida and costo < mejor_costo:
    mejor_costo = costo
    mejor_evaluacion = eval_item

rutas_validas = [r for r in evaluaciones if r["valida"]]
rutas_validas_ordenadas = sorted(rutas_validas, key=lambda x: x["costo"])

# -------------------------------------------------------------
# CABECERA MATEMÁTICA
# -------------------------------------------------------------
c_head, c_badges = st.columns([2.6, 1.4])
with c_head:
  st.markdown(
      '<div class="editorial-kicker">MATEMÁTICA COMPUTACIONAL • TEORÍA DE'
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
      " total acumulada en el espacio factorial."
      "</div>",
      unsafe_allow_html=True,
  )

with c_badges:
  st.write("")
  st.markdown(
      f"""
    <div style="display:flex; flex-direction:column; gap:8px; align-items:flex-end;">
        <span class="stat-badge badge-primary">Grafo G = (V, E)</span>
        <span class="stat-badge badge-accent">Espacio: {len(evaluaciones):,} rutas</span>
        <span class="stat-badge badge-primary">Ciclos Factibles: {len(rutas_validas)}</span>
    </div>
    """,
      unsafe_allow_html=True,
  )

st.latex(r"\min_{\pi} \quad C(\pi) = \sum_{i=0}^{n-1} w(v_i, v_{i+1})")
st.write("")

# KPIs
kpi1, kpi2, kpi3, kpi4 = st.columns(4)
with kpi1:
  st.metric("Ciudades |V|", f"{n} Nodos")
with kpi2:
  aristas_totales = sum(
      1 for i in range(n) for j in range(i + 1, n) if matriz[i][j] is not None
  )
  st.metric("Caminos Activos |E|", f"{aristas_totales}")
with kpi3:
  st.metric(
      "Ciclos Factibles",
      f"{len(rutas_validas)} / {len(evaluaciones)}",
  )
with kpi4:
  st.metric(
      "Distancia Mínima",
      f"{mejor_costo}" if mejor_costo != float("inf") else "Infactible",
  )

st.write("")

# -------------------------------------------------------------
# PESTAÑAS ANALÍTICAS
# -------------------------------------------------------------
tab_sim, tab_matriz, tab_auditoria = st.tabs([
    "🗺️ Mapa y Evaluación de Rutas",
    "🔢 Matriz de Costos",
    "🛡️ Auditoría de Hamiltonicidad",
])

# -------------------------------------------------------------
# PESTAÑA 1: MAPA Y EVALUACIÓN
# -------------------------------------------------------------
with tab_sim:
  col_graf, col_interac = st.columns([1.5, 1])

  with col_interac:
    st.markdown("#### Selección de Trayectoria")
    modo_vista = st.radio(
        "Modo de análisis en el mapa:",
        [
            "⭐ Mejor Ruta Identificada (Óptimo)",
            "🔍 Inspeccionar otra Ruta del Espacio Muestral",
            "🌐 Grafo Completo (Sin resaltar)",
        ],
        index=0,
    )

    ruta_a_dibujar = None

    if modo_vista == "⭐ Mejor Ruta Identificada (Óptimo)":
      if mejor_evaluacion:
        ruta_a_dibujar = mejor_evaluacion["ruta_indices"]
        st.markdown(
            f"""
                <div class="calc-box">
                    <span style="color:#664930; font-weight:800;">★ RUTA ÓPTIMA:</span><br/>
                    <b>{mejor_evaluacion['ruta_str']}</b><br/><br/>
                    <span style="color:#997E67; font-weight:600;">Suma de pesos:</span><br/>
                    {mejor_evaluacion['desglose']} = <b style="color:#664930;">{mejor_costo} unidades</b>
                </div>
                """,
            unsafe_allow_html=True,
        )

    elif modo_vista == "🔍 Inspeccionar otra Ruta del Espacio Muestral":
      if rutas_validas_ordenadas:
        idx_ruta = st.slider(
            "Ciclo ordenado por costo (1 = Menor costo):",
            min_value=1,
            max_value=len(rutas_validas_ordenadas),
            value=min(2, len(rutas_validas_ordenadas)),
        )
        seleccionada = rutas_validas_ordenadas[idx_ruta - 1]
        ruta_a_dibujar = seleccionada["ruta_indices"]

        diferencia = seleccionada["costo"] - mejor_costo
        st.markdown(
            f"""
                <div class="calc-box" style="border-left-color:#997E67;">
                    <span style="color:#664930; font-weight:800;">RUTA #{idx_ruta} EVALUADA:</span><br/>
                    <b>{seleccionada['ruta_str']}</b><br/><br/>
                    <span style="color:#997E67; font-weight:600;">Suma de pesos:</span><br/>
                    {seleccionada['desglose']} = <b style="color:#664930;">{seleccionada['costo']} unidades</b><br/>
                    <span style="color:#997E67; font-size:12px; font-weight:bold;">(+{diferencia} unidades sobre el óptimo)</span>
                </div>
                """,
            unsafe_allow_html=True,
        )
      else:
        st.warning(
            "El grafo actual no posee ciclos hamiltonianos en esta"
            " configuración."
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

  # Representación Gráfica del Grafo
  with col_graf:
    G = nx.Graph()
    for nombre in nombres:
      G.add_node(nombre)
    for i in range(n):
      for j in range(i + 1, n):
        if matriz[i][j] is not None:
          G.add_edge(nombres[i], nombres[j], weight=matriz[i][j])

    # Posición poligonal asimétrica y regular
    pos = {}
    for i in range(n):
      angulo = (2 * math.pi * i / n) + (math.pi / 2)  # Nodo A en la cima
      radio = 1.0 + 0.05 * math.sin(i * 1.5)
      pos[nombres[i]] = (radio * math.cos(angulo), radio * math.sin(angulo))

    fig, ax = plt.subplots(figsize=(6.8, 5.2), dpi=140)

    # Lienzo con color claro melocotón/crema (#FFDBBB)
    fig.patch.set_facecolor("#FFDBBB")
    ax.set_facecolor("#FFDBBB")

    # 1. Caminos base (Gris cálido #CCBEB1)
    nx.draw_networkx_edges(
        G, pos, ax=ax, edge_color="#CCBEB1", width=1.8, alpha=0.95
    )

    # 2. Resaltar la ruta seleccionada (Marrón café #664930 o Marrón topo #997E67)
    if ruta_a_dibujar:
      color_ruta = (
          "#664930"
          if modo_vista == "⭐ Mejor Ruta Identificada (Óptimo)"
          else "#997E67"
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

    # 3. Nodos en Marrón Café Profundo (#664930)
    nx.draw_networkx_nodes(
        G,
        pos,
        ax=ax,
        node_color="#664930",
        node_size=880,
        edgecolors="#997E67",
        linewidths=2.2,
    )

    # Letras de los nodos en Crema Claro (#FFDBBB) para alto contraste
    for idx, nombre in enumerate(nombres):
      ax.text(
          pos[nombre][0],
          pos[nombre][1],
          nombre,
          fontsize=12,
          fontweight="bold",
          color="#FFDBBB",
          ha="center",
          va="center",
      )

    # 4. Pesos en las aristas (Horizontales sin rotar, fondo #CCBEB1, texto #664930)
    edge_labels = nx.get_edge_attributes(G, "weight")
    nx.draw_networkx_edge_labels(
        G,
        pos,
        edge_labels=edge_labels,
        ax=ax,
        rotate=False,
        font_size=8.5,
        font_color="#664930",
        font_family="monospace",
        font_weight="bold",
        bbox=dict(
            boxstyle="round,pad=0.22",
            facecolor="#FFDBBB",
            edgecolor="#997E67",
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
      '<div style="font-size:14px; color:#664930; margin-bottom:12px;">Matriz'
      " de adyacencia ponderada simétrica correspondiente al grafo <b>G = (V, E,"
      " W)</b>. El símbolo '—' denota ausencia de camino directo ($w ="
      " \\infty$).</div>",
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
      '<div style="font-size:14px; color:#664930; margin-bottom:14px;">En'
      " teoría de grafos, para que un ciclo hamiltoniano exista es necesario que"
      " cada ciudad cuente con al menos dos caminos incidentes: <b>deg(v) ≥"
      " 2</b> (uno para entrar y otro para salir sin repetir).</div>",
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
