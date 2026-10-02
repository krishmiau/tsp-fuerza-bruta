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
    .stApp {
        background-color: #181826 !important;
        color: #f1f5f9 !important;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }
    p, span, label, div, h1, h2, h3, h4 {
        color: #f1f5f9 !important;
    }
    .editorial-kicker {
        font-family: 'Courier New', monospace;
        font-size: 11px;
        letter-spacing: 2px;
        color: #a7f3d0 !important;
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
        color: #ddd6fe !important;
    }
    .desc-text {
        color: #cbd5e1 !important;
        font-size: 14.5px;
        line-height: 1.6;
    }
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
        background-color: #a7f3d0 !important;
        color: #064e3b !important;
        border: 1px solid #6ee7b7;
    }
    .badge-lavender {
        background-color: #ddd6fe !important;
        color: #3b0764 !important;
        border: 1px solid #c4b5fd;
    }
    .badge-peach {
        background-color: #fed7aa !important;
        color: #7c2d12 !important;
        border: 1px solid #fdba74;
    }
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
    section[data-testid="stSidebar"] {
        background-color: #12121d !important;
        border-right: 1px solid #2a2a3f !important;
    }
    section[data-testid="stSidebar"] * {
        color: #f1f5f9 !important;
    }
    div[data-testid="stNumberInput"] input {
        background-color: #222235 !important;
        color: #ffffff !important;
        border: 1px solid #3f3f5a !important;
        border-radius: 6px !important;
        font-weight: 700 !important;
    }
    div.stButton > button {
        background-color: #c4b5fd !important;
        color: #1e1b4b !important;
        border: none !important;
        border-radius: 6px !important;
        font-weight: 800 !important;
        padding: 8px 16px !important;
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
    div.stDownloadButton > button {
        background-color: #222235 !important;
        color: #ddd6fe !important;
        border: 1px solid #3f3f5a !important;
        border-radius: 6px !important;
        font-weight: 700 !important;
    }
    div.stDownloadButton > button p {
        color: #ddd6fe !important;
    }
    button[data-baseweb="tab"] {
        color: #94a3b8 !important;
        font-weight: 700 !important;
    }
    button[data-baseweb="tab"][aria-selected="true"] {
        color: #ddd6fe !important;
        border-bottom-color: #ddd6fe !important;
    }
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
      max_value=8,
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
        Al descartar reflexiones reversas en grafos no dirigidos, el espacio de ciclos hamiltonianos únicos es de <code>(n - 1)! / 2</code>.
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
  st.session_state.paso_actual = 0

matriz = st.session_state.matriz
nombres = [chr(65 + i) for i in range(n)]

# -------------------------------------------------------------
# ANÁLISIS HISTÓRICO SECUENCIAL DEL ESPACIO MUESTRAL
# -------------------------------------------------------------
evaluaciones = []
mejor_costo_global = float("inf")
mejor_evaluacion_global = None
ciclos_vistos = set()

costo_record_historico = float("inf")
ruta_record_historica = None

for perm in itertools.permutations(range(1, n)):
  ruta_tupla = (0,) + perm + (0,)
  ruta_reversa = (0,) + tuple(reversed(perm)) + (0,)

  if ruta_reversa in ciclos_vistos:
    continue
  ciclos_vistos.add(ruta_tupla)

  ruta = list(ruta_tupla)
  costo = 0
  valida = True
  desglose_terminos = []
  arista_rota = None

  for k in range(n):
    u, v = ruta[k], ruta[k + 1]
    w = matriz[u][v]
    if w is None:
      valida = False
      arista_rota = (nombres[u], nombres[v])
      desglose_terminos.append(f"w({nombres[u]},{nombres[v]})=—")
      break
    costo += w
    desglose_terminos.append(f"{w}")

  # Comparación con el mejor costo conocido hasta ese instante
  hubo_mejora = False
  if valida:
    if costo < costo_record_historico:
      costo_record_historico = costo
      ruta_record_historica = ruta
      hubo_mejora = True
      estado = "MEJORA_RECORD"
    elif costo == costo_record_historico:
      estado = "EMPATA_RECORD"
    else:
      estado = "DESCARTADA_COSTOSA"
  else:
    estado = "INFACTIBLE"

  eval_item = {
      "paso": len(evaluaciones) + 1,
      "ruta_indices": ruta,
      "ruta_str": " → ".join([nombres[idx] for idx in ruta]),
      "costo": costo if valida else None,
      "valida": valida,
      "desglose": " + ".join(desglose_terminos) if valida else "Trayectoria discontinua",
      "arista_rota": arista_rota,
      "estado": estado,
      "costo_record": costo_record_historico if costo_record_historico != float("inf") else None,
      "ruta_record": ruta_record_historica,
  }
  evaluaciones.append(eval_item)

  if valida and costo < mejor_costo_global:
    mejor_costo_global = costo
    mejor_evaluacion_global = eval_item

rutas_validas = [r for r in evaluaciones if r["valida"]]
total_pasos = len(evaluaciones)

# -------------------------------------------------------------
# CABECERA MATEMÁTICA Y CONTEXTUALIZACIÓN
# -------------------------------------------------------------
c_head, c_badges = st.columns([2.6, 1.4])
with c_head:
  st.markdown(
      '<div class="editorial-kicker">MATEMÁTICA COMPUTACIONAL • TEORÍA DE GRAFOS</div>',
      unsafe_allow_html=True,
  )
  st.markdown(
      '<div class="main-title">Problema del Agente <span>Viajero</span></div>',
      unsafe_allow_html=True,
  )
  st.markdown(
      '<div class="desc-text">'
      "Explorador y simulador de optimización discreta en grafos ponderados $G = (V, E, W)$. "
      "Visualización algorítmica de la búsqueda exhaustiva para determinar el ciclo hamiltoniano de coste mínimo."
      "</div>",
      unsafe_allow_html=True,
  )

with c_badges:
  st.write("")
  st.markdown(
      f"""
    <div style="display:flex; flex-direction:column; gap:8px; align-items:flex-end;">
        <span class="stat-badge badge-mint">Grafo G = (V, E)</span>
        <span class="stat-badge badge-lavender">Espacio Único: {total_pasos:,} permutaciones</span>
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
  st.metric("Vértices |V|", f"{n} Nodos")
with kpi2:
  aristas_totales = sum(1 for i in range(n) for j in range(i + 1, n) if matriz[i][j] is not None)
  st.metric("Aristas |E|", f"{aristas_totales}")
with kpi3:
  st.metric("Ciclos Conexos Únicos", f"{len(rutas_validas)} / {total_pasos}")
with kpi4:
  st.metric("Costo Mínimo Global", f"{mejor_costo_global}" if mejor_costo_global != float("inf") else "Infactible")

st.write("")

# -------------------------------------------------------------
# PESTAÑAS PRINCIPALES
# -------------------------------------------------------------
tab_contexto, tab_simulador, tab_matriz, tab_auditoria = st.tabs([
    "📖 Contexto y Fundamento Teórico",
    "🎬 Simulador Paso a Paso",
    "🔢 Matriz de Costos",
    "🛡️ Auditoría de Hamiltonicidad",
])

# -------------------------------------------------------------
# PESTAÑA 0: CONTEXTUALIZACIÓN DEL PROYECTO
# -------------------------------------------------------------
with tab_contexto:
  with st.container(border=True):
    st.subheader("¿Qué problema resuelve esta aplicación y cómo lo hace?")
    st.markdown(
        """
        El **Problema del Agente Viajero** (*Traveling Salesperson Problem* o **TSP**) es uno de los desafíos centrales en la **Matemática Computacional** y la **Optimización Combinatoria**.

        * **El Objetivo Formal:** Dado un grafo no dirigido ponderado $G = (V, E, W)$, encontrar una secuencia cerrada ordenada de vértices $\\pi = (v_0, v_1, \\dots, v_{n-1}, v_0)$ tal que:
          1. Visite **cada vértice exactamente una vez** (excepto el de inicio y fin).
          2. Regrese al vértice de partida $v_0$.
          3. Minimice la función objetivo $C(\\pi) = \\sum_{i=0}^{n-1} w(v_i, v_{i+1})$.

        * **Espacio Muestral y Simetría Bidireccional:**  
          Fijando el vértice inicial en $A$, el número de permutaciones posibles de los vértices restantes es $(n-1)!$. Dado que el grafo es no dirigido ($w(u, v) = w(v, u)$), recorrer un ciclo en sentido horario genera exactamente el mismo costo que recorrerlo en sentido antihorario. Esta herramienta descarta sistemáticamente las reflexiones reversas, reduciendo el espacio muestral evaluado a:
        """
    )
    st.latex(r"\frac{(n-1)!}{2}")
    st.markdown(
        """
        * **Mecanismo de Evaluación:**
          1. **Comprobación de conectividad:** Se evalúa si cada arista consecutiva existe en la matriz de adyacencia. Si falta una sola conexión, la ruta se clasifica como **Infactible** ($C = \\infty$).
          2. **Cálculo de costo acumulado:** Se suman los pesos de las aristas del ciclo.
          3. **Poda y comparación:** Se contrasta con el récord mínimo encontrado hasta ese momento; si es menor, se actualiza la solución óptima.
        """
    )

# -------------------------------------------------------------
# PESTAÑA 1: SIMULADOR PASO A PASO (MANUAL Y AUTOMÁTICO)
# -------------------------------------------------------------
with tab_simulador:
  col_graf, col_interac = st.columns([1.5, 1])

  with col_interac:
    st.markdown("#### Control de Ejecución")

    modo_sim = st.radio(
        "Modo de simulación:",
        ["Manual (Paso a paso)", "Automático (Continuo)"],
        horizontal=True,
    )

    if "paso_actual" not in st.session_state:
      st.session_state.paso_actual = 0

    if modo_sim == "Manual (Paso a paso)":
      b_prev, b_next, b_reset = st.columns(3)
      with b_prev:
        if st.button("⬅️ Anterior", use_container_width=True):
          st.session_state.paso_actual = max(0, st.session_state.paso_actual - 1)
      with b_next:
        if st.button("Siguiente ➡️", use_container_width=True):
          st.session_state.paso_actual = min(total_pasos - 1, st.session_state.paso_actual + 1)
      with b_reset:
        if st.button("⏮️ Reiniciar", use_container_width=True):
          st.session_state.paso_actual = 0

      idx_paso = st.slider(
          "Permutación evaluada:",
          min_value=1,
          max_value=total_pasos,
          value=st.session_state.paso_actual + 1,
      )
      st.session_state.paso_actual = idx_paso - 1

    else:
      vel = st.slider("Velocidad de simulación (segundos por paso):", min_value=0.05, max_value=1.5, value=0.4, step=0.05)
      c_play, c_stop = st.columns(2)
      with c_play:
        iniciar_auto = st.button("▶️ Iniciar Simulación Automática", use_container_width=True)
      with c_stop:
        reset_auto = st.button("⏮️ Reiniciar al Inicio", use_container_width=True)

      if reset_auto:
        st.session_state.paso_actual = 0

      if iniciar_auto:
        contenedor_placeholder = st.empty()
        for p in range(st.session_state.paso_actual, total_pasos):
          st.session_state.paso_actual = p
          time.sleep(vel)
          st.rerun()

    # Datos del paso en análisis
    paso_info = evaluaciones[st.session_state.paso_actual]
    ruta_a_dibujar = paso_info["ruta_indices"]

    # Cuadro comparativo del paso
    with st.container(border=True):
      st.markdown(f"**EVALUANDO PERMUTACIÓN {paso_info['paso']} / {total_pasos}**")
      st.markdown(f"**Ruta:** `{paso_info['ruta_str']}`")
      st.caption("Cálculo de pesos:")
      st.code(f"{paso_info['desglose']}", language="text")

      st.markdown("---")
      st.markdown("**Estado de la Comparación:**")

      if paso_info["estado"] == "MEJORA_RECORD":
        st.markdown(f":green[**★ ¡NUEVO RÉCORD MÍNIMO! Costo = {paso_info['costo']} unidades**]")
        st.caption("Esta ruta superó al mejor costo anterior y se establece como la nueva solución óptima provisional.")
      elif paso_info["estado"] == "EMPATA_RECORD":
        st.markdown(f":blue[**⚖️ EMPATE CON EL RÉCORD: Costo = {paso_info['costo']} unidades**]")
        st.caption("Empata el valor del óptimo provisional actual.")
      elif paso_info["estado"] == "DESCARTADA_COSTOSA":
        dif = paso_info["costo"] - paso_info["costo_record"]
        st.markdown(f":orange[**❌ RUTA DESCARTADA POR MAYOR COSTO: {paso_info['costo']} unidades**]")
        st.caption(f"Es **+{dif} unidades** más larga que el mejor camino conocido (`{paso_info['costo_record']}`). Se desecha.")
      else:
        st.markdown(":red[**🚫 TRAYECTORIA INFACTIBLE (ARISTA INEXISTENTE)**]")
        u_rot, v_rot = paso_info["arista_rota"]
        st.caption(f"No existe conexión directa entre **{u_rot}** y **{v_rot}**. El ciclo no puede completarse.")

      st.markdown("---")
      if paso_info["costo_record"] is not None:
        st.markdown(f"**Óptimo provisional al momento:** `{paso_info['costo_record']} unidades`")
      else:
        st.markdown("**Óptimo provisional:** `Aún no encontrado`")

    # Explicación del funcionamiento interno
    with st.expander("ℹ️ ¿Qué está sucediendo internamente?"):
      st.markdown(
          """
          1. El algoritmo genera la siguiente permutación matemática del conjunto de ciudades.
          2. Verifica una a una las aristas en la matriz de adyacencia.
          3. Si alguna arista tiene peso $\\infty$ (no existe), la trayectoria se descarta inmediatamente.
          4. Si el ciclo existe, su suma se compara con el récord vigente:
             * **Menor:** actualiza el récord.
             * **Mayor o igual:** se almacena pero se rechaza como solución mínima.
          """
      )

  # -------------------------------------------------------------
  # DIBUJADO DEL GRAFO CON DETECCIÓN GEOMÉTRICA DE CRUCES
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

    pos = {}
    for i in range(n):
      angulo = (2 * math.pi * i / n) + (math.pi / 2)
      radio = 1.0 + 0.04 * math.sin(i * 1.5)
      pos[nombres[i]] = (radio * math.cos(angulo), radio * math.sin(angulo))

    fig, ax = plt.subplots(figsize=(6.8, 5.2), dpi=140)
    fig.patch.set_facecolor("#222235")
    ax.set_facecolor("#222235")

    # Aristas base
    nx.draw_networkx_edges(G, pos, ax=ax, edge_color="#454562", width=1.6, alpha=0.85)

    # Aristas de la ruta evaluada en el paso actual
    if paso_info["valida"]:
      color_ruta = "#86efac" if paso_info["estado"] == "MEJORA_RECORD" else "#fed7aa"
      aristas_resaltadas = [(nombres[ruta_a_dibujar[i]], nombres[ruta_a_dibujar[i + 1]]) for i in range(n)]
      nx.draw_networkx_edges(G, pos, edgelist=aristas_resaltadas, ax=ax, edge_color=color_ruta, width=3.8, alpha=0.98)
    else:
      # Si es rota, se dibujan en rojo las aristas que sí existen hasta el corte
      aristas_parciales = []
      for i in range(n):
        u, v = ruta_a_dibujar[i], ruta_a_dibujar[i + 1]
        if matriz[u][v] is not None:
          aristas_parciales.append((nombres[u], nombres[v]))
        else:
          break
      if aristas_parciales:
        nx.draw_networkx_edges(G, pos, edgelist=aristas_parciales, ax=ax, edge_color="#fca5a5", width=3.2, style="dashed", alpha=0.95)

    # Nodos
    colores_nodos = ["#86efac" if i == 0 else "#ddd6fe" for i in range(n)]
    bordes_nodos = ["#4ade80" if i == 0 else "#c4b5fd" for i in range(n)]
    colores_letras = ["#064e3b" if i == 0 else "#0f172a" for i in range(n)]

    nx.draw_networkx_nodes(G, pos, ax=ax, node_color=colores_nodos, node_size=880, edgecolors=bordes_nodos, linewidths=2.2)

    for idx, nombre in enumerate(nombres):
      ax.text(pos[nombre][0], pos[nombre][1], nombre, fontsize=12, fontweight="bold", color=colores_letras[idx], ha="center", va="center")

    def interseccion_t(p1, p2, q1, q2):
      dx1, dy1 = p2[0] - p1[0], p2[1] - p1[1]
      dx2, dy2 = q2[0] - q1[0], q2[1] - q1[1]
      det = dx1 * dy2 - dy1 * dx2
      if abs(det) < 1e-9:
        return None
      t = ((q1[0] - p1[0]) * dy2 - (q1[1] - p1[1]) * dx2) / det
      s = ((q1[0] - p1[0]) * dy1 - (q1[1] - p1[1]) * dx1) / det
      if 0.05 < t < 0.95 and 0.05 < s < 0.95:
        return t
      return None

    # Ubicación limpia de los pesos sobre la recta
    for i, j, peso in aristas_info:
      p1 = pos[nombres[i]]
      p2 = pos[nombres[j]]

      cruces_t = []
      for k, l, _ in aristas_info:
        if (i, j) == (k, l) or len({i, j, k, l}) < 4:
          continue
        q1 = pos[nombres[k]]
        q2 = pos[nombres[l]]
        t_cruce = interseccion_t(p1, p2, q1, q2)
        if t_cruce is not None:
          cruces_t.append(t_cruce)

      puntos_t = sorted([0.22] + [t for t in cruces_t if 0.22 < t < 0.78] + [0.78])

      max_espacio = -1.0
      t_optimo = 0.50
      for idx_t in range(len(puntos_t) - 1):
        espacio = puntos_t[idx_t + 1] - puntos_t[idx_t]
        if espacio > max_espacio:
          max_espacio = espacio
          t_optimo = (puntos_t[idx_t] + puntos_t[idx_t + 1]) / 2.0

      x_peso = (1.0 - t_optimo) * p1[0] + t_optimo * p2[0]
      y_peso = (1.0 - t_optimo) * p1[1] + t_optimo * p2[1]

      ax.text(
          x_peso,
          y_peso,
          str(peso),
          fontsize=8.5,
          fontweight="bold",
          fontfamily="monospace",
          color="#0f172a",
          ha="center",
          va="center",
          bbox=dict(
              boxstyle="round,pad=0.22",
              facecolor="#f8fafc",
              edgecolor="#94a3b8",
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
  st.markdown("Matriz de adyacencia ponderada simétrica correspondiente al grafo $G = (V, E, W)$:")
  df_matriz = pd.DataFrame([[val if val is not None else "—" for val in fila] for fila in matriz], index=nombres, columns=nombres)
  st.dataframe(df_matriz, use_container_width=True)
  csv = df_matriz.to_csv().encode("utf-8")
  st.download_button(label="📥 Exportar Matriz a CSV", data=csv, file_name="matriz_adyacencia.csv", mime="text/csv")

# -------------------------------------------------------------
# PESTAÑA 3: AUDITORÍA DE HAMILTONICIDAD
# -------------------------------------------------------------
with tab_auditoria:
  st.markdown("#### Condición Necesaria de Grado Mínimo")
  st.markdown("Para que exista ciclo hamiltoniano, cada vértice debe satisfacer la condición necesaria $deg(v) \\ge 2$:")
  grados_data = []
  for i in range(n):
    g = sum(1 for j in range(n) if matriz[i][j] is not None)
    cumple = g >= 2
    grados_data.append({
        "Vértice": nombres[i],
        "Grado deg(v)": g,
        "Condición deg(v) ≥ 2": "✅ Satisfecho" if cumple else "❌ No cumple (deg < 2)",
    })
  st.table(pd.DataFrame(grados_data))
