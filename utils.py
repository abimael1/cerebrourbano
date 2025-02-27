import streamlit as st

def create_sidebar():
    """Create sidebar with modern navigation options"""
    st.sidebar.markdown("""
    <div style="text-align: center; padding: 20px 0;">
        <div style="font-size: 24px; background: linear-gradient(120deg, #00f2fe, #4facfe); 
                    -webkit-background-clip: text; -webkit-text-fill-color: transparent; 
                    font-weight: 700; margin-bottom: 10px;">
            Urban Brain
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.sidebar.markdown("---")

    options = {
        "Dashboard": {
            "icon": "📊",
            "desc": "Visão geral do sistema"
        },
        "Monitoramento": {
            "icon": "📡",
            "desc": "Dados em tempo real"
        },
        "Chatbot": {
            "icon": "💬",
            "desc": "Assistente virtual"
        },
        "Análise Preditiva": {
            "icon": "📈",
            "desc": "Previsões e tendências"
        },
        "Sobre": {
            "icon": "ℹ️",
            "desc": "Informações do projeto"
        }
    }

    st.sidebar.markdown("""
    <style>
    div[data-testid="stRadio"] > div {
        background-color: rgba(22, 32, 48, 0.7);
        border-radius: 15px;
        padding: 10px;
        margin-bottom: 10px;
        border: 1px solid rgba(0,242,254,0.2);
        backdrop-filter: blur(10px);
    }

    div[data-testid="stRadio"] > div:hover {
        border-color: rgba(0,242,254,0.4);
        transform: translateY(-2px);
        transition: all 0.3s ease;
    }

    div[data-testid="stRadio"] > div > label {
        background: transparent !important;
        border: none !important;
        padding: 10px !important;
    }

    div[data-testid="stRadio"] > div > label > div {
        color: white !important;
    }

    div[data-testid="stRadio"] > div > label[data-checked="true"] {
        background: linear-gradient(135deg, rgba(0,242,254,0.2), rgba(0,242,254,0.1)) !important;
        border-radius: 10px;
    }

    .navigation-desc {
        font-size: 0.8em;
        opacity: 0.7;
        margin-top: 2px;
    }
    </style>
    """, unsafe_allow_html=True)

    selected = st.sidebar.radio(
        "Navegação",
        options.keys(),
        format_func=lambda x: f'{options[x]["icon"]} {x}\n<div class="navigation-desc">{options[x]["desc"]}</div>',
        label_visibility="collapsed"
    )

    # Add system status indicators
    st.sidebar.markdown("---")
    st.sidebar.markdown("""
    <div style='padding: 10px; background: rgba(22, 32, 48, 0.7); border-radius: 10px; 
                border: 1px solid rgba(0,242,254,0.2);'>
        <div style='font-size: 0.8em; color: #00f2fe;'>Status do Sistema</div>
        <div style='display: flex; align-items: center; margin-top: 5px;'>
            <span style='color: #00ff00; margin-right: 5px;'>●</span>
            <span style='font-size: 0.9em;'>Todos serviços operacionais</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    return selected

def show_metrics(data_processor):
    """Display key metrics in the dashboard"""
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            label="Média Diária de Resíduos",
            value=f"{data_processor.get_daily_summary()} kg"
        )

    stats = data_processor.get_area_statistics()
    with col2:
        st.metric(
            label="Área Mais Produtiva",
            value=f"{stats['mean'].idxmax()}",
            delta=f"{stats['mean'].max():.0f} kg"
        )

    with col3:
        st.metric(
            label="Área Menos Produtiva",
            value=f"{stats['mean'].idxmin()}",
            delta=f"{stats['mean'].min():.0f} kg"
        )

def show_about():
    """Display information about the project"""
    st.markdown("""
    # Sobre o Cérebro Urbano

    O Cérebro Urbano é uma iniciativa inovadora que utiliza inteligência artificial 
    para transformar cidades em ecossistemas inteligentes e sustentáveis.

    ## Funcionalidades
    - 🤖 Chatbot inteligente para interação
    - 📊 Análise de dados urbanos
    - 🔮 Previsões baseadas em ML
    - 📈 Visualizações interativas

    ## Objetivos
    - Otimizar a gestão de resíduos
    - Melhorar a eficiência urbana
    - Promover sustentabilidade
    - Facilitar tomada de decisões
    """)