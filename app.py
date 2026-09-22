import itertools
import random
import time
import matplotlib.pyplot as plt
import networkx as nx
import pandas as pd
import streamlit as st

# Configuración inicial de la página
st.set_page_config(
    page_title="TSP Solver • UPC",
    page_icon="⚡",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# -------------------------------------------------------------
# ESTILOS CSS PERSONALIZADOS
# -------------------------------------------------------------
st.markdown(
    """
<style>
    /* 1. Base clara y tipografía */
    .stApp {
        background-color: #f8fafc;
        color: #0f172a !important;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }

    /* 2. Alto contraste en textos generales */
    p, span, label, div, h1, h2, h3, h4, h5, h6 {
        color: #0f172a !important;
    }
    [data-testid="stWidgetLabel"] p, .stWidgetLabel label {
        color: #1e293b !important;
        font-weight: 700 !important;
        font-size: 13px !important;
        letter-spacing: 0.5px;
    }

    /* 3. Encabezado principal */
    .kicker {
        text-align: center;
        font-family: 'Courier New', Courier, monospace;
        font-size: 11px;
        letter-spacing: 3px;
        color: #4f46e5 !important;
        font-weight: 800;
        margin-bottom: 6px;
        text-transform: uppercase;
    }
    .hero-title {
        text-align: center;
        font-family: 'Georgia', serif;
        font-size: 38px;
        font-weight: 700;
        color: #0f172a !important;
        margin-bottom: 8px;
    }
    .hero-title span {
        color: #4f46e5 !important;
    }
    .hero-subtitle {
        text-align: center;
        font-size: 14px;
        color: #475569 !important;
        max-width: 620px;
        margin: 0 auto 12px auto;
        line-height: 1.5;
    }

    /* 4. Bloque aislado para la fórmula matemática */
    .formula-box {
        background-color: #eef2ff;
        border: 1px solid #c7d2fe;
        color: #3730a3 !important;
        padding: 8px 18px;
        border-radius: 8px;
        font-family: 'Courier New', monospace;
        font-weight: 700;
        font-size: 13px;
        display: inline-block;
        margin: 4px auto 20px auto;
        white-space: nowrap;
    }

    /* 5. Tarjetas estructuradas */
    .card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 16px;
        padding: 22px;
        margin-bottom: 20px;
        box-shadow: 0 4px 15px -2px rgba(15, 23, 42, 0.04);
    }
    .card-header {
        display: flex;
        align-items: center;
        gap: 12px;
        margin-bottom: 8px;
    }
    .step-badge {
        background: #e0e7ff;
        color: #4338ca !important;
        font-size: 13px;
        font-weight: 800;
        width: 30px;
        height: 30px;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: 8px;
        border: 1px solid #c7d2fe;
    }
    .card-title {
        font-family: 'Georgia', serif;
        font-size: 18px;
        font-weight: 700;
        color: #0f172a !important;
        margin: 0;
    }
    .card-desc {
        font-size: 13px;
        color: #64748b !important;
        margin: 0 0 16px 0;
    }

    /* 6. Píldoras superiores */
    .chip-container {
        display: flex;
        justify-content: center;
        gap: 10px;
        margin-bottom: 22px;
        flex-wrap: wrap;
    }
    .chip {
        padding: 4px 14px;
        border-radius: 20px;
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 0.5px;
        text-transform: uppercase;
        display: inline-block;
    }
    .chip-indigo {
        background: #eef2ff;
        color: #4338ca !important;
        border: 1px solid #c7d2fe;
    }
    .chip-slate {
        background: #f1f5f9;
        color: #334155 !important;
        border: 1px solid #e2e8f0;
    }

    /* 7. Entradas numéricas */
    div[data-testid="stNumberInput"] input {
        border-radius: 8px !important;
        border: 1.5px solid #cbd5e1 !important;
        background-color: #ffffff !important;
        font-family: 'Courier New', monospace !important;
        color: #0f172a !important;
        font-weight: 800 !important;
        font-size: 15px !important;
    }
    div[data-testid="stNumberInput"] button {
        background-color: #f1f5f9 !important;
        color: #0f172a !important;
        border-color: #cbd5e1 !important;
    }

    /* 8. Botón primario */
    div.stButton > button {
        border-radius: 8px !important;
        border: none !important;
        background-color: #4f46e5 !important;
        color: #ffffff !important;
        font-weight: 700 !important;
        font-size: 14px !important;
        padding: 8px 16px !important;
        box-shadow: 0 2px 8px rgba(79, 70, 229, 0.25) !important;
        transition: all 0.2s ease !important;
    }
    div.stButton > button:hover {
        background-color: #4338ca !important;
        box-shadow: 0 4px 12px rgba(79, 70, 229, 0.35) !important;
        color: #ffffff !important;
    }
    div.stButton > button p {
        color: #ffffff !important;
    }

    /* 9. Botón de descarga CSV */
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

    /* 10. Métricas */
    div[data-testid="stMetricValue"] {
        color: #0f172a !important;
        font-weight: 800 !important;
        font-size: 26px !important;
        font-family: 'Courier New', monospace !important;
    }
    div[data-testid="stMetricLabel"] p {
        color: #64748b !important;
        font-size: 12px !important;
        font-weight: 700 !important;
        letter-spacing: 0.5px !important;
    }

    /* 11. Ocultar barra flotante nativa */
    [data-testid="stElementToolbar"] {
        display: none !important;
    }

    /* 12. Forzar blanco en el menú desplegable de columnas */
    .glideDataGrid-context-menu,
    [data-testid="stDataFrame"] div[role="menu"],
    div[class*="context-menu"],
    div[class*="glideDataGrid"] {
        color: #ffffff !important;
    }

    .glideDataGrid-context-menu *,
    [data-testid="stDataFrame"] div[role="menu"] *,
    div[class*="context-menu"] *,
    div[role="menuitem"],
    div[role="menuitem"] span,
    div[role="menuitem"] p {
        color: #ffffff !important;
        fill: #ffffff !important;
        stroke: #ffffff !important;
    }

    div[role="menu"] svg,
    div[class*="context-menu"] svg {
        fill: #ffffff !important;
        stroke: #ffffff !important;
        color: #ffffff !important;
    }

    div[role="menu"] input,
    div[class*="context-menu"] input {
        color: #ffffff !important;
        background-color: #1e293b !important;
        border: 1px solid #475569 !important;
    }

    div[role="menuitem"]:hover {
        background-color: #334155 !important;
        color: #38bdf8 !important;
    }
</style>
""",
    unsafe_allow_html=True,
)

# -------------------------------------------------------------
# CABECERA VISUAL
# -------------------------------------------------------------
st.markdown(
    '<div class="kicker">OPTIMIZACIÓN COMBINATORIA • MATEMÁTICA COMPUTACIONAL</div>',
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="hero-title">Problema del Agente <span>Viajero</span></div>',
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="hero-subtitle">Búsqueda exhaustiva por fuerza bruta para hallar el ciclo hamiltoniano de coste mínimo en grafos ponderados no dirigidos.</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div style="text-align:center;"><div class="formula-box">Función Objetivo: &nbsp; C(π) = ∑ w(vi, vi+1)</div></div>',
    unsafe_allow_html=True,
)

st.markdown(
    """
<div class="chip-container">
    <span class="chip chip-indigo">● FUERZA BRUTA O(N!)</span>
    <span class="chip chip-slate">RANGO: N ∈ [5, 10]</span>
    <span class="chip chip-slate">TOPOLOGÍA PONDERADA</span>
    <span class="chip chip-slate">SOLUCIÓN EXACTA</span>
</div>
""",
    unsafe_allow_html=True,
)

# -------------------------------------------------------------
# TARJETA 1: ENTRADA DE PARÁMETROS
# -------------------------------------------------------------
st.markdown(
    """
<div class="card">
    <div class="card-header">
        <div class="step-badge">1</div>
        <div class="card-title">Configuración de vértices y topología</div>
    </div>
    <div class="card-desc">Define el número de vértices (n) y la densidad para construir la matriz de costos y calcular las rutas.</div>
</div>
""",
    unsafe_allow_html=True,
)

c_input1, c_input2, c_btn = st.columns([1, 1, 1.4])
with c_input1:
  n = st.number_input(
      "CANTIDAD DE VÉRTICES (N)", min_value=5, max_value=10, value=6, step=1
  )
with c_input2:
  densidad = st.number_input(
      "DENSIDAD DE ARISTAS (%)", min_value=20, max_value=100, value=50, step=10
  )
with c_btn:
  st.write("&nbsp;")
  generar = st.button("🎲 Generar Nuevo Grafo", use_container_width=True)

# -------------------------------------------------------------
# [LÓGICA CLAVE 1]: MODELADO MATRICIAL Y GENERACIÓN NO CIRCULAR
# -------------------------------------------------------------
if "matriz" not in st.session_state or generar or len(st.session_state.matriz) != n:
  random.seed(int(time.time()) if generar else 100)

  matriz = [[None for _ in range(n)] for _ in range(n)]

  # Ciclo hamiltoniano base desordenado
  orden_base = list(range(n))
  random.shuffle(orden_base)
  for i in range(n):
    u = orden_base[i]
    v = orden_base[(i + 1) % n]
    peso = random.randint(10, 35)
    matriz[u][v] = peso
    matriz[v][u] = peso

  # Conexiones transversales según densidad
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
# [LÓGICA CLAVE 2]: FUERZA BRUTA PARA EL TSP (O(n!))
# -------------------------------------------------------------
rutas = []
mejor_costo = float("inf")
mejor_ruta = None

for perm in itertools.permutations(range(1, n)):
  ruta = [0] + list(perm) + [0]
  costo = 0
  valida = True

  for k in range(n):
    u, v = ruta[k], ruta[k + 1]
    if matriz[u][v] is None:
      valida = False
      break
    costo += matriz[u][v]

  rutas.append((ruta, costo, valida))

  if valida and costo < mejor_costo:
    mejor_costo = costo
    mejor_ruta = ruta

# -------------------------------------------------------------
# TARJETA 2: VISUALIZACIÓN DEL GRAFO ORGÁNICO
# -------------------------------------------------------------
st.markdown(
    """
<div class="card">
    <div class="card-header">
        <div class="step-badge">2</div>
        <div class="card-title">Representación topológica y ciclo óptimo</div>
    </div>
    <div class="card-desc">Disposición de fuerzas orgánicas (spring layout). En verde esmeralda se resalta el ciclo de menor costo global.</div>
</div>
""",
    unsafe_allow_html=True,
)

G = nx.Graph()
for nombre in nombres:
  G.add_node(nombre)
for i in range(n):
  for j in range(i + 1, n):
    if matriz[i][j] is not None:
      G.add_edge(nombres[i], nombres[j], weight=matriz[i][j])

pos = nx.spring_layout(G, seed=42, k=1.8 / (n**0.5), iterations=50)

fig, ax = plt.subplots(figsize=(7.2, 4.8), dpi=140)
fig.patch.set_facecolor("#ffffff")
ax.set_facecolor("#ffffff")

# Aristas base
nx.draw_networkx_edges(
    G, pos, ax=ax, edge_color="#e2e8f0", width=1.4, style="solid", alpha=0.9
)

# Resaltar ciclo óptimo
if mejor_ruta:
  aristas_opt = [
      (nombres[mejor_ruta[i]], nombres[mejor_ruta[i + 1]]) for i in range(n)
  ]
  nx.draw_networkx_edges(
      G,
      pos,
      edgelist=aristas_opt,
      ax=ax,
      edge_color="#059669",
      width=3.6,
      alpha=0.95,
  )

# Nodos
colores_nodos = ["#4f46e5" if i == 0 else "#ffffff" for i in range(n)]
bordes_nodos = ["#3730a3" if i == 0 else "#64748b" for i in range(n)]
colores_texto = ["#ffffff" if i == 0 else "#0f172a" for i in range(n)]

nx.draw_networkx_nodes(
    G,
    pos,
    ax=ax,
    node_color=colores_nodos,
    node_size=820,
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
      fontfamily="sans-serif",
      color=colores_texto[idx],
      ha="center",
      va="center",
  )

# Pesos en aristas
edge_labels = nx.get_edge_attributes(G, "weight")
nx.draw_networkx_edge_labels(
    G,
    pos,
    edge_labels=edge_labels,
    ax=ax,
    font_size=8,
    font_color="#334155",
    font_family="monospace",
    bbox=dict(
        boxstyle="round,pad=0.25",
        facecolor="#f8fafc",
        edgecolor="#cbd5e1",
        linewidth=0.9,
        alpha=0.98,
    ),
)

ax.axis("off")
plt.tight_layout()
st.pyplot(fig)

# -------------------------------------------------------------
# TARJETA 3: RESULTADOS FACTORIALES
# -------------------------------------------------------------
st.markdown(
    """
<div class="card">
    <div class="card-header">
        <div class="step-badge">3</div>
        <div class="card-title">Métricas de la búsqueda exhaustiva</div>
    </div>
    <div class="card-desc">Resumen del espacio factorial explorado frente a la cota mínima calculada.</div>
</div>
""",
    unsafe_allow_html=True,
)

m1, m2, m3 = st.columns(3)
with m1:
  st.metric(label="PERMUTACIONES EVALUADAS", value=f"{len(rutas):,}")
with m2:
  ciclos_validos = sum(1 for _, _, v in rutas if v)
  st.metric(label="CICLOS HAMILTONIANOS", value=ciclos_validos)
with m3:
  val_min = str(mejor_costo) if mejor_costo != float("inf") else "N/A"
  st.metric(label="COSTO MÍNIMO GLOBAL", value=val_min)

if mejor_ruta:
  ruta_str = " → ".join([nombres[idx] for idx in mejor_ruta])
  st.markdown(
      f"""
    <div style="background:#f0fdf4; border:1px solid #bbf7d0; border-radius:12px; padding:16px; margin-top:10px;">
        <div style="color:#166534 !important; font-weight:800; font-size:12px; text-transform:uppercase; letter-spacing:1px;">
            ★ Ruta Óptima Identificada (Menor Distancia):
        </div>
        <div style="font-family:'Courier New', monospace; font-size:17px; font-weight:800; color:#14532d !important; margin-top:5px;">
            {ruta_str}
        </div>
        <div style="font-size:13px; color:#15803d !important; margin-top:4px;">
            Costo total acumulado: <b>{mejor_costo} unidades</b>.
        </div>
    </div>
    """,
      unsafe_allow_html=True,
  )

# -------------------------------------------------------------
# TARJETA 4: MATRIZ DE COSTOS
# -------------------------------------------------------------
st.markdown(
    """
<div class="card">
    <div class="card-header">
        <div class="step-badge">4</div>
        <div class="card-title">Matriz de Costos / Adyacencia Ponderada</div>
    </div>
    <div class="card-desc">Modelado formal de costos directos entre vértices. El símbolo '—' denota ausencia de conexión directa.</div>
</div>
""",
    unsafe_allow_html=True,
)

df_matriz = pd.DataFrame(
    [[val if val is not None else "—" for val in fila] for fila in matriz],
    index=nombres,
    columns=nombres,
)

st.dataframe(df_matriz, use_container_width=True)

csv_data = df_matriz.to_csv().encode("utf-8")
st.download_button(
    label="📥 Descargar Matriz de Costos (CSV)",
    data=csv_data,
    file_name="matriz_adyacencia_tsp.csv",
    mime="text/csv",
)
