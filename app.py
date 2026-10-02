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
    page_icon="🗺️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -------------------------------------------------------------
# PALETA TIERRA / PERGAMINO (INSPIRADA EN LA IMAGEN DE REFERENCIA)
# -------------------------------------------------------------
st.markdown(
    """
<style>
    /* 1. Fondo Global Tierra / Café Oscuro */
    .stApp {
        background-color: #3e3427;
        color: #f5eedc !important;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }

    /* 2. Jerarquía de texto */
    h1, h2, h3, h4, p, span, label {
        color: #f5eedc !important;
    }
    
    .terminal-kicker {
        font-family: 'Courier New', monospace;
        font-size: 11px;
        letter-spacing: 2px;
        color: #e5be7a !important; /* Dorado arena */
        font-weight: 700;
        text-transform: uppercase;
    }
    
    .main-title {
        font-family: 'Georgia', serif;
        font-size: 32px;
        font-weight: 800;
        letter-spacing: -0.5px;
        color: #fff9ed !important;
        margin-top: 4px;
        margin-bottom: 8px;
    }
    .main-title span {
        color: #e5be7a !important;
    }

    .desc-text {
        color: #dfd3bd !important;
        font-size: 14px;
        line-height: 1.5;
    }

    /* 3. Píldoras / Insignias superiores */
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
    .badge-gold {
        background: #564939;
        color: #f7d697 !important;
        border: 1px solid #75634d;
    }
    .badge-green {
        background: #475a34;
        color: #c9e89d !important;
        border: 1px solid #5a7342;
    }
    .badge-teal {
        background: #284c4f;
        color: #9fe2ea !important;
        border: 1px solid #36656a;
    }

    /* 4. Métricas */
    div[data-testid="stMetricValue"] {
        color: #fff9ed !important;
        font-family: 'Courier New', monospace !important;
        font-size: 26px !important;
        font-weight: 800 !important;
    }
    div[data-testid="stMetricLabel"] p {
        color: #c2b59d !important;
        font-size: 11px !important;
        letter-spacing: 0.5px !important;
        text-transform: uppercase !important;
    }

    /* 5. Barra Lateral y Controles */
    section[data-testid="stSidebar"] {
        background-color: #352c21 !important;
        border-right: 1px solid #4a3e2f;
    }
    div[data-testid="stNumberInput"] input {
        background-color: #4a3e30 !important;
        color: #ffffff !important;
        border: 1px solid #635340 !important;
        border-radius: 6px !important;
    }

    /* 6. Botones principales (Verde tierra cálido) */
    div.stButton > button {
        background-color: #5a8731 !important;
        color: #ffffff !important;
        border: 1px solid #486d26 !important;
        border-radius: 6px !important;
        font-weight: 700 !important;
        padding: 8px 16px !important;
        box-shadow: 0 3px 8px rgba(0,0,0, 0.25) !important;
        transition: all 0.2s ease !important;
    }
    div.stButton > button:hover {
        background-color: #6b9e3a !important;
        transform: translateY(-1px);
    }

    /* Botón de exportación */
    div.stDownloadButton > button {
        background-color: #1d7882 !important;
        color: #ffffff !important;
        border: 1px solid #145961 !important;
        border-radius: 6px !important;
        font-weight: 700 !important;
    }

    /* 7. Caja de Desglose de Cálculo */
    .calc-box {
        background: #4a3f31;
        border: 1px solid #635340;
        border-left: 5px solid #5a8731;
        border-radius: 8px;
        padding: 14px 18px;
        font-family: 'Courier New', monospace;
        font-size: 13.5px;
        color: #fff9ed;
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
  st.markdown("### Configura tu Mapa")

  n = st.slider(
      "Ciudades / Vértices (n)",
      min_value=5,
      max_value=9,
      value=7,
      help="Número de vértices en el grafo.",
  )
  densidad = st.slider(
      "Densidad de Caminos (%)",
      min_value=30,
      max_value=100,
      value=60,
      step=5,
      help="Grado de interconexión entre las ciudades.",
  )

  st.write("")
  generar = st.button("🔨 Construir / Regenerar", use_container_width=True)

  st.markdown("---")
  st.markdown(
      """
    <div style="font-size: 12px; color: #c2b59d; line-height: 1.5;">
        <b>Propiedad Combinatoria:</b><br/>
        Fijando el origen en <code>A</code>, el espacio factorial equivale a <code>(n - 1)!</code> rutas evaluadas.
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

  # Caminos adicionales según densidad
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
      "Optimización en grafos ponderados <b>G = (V, E, W)</b>. Búsqueda"
      " exhaustiva del ciclo hamiltoniano que minimiza la distancia total en el"
      " espacio factorial."
      "</div>",
      unsafe_allow_html=True,
  )

with c_badges:
  st.write("")
  st.markdown(
      f"""
    <div style="display:flex; flex-direction:column; gap:8px; align-items:flex-end;">
        <span class="stat-badge badge-gold">Grafo G = (V, E)</span>
        <span class="stat-badge badge-teal">Espacio: {len(evaluaciones):,} rutas</span>
        <span class="stat-badge badge-green">Ciclos Factibles: {len(rutas_validas)}</span>
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
# PESTAÑA 1: MAPA PERGAMINO Y EVALUACIÓN
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
                    <span style="color:#c9e89d; font-weight:700;">★ RUTA ÓPTIMA:</span><br/>
                    <b>{mejor_evaluacion['ruta_str']}</b><br/><br/>
                    <span style="color:#dfd3bd;">Suma de pesos:</span><br/>
                    {mejor_evaluacion['desglose']} = <b style="color:#c9e89d;">{mejor_costo} unidades</b>
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
                <div class="calc-box" style="border-left-color:#e5be7a;">
                    <span style="color:#f7d697; font-weight:700;">RUTA #{idx_ruta} EVALUADA:</span><br/>
                    <b>{seleccionada['ruta_str']}</b><br/><br/>
                    <span style="color:#dfd3bd;">Suma de pesos:</span><br/>
                    {seleccionada['desglose']} = <b style="color:#f7d697;">{seleccionada['costo']} unidades</b><br/>
                    <span style="color:#f87171; font-size:12px;">(+{diferencia} unidades sobre el óptimo)</span>
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

  # Representación Gráfica con Estilo Pergamino / Tierra
  with col_graf:
    G = nx.Graph()
    for nombre in nombres:
      G.add_node(nombre)
    for i in range(n):
      for j in range(i + 1, n):
        if matriz[i][j] is not None:
          G.add_edge(nombres[i], nombres[j], weight=matriz[i][j])

    # Posición poligonal asimétrica y regular (sin cruces caóticos)
    pos = {}
    for i in range(n):
      angulo = (2 * math.pi * i / n) + (math.pi / 2)  # Nodo A en la cima
      radio = 1.0 + 0.05 * math.sin(i * 1.5)
      pos[nombres[i]] = (radio * math.cos(angulo), radio * math.sin(angulo))

    fig, ax = plt.subplots(figsize=(6.8, 5.2), dpi=140)

    # Fondo Pergamino cálido como en la imagen de referencia
    fig.patch.set_facecolor("#f4eedb")
    ax.set_facecolor("#f4eedb")

    # 1. Caminos base (Gris/arena claro)
    nx.draw_networkx_edges(
        G, pos, ax=ax, edge_color="#c8bfa9", width=1.6, alpha=0.9
    )

    # 2. Resaltar la ruta seleccionada
    if ruta_a_dibujar:
      color_ruta = (
          "#5a8731"
          if modo_vista == "⭐ Mejor Ruta Identificada (Óptimo)"
          else "#c0533e"
      )  # Verde bosque o Terracota
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

    # 3. Nodos estilo chocolate de la referencia
    nx.draw_networkx_nodes(
        G,
        pos,
        ax=ax,
        node_color="#5a4632",
        node_size=880,
        edgecolors="#3d2f21",
        linewidths=2.0,
    )

    # Letras de los nodos en blanco nítido
    for idx, nombre in enumerate(nombres):
      ax.text(
          pos[nombre][0],
          pos[nombre][1],
          nombre,
          fontsize=12,
          fontweight="bold",
          color="#ffffff",
          ha="center",
          va="center",
      )

    # 4. Pesos en las aristas con fondo pergamino
    edge_labels = nx.get_edge_attributes(G, "weight")
    nx.draw_networkx_edge_labels(
        G,
        pos,
        edge_labels=edge_labels,
        ax=ax,
        font_size=8,
        font_color="#2b2319",
        font_family="monospace",
        font_weight="bold",
        bbox=dict(
            boxstyle="round,pad=0.2",
            facecolor="#f4eedb",
            edgecolor="#c8bfa9",
            linewidth=0.8,
            alpha=0.95,
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
      '<div style="font-size:14px; color:#dfd3bd; margin-bottom:12px;">Matriz'
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
      '<div style="font-size:14px; color:#dfd3bd; margin-bottom:14px;">En'
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
