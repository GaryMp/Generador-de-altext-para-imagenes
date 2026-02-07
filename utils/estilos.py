"""Módulo de estilos: CSS WCAG 2.2 AA para la interfaz"""

CSS_WCAG = """
<style>
    #MainMenu, footer, header {visibility: hidden;}

    /* Forzar tema claro */
    .stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
        background-color: #ffffff !important;
    }

    [data-testid="stSidebar"] {
        background-color: #f8f9fa !important;
    }

    /* Opción 1: Borde superior degradado rasta */
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

    *:focus {
        outline: 3px solid #0056b3 !important;
        outline-offset: 3px !important;
    }

    body, .stMarkdown, p, span, label, .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
        color: #1a1a1a !important;
    }

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

    .block-container {
        max-width: 600px;
        padding: 1rem;
    }

    /* Opción 3: Separadores con degradado rasta */
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
    }

    .stRadio > div > label:focus-within {
        border-color: #0056b3 !important;
        outline: 2px solid #0056b3 !important;
    }

    .stRadio > div > label > div:first-child {
        min-width: 24px !important;
        min-height: 24px !important;
    }

    /* Opción 2: Estilo para título con colores rasta */
    .rasta-title .gary-g { color: #228B22; }
    .rasta-title .gary-a { color: #FFD700; }
    .rasta-title .gary-r { color: #DC143C; }
    .rasta-title .gary-y { color: #228B22; }

    /* Opción 5: Footer con banda rasta */
    .rasta-footer {
        text-align: center;
        padding-top: 0.5rem;
        border-top: 3px solid;
        border-image: linear-gradient(90deg, #228B22 0%, #FFD700 50%, #DC143C 100%) 1;
    }
</style>
"""
