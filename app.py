import itertools
import math
import random
import time
import matplotlib.pyplot as plt
import networkx as nx
import pandas as pd
import streamlit as st

# Configuración de página
st.set_page_config(
    page_title="TSP • Matemática Computacional",
    page_icon="📐",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -------------------------------------------------------------
# ESTILOS CSS CON CONTRASTE ESTRICTO Y PALETA PASTEL
# -------------------------------------------------------------
st.markdown(
    """
<style>
    /* 1. Fondo Global y Tipografía */
    .stApp {
        background-color: #181826 !important;
        color: #f1f5f9 !important;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }

    /* 2. Textos sobre fondo oscuro: siempre claros */
    p, span, label, div, h1, h2, h3, h4 {
        color: #f1f5f9 !important;
    }

    .editorial-kicker {
        font-family: 'Courier New', monospace;
        font-size: 11px;
        letter-spacing: 2px;
        color: #a7f3d0 !important; /* Menta pastel */
        font-weight: 700;
        text-transform: uppercase;
        margin-bottom: 2px;
    }

    .main-title {
        font-family: 'Georgia', serif;
        font-size: 34px;
        font-weight: 800;
        letter-spacing: -0.5px;
        color: #ffffff !important;
        margin-top: 4px;
        margin-bottom: 8px;
    }
    .main-title span {
        color: #ddd6fe !important; /* Lavanda pastel */
    }

    .desc-text {
        color: #cbd5e1 !important;
        font-size: 14.5px;
        line-height: 1.6;
    }

    /* 3. Píldoras con fondos pasteles claros: TEXTO OSCURO */
    .stat-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 5px 12px;
        border-radius: 6px;
        font-size: 12px;
        font-weight: 800;
        font-family: 'Courier New', monospace;
    }
    .badge-mint {
        background-color: #a7f3d0 !important; /* Pastel claro */
        color: #064e3b !important;            /* Texto verde oscuro legible */
        border: 1px solid #6ee7b7;
    }
    .badge-lavender {
        background-color: #ddd6fe !important; /* Pastel claro */
        color: #3b0764 !important;            /* Texto morado oscuro legible */
        border: 1px solid #c4b5fd;
    }
    .badge-peach {
        background-color: #fed7aa !important; /* Pastel claro */
        color: #7c2d12 !important;            /* Texto café/naranja oscuro legible */
        border: 1px solid #fdba74;
    }

    /* 4. Métricas sobre fondo oscuro: valores en blanco nítido */
    div[data-testid="stMetricValue"] {
        color: #ffffff !important;
        font-family: 'Courier New', monospace !important;
        font-size: 26px !important;
        font-weight: 800 !important;
    }
    div[data-testid="stMetricLabel"] p {
        color: #94a3b8 !important;
        font-size: 11px !important;
        letter-spacing: 0.5px !important;
        text-transform: uppercase !important;
        font-weight: 700 !important;
    }

    /* 5. Barra Lateral */
    section[data-testid="stSidebar"] {
        background-color: #12121d !important;
        border-right: 1px solid #2a2a3f !important;
    }
    section[data-testid="stSidebar"] * {
        color: #f1f5f9 !important;
    }

    /* Inputs */
    div[data-testid="stNumberInput"] input {
        background-color: #222235 !important;
        color: #ffffff !important;
        border: 1px solid #3f3f5a !important;
        border-radius: 6px !important;
        font-weight: 700 !important;
    }
    div[data-testid="stNumberInput"] button {
        background-color: #313149 !important;
        color: #ffffff !important;
    }

    /* 6. Botón Primario: Fondo pastel lavanda intenso con texto oscuro */
    div.stButton > button {
        background-color: #c4b5fd !important; /* Lavanda pastel */
        color: #1e1b4b !important;            /* Texto índigo oscuro */
        border: none !important;
        border-radius: 6px !important;
        font-weight: 800 !important;
        padding: 8px 16px !important;
        box-shadow: 0 4px 12px rgba(196, 181, 253, 0.25) !important;
        transition: all 0.2s ease !important;
    }
    div.stButton > button:hover {
        background-color: #ddd6fe !important;
        color: #0f172a !important;
        transform: translateY(-1px);
    }
    div.stButton > button p {
        color: #1e1b4b !important;
    }

    /* Botón de descarga CSV */
    div.stDownloadButton > button {
        background-color: #222235 !important;
        color: #ddd6fe !important;
        border: 1px solid #3f3f5a !important;
        border-radius: 6px !important;
        font-weight: 700 !important;
    }
    div.stDownloadButton > button:hover {
        background-color: #2e2e46 !important;
        color: #ffffff !important;
    }
    div.stDownloadButton > button p {
        color: #ddd6fe !important;
    }

    /* 7. Caja de Desglose de Cálculo */
    .calc-box {
        background: #222235;
        border: 1px solid #34344d;
        border-left: 5px solid #a7f3d0;
        border-radius: 8px;
        padding: 14px 18px;
        font-family: 'Courier New', monospace;
        font-size: 13.5px;
        color: #f1f5f9;
        margin: 10px 0;
    }

    /* Pestañas */
    button[data-baseweb="tab"] {
        color: #94a3b8 !important;
        font-weight: 700 !important;
    }
    button[data-baseweb="tab"][aria-selected="true"] {
        color: #ddd6fe !important;
        border-bottom-color: #ddd6fe !important;
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
      value=6,
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
  generar = st.button("📐 Construir / Regenerar", use_container_width=True)

  st.markdown("---")
  st.markdown(
      """
    <div style="font-size: 12px; color: #94a3b8; line-height: 1.5;">
        <b>Propiedad Combinatoria:</b><br/>
        Fijando el origen en <code>A</code>, el espacio factorial examinado es exactamente de <code>(n - 1)!</code> permutaciones.
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
        <span class="stat-badge badge-mint">Grafo G = (V, E)</span>
        <span class="stat-badge badge-lavender">Espacio: {len(evaluaciones):,} rutas</span>
        <span class="stat-badge badge-peach">Ciclos Factibles: {len(rutas_validas)}</span>
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
                    <span style="color:#a7f3d0; font-weight:800;">★ RUTA ÓPTIMA:</span><br/>
                    <b>{mejor_evaluacion['ruta_str']}</b><br/><br/>
                    <span style="color:#cbd5e1; font-weight:600;">Suma de pesos:</span><br/>
                    {mejor_evaluacion['desglose']} = <b style="color:#a7f3d0;">{mejor_costo} unidades</b>
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
                <div class="calc-box" style="border-left-color:#fed7aa;">
                    <span style="color:#fed7aa; font-weight:800;">RUTA #{idx_ruta} EVALUADA:</span><br/>
                    <b>{seleccionada['ruta_str']}</b><br/><br/>
                    <span style="color:#cbd5e1; font-weight:600;">Suma de pesos:</span><br/>
                    {seleccionada['desglose']} = <b style="color:#fed7aa;">{seleccionada['costo']} unidades</b><br/>
                    <span style="color:#fca5a5; font-size:12px; font-weight:bold;">(+{diferencia} unidades sobre el óptimo)</span>
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

  # -------------------------------------------------------------
  # DIBUJADO DEL GRAFO CON POSICIONAMIENTO MATEMÁTICO SOBRE LA RECTA
  # -------------------------------------------------------------
  with col_graf:
    G = nx.Graph()
    for nombre in nombres:
      G.add_node(nombre)
    aristas_info = []
    for i in range(n):
      for j in range(i + 1, n):
        if matriz[i][j] is not None:
          G.add_edge(nombres[i], nombres[j], weight=matriz[i][j])
          aristas_info.append((i, j, matriz[i][j]))

    # Posición poligonal estructurada
    pos = {}
    for i in range(n):
      angulo = (2 * math.pi * i / n) + (math.pi / 2)  # Nodo A en la cima
      radio = 1.0 + 0.04 * math.sin(i * 1.5)
      pos[nombres[i]] = (radio * math.cos(angulo), radio * math.sin(angulo))

    fig, ax = plt.subplots(figsize=(6.8, 5.2), dpi=140)
    fig.patch.set_facecolor("#222235")
    ax.set_facecolor("#222235")

    # 1. Caminos base (Gris violáceo suave)
    nx.draw_networkx_edges(
        G, pos, ax=ax, edge_color="#454562", width=1.6, alpha=0.85
    )

    # 2. Resaltar la ruta seleccionada (Menta pastel o Durazno pastel)
    if ruta_a_dibujar:
      color_ruta = (
          "#86efac"
          if modo_vista == "⭐ Mejor Ruta Identificada (Óptimo)"
          else "#fed7aa"
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
          alpha=0.98,
      )

    # 3. Nodos en colores pasteles claros con TEXTO OSCURO (Contraste estricto)
    colores_nodos = ["#86efac" if i == 0 else "#ddd6fe" for i in range(n)]
    bordes_nodos = ["#4ade80" if i == 0 else "#c4b5fd" for i in range(n)]
    colores_letras = ["#064e3b" if i == 0 else "#0f172a" for i in range(n)]

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
          fontsize=12,
          fontweight="bold",
          color=colores_letras[idx],
          ha="center",
          va="center",
      )

    # 4. FUNCIÓN PARA ENCONTRAR INTERSECCIÓN ENTRE DOS LÍNEAS
    def interseccion_t(p1, p2, q1, q2):
      """Retorna el parámetro t en [0,1] a lo largo del segmento p1->p2 si se corta con q1->q2."""

      dx1, dy1 = p2[0] - p1[0], p2[1] - p1[1]
      dx2, dy2 = q2[0] - q1[0], q2[1] - q1[1]
      det = dx1 * dy2 - dy1 * dx2
      if abs(det) < 1e-9:
        return None  # Paralelas o colineales
      t = ((q1[0] - p1[0]) * dy2 - (q1[1] - p1[1]) * dx2) / det
      s = ((q1[0] - p1[0]) * dy1 - (q1[1] - p1[1]) * dx1) / det
      if 0.05 < t < 0.95 and 0.05 < s < 0.95:
        return t
      return None

    # Ubicación EXACTA de cada peso sobre su segmento evitando cruces
    for i, j, peso in aristas_info:
      p1 = pos[nombres[i]]
      p2 = pos[nombres[j]]

      # Encontramos todos los puntos de cruce con otras aristas a lo largo de este segmento
      cruces_t = []
      for k, l, _ in aristas_info:
        if (i, j) == (k, l) or len({i, j, k, l}) < 4:
          continue  # Mismo segmento o comparten nodo extremo
        q1 = pos[nombres[k]]
        q2 = pos[nombres[l]]
        t_cruce = interseccion_t(p1, p2, q1, q2)
        if t_cruce is not None:
          cruces_t.append(t_cruce)

      # Puntos de frontera para que el peso no toque los círculos de los nodos extremos
      puntos_t = sorted([0.22] + [t for t in cruces_t if 0.22 < t < 0.78] + [0.78])

      # Buscamos el intervalo libre más grande a lo largo del segmento
      max_espacio = -1.0
      t_optimo = 0.50

      for idx_t in range(len(puntos_t) - 1):
        espacio = puntos_t[idx_t + 1] - puntos_t[idx_t]
        if espacio > max_espacio:
          max_espacio = espacio
          t_optimo = (puntos_t[idx_t] + puntos_t[idx_t + 1]) / 2.0

      # Posición matemática ESTRICTAMENTE sobre la recta: (1 - t)*P1 + t*P2
      x_peso = (1.0 - t_optimo) * p1[0] + t_optimo * p2[0]
      y_peso = (1.0 - t_optimo) * p1[1] + t_optimo * p2[1]

      # Pastilla clara con texto oscuro: máximo contraste y 100% legible
      ax.text(
          x_peso,
          y_peso,
          str(peso),
          fontsize=8.5,
          fontweight="bold",
          fontfamily="monospace",
          color="#0f172a",  # Texto oscuro legible sobre fondo claro
          ha="center",
          va="center",
          bbox=dict(
              boxstyle="round,pad=0.22",
              facecolor="#f8fafc",  # Blanco crema claro
              edgecolor="#94a3b8",  # Borde grafito suave
              linewidth=0.9,
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
      '<div style="font-size:14px; color:#cbd5e1; margin-bottom:12px;">Matriz'
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
      '<div style="font-size:14px; color:#cbd5e1; margin-bottom:14px;">En'
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
