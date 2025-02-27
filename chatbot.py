"""
Chatbot for the Urban Intelligence Platform
"""
import os
import requests
import json
from datetime import datetime
import random
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)  # Changed to DEBUG for more detailed logs

class UrbanChatbot:
    def __init__(self):
        self.api_key = os.environ.get('DEEPSEEK_API_KEY')

        # Respostas locais para quando a API falhar
        self.fallback_responses = {
            "qualidade_ar": "De acordo com os últimos dados dos sensores, a qualidade do ar está dentro dos padrões normais. Você pode verificar dados detalhados no painel de monitoramento.",
            "trafego": "O tráfego está fluindo normalmente nas principais vias. Recomendo verificar o mapa de calor de tráfego para informações em tempo real.",
            "alagamento": "Não há alertas de alagamento no momento. Os níveis de chuva estão dentro do normal.",
            "temperatura": "A temperatura atual está dentro da média para esta época do ano. Consulte o painel de monitoramento para dados específicos por região.",
            "default": "Desculpe, estou com dificuldade para acessar algumas informações no momento. Por favor, consulte o painel de monitoramento para dados em tempo real ou tente reformular sua pergunta."
        }

        # Palavras-chave para identificar tópicos
        self.topic_keywords = {
            "qualidade_ar": ["ar", "poluição", "qualidade", "respirar", "aqi"],
            "trafego": ["trânsito", "tráfego", "congestionamento", "via", "rua", "avenida"],
            "alagamento": ["chuva", "alagamento", "enchente", "água", "inundação"],
            "temperatura": ["temperatura", "calor", "frio", "clima", "tempo"]
        }

        # Mensagens de boas-vindas
        self.welcome_messages = [
            "Olá! Sou o assistente virtual de Mossoró. Posso ajudar com informações sobre:"
            "\n• Qualidade do ar e condições ambientais"
            "\n• Situação do trânsito em tempo real"
            "\n• Alertas de alagamentos"
            "\n• Projetos smart city em andamento"
            "\n\nComo posso ajudar?",

            "Oi! Sou especialista em dados urbanos de Mossoró. Posso informar sobre:"
            "\n• Monitoramento ambiental"
            "\n• Condições de tráfego"
            "\n• Alertas meteorológicos"
            "\n• Iniciativas de cidade inteligente"
            "\n\nO que você gostaria de saber?"
        ]

        # Tópicos sugeridos com perguntas exemplo
        self.suggested_topics = {
            'qualidade_ar': {
                'titulo': '🌡️ Qualidade do Ar',
                'perguntas': [
                    "Como está a qualidade do ar no Centro hoje?",
                    "Quais áreas têm melhor qualidade do ar?",
                    "Existe algum alerta de poluição?"
                ]
            },
            'trafego': {
                'titulo': '🚗 Trânsito',
                'perguntas': [
                    "Como está o trânsito na região central?",
                    "Quais vias estão congestionadas?",
                    "Qual o melhor horário para evitar congestionamentos?"
                ]
            },
            'alagamentos': {
                'titulo': '💧 Alagamentos',
                'perguntas': [
                    "Existe risco de alagamento hoje?",
                    "Quais áreas estão em alerta?",
                    "Como está o nível de chuva nas últimas horas?"
                ]
            },
            'projetos': {
                'titulo': '🏗️ Projetos Smart City',
                'perguntas': [
                    "Quais projetos smart city estão em andamento?",
                    "Como funcionam os sensores urbanos?",
                    "Quando serão instaladas novas câmeras inteligentes?"
                ]
            }
        }

        # Respostas rápidas para interações comuns
        self.quick_responses = {
            'saudacao': [
                "Olá! Sou o assistente virtual de Mossoró. Como posso ajudar?",
                "Oi! Estou aqui para ajudar com informações sobre nossa cidade inteligente.",
                "Bem-vindo! Como posso auxiliar você hoje?"
            ],
            'agradecimento': [
                "Por nada! Estou sempre aqui para ajudar a tornar Mossoró mais inteligente.",
                "Disponível sempre que precisar! Juntos estamos construindo uma cidade melhor.",
                "É um prazer ajudar! Continue acompanhando as novidades da nossa smart city."
            ],
            'despedida': [
                "Até mais! Continuarei monitorando nossa cidade 24/7.",
                "Até a próxima! Não deixe de acompanhar os projetos de transformação digital.",
                "Tchau! Volte sempre para saber mais sobre Mossoró."
            ],
            'erro': [
                "Desculpe, estou com algumas limitações técnicas no momento. Posso tentar ajudar com informações básicas sobre a cidade.",
                "Estou passando por uma atualização. Por favor, tente novamente em alguns minutos.",
                "Minhas respostas estão limitadas no momento, mas posso ajudar com informações do painel de monitoramento."
            ]
        }

    def identify_topic(self, text: str) -> str:
        """Identifica o tópico principal da pergunta"""
        text = text.lower()
        for topic, keywords in self.topic_keywords.items():
            if any(keyword in text for keyword in keywords):
                return topic
        return "default"

    def get_fallback_response(self, text: str) -> str:
        """Retorna uma resposta local baseada no tópico identificado"""
        topic = self.identify_topic(text)
        return self.fallback_responses.get(topic, self.fallback_responses["default"])

    def get_topic_suggestions(self):
        """Retorna sugestões de tópicos e perguntas"""
        return self.suggested_topics

    def get_welcome_message(self):
        """Retorna mensagem de boas-vindas aleatória"""
        return random.choice(self.welcome_messages)

    def get_response(self, user_input):
        """Generate response based on user input"""
        if not user_input.strip():
            return "Por favor, digite sua mensagem."

        try:
            # Detectar saudações
            greetings = ['oi', 'olá', 'ola', 'bom dia', 'boa tarde', 'boa noite']
            if any(greeting in user_input.lower() for greeting in greetings):
                return random.choice(self.quick_responses['saudacao'])

            # Detectar agradecimentos
            thanks = ['obrigado', 'obrigada', 'valeu', 'agradeço']
            if any(thank in user_input.lower() for thank in thanks):
                return random.choice(self.quick_responses['agradecimento'])

            # Detectar despedidas
            goodbyes = ['tchau', 'até', 'adeus', 'falou']
            if any(bye in user_input.lower() for bye in goodbyes):
                return random.choice(self.quick_responses['despedida'])

            try:
                # API request setup
                headers = {
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {self.api_key}'
                }

                # Create system prompt
                system_prompt = """Você é o Cérebro Urbano, assistente virtual especializado em Mossoró.
                Forneça respostas diretas e práticas sobre:
                1. Qualidade do ar e condições ambientais
                2. Situação do trânsito em tempo real
                3. Alertas de alagamentos
                4. Projetos smart city

                Use dados em tempo real quando disponíveis e mantenha um tom informativo e prestativo."""

                # Create API payload
                payload = {
                    'model': 'deepseek-chat',
                    'messages': [
                        {
                            'role': 'system',
                            'content': system_prompt
                        },
                        {
                            'role': 'user',
                            'content': user_input
                        }
                    ],
                    'temperature': 0.7,
                    'max_tokens': 500
                }

                # Make API request
                response = requests.post(
                    'https://api.deepinfra.com/v1/openai/chat/completions',
                    headers=headers,
                    json=payload,
                    timeout=10
                )

                # Handle API response
                if response.status_code == 200:
                    return response.json()['choices'][0]['message']['content']
                else:
                    logger.error(f"API Error: {response.status_code} - {response.text}")
                    # Fallback to local response system
                    return self.get_fallback_response(user_input)

            except requests.exceptions.RequestException as e:
                logger.error(f"API Request Error: {str(e)}")
                return self.get_fallback_response(user_input)

        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            return random.choice(self.quick_responses['erro'])