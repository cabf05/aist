import streamlit as st
import requests
import cohere
import os
from huggingface_hub import list_models

# Configuração inicial da página
st.set_page_config(page_title="AI Solutions Interface", layout="wide")

# Dicionário de soluções de IA com limites e informações
AI_SOLUTIONS = {
    "Hugging Face": {
        "config_steps": [
            "1. Crie uma conta no Hugging Face (https://huggingface.co/)",
            "2. Acesse suas configurações de perfil e gere um Token de Acesso",
            "3. Selecione o modelo desejado (alguns modelos requerem aceitação de termos)"
        ],
        "limits": "Limite gratuito: ~30,000 tokens/dia\nAlguns modelos têm restrições específicas",
        "models": {
            "gpt2": {"requires_auth": False},
            "bigscience/bloom-560m": {"requires_auth": False},
            "google/flan-t5-base": {"requires_auth": False},
            "meta-llama/Llama-2-7b-chat-hf": {"requires_auth": True}
        }
    },
    "Cohere": {
        "config_steps": [
            "1. Crie uma conta na Cohere (https://dashboard.cohere.com/)",
            "2. Acesse a seção API Keys no dashboard",
            "3. Gere e copie sua chave API gratuita"
        ],
        "limits": "Plano free: 5 chamadas/minuto\n100 chamadas/dia",
        "api_key": ""
    },
    "DeepInfra": {
        "config_steps": [
            "1. Crie uma conta no DeepInfra (https://deepinfra.com/)",
            "2. Acesse sua dashboard para obter a API Key",
            "3. Selecione um modelo dos disponíveis"
        ],
        "limits": "Limite gratuito: 1000 requisições/mês",
        "models": ["meta-llama/Llama-2-70b-chat", "databricks/dolly-v2-12b"]
    }
}

# Funções para cada provedor de IA
def handle_huggingface(prompt):
    API_URL = f"https://api-inference.huggingface.co/models/{st.session_state.selected_model}"
    headers = {"Authorization": f"Bearer {st.session_state.hf_token}"}
    
    try:
        response = requests.post(API_URL, headers=headers, json={"inputs": prompt})
        return response.json()[0]['generated_text']
    except Exception as e:
        return f"Erro: {str(e)}"

def handle_cohere(prompt):
    try:
        co = cohere.Client(st.session_state.cohere_token)
        response = co.generate(
            model='command-nightly',
            prompt=prompt,
            max_tokens=300)
        return response.generations[0].text
    except Exception as e:
        return f"Erro: {str(e)}"

# Interface principal
def main():
    st.title("Interface de Soluções de IA Gratuitas")
    
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "select_provider"
    
    # Seleção do provedor
    if st.session_state.current_page == "select_provider":
        st.header("Escolha seu provedor de IA")
        selected_provider = st.selectbox("Selecione uma solução de IA:", list(AI_SOLUTIONS.keys()))
        
        st.markdown("### Informações do Plano Gratuito")
        st.markdown(AI_SOLUTIONS[selected_provider]["limits"])
        
        if st.button("Configurar esta solução"):
            st.session_state.selected_provider = selected_provider
            st.session_state.current_page = "configure_provider"
            st.rerun()
    
    # Configuração do provedor
    elif st.session_state.current_page == "configure_provider":
        st.header(f"Configuração do {st.session_state.selected_provider}")
        
        provider_info = AI_SOLUTIONS[st.session_state.selected_provider]
        
        for step in provider_info["config_steps"]:
            st.markdown(step)
        
        if st.session_state.selected_provider == "Hugging Face":
            st.session_state.hf_token = st.text_input("Token de Acesso do Hugging Face:", type="password")
            model_list = list(provider_info["models"].keys())
            st.session_state.selected_model = st.selectbox("Selecione o modelo:", model_list)
            
            if provider_info["models"][st.session_state.selected_model]["requires_auth"]:
                st.warning("Este modelo requer aceitação de termos no site do Hugging Face!")
        
        elif st.session_state.selected_provider == "Cohere":
            st.session_state.cohere_token = st.text_input("Chave API da Cohere:", type="password")
        
        if st.button("Salvar Configurações"):
            st.session_state.current_page = "use_ai"
            st.rerun()
        
        if st.button("Voltar"):
            st.session_state.current_page = "select_provider"
            st.rerun()
    
    # Interface de uso da IA
    elif st.session_state.current_page == "use_ai":
        st.header("Utilize a Inteligência Artificial")
        
        # Verificação de configuração
        config_valid = True
        if st.session_state.selected_provider == "Hugging Face":
            if not hasattr(st.session_state, "hf_token") or not st.session_state.hf_token:
                config_valid = False
        
        elif st.session_state.selected_provider == "Cohere":
            if not hasattr(st.session_state, "cohere_token") or not st.session_state.cohere_token:
                config_valid = False
        
        if not config_valid:
            st.error("Verifique a configuração de inteligência artificial!")
            if st.button("Voltar para configuração"):
                st.session_state.current_page = "configure_provider"
                st.rerun()
            return
        
        # Interface de prompt
        prompt = st.text_area("Digite seu prompt:", height=150)
        
        if st.button("Requisitar Resposta"):
            with st.spinner("Processando..."):
                if st.session_state.selected_provider == "Hugging Face":
                    response = handle_huggingface(prompt)
                elif st.session_state.selected_provider == "Cohere":
                    response = handle_cohere(prompt)
                
                st.subheader("Resposta:")
                st.write(response)
        
        if st.button("Alterar Provedor"):
            st.session_state.current_page = "select_provider"
            st.rerun()

if __name__ == "__main__":
    main()

        else:
            st.error(f"Erro ao processar a requisição. Código: {response.status_code if response else 'N/A'} - {response.text if response else 'Sem resposta'}")
