import itertools
import random
import time
import matplotlib.pyplot as plt
import networkx as nx
import pandas as pd
import streamlit as st

# Configuración inicial de la página
st.set_page_config(
    page_title="TSP Engine • Graph Explorer",
    page_icon="🌌",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -------------------------------------------------------------
# ESTILOS CSS PERSONALIZADOS (DARK MODE PASTEL & DASHBOARD MODERNO)
# -------------------------------------------------------------
st.markdown(
    """
<style>
    /* 1. Fondo Global Dark Slate */
    .stApp {
        background-color: #0b0f19;
        color: #e2e8f0 !important;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }

    /* 2. Jerarquía de texto y colores pastel */
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

    /* 3. Paneles y Cajas de Control */
    .dark-panel {
        background-color: #111827;
        border: 1px solid #1f2937;
        border-radius: 14px;
        padding: 18px 20px;
        margin-bottom: 16px;
    }

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

    /* 4. Métricas rediseñadas */
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

    /* 5. Inputs y Sliders en Dark */
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

    /* 6. Botón de Generación */
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

    /* 7. Caja de Fórmula Desglosada */
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

    /* Ocultar barra no deseada */
    [data-testid="stElementToolbar"] {
        display: none !important;
    }
</style>
""",
    unsafe_allow_html=True,
)

# -------------------------------------------------------------
# SIDEBAR: PARÁMETROS Y CONTROL DEL MOTOR
# -------------------------------------------------------------
with st.sidebar:
  st.markdown(
      '<div class="terminal-kicker">CONTROL DE TOPOLOGÍA</div>',
      unsafe_allow_html=True,
  )
  st.markdown("### Configuración")

  n = st.slider(
      "Cantidad de Nodos (Ciudades)",
      min_value=5,
      max_value=9,
      value=6,
      help="Espacio factorial de búsqueda evaluado: (n-1)!",
  )
  densidad = st.slider(
      "Densidad de Conexiones (%)",
      min_value=30,
      max_value=100,
      value=60,
      step=5,
      help="Determina el grado de interconexión entre nodos.",
  )

  st.write("")
  generar = st.button("⚡ Regenerar Grafo", use_container_width=True)

  st.markdown("---")
  st.markdown(
      """
    <div style="font-size: 12px; color: #94a3b8; line-height: 1.5;">
        <b>Regla de Búsqueda:</b><br/>
        Fijación de nodo origen en <code>A</code> (índice 0) para descartar permutaciones equivalentes por rotación.
    </div>
    """,
      unsafe_allow_html=True,
  )

# -------------------------------------------------------------
# GENERACIÓN DE GRAFO Y CONTROL DE SESIÓN
# -------------------------------------------------------------
if "matriz" not in st.session_state or generar or len(st.session_state.matriz) != n:
  random.seed(int(time.time()) if generar else 42)
  matriz = [[None for _ in range(n)] for _ in range(n)]

  # Ciclo base garantizado con permutación para geometría compleja
  orden_base = list(range(n))
  random.shuffle(orden_base)
  for i in range(n):
    u = orden_base[i]
    v = orden_base[(i + 1) % n]
    peso = random.randint(12, 38)
    matriz[u][v] = peso
    matriz[v][u] = peso

  # Aristas transversales
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
# MOTOR DE FUERZA BRUTA Y EVALUACIÓN FACTORIAL
# -------------------------------------------------------------
evaluaciones = []
mejor_costo = float("inf")
mejor_ruta = None

for perm in itertools.permutations(range(1, n)):
  ruta = [0] + list(perm) + [0]
  costo = 0
  valida = True
  desglose = []

  for k in range(n):
    u, v = ruta[k], ruta[k + 1]
    w = matriz[u][v]
    if w is None:
      valida = False
      desglose.append(f"w({nombres[u]},{nombres[v]})=∞")
      break
    costo += w
    desglose.append(f"{w}")

  evaluaciones.append({
      "ruta_indices": ruta,
      "ruta_str": " → ".join([nombres[idx] for idx in ruta]),
      "costo": costo if valida else None,
      "valida": valida,
      "desglose": " + ".join(desglose),
  })

  if valida and costo < mejor_costo:
    mejor_costo = costo
    mejor_ruta = ruta

# Rutas que lograron cerrar el ciclo completo
rutas_validas = [r for r in evaluaciones if r["valida"]]
rutas_validas_ordenadas = sorted(rutas_validas, key=lambda x: x["costo"])

# -------------------------------------------------------------
# ENCABEZADO TIPO DASHBOARD ANALÍTICO
# -------------------------------------------------------------
c_head, c_badges = st.columns([2.5, 1.5])
with c_head:
  st.markdown(
      '<div class="terminal-kicker">LABORATORIO DE ALGORITMOS • FUERZA'
      " BRUTA</div>",
      unsafe_allow_html=True,
  )
  st.markdown(
      '<div class="main-title">TSP Solver <span>Studio</span></div>',
      unsafe_allow_html=True,
  )
  st.markdown(
      '<div class="desc-text">'
      "Exploración combinatoria paso a paso sobre el Problema del Agente"
      " Viajero. Inspecciona el comportamiento de cada ciclo hamiltoniano y la"
      " descomposición del costo."
      "</div>",
      unsafe_allow_html=True,
  )

with c_badges:
  st.write("")
  st.markdown(
      f"""
    <div style="display:flex; flex-direction:column; gap:8px; align-items:flex-end;">
        <span class="stat-badge badge-mint">● Complejidad: O((n-1)!)</span>
        <span class="stat-badge badge-lavender">Espacio: {len(evaluaciones):,} permutaciones</span>
        <span class="stat-badge badge-rose">Factibles: {len(rutas_validas)} ciclos</span>
    </div>
    """,
      unsafe_allow_html=True,
  )

st.write("")

# Fila de métricas clave (KPIs)
kpi1, kpi2, kpi3, kpi4 = st.columns(4)
with kpi1:
  st.metric("Vértices Conectados", f"{n} Nodos")
with kpi2:
  aristas_totales = sum(
      1 for i in range(n) for j in range(i + 1, n) if matriz[i][j] is not None
  )
  st.metric("Aristas Activas", f"{aristas_totales}")
with kpi3:
  st.metric(
      "Ciclos Válidos",
      f"{len(rutas_validas)} / {len(evaluaciones)}",
  )
with kpi4:
  st.metric(
      "Distancia Mínima Global",
      f"{mejor_costo}" if mejor_costo != float("inf") else "Sin solución",
  )

st.write("")

# -------------------------------------------------------------
# ESTRUCTURA PRINCIPAL: VISUALIZADOR + PANEL DE INTERACCIÓN
# -------------------------------------------------------------
tab_sim, tab_matriz, tab_auditoria = st.tabs([
    "🔭 Simulador e Inspección Visual",
    "🔢 Matriz de Costos",
    "🛡️ Auditoría de Hamiltonicidad",
])

# -------------------------------------------------------------
# PESTAÑA 1: SIMULADOR INTERACTIVO
# -------------------------------------------------------------
with tab_sim:
  col_graf, col_interac = st.columns([1.5, 1])

  with col_interac:
    st.markdown("#### Selector de Trayectorias")
    modo_vista = st.radio(
        "Modo de visualización en el grafo:",
        [
            "⭐ Solución Óptima Global",
            "🔍 Inspeccionar otra Ruta del Espacio Muestral",
            "🌐 Grafo Completo (Sin resaltar)",
        ],
        index=0,
    )

    ruta_a_dibujar = None

    if modo_vista == "⭐ Solución Óptima Global":
      ruta_a_dibujar = mejor_ruta
      st.markdown(
          f"""
            <div class="calc-box">
                <span style="color:#a7f3d0; font-weight:700;">Trayectoria Óptima:</span><br/>
                <b>{' → '.join([nombres[i] for i in mejor_ruta])}</b><br/><br/>
                <span style="color:#94a3b8;">Desglose de pesos:</span><br/>
                {evaluaciones[0]['desglose']} = <b style="color:#a7f3d0;">{mejor_costo} unidades</b>
            </div>
            """,
          unsafe_allow_html=True,
      )

    elif modo_vista == "🔍 Inspeccionar otra Ruta del Espacio Muestral":
      if rutas_validas_ordenadas:
        idx_ruta = st.slider(
            "Seleccionar Ruta ordenada por costo (1 = Mejor, N = Peor):",
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
                    <span style="color:#fde68a; font-weight:700;">Ruta #{idx_ruta} evaluada:</span><br/>
                    <b>{seleccionada['ruta_str']}</b><br/><br/>
                    <span style="color:#94a3b8;">Suma acumulada:</span><br/>
                    {seleccionada['desglose']} = <b style="color:#fde68a;">{seleccionada['costo']} unidades</b><br/>
                    <span style="color:#f87171; font-size:11px;">(+{diferencia} unidades respecto al óptimo)</span>
                </div>
                """,
            unsafe_allow_html=True,
        )
      else:
        st.warning(
            "No se encontraron ciclos hamiltonianos válidos en esta"
            " configuración."
        )

    # Explicación pedagógica de cómo calcula el algoritmo
    with st.expander("ℹ️ ¿Cómo calcula el algoritmo el costo total?"):
      st.markdown(
          """
            Para cada permutación $\\pi = (v_0, v_1, \\dots, v_{n-1}, v_0)$:
            1. Se toma el costo directo de cada enlace consecutivo en la matriz: $w(v_k, v_{k+1})$.
            2. Si en algún par de nodos la matriz tiene `—` (sin conexión), la ruta entera se anula de inmediato ($C = \\infty$).
            3. Si todos los tramos existen, se suman sus pesos y se almacena en memoria. La de menor suma es la ruta ganadora.
            """
      )

  # Dibujar el grafo en Matplotlib con Estilo Dark
  with col_graf:
    G = nx.Graph()
    for nombre in nombres:
      G.add_node(nombre)
    for i in range(n):
      for j in range(i + 1, n):
        if matriz[i][j] is not None:
          G.add_edge(nombres[i], nombres[j], weight=matriz[i][j])

    # Disposición física orgánica
    pos = nx.spring_layout(G, seed=42, k=2.0 / (n**0.5), iterations=60)

    fig, ax = plt.subplots(figsize=(6.8, 5.2), dpi=140)
    fig.patch.set_facecolor("#111827")
    ax.set_facecolor("#111827")

    # 1. Aristas base (Gris oscuro suave)
    nx.draw_networkx_edges(
        G, pos, ax=ax, edge_color="#334155", width=1.5, alpha=0.7
    )

    # 2. Resaltado de trayectoria activa
    if ruta_a_dibujar:
      color_ruta = (
          "#a7f3d0"
          if modo_vista == "⭐ Solución Óptima Global"
          else "#fde68a"
      )  # Menta o Ámbar pastel
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

    # 3. Nodos (Nodo A en Verde Pastel, el resto en Lavanda Pastel)
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

    # 4. Pesos numéricos en etiquetas dark mode
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
      " de adyacencia ponderada simétrica correspondiente al grafo generado."
      " Los guiones representan ausencia de conexión directa.</div>",
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
      file_name="matriz_costos_tsp.csv",
      mime="text/csv",
  )

# -------------------------------------------------------------
# PESTAÑA 3: AUDITORÍA DE HAMILTONICIDAD
# -------------------------------------------------------------
with tab_auditoria:
  st.markdown("#### Análisis Estructural de Grados")
  st.markdown(
      '<div style="font-size:13px; color:#94a3b8; margin-bottom:14px;">Para'
      " que un grafo admita un Ciclo Hamiltoniano, es condición necesaria que"
      " cada nodo tenga al menos grado 2 (una arista de entrada y una de"
      " salida).</div>",
      unsafe_allow_html=True,
  )

  grados_data = []
  for i in range(n):
    g = sum(1 for j in range(n) if matriz[i][j] is not None)
    cumple = g >= 2
    grados_data.append({
        "Vértice": nombres[i],
        "Grado (Conexiones)": g,
        "Condición Mínima (deg ≥ 2)": "✅ Cumple" if cumple else "❌ Insuficiente",
    })

  st.table(pd.DataFrame(grados_data))
