"""Módulo de estilos: CSS WCAG 2.2 AA para la interfaz"""

CSS_WCAG = """
<style>
    /* Ocultar todo el chrome de Streamlit del árbol de accesibilidad */
    #MainMenu, footer, header,
    [data-testid="stHeader"],
    [data-testid="stToolbar"],
    [data-testid="stToolbarActions"],
    [data-testid="stDecoration"],
    [data-testid="stMainMenu"],
    [data-testid="stStatusWidget"],
    .stDeployButton,
    .stAppDeployButton,
    .stStatusWidget,
    [data-testid="manage-app-button"],
    [data-testid="stManageApp"],
    [data-testid="stBottom"],
    [data-testid="stBottomBlockContainer"] {
        display: none !important;
    }

    /* Ocultar anchor links de headings (Streamlit los agrega automáticamente) */
    [data-testid="stHeaderActionElements"],
    a[data-testid="stHeaderLink"],
    .stMarkdown h1 a,
    .stMarkdown h2 a,
    .stMarkdown h3 a {
        display: none !important;
    }

    /* Streamlit Cloud: ocultar manage app overlay */
    [class*="manage"], [data-testid*="manage"],
    iframe[title="Manage app"] {
        display: none !important;
    }

    /* Ocultar iframes invisibles (contador) de lectores de pantalla */
    iframe[height="0"],
    iframe[style*="height: 0px"] {
        display: none !important;
    }

    /* Forzar tema claro global */
    .stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
        background-color: #ffffff !important;
        color: #1a1a1a !important;
    }

    [data-testid="stSidebar"] {
        background-color: #f8f9fa !important;
    }

    /* Borde superior degradado rasta */
    .stApp::before {
        content: '';
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, #228B22 0%, #228B22 33%, #FFD700 33%, #FFD700 66%, #DC143C 66%, #DC143C 100%);
        z-index: 9999;
    }

    /* Animación rasta durante procesamiento */
    @keyframes rasta-slide {
        0% { background-position: 0% 0; }
        100% { background-position: 200% 0; }
    }

    .rasta-processing .stApp::before {
        height: 6px;
        background: repeating-linear-gradient(90deg, #228B22 0%, #FFD700 16%, #DC143C 33%, #228B22 50%);
        background-size: 200% 100%;
        animation: rasta-slide 1.5s linear infinite;
    }

    *:focus {
        outline: 3px solid #0056b3 !important;
        outline-offset: 3px !important;
    }

    /* Texto general */
    body, .stMarkdown, p, label, .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
        color: #1a1a1a !important;
    }

    /* Expander: fondo claro y texto visible siempre */
    [data-testid="stExpander"] {
        background-color: #ffffff !important;
        border-color: #ccc !important;
    }

    [data-testid="stExpander"] summary,
    [data-testid="stExpander"] summary span,
    [data-testid="stExpander"] div[data-testid="stExpanderDetails"],
    [data-testid="stExpander"] div[data-testid="stExpanderDetails"] p,
    [data-testid="stExpander"] div[data-testid="stExpanderDetails"] li {
        color: #1a1a1a !important;
        background-color: #ffffff !important;
    }

    /* Selectbox: fondo claro y texto visible */
    .stSelectbox [data-testid="stMarkdownContainer"],
    .stSelectbox div[data-baseweb="select"],
    .stSelectbox div[data-baseweb="select"] > div {
        background-color: #ffffff !important;
        color: #1a1a1a !important;
    }

    .stSelectbox svg {
        fill: #1a1a1a !important;
    }

    /* Dropdown del selectbox (lista desplegable) */
    div[data-baseweb="popover"],
    div[data-baseweb="popover"] ul,
    div[data-baseweb="popover"] li {
        background-color: #ffffff !important;
        color: #1a1a1a !important;
    }

    /* Text area: fondo claro y texto visible siempre */
    .stTextArea textarea {
        color: #1a1a1a !important;
        background-color: #ffffff !important;
        border-color: #ccc !important;
    }

    .stTextArea label {
        color: #1a1a1a !important;
    }

    /* File uploader: fondo claro y texto visible */
    [data-testid="stFileUploader"],
    [data-testid="stFileUploader"] section,
    [data-testid="stFileUploader"] section > div {
        background-color: #ffffff !important;
        color: #1a1a1a !important;
    }

    [data-testid="stFileUploader"] small,
    [data-testid="stFileUploader"] span {
        color: #1a1a1a !important;
    }

    [data-testid="stFileUploader"] section > button {
        color: #0056b3 !important;
    }

    /* Botones principales */
    .stButton > button {
        min-height: 44px;
        min-width: 44px;
        font-size: 1rem;
        padding: 0.75rem 1.5rem;
        background-color: #0056b3 !important;
        color: #ffffff !important;
        border: 2px solid #0056b3 !important;
    }

    .stButton > button:hover {
        background-color: #004494 !important;
    }

    .stButton > button:focus {
        box-shadow: 0 0 0 3px #ffffff, 0 0 0 6px #0056b3 !important;
    }

    /* Download buttons */
    .stDownloadButton > button {
        min-height: 44px;
        min-width: 44px;
        font-size: 1rem;
        padding: 0.75rem 1.5rem;
        background-color: #0056b3 !important;
        color: #ffffff !important;
        border: 2px solid #0056b3 !important;
    }

    .stDownloadButton > button:hover {
        background-color: #004494 !important;
    }

    .stDownloadButton > button:focus {
        box-shadow: 0 0 0 3px #ffffff, 0 0 0 6px #0056b3 !important;
    }

    /* Barra de progreso */
    .stProgress > div {
        background-color: #ffffff !important;
    }

    .stProgress [data-testid="stMarkdownContainer"] p {
        color: #1a1a1a !important;
    }

    /* Alertas: st.success y st.error */
    [data-testid="stAlert"] {
        color: #1a1a1a !important;
    }

    [data-testid="stAlert"] p {
        color: #1a1a1a !important;
    }

    .block-container {
        max-width: 600px;
        padding: 1rem;
    }

    /* Separadores con degradado rasta */
    hr {
        border: none !important;
        height: 2px !important;
        background: linear-gradient(90deg, #228B22 0%, #FFD700 50%, #DC143C 100%) !important;
        opacity: 0.6 !important;
        margin: 1rem 0 !important;
    }

    /* Radio buttons más accesibles */
    .stRadio > div {
        display: flex;
        flex-direction: column;
        gap: 8px;
    }

    .stRadio > div > label {
        min-height: 44px !important;
        display: flex !important;
        align-items: center !important;
        padding: 8px 12px !important;
        border: 2px solid #ccc !important;
        border-radius: 4px !important;
        cursor: pointer !important;
        background: #fff !important;
        color: #1a1a1a !important;
    }

    .stRadio > div > label:focus-within {
        border-color: #0056b3 !important;
        outline: 2px solid #0056b3 !important;
    }

    .stRadio > div > label > div:first-child {
        min-width: 24px !important;
        min-height: 24px !important;
    }

    /* Estilo para título con colores rasta */
    .rasta-title .gary-g { color: #228B22; }
    .rasta-title .gary-a { color: #B8860B; }
    .rasta-title .gary-r { color: #DC143C; }
    .rasta-title .gary-y { color: #228B22; }

    /* Footer con banda rasta */
    .rasta-footer {
        text-align: center;
        padding-top: 0.5rem;
        border-top: 3px solid;
        border-image: linear-gradient(90deg, #228B22 0%, #FFD700 50%, #DC143C 100%) 1;
        color: #1a1a1a !important;
    }

    .rasta-footer p {
        color: #555 !important;
    }

    /* Ocultar lista de archivos subidos (el flujo es directo) */
    [data-testid="stFileUploaderFile"] {
        display: none !important;
    }

    /* Accesibilidad: ocultar icono Material de lectores de pantalla */
    [data-testid="stExpander"] summary [data-testid="stIconMaterial"],
    [data-testid="stExpander"] summary span[translate="no"],
    [data-testid="stExpander"] summary .exvv1vr0 {
        display: none !important;
    }

    [data-testid="stExpander"] details > summary {
        list-style: none !important;
    }

    [data-testid="stExpander"] details > summary::-webkit-details-marker {
        display: none !important;
    }

    [data-testid="stExpander"] details > summary::before {
        content: "" !important;
        display: inline-block !important;
        width: 0 !important;
        height: 0 !important;
        border-left: 6px solid #1a1a1a !important;
        border-top: 5px solid transparent !important;
        border-bottom: 5px solid transparent !important;
        margin-right: 8px !important;
        vertical-align: middle !important;
        transition: transform 0.2s !important;
    }

    [data-testid="stExpander"] details[open] > summary::before {
        transform: rotate(90deg) !important;
    }

    /* Texto solo para screen readers (invisible visualmente) */
    .sr-only {
        position: absolute !important;
        width: 1px !important;
        height: 1px !important;
        padding: 0 !important;
        margin: -1px !important;
        overflow: hidden !important;
        clip: rect(0, 0, 0, 0) !important;
        white-space: nowrap !important;
        border: 0 !important;
    }

    /* ========== RESPONSIVE MÓVIL ========== */
    @media (max-width: 640px) {
        /* Contenedor principal: más padding lateral */
        .block-container {
            max-width: 100% !important;
            padding: 0.5rem 0.75rem !important;
        }

        /* Título más pequeño en móvil */
        .rasta-title {
            font-size: 1.8rem !important;
        }

        /* Botones: texto más compacto, siempre ancho completo */
        .stButton > button,
        .stDownloadButton > button {
            font-size: 0.9rem !important;
            padding: 0.6rem 0.8rem !important;
            white-space: nowrap !important;
            overflow: hidden !important;
            text-overflow: ellipsis !important;
        }

        /* Columnas de resultados: apilar verticalmente */
        [data-testid="stHorizontalBlock"] {
            flex-wrap: wrap !important;
        }

        [data-testid="stHorizontalBlock"] > [data-testid="stColumn"] {
            min-width: 100% !important;
            flex: 1 1 100% !important;
        }

        /* Thumbnail centrado en móvil */
        [data-testid="stImage"] {
            text-align: center !important;
        }

        [data-testid="stImage"] img {
            margin: 0 auto !important;
        }

        /* Text area más bajo en móvil */
        .stTextArea textarea {
            height: 80px !important;
        }

        /* Footer texto más pequeño */
        .rasta-footer p {
            font-size: 0.75rem !important;
        }

        /* Expander más compacto */
        [data-testid="stExpander"] summary {
            font-size: 0.9rem !important;
            padding: 8px !important;
        }

        /* File uploader: ocultar drag & drop, dejar solo botón */
        [data-testid="stFileUploader"] section {
            border: none !important;
            padding: 0 !important;
            background: transparent !important;
            min-height: auto !important;
        }

        /* Ocultar textos, iconos y separadores del drag & drop */
        [data-testid="stFileUploader"] section span,
        [data-testid="stFileUploader"] section small,
        [data-testid="stFileUploader"] section p,
        [data-testid="stFileUploader"] section svg,
        [data-testid="stFileUploader"] section img {
            display: none !important;
        }

        /* Mostrar solo el botón */
        [data-testid="stFileUploader"] section button {
            display: inline-flex !important;
            width: 100% !important;
            min-height: 44px !important;
            font-size: 1rem !important;
            background-color: #0056b3 !important;
            color: #ffffff !important;
            border: 2px solid #0056b3 !important;
            border-radius: 4px !important;
            padding: 0.75rem 1rem !important;
            justify-content: center !important;
        }

        /* Texto dentro del botón debe ser visible */
        [data-testid="stFileUploader"] section button span,
        [data-testid="stFileUploader"] section button p {
            display: inline !important;
            color: #ffffff !important;
        }
    }

</style>
"""
