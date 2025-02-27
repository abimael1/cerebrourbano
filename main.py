import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from iot_manager import IoTManager
from sensor_processor import SensorDataProcessor
from chatbot import UrbanChatbot
from pages.monitoring import show_monitoring_dashboard
from pages.predictive import show_predictive_analysis
from pages.about import show_about_page
from assets.sample_data import generate_sample_data
from data_processor import DataProcessor
from utils import create_sidebar
from notifications import NotificationSystem, EmergencySystem, PredictiveAnalysis


# Set page config must be the first Streamlit command
st.set_page_config(
    page_title="Urban Brain - Mossoró",
    page_icon="🏙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
/* Global Theme */
.stApp {
    background: linear-gradient(to bottom right, #0b1120, #162030);
}

/* Main Title */
.main-title {
    color: #00f2fe;
    font-size: 2.5em;
    text-align: center;
    margin-bottom: 1rem;
}

.subtitle {
    color: rgba(255,255,255,0.7);
    text-align: center;
    font-size: 1.2em;
    margin-bottom: 2rem;
}

/* Features Grid */
.features-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 20px;
    margin: 40px 0;
}

.feature-card {
    background: rgba(22,32,48,0.7);
    border: 1px solid rgba(0,242,254,0.2);
    border-radius: 15px;
    padding: 25px;
    color: white;
    transition: all 0.3s ease;
}

.feature-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 8px 32px rgba(0,242,254,0.15);
}

.feature-icon {
    font-size: 2.5em;
    color: #00f2fe;
    margin-bottom: 15px;
}

.feature-title {
    color: #00f2fe;
    font-size: 1.5em;
    margin-bottom: 10px;
}

.feature-description {
    color: rgba(255,255,255,0.9);
    line-height: 1.6;
}

/* Chat Interface */
.chat-container {
    background: rgba(22,32,48,0.7);
    border: 1px solid rgba(0,242,254,0.2);
    border-radius: 15px;
    padding: 20px;
    height: 600px;
    display: flex;
    flex-direction: column;
    margin: 20px 0;
}

.messages-container {
    flex-grow: 1;
    overflow-y: auto;
    padding: 20px;
    margin-bottom: 20px;
}

.chat-message {
    display: flex;
    align-items: flex-start;
    margin-bottom: 20px;
    animation: fadeIn 0.3s ease-out;
}

.message-avatar {
    width: 35px;
    height: 35px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: bold;
    margin-right: 15px;
}

.user-avatar {
    background: linear-gradient(135deg, #00f2fe, #4facfe);
    color: white;
}

.assistant-avatar {
    background: rgba(0,242,254,0.2);
    color: #00f2fe;
}

.user-message {
    background: rgba(52, 53, 65, 0.7);
    padding: 15px;
    border-radius: 15px;
    margin-left: 50px;
    max-width: 80%;
}

.assistant-message {
    background: rgba(68, 70, 84, 0.7);
    padding: 15px;
    border-radius: 15px;
    margin-right: 50px;
    max-width: 80%;
}

.message-content {
    color: #ECECF1;
    line-height: 1.5;
}

.input-container {
    background: rgba(52, 53, 65, 0.9);
    border-top: 1px solid rgba(0,242,254,0.2);
    padding: 20px;
    display: flex;
    gap: 10px;
}

/* Sidebar */
section[data-testid="stSidebar"] > div {
    background: linear-gradient(to bottom, rgba(11,17,32,0.95), rgba(22,32,48,0.95));
    backdrop-filter: blur(10px);
}

.sidebar-header {
    text-align: center;
    padding: 20px;
    border-bottom: 1px solid rgba(0,242,254,0.2);
}

.sidebar-title {
    color: #00f2fe;
    font-size: 1.5em;
    margin-bottom: 10px;
}

/* Status Cards */
.status-card {
    background: rgba(0,242,254,0.1);
    border: 1px solid rgba(0,242,254,0.2);
    border-radius: 10px;
    padding: 15px;
    margin: 10px 0;
    text-align: center;
}

.status-icon {
    font-size: 1.5em;
    margin-bottom: 5px;
}

.status-value {
    color: #00f2fe;
    font-size: 1.2em;
    font-weight: bold;
    margin-bottom: 5px;
}

.status-label {
    color: rgba(255,255,255,0.7);
}

/* Topics Section */
.topics-section {
    background: rgba(22,32,48,0.7);
    border: 1px solid rgba(0,242,254,0.2);
    border-radius: 15px;
    padding: 20px;
    margin-bottom: 20px;
}

.topic-button {
    background: rgba(0,242,254,0.1);
    border: 1px solid rgba(0,242,254,0.2);
    border-radius: 10px;
    padding: 10px;
    margin: 5px 0;
    color: white;
    width: 100%;
    text-align: left;
    transition: all 0.3s ease;
}

.topic-button:hover {
    background: rgba(0,242,254,0.2);
    transform: translateX(5px);
}

@keyframes fadeIn {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
}
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'current_page' not in st.session_state:
    st.session_state.current_page = "Dashboard"
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'chatbot' not in st.session_state:
    st.session_state.chatbot = UrbanChatbot()
if 'notification_system' not in st.session_state:
    st.session_state.notification_system = NotificationSystem()
if 'emergency_system' not in st.session_state:
    st.session_state.emergency_system = EmergencySystem()
if 'predictive_analysis' not in st.session_state:
    st.session_state.predictive_analysis = PredictiveAnalysis()

def create_sidebar():
    st.sidebar.markdown("""
        <div class="sidebar-header">
            <div class="sidebar-title">Urban Brain</div>
        </div>
    """, unsafe_allow_html=True)

    navigation_options = {
        "Dashboard": "Página inicial com visão geral do sistema",
        "Monitoramento": "Dados em tempo real dos sensores",
        "Análise Preditiva": "Previsões e análises avançadas",
        "Sobre": "Informações sobre o projeto"
    }

    selected = st.sidebar.radio(
        "Navegação",
        list(navigation_options.keys()),
        format_func=lambda x: f"{x}\n{navigation_options[x]}"
    )

    return selected

def display_chat_interface():
    """Display the chatbot interface with ChatGPT-like styling"""

    # Layout com 3 colunas
    col1, col2, col3 = st.columns([1,2,1])

    # Coluna da esquerda: Tópicos sugeridos
    with col1:
        st.markdown("""
            <div class="topics-section">
                <h3 style="color: #00f2fe; margin-bottom: 15px;">Tópicos Sugeridos</h3>
            </div>
        """, unsafe_allow_html=True)

        topics = st.session_state.chatbot.get_topic_suggestions()
        for topic_id, topic_data in topics.items():
            with st.expander(topic_data['titulo']):
                for pergunta in topic_data['perguntas']:
                    if st.button(pergunta, key=f"btn_{topic_id}_{hash(pergunta)}"):
                        st.session_state.chat_history.append({
                            'role': 'user',
                            'content': pergunta
                        })
                        response = st.session_state.chatbot.get_response(pergunta)
                        st.session_state.chat_history.append({
                            'role': 'assistant',
                            'content': response
                        })
                        st.rerun()

    # Coluna central: Chat
    with col2:
        # Chat container
        st.markdown('<div class="chat-container">', unsafe_allow_html=True)

        # Welcome message if chat is empty
        if not st.session_state.chat_history:
            welcome_msg = st.session_state.chatbot.get_welcome_message()
            st.markdown(f"""
                <div class="chat-message">
                    <div class="message-avatar assistant-avatar">AI</div>
                    <div class="assistant-message">
                        <div class="message-content">{welcome_msg}</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

        # Messages container
        st.markdown('<div class="messages-container">', unsafe_allow_html=True)

        # Display chat messages
        for message in st.session_state.chat_history:
            if message['role'] == 'user':
                st.markdown(f"""
                    <div class="chat-message">
                        <div class="message-avatar user-avatar">U</div>
                        <div class="user-message">
                            <div class="message-content">{message['content']}</div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                    <div class="chat-message">
                        <div class="message-avatar assistant-avatar">AI</div>
                        <div class="assistant-message">
                            <div class="message-content">{message['content']}</div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

        # Input container
        st.markdown('<div class="input-container">', unsafe_allow_html=True)

        col1, col2 = st.columns([5,1])
        with col1:
            user_input = st.text_input(
                "",
                key="chat_input",
                placeholder="Digite sua mensagem...",
                label_visibility="collapsed"
            )
        with col2:
            send_button = st.button("Enviar", key="send_button")

        st.markdown('</div></div>', unsafe_allow_html=True)

        # Process input and generate response
        if send_button and user_input:
            st.session_state.chat_history.append({
                'role': 'user',
                'content': user_input
            })
            response = st.session_state.chatbot.get_response(user_input)
            st.session_state.chat_history.append({
                'role': 'assistant',
                'content': response
            })
            st.rerun()

    # Coluna da direita: Status da cidade
    with col3:
        st.markdown("""
            <div class="topics-section">
                <h3 style="color: #00f2fe; margin-bottom: 15px;">Status da Cidade</h3>
            </div>
        """, unsafe_allow_html=True)

        metrics = {
            '🌡️': {'value': '28°C', 'label': 'Temperatura'},
            '💨': {'value': 'Boa', 'label': 'Qualidade do Ar'},
            '🚗': {'value': '45%', 'label': 'Tráfego'},
            '💧': {'value': 'Normal', 'label': 'Nível de Chuva'},
            '⚡': {'value': '2.8MW', 'label': 'Consumo Energia'}
        }

        for emoji, data in metrics.items():
            st.markdown(f"""
                <div class="status-card">
                    <div class="status-icon">{emoji}</div>
                    <div class="status-value">{data['value']}</div>
                    <div class="status-label">{data['label']}</div>
                </div>
            """, unsafe_allow_html=True)


def load_data():
    return generate_sample_data()

data = load_data()
data_processor = DataProcessor(data)


def display_emergency_panel():
    """Display emergency controls and alerts panel"""
    st.markdown("""
        <div style="margin-top: 40px;">
            <h2 style="color: #00f2fe; margin-bottom: 20px;">Centro de Controle de Emergências</h2>
        </div>
    """, unsafe_allow_html=True)

    # Layout em três colunas
    alert_col, emergency_col, predict_col = st.columns(3)

    # Coluna de Alertas
    with alert_col:
        st.markdown("""
            <div style="background: rgba(22,32,48,0.7); padding: 20px; border-radius: 15px; border: 1px solid rgba(0,242,254,0.2);">
                <h3 style="color: #00f2fe; margin-bottom: 15px;">Alertas Ativos</h3>
            </div>
        """, unsafe_allow_html=True)

        active_alerts = st.session_state.notification_system.get_active_alerts()
        for alert in active_alerts:
            severity_color = {
                "high": "🔴",
                "medium": "🟡",
                "low": "🟢"
            }.get(alert["severity"], "⚪")

            st.markdown(f"""
                <div style="background: rgba(0,242,254,0.1); padding: 15px; border-radius: 10px; margin: 10px 0;">
                    <div style="display: flex; align-items: center;">
                        <span>{severity_color} {alert['type'].upper()}</span>
                    </div>
                    <div style="color: rgba(255,255,255,0.9); margin: 10px 0;">
                        {alert['message']}
                    </div>
                    <div style="color: rgba(255,255,255,0.6); font-size: 0.9em;">
                        {alert['location']} - {alert['timestamp'].split('T')[1][:5]}
                    </div>
                </div>
            """, unsafe_allow_html=True)

    # Coluna de Emergência
    with emergency_col:
        st.markdown("""
            <div style="background: rgba(22,32,48,0.7); padding: 20px; border-radius: 15px; border: 1px solid rgba(0,242,254,0.2);">
                <h3 style="color: #00f2fe; margin-bottom: 15px;">Serviços de Emergência</h3>
            </div>
        """, unsafe_allow_html=True)

        # Botões de Emergência
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🚨 POLÍCIA", key="police_btn", use_container_width=True):
                st.session_state.emergency_system.dispatch_unit(
                    "police", "Centro", "emergency_call"
                )
                st.success("Polícia notificada! Unidades a caminho.")

            if st.button("🚑 AMBULÂNCIA", key="ambulance_btn", use_container_width=True):
                st.session_state.emergency_system.dispatch_unit(
                    "ambulance", "Centro", "medical_emergency"
                )
                st.success("Ambulância notificada! Unidades a caminho.")

        with col2:
            if st.button("🚒 BOMBEIROS", key="fire_btn", use_container_width=True):
                st.session_state.emergency_system.dispatch_unit(
                    "fire", "Centro", "fire_emergency"
                )
                st.success("Bombeiros notificados! Unidades a caminho.")

            if st.button("🆘 PÂNICO", key="panic_btn", use_container_width=True):
                st.session_state.notification_system.create_alert(
                    "panic", "Botão de pânico acionado!", "high", "Centro"
                )
                st.error("Alerta de pânico enviado! Todas as unidades notificadas.")

    # Coluna de Análise Preditiva
    with predict_col:
        st.markdown("""
            <div style="background: rgba(22,32,48,0.7); padding: 20px; border-radius: 15px; border: 1px solid rgba(0,242,254,0.2);">
                <h3 style="color: #00f2fe; margin-bottom: 15px;">Análise Preditiva</h3>
            </div>
        """, unsafe_allow_html=True)

        # Mapa de Calor de Risco
        high_risk_zones = st.session_state.predictive_analysis.get_high_risk_zones()
        st.markdown("### 🎯 Zonas de Alto Risco")
        for zone, data in high_risk_zones.items():
            st.markdown(f"""
                <div style="background: rgba(0,242,254,0.1); padding: 15px; border-radius: 10px; margin: 5px 0;">
                    <div style="color: #00f2fe;">{zone}</div>
                    <div style="color: rgba(255,255,255,0.7);">
                        Risco: {data['risk_score']:.1f}%
                    </div>
                </div>
            """, unsafe_allow_html=True)

        # Padrões de Incidentes
        patterns = st.session_state.predictive_analysis.analyze_patterns()
        st.markdown("### 📊 Padrões Detectados")
        st.markdown(f"""
            <div style="background: rgba(0,242,254,0.1); padding: 15px; border-radius: 10px; margin: 5px 0;">
                <div><strong>Horários de Pico:</strong> {', '.join(patterns['peak_hours'])}</div>
                <div><strong>Dias Críticos:</strong> {', '.join(patterns['high_risk_days'])}</div>
                <div><strong>Tipos Comuns:</strong> {', '.join(patterns['common_types'])}</div>
            </div>
        """, unsafe_allow_html=True)


def main():
    selected_page = create_sidebar()

    if selected_page == "Dashboard":
        st.markdown("""
            <div class="main-title">Urban Brain</div>
            <div class="subtitle">Sistema de Gerenciamento Urbano Inteligente de Mossoró</div>
        """, unsafe_allow_html=True)

        # Features Grid
        st.markdown("""
        <div class="features-grid">
            <div class="feature-card">
                <div class="feature-icon">🤖</div>
                <div class="feature-title">IA Avançada</div>
                <div class="feature-description">
                    Processamento em tempo real de dados urbanos com inteligência artificial.
                </div>
            </div>
            <div class="feature-card">
                <div class="feature-icon">📊</div>
                <div class="feature-title">Análise em Tempo Real</div>
                <div class="feature-description">
                    Monitoramento contínuo de métricas urbanas e alertas importantes.
                </div>
            </div>
            <div class="feature-card">
                <div class="feature-icon">🌍</div>
                <div class="feature-title">Foco Local</div>
                <div class="feature-description">
                    Soluções personalizadas para as necessidades de Mossoró.
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        display_chat_interface()
        display_emergency_panel()

    elif selected_page == "Monitoramento":
        show_monitoring_dashboard()
    elif selected_page == "Análise Preditiva":
        show_predictive_analysis()
    else:
        show_about_page()

if __name__ == "__main__":
    main()