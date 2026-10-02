import itertools
import math
import random
import time
import matplotlib.pyplot as plt
import networkx as nx
import pandas as pd
import streamlit as st

# =============================================================================
# 1. CAPA LÓGICA Y MATEMÁTICA ("BACKEND")
# =============================================================================

def generar_topologia(n, densidad, semilla=None):
    """Genera la matriz de adyacencia ponderada simétrica garantizando conexidad."""
    if semilla is not None:
        random.seed(semilla)
        
    matriz = [[None for _ in range(n)] for _ in range(n)]
    
    # Ciclo hamiltoniano base para asegurar solución factible
    orden_base = list(range(n))
    random.shuffle(orden_base)
    for i in range(n):
        u, v = orden_base[i], orden_base[(i + 1) % n]
        peso = random.randint(7, 35)
        matriz[u][v] = peso
        matriz[v][u] = peso

    # Conexiones adicionales según la densidad seleccionada
    for i in range(n):
        for j in range(i + 1, n):
            if matriz[i][j] is None and random.random() < (densidad / 100.0):
                peso = random.randint(15, 60)
                matriz[i][j] = peso
                matriz[j][i] = peso

    return matriz


def evaluar_espacio_muestral(n, matriz, nombres):
    """Evalúa las permutaciones cerradas descartando simetrías reversas."""
    evaluaciones = []
    mejor_costo_global = float("inf")
    mejor_evaluacion_global = None
    ciclos_vistos = set()
    record_historico = float("inf")
    ruta_record_historica = None

    for perm in itertools.permutations(range(1, n)):
        ruta_tupla = (0,) + perm + (0,)
        ruta_reversa = (0,) + tuple(reversed(perm)) + (0,)

        # Filtro de grafo no dirigido: descarta el ciclo en reversa exacta
        if ruta_reversa in ciclos_vistos:
            continue
        ciclos_vistos.add(ruta_tupla)

        ruta = list(ruta_tupla)
        costo = 0
        valida = True
        desglose_terminos = []
        arista_rota = None

        # Verificación arista por arista
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

        # Análisis comparativo secuencial
        if valida:
            if costo < record_historico:
                record_historico = costo
                ruta_record_historica = ruta
                estado = "MEJORA_RECORD"
                motivo = f"Supera al récord anterior. Se convierte en la mejor solución provisional ({costo} u)."
            elif costo == record_historico:
                estado = "EMPATA_RECORD"
                motivo = f"Empata en costo ({costo} u) con la mejor solución provisional vigente."
            else:
                estado = "DESCARTADA_COSTOSA"
                dif = costo - record_historico
                motivo = f"Descartada: costo de {costo} u (+{dif} u respecto al récord actual de {record_historico} u)."
        else:
            estado = "INFACTIBLE"
            motivo = f"Descartada: trayectoria interrumpida. No existe arista entre {arista_rota[0]} y {arista_rota[1]}."

        eval_item = {
            "paso": len(evaluaciones) + 1,
            "ruta_indices": ruta,
            "ruta_str": " → ".join([nombres[idx] for idx in ruta]),
            "costo": costo if valida else None,
            "valida": valida,
            "desglose": " + ".join(desglose_terminos) if valida else "Trayectoria discontinua",
            "arista_rota": arista_rota,
            "estado": estado,
            "motivo": motivo,
            "costo_record": record_historico if record_historico != float("inf") else None,
            "ruta_record": ruta_record_historica,
        }
        evaluaciones.append(eval_item)

        if valida and costo < mejor_costo_global:
            mejor_costo_global = costo
            mejor_evaluacion_global = eval_item

    rutas_validas = [r for r in evaluaciones if r["valida"]]
    rutas_validas_ranking = sorted(rutas_validas, key=lambda x: x["costo"])
    
    return evaluaciones, rutas_validas_ranking, mejor_costo_global, mejor_evaluacion_global


def _interseccion_t(p1, p2, q1, q2):
    """Calcula el factor de corte t en [0,1] para dos segmentos de recta."""
    dx1, dy1 = p2[0] - p1[0], p2[1] - p1[1]
    dx2, dy2 = q2[0] - q1[0], q2[1] - q1[1]
    det = dx1 * dy2 - dy1 * dx2
    if abs(det) < 1e-9:
        return None
    t = ((q1[0] - p1[0]) * dy2 - (q1[1] - p1[1]) * dx2) / det
    s = ((q1[0] - p1[0]) * dy1 - (q1[1] - p1[1]) * dx1) / det
    return t if 0.05 < t < 0.95 and 0.05 < s < 0.95 else None


def generar_figura_grafo(n, nombres, matriz, ruta_indices=None, estado="BASE"):
    """Construye el lienzo Matplotlib del grafo con pesos alineados sin superposición."""
    # Distribución en polígono regular con asimetría sutil
    pos = {}
    for i in range(n):
        angulo = (2 * math.pi * i / n) + (math.pi / 2)
        radio = 1.0 + 0.04 * math.sin(i * 1.5)
        pos[nombres[i]] = (radio * math.cos(angulo), radio * math.sin(angulo))

    G = nx.Graph()
    for nombre in nombres:
        G.add_node(nombre)
        
    aristas_info = []
    for i in range(n):
        for j in range(i + 1, n):
            if matriz[i][j] is not None:
                G.add_edge(nombres[i], nombres[j], weight=matriz[i][j])
                aristas_info.append((i, j, matriz[i][j]))

    fig, ax = plt.subplots(figsize=(6.8, 5.0), dpi=130)
    fig.patch.set_facecolor("#131b26")
    ax.set_facecolor("#131b26")

    # 1. Aristas base
    nx.draw_networkx_edges(G, pos, ax=ax, edge_color="#2e3d52", width=1.6, alpha=0.85)

    # 2. Resaltar ciclo evaluado
    if ruta_indices:
        if estado == "INFACTIBLE":
            aristas_ok = []
            for k in range(n):
                u, v = ruta_indices[k], ruta_indices[k + 1]
                if matriz[u][v] is not None:
                    aristas_ok.append((nombres[u], nombres[v]))
                else:
                    break
            if aristas_ok:
                nx.draw_networkx_edges(G, pos, edgelist=aristas_ok, ax=ax, edge_color="#fca5a5", width=3.2, style="dashed", alpha=0.95)
        else:
            color_arista = "#5eead4" if estado == "MEJORA_RECORD" else "#fed7aa"
            aristas_ciclo = [(nombres[ruta_indices[k]], nombres[ruta_indices[k + 1]]) for k in range(n)]
            nx.draw_networkx_edges(G, pos, edgelist=aristas_ciclo, ax=ax, edge_color=color_arista, width=3.8, alpha=0.98)

    # 3. Nodos: fondo pastel con texto oscuro
    colores_nodos = ["#5eead4" if i == 0 else "#c7d2fe" for i in range(n)]
    bordes_nodos = ["#2dd4bf" if i == 0 else "#a5b4fc" for i in range(n)]
    colores_letras = ["#042f2e" if i == 0 else "#090d16" for i in range(n)]

    nx.draw_networkx_nodes(G, pos, ax=ax, node_color=colores_nodos, node_size=880, edgecolors=bordes_nodos, linewidths=2.2)

    for idx, nombre in enumerate(nombres):
        ax.text(pos[nombre][0], pos[nombre][1], nombre, fontsize=12, fontweight="bold", color=colores_letras[idx], ha="center", va="center")

    # 4. Cálculo de posición despejada sobre la recta para cada etiqueta de peso
    for i, j, peso in aristas_info:
        p1, p2 = pos[nombres[i]], pos[nombres[j]]

        cruces_t = []
        for k, l, _ in aristas_info:
            if (i, j) == (k, l) or len({i, j, k, l}) < 4:
                continue
            t_cruce = _interseccion_t(p1, p2, pos[nombres[k]], pos[nombres[l]])
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
            x_peso, y_peso, str(peso),
            fontsize=8.5, fontweight="bold", fontfamily="monospace",
            color="#090d16", ha="center", va="center",
            bbox=dict(boxstyle="round,pad=0.22", facecolor="#f1f5f9", edgecolor="#64748b", linewidth=0.9, alpha=0.98),
        )

    ax.axis("off")
    plt.tight_layout()
    return fig


# =============================================================================
# 2. CAPA VISUAL / INTERFAZ DE USUARIO ("FRONTEND")
# =============================================================================

st.set_page_config(
    page_title="TSP • Matemática Computacional",
    page_icon="📐",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Estilos CSS generales (Dark slate / Pasteles con contraste riguroso)
st.markdown(
    """
<style>
    .stApp { background-color: #0f141c !important; color: #e2e8f0 !important; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
    p, span, label, div, h1, h2, h3, h4 { color: #e2e8f0 !important; }
    .editorial-kicker { font-family: 'Courier New', monospace; font-size: 11px; letter-spacing: 2px; color: #5eead4 !important; font-weight: 700; text-transform: uppercase; margin-bottom: 2px; }
    .main-title { font-family: 'Georgia', serif; font-size: 34px; font-weight: 800; letter-spacing: -0.5px; color: #ffffff !important; margin-top: 4px; margin-bottom: 8px; }
    .main-title span { color: #c7d2fe !important; }
    .desc-text { color: #cbd5e1 !important; font-size: 14.5px; line-height: 1.6; }
    
    .stat-badge { display: inline-flex; align-items: center; gap: 6px; padding: 5px 12px; border-radius: 6px; font-size: 12px; font-weight: 800; font-family: 'Courier New', monospace; }
    .badge-teal { background-color: #99f6e4 !important; color: #042f2e !important; border: 1px solid #5eead4; }
    .badge-lavender { background-color: #c7d2fe !important; color: #1e1b4b !important; border: 1px solid #a5b4fc; }
    .badge-rose { background-color: #fbcfe8 !important; color: #701a75 !important; border: 1px solid #f472b6; }
    
    div[data-testid="stMetricValue"] { color: #ffffff !important; font-family: 'Courier New', monospace !important; font-size: 26px !important; font-weight: 800 !important; }
    div[data-testid="stMetricLabel"] p { color: #94a3b8 !important; font-size: 11px !important; letter-spacing: 0.5px !important; text-transform: uppercase !important; font-weight: 700 !important; }
    
    section[data-testid="stSidebar"] { background-color: #0b0f15 !important; border-right: 1px solid #1f2937 !important; }
    section[data-testid="stSidebar"] * { color: #e2e8f0 !important; }
    
    div[data-testid="stNumberInput"] input { background-color: #17202e !important; color: #ffffff !important; border: 1px solid #2d3b4e !important; border-radius: 6px !important; font-weight: 700 !important; }
    div[data-testid="stNumberInput"] button { background-color: #243042 !important; color: #ffffff !important; }
    
    div.stButton > button { background-color: #a5b4fc !important; color: #0f172a !important; border: none !important; border-radius: 6px !important; font-weight: 800 !important; padding: 8px 16px !important; transition: all 0.2s ease !important; }
    div.stButton > button:hover { background-color: #c7d2fe !important; color: #020617 !important; transform: translateY(-1px); }
    div.stButton > button p { color: #0f172a !important; }
    
    div.stDownloadButton > button { background-color: #17202e !important; color: #c7d2fe !important; border: 1px solid #2d3b4e !important; border-radius: 6px !important; font-weight: 700 !important; }
    div.stDownloadButton > button p { color: #c7d2fe !important; }
    
    button[data-baseweb="tab"] { color: #94a3b8 !important; font-weight: 700 !important; }
    button[data-baseweb="tab"][aria-selected="true"] { color: #c7d2fe !important; border-bottom-color: #c7d2fe !important; }
    [data-testid="stElementToolbar"] { display: none !important; }
</style>
""",
    unsafe_allow_html=True,
)

# Inicialización de variables en Session State
if "puesto_ranking" not in st.session_state:
    st.session_state.puesto_ranking = 1
if "paso_manual" not in st.session_state:
    st.session_state.paso_manual = 0
if "sim_activa" not in st.session_state:
    st.session_state.sim_activa = False
if "paso_auto" not in st.session_state:
    st.session_state.paso_auto = 0

# Configuración en la Barra Lateral
with st.sidebar:
    st.markdown('<div class="editorial-kicker">MODELO TOPOLÓGICO G = (V, E)</div>', unsafe_allow_html=True)
    st.markdown("### Configuración")

    n = st.slider("Ciudades / Vértices (n)", min_value=5, max_value=8, value=7, help="Número de vértices del grafo.")
    densidad = st.slider("Densidad de Caminos (%)", min_value=30, max_value=100, value=75, step=5, help="Porcentaje de aristas.")

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

# Control de regeneración del backend
if "matriz" not in st.session_state or generar or len(st.session_state.matriz) != n:
    semilla = int(time.time()) if generar else 42
    st.session_state.matriz = generar_topologia(n, densidad, semilla)
    st.session_state.puesto_ranking = 1
    st.session_state.paso_manual = 0
    st.session_state.sim_activa = False
    st.session_state.paso_auto = 0

matriz = st.session_state.matriz
nombres = [chr(65 + i) for i in range(n)]

# Ejecución del backend
evaluaciones, rutas_validas_ranking, mejor_costo_global, mejor_evaluacion_global = evaluar_espacio_muestral(n, matriz, nombres)
total_pasos = len(evaluaciones)
total_factibles = len(rutas_validas_ranking)

if st.session_state.puesto_ranking > max(1, total_factibles):
    st.session_state.puesto_ranking = 1

# Cabecera principal
c_head, c_badges = st.columns([2.6, 1.4])
with c_head:
    st.markdown('<div class="editorial-kicker">MATEMÁTICA COMPUTACIONAL • TEORÍA DE GRAFOS</div>', unsafe_allow_html=True)
    st.markdown('<div class="main-title">Problema del Agente <span>Viajero</span></div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="desc-text">'
        "Optimización en grafos ponderados <b>G = (V, E, W)</b>. "
        "Búsqueda exhaustiva del ciclo hamiltoniano óptimo con análisis comparativo paso a paso y descarte en tiempo real."
        "</div>",
        unsafe_allow_html=True,
    )

with c_badges:
    st.write("")
    st.markdown(
        f"""
        <div style="display:flex; flex-direction:column; gap:8px; align-items:flex-end;">
            <span class="stat-badge badge-teal">Grafo G = (V, E)</span>
            <span class="stat-badge badge-lavender">Espacio Único: {total_pasos:,} permutaciones</span>
            <span class="stat-badge badge-rose">Ciclos Factibles: {total_factibles}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.latex(r"\min_{\pi} \quad C(\pi) = \sum_{i=0}^{n-1} w(v_i, v_{i+1})")
st.write("")

# KPIs superiores
kpi1, kpi2, kpi3, kpi4 = st.columns(4)
with kpi1:
    st.metric("Vértices |V|", f"{n} Nodos")
with kpi2:
    aristas_totales = sum(1 for i in range(n) for j in range(i + 1, n) if matriz[i][j] is not None)
    st.metric("Aristas |E|", f"{aristas_totales}")
with kpi3:
    st.metric("Ciclos Conexos Únicos", f"{total_factibles} / {total_pasos}")
with kpi4:
    st.metric("Costo Mínimo Global", f"{mejor_costo_global}" if mejor_costo_global != float("inf") else "Infactible")

st.write("")

# Navegación por pestañas
tab_ranking, tab_simulador, tab_contexto, tab_matriz, tab_auditoria = st.tabs([
    "🏆 Resultados Ordenados (Ranking)",
    "🎬 Explorador Paso a Paso (Simulador)",
    "📖 Contexto del Proyecto",
    "🔢 Matriz de Costos",
    "🛡️ Auditoría de Hamiltonicidad",
])

# -------------------------------------------------------------
# PESTAÑA 1: RESULTADOS ORDENADOS (RANKING)
# -------------------------------------------------------------
with tab_ranking:
    st.markdown("### Ranking de Ciclos Factibles (Menor a Mayor Costo)")
    st.markdown("Clasificación de todos los ciclos hamiltonianos conexos ordenados desde la solución óptima global.")

    if total_factibles > 0:
        col_r_graf, col_r_info = st.columns([1.35, 1.05])

        with col_r_info:
            st.markdown(f"**Navegación del Ranking ({total_factibles} ciclos encontrados):**")

            b_first, b_prev, b_next, b_last = st.columns(4)
            with b_first:
                if st.button("⏮️ Inicio", use_container_width=True):
                    st.session_state.puesto_ranking = 1
                    st.rerun()
            with b_prev:
                if st.button("◀️ Ant.", use_container_width=True):
                    st.session_state.puesto_ranking = max(1, st.session_state.puesto_ranking - 1)
                    st.rerun()
            with b_next:
                if st.button("Sig. ▶️", use_container_width=True):
                    st.session_state.puesto_ranking = min(total_factibles, st.session_state.puesto_ranking + 1)
                    st.rerun()
            with b_last:
                if st.button("Fin ⏭️", use_container_width=True):
                    st.session_state.puesto_ranking = total_factibles
                    st.rerun()

            nuevo_puesto = st.number_input(
                f"Ir directo al puesto (1 al {total_factibles}):",
                min_value=1,
                max_value=total_factibles,
                value=st.session_state.puesto_ranking,
                step=1,
            )
            if nuevo_puesto != st.session_state.puesto_ranking:
                st.session_state.puesto_ranking = nuevo_puesto
                st.rerun()

            idx_ranking = st.session_state.puesto_ranking
            seleccion_ranking = rutas_validas_ranking[idx_ranking - 1]
            diferencia_opt = seleccion_ranking["costo"] - mejor_costo_global

            with st.container(border=True):
                if idx_ranking == 1:
                    st.markdown("**:green[★ RUTA ÓPTIMA GLOBAL (1er Puesto):]**")
                else:
                    st.markdown(f"**:orange[PUESTO #{idx_ranking} EN EL RANKING:]**")

                st.markdown(f"**{seleccion_ranking['ruta_str']}**")
                st.caption("Suma de pesos de la trayectoria:")
                st.code(f"{seleccion_ranking['desglose']} = {seleccion_ranking['costo']} unidades", language="text")

                if diferencia_opt == 0:
                    st.caption(":green[*(Menor distancia posible del grafo)*]")
                else:
                    st.caption(f":red[*(+{diferencia_opt} unidades por encima de la ruta óptima)*]")

        with col_r_graf:
            fig_rank = generar_figura_grafo(
                n, nombres, matriz,
                seleccion_ranking["ruta_indices"],
                "MEJORA_RECORD" if idx_ranking == 1 else "DESCARTADA_COSTOSA",
            )
            st.pyplot(fig_rank)
            plt.close(fig_rank)

        st.markdown("---")
        st.markdown("#### Tabla Comparativa de Soluciones Factibles")
        df_ranking = pd.DataFrame([
            {
                "Puesto": i + 1,
                "Ciclo Hamiltoniano": r["ruta_str"],
                "Costo Total": r["costo"],
                "Diferencia con Óptimo": f"+{r['costo'] - mejor_costo_global} u",
            }
            for i, r in enumerate(rutas_validas_ranking)
        ])
        st.dataframe(df_ranking, use_container_width=True, height=240)
    else:
        st.warning("El grafo generado no contiene ciclos hamiltonianos conexos con los parámetros actuales.")

# -------------------------------------------------------------
# PESTAÑA 2: SIMULADOR PASO A PASO (MANUAL Y AUTOMÁTICO CON PAUSA)
# -------------------------------------------------------------
with tab_simulador:
    st.markdown("### Simulación de Búsqueda, Comparaciones y Descartes")
    st.markdown("Observa cómo la computadora evalúa secuencialmente cada permutación, calcula su costo acumulado y decide si la descarta o si actualiza el récord.")

    modo_ejecucion = st.radio(
        "Modo de control:",
        ["🕹️ Manual (Paso a paso)", "▶️ Automático (Animación en vivo)"],
        horizontal=True,
    )

    if modo_ejecucion == "🕹️ Manual (Paso a paso)":
        c_nav1, c_nav2, c_nav3 = st.columns([1, 1, 2])
        with c_nav1:
            if st.button("⬅️️ Anterior (Paso)", use_container_width=True):
                st.session_state.paso_manual = max(0, st.session_state.paso_manual - 1)
        with c_nav2:
            if st.button("Siguiente (Paso) ➡️", use_container_width=True):
                st.session_state.paso_manual = min(total_pasos - 1, st.session_state.paso_manual + 1)
        with c_nav3:
            st.session_state.paso_manual = st.slider(
                "Navegador de iteración:",
                min_value=1,
                max_value=total_pasos,
                value=st.session_state.paso_manual + 1,
            ) - 1

        paso_actual_info = evaluaciones[st.session_state.paso_manual]

        c_graph_m, c_info_m = st.columns([1.4, 1])
        with c_graph_m:
            fig_m = generar_figura_grafo(n, nombres, matriz, paso_actual_info["ruta_indices"], paso_actual_info["estado"])
            st.pyplot(fig_m)
            plt.close(fig_m)

        with c_info_m:
            with st.container(border=True):
                st.markdown(f"#### Paso {paso_actual_info['paso']} de {total_pasos}")
                st.markdown(f"**Ruta Evaluada:** `{paso_actual_info['ruta_str']}`")
                st.caption("Cálculo de pesos:")
                st.code(paso_actual_info["desglose"], language="text")

                st.markdown("---")
                st.markdown("**Resultado del Análisis:**")
                if paso_actual_info["estado"] == "MEJORA_RECORD":
                    st.markdown(f":green[**★ NUEVO RÉCORD: {paso_actual_info['costo']} unidades**]")
                elif paso_actual_info["estado"] == "EMPATA_RECORD":
                    st.markdown(f":blue[**⚖️ EMPATE CON EL RÉCORD: {paso_actual_info['costo']} unidades**]")
                elif paso_actual_info["estado"] == "DESCARTADA_COSTOSA":
                    st.markdown(f":orange[**❌ DESCARTADA POR EXCESO DE COSTO ({paso_actual_info['costo']} u)**]")
                else:
                    st.markdown(":red[**🚫 DESCARTADA POR INFACTIBILIDAD**]")

                st.caption(f"**Decisión:** {paso_actual_info['motivo']}")

                st.markdown("---")
                record_texto = f"{paso_actual_info['costo_record']} unidades" if paso_actual_info["costo_record"] is not None else "Ninguno"
                st.markdown(f"**Récord Mínimo Vigente en este paso:** `{record_texto}`")

    else:
        # Modo Automático con Reproducción, Pausa y Reinicio
        velocidad = st.slider("Velocidad de simulación (segundos por paso):", min_value=0.05, max_value=1.0, value=0.25, step=0.05)

        c_play, c_pause, c_reset = st.columns(3)
        with c_play:
            if st.button("▶️ Iniciar / Reanudar", use_container_width=True):
                st.session_state.sim_activa = True
                st.rerun()
        with c_pause:
            if st.button("⏸️ Pausar", use_container_width=True):
                st.session_state.sim_activa = False
                st.rerun()
        with c_reset:
            # Texto corregido sin redundancia
            if st.button("⏮️ Reiniciar", use_container_width=True):
                st.session_state.sim_activa = False
                st.session_state.paso_auto = 0
                st.rerun()

        contenedor_animacion = st.empty()

        if st.session_state.sim_activa:
            while st.session_state.paso_auto < total_pasos and st.session_state.sim_activa:
                paso_datos = evaluaciones[st.session_state.paso_auto]
                with contenedor_animacion.container():
                    c_g_auto, c_i_auto = st.columns([1.4, 1])
                    with c_g_auto:
                        fig_auto = generar_figura_grafo(n, nombres, matriz, paso_datos["ruta_indices"], paso_datos["estado"])
                        st.pyplot(fig_auto)
                        plt.close(fig_auto)
                    with c_i_auto:
                        with st.container(border=True):
                            st.progress((st.session_state.paso_auto + 1) / total_pasos, text=f"Progreso: {st.session_state.paso_auto + 1}/{total_pasos} permutaciones")
                            st.markdown(f"#### Paso {paso_datos['paso']} / {total_pasos}")
                            st.markdown(f"**Trayectoria:** `{paso_datos['ruta_str']}`")
                            st.caption("Suma analítica:")
                            st.code(paso_datos["desglose"], language="text")

                            st.markdown("---")
                            if paso_datos["estado"] == "MEJORA_RECORD":
                                st.markdown(f":green[**★ NUEVO RÉCORD: {paso_datos['costo']} unidades**]")
                            elif paso_datos["estado"] == "EMPATA_RECORD":
                                st.markdown(f":blue[**⚖️ EMPATE CON EL RÉCORD: {paso_datos['costo']} unidades**]")
                            elif paso_datos["estado"] == "DESCARTADA_COSTOSA":
                                st.markdown(f":orange[**❌ DESCARTADA: {paso_datos['costo']} unidades**]")
                            else:
                                st.markdown(":red[**🚫 RUTA ROTA (INFACTIBLE)**]")

                            st.caption(f"**Motivo:** {paso_datos['motivo']}")
                            st.markdown("---")
                            rec_str = f"{paso_datos['costo_record']} unidades" if paso_datos["costo_record"] else "Aún sin solución"
                            st.markdown(f"**Récord Óptimo al momento:** `{rec_str}`")

                st.session_state.paso_auto += 1
                time.sleep(velocidad)

            if st.session_state.paso_auto >= total_pasos:
                st.session_state.sim_activa = False
                st.session_state.paso_auto = total_pasos - 1
                st.rerun()
        else:
            paso_pausa = evaluaciones[min(st.session_state.paso_auto, total_pasos - 1)]
            with contenedor_animacion.container():
                c_g_auto, c_i_auto = st.columns([1.4, 1])
                with c_g_auto:
                    fig_pausa = generar_figura_grafo(n, nombres, matriz, paso_pausa["ruta_indices"], paso_pausa["estado"])
                    st.pyplot(fig_pausa)
                    plt.close(fig_pausa)
                with c_i_auto:
                    with st.container(border=True):
                        st.markdown(f"#### ⏸️ Simulación en Pausa (Paso {paso_pausa['paso']} / {total_pasos})")
                        st.write("Pulsa **'Iniciar / Reanudar'** para continuar la animación automática desde este paso.")
                        st.markdown("---")
                        st.markdown(f"**Ruta actual retenida:** `{paso_pausa['ruta_str']}`")
                        st.caption(f"**Estado:** {paso_pausa['motivo']}")

    st.markdown("---")
    st.markdown("#### 📋 Bitácora Completa de Comparaciones y Descartes")
    st.caption("Detalle cronológico de cada decisión tomada por la fuerza bruta durante la búsqueda exhaustiva:")

    df_historial = pd.DataFrame([
        {
            "Paso": item["paso"],
            "Ruta Evaluada": item["ruta_str"],
            "Costo": item["costo"] if item["costo"] is not None else "—",
            "Condición": "Factible" if item["valida"] else "Infactible",
            "Decisión Matemática": item["motivo"],
        }
        for item in evaluaciones
    ])
    st.dataframe(df_historial, use_container_width=True, height=260)

# -------------------------------------------------------------
# PESTAÑA 3: CONTEXTO DEL PROYECTO
# -------------------------------------------------------------
with tab_contexto:
    with st.container(border=True):
        st.subheader("Fundamentación Teórica del Problema")
        st.markdown(
            """
            El **Problema del Agente Viajero** (*Traveling Salesperson Problem* o **TSP**) es uno de los problemas fundamentales de la **Matemática Computacional** y la **Optimización Combinatoria**:

            * **Definición Formal:** Sea un grafo no dirigido ponderado $G = (V, E, W)$, se busca una permutación cerrada $\\pi = (v_0, v_1, \\dots, v_{n-1}, v_0)$ con $v_0 = A$ que minimice la función objetivo:
            """
        )
        st.latex(r"C(\pi) = \sum_{i=0}^{n-1} w(v_i, v_{i+1})")
        st.markdown(
            """
            * **Filtrado de Simetría Bidireccional:**  
              En grafos no dirigidos, recorrer el ciclo en sentido horario genera exactamente el mismo costo que en sentido antihorario. Esta aplicación elimina automáticamente las reflexiones simétricas redundantes, reduciendo el espacio evaluado a la mitad exacta:
            """
        )
        st.latex(r"\frac{(n-1)!}{2}")
        st.markdown(
            """
            * **Metodología de Resolución:**
              1. **Generación Exhaustiva:** Se producen sistemáticamente las permutaciones independientes de los vértices restantes.
              2. **Auditoría de Aristas:** Se evalúa si el trayecto entre cada par de vértices consecutivos existe en la matriz de adyacencia. Si una sola arista no existe ($w = \\infty$), la ruta se cataloga como infactible.
              3. **Comparación y Récord Provisional:** Cada ciclo factible se contrasta contra el menor valor encontrado hasta ese paso. Si mejora la cota mínima, se actualiza el óptimo provisional; en caso contrario, se documenta el motivo del descarte.
            """
        )

# -------------------------------------------------------------
# PESTAÑA 4: MATRIZ DE COSTOS
# -------------------------------------------------------------
with tab_matriz:
    st.markdown("Matriz de adyacencia ponderada simétrica correspondiente al grafo $G = (V, E, W)$:")
    df_matriz = pd.DataFrame([[val if val is not None else "—" for val in fila] for fila in matriz], index=nombres, columns=nombres)
    st.dataframe(df_matriz, use_container_width=True)
    csv = df_matriz.to_csv().encode("utf-8")
    st.download_button(label="📥 Exportar Matriz a CSV", data=csv, file_name="matriz_adyacencia.csv", mime="text/csv")

# -------------------------------------------------------------
# PESTAÑA 5: AUDITORÍA DE HAMILTONICIDAD
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
