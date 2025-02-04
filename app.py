import streamlit as st
import requests
import json

def get_free_ai_solutions():
    return {
        "Hugging Face": {
            "description": "Plataforma de modelos de IA open-source.",
            "limits": "Gratuito com limite de chamadas e necessidade de token.",
            "average_daily_requests": "~500 dependendo do modelo.",
            "setup_steps": [
                "Criar uma conta no Hugging Face.",
                "Gerar um Token de Acesso (Settings > Access Tokens).",
                "Selecionar um modelo gratuito disponível."
            ],
            "config_fields": ["Hugging Face Token", "Modelo"]
        },
        "Cohere": {
            "description": "Modelos de linguagem avançados para geração de texto.",
            "limits": "Plano gratuito permite 100 chamadas por mês.",
            "average_daily_requests": "~3 chamadas por dia no plano gratuito.",
            "setup_steps": [
                "Criar uma conta no Cohere.",
                "Obter a API Key na dashboard do Cohere."
            ],
            "config_fields": ["Cohere API Key"]
        },
        "OpenAI (GPT)": {
            "description": "Modelos GPT da OpenAI.",
            "limits": "Plano gratuito permite US$5 em créditos por 3 meses.",
            "average_daily_requests": "Varia conforme o uso dos créditos.",
            "setup_steps": [
                "Criar uma conta na OpenAI.",
                "Obter a API Key na dashboard da OpenAI."
            ],
            "config_fields": ["OpenAI API Key"]
        }
    }

def get_hugging_face_models():
    response = requests.get("https://huggingface.co/api/models?sort=downloads&limit=5")
    if response.status_code == 200:
        return [model['modelId'] for model in response.json()]
    return []

st.title("Configuração de IA Gratuita")

solutions = get_free_ai_solutions()
solution_name = st.selectbox("Escolha a solução de IA:", list(solutions.keys()))

if solution_name:
    solution = solutions[solution_name]
    st.subheader(solution_name)
    st.write(f"**Descrição:** {solution['description']}")
    st.write(f"**Limites:** {solution['limits']}")
    st.write(f"**Média de requisições diárias:** {solution['average_daily_requests']}")
    
    st.subheader("Passo a passo para configuração:")
    for step in solution["setup_steps"]:
        st.write(f"- {step}")
    
    st.subheader("Configuração")
    config = {}
    for field in solution["config_fields"]:
        config[field] = st.text_input(field, type="password" if "Key" in field else "default")
    
    if solution_name == "Hugging Face":
        st.subheader("Escolha um Modelo Gratuito:")
        models = get_hugging_face_models()
        if models:
            config["Modelo"] = st.selectbox("Modelos disponíveis:", models)
        else:
            st.write("Não foi possível obter os modelos gratuitos.")
    
    if st.button("Salvar Configuração"):
        st.session_state["ai_config"] = {"solution": solution_name, "config": config}
        st.success("Configuração salva com sucesso!")

st.title("Usar Inteligência Artificial")
if "ai_config" not in st.session_state:
    st.warning("Verifique configuração de inteligência artificial.")
else:
    prompt = st.text_area("Digite seu prompt:")
    if st.button("Requisitar Resposta"):
        ai_config = st.session_state["ai_config"]
        if ai_config["solution"] == "Hugging Face":
            headers = {"Authorization": f"Bearer {ai_config['config']['Hugging Face Token']}"}
            data = {"inputs": prompt}
            url = f"https://api-inference.huggingface.co/models/{ai_config['config']['Modelo']}"
            response = requests.post(url, headers=headers, json=data)
        elif ai_config["solution"] == "Cohere":
            headers = {"Authorization": f"Bearer {ai_config['config']['Cohere API Key']}", "Content-Type": "application/json"}
            data = {"model": "command-xlarge", "prompt": prompt, "max_tokens": 100}
            response = requests.post("https://api.cohere.ai/v1/generate", headers=headers, json=data)
        elif ai_config["solution"] == "OpenAI (GPT)":
            headers = {"Authorization": f"Bearer {ai_config['config']['OpenAI API Key']}", "Content-Type": "application/json"}
            data = {"model": "gpt-3.5-turbo", "messages": [{"role": "user", "content": prompt}]}
            response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=data)
        
        if response.status_code == 200:
            st.write("**Resposta da IA:**")
            st.write(response.json())
        else:
            st.error("Erro ao processar a requisição. Verifique sua configuração.")
