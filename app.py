import streamlit as st
import requests
import cohere
import re

# Configuração inicial da página
st.set_page_config(page_title="AI Solutions Interface", layout="wide")

# Dicionário de soluções de IA com limites e informações
AI_SOLUTIONS = {
    "Hugging Face": {
        "config_steps": [
            "1. Crie uma conta no Hugging Face (https://huggingface.co/)",
            "2. Acesse suas configurações de perfil > Tokens de Acesso",
            "3. Gere um Token do tipo **Read** (não use Write ou Fine-grained)",
            "4. Na página do modelo desejado, clique em 'Use this model'",
            "5. Cole o código da seção 'Use a pipeline as a high-level helper' abaixo"
        ],
        "limits": "Limite gratuito: ~30,000 tokens/dia\nAlguns modelos têm restrições específicas"
    },
    "Cohere": {
        "config_steps": [
            "1. Crie uma conta na Cohere (https://dashboard.cohere.com/)",
            "2. Acesse a seção API Keys no dashboard",
            "3. Gere e copie sua chave API gratuita"
        ],
        "limits": "Plano free: 5 chamadas/minuto\n100 chamadas/dia",
    },
    "DeepInfra": {
        "config_steps": [
            "1. Crie uma conta no DeepInfra (https://deepinfra.com/)",
            "2. Acesse sua dashboard para obter a API Key",
            "3. Cole sua chave API abaixo"
        ],
        "limits": "Limite gratuito: 1000 requisições/mês"
    }
}

def extract_model_id(code):
    # Tentar encontrar padrões comuns no código fornecido
    patterns = [
        r"model='([^']+)'",          # Para pipeline
        r"from_pretrained\('([^']+)'" # Para load direct
    ]
    
    for pattern in patterns:
        match = re.search(pattern, code)
        if match:
            return match.group(1)
    return None

def handle_huggingface(prompt):
    try:
        if not hasattr(st.session_state, 'hf_model_id') or not st.session_state.hf_model_id:
            return "Model ID não configurado corretamente"
        
        API_URL = f"https://api-inference.huggingface.co/models/{st.session_state.hf_model_id}"
        headers = {"Authorization": f"Bearer {st.session_state.hf_token}"}
        
        payload = {
            "inputs": prompt,
            "parameters": {"max_new_tokens": 200}
        }
        
        response = requests.post(API_URL, headers=headers, json=payload, timeout=30)

        if response.status_code == 503:
            estimated_time = response.json().get('estimated_time', 30)
            return f"Modelo está carregando... Tente novamente em {estimated_time} segundos"
        
        if response.status_code != 200:
            error = response.json().get('error', 'Erro desconhecido')
            return f"Erro na API ({response.status_code}): {error}"

        result = response.json()
        
        if isinstance(result, list):
            return result[0].get('generated_text', str(result))
            
        return result.get('generated_text', str(result))

    except Exception as e:
        return f"Erro na requisição: {str(e)}"

def handle_cohere(prompt):
    try:
        co = cohere.Client(st.session_state.cohere_token)
        response = co.generate(
            model='command-nightly',
            prompt=prompt,
            max_tokens=300
        )
        return response.generations[0].text
    except Exception as e:
        return f"Erro na Cohere: {str(e)}"

def handle_deepinfra(prompt):
    try:
        API_URL = "https://api.deepinfra.com/v1/openai/chat/completions"
        headers = {
            "Authorization": f"Bearer {st.session_state.deepinfra_token}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": st.session_state.deepinfra_model,
            "messages": [{"role": "user", "content": prompt}]
        }
        
        response = requests.post(API_URL, headers=headers, json=payload, timeout=30)
        
        if response.status_code != 200:
            return f"Erro na API ({response.status_code}): {response.text}"
            
        return response.json()['choices'][0]['message']['content']
    
    except Exception as e:
        return f"Erro no DeepInfra: {str(e)}"

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
            st.markdown("### Exemplo de código válido:")
            st.code("from transformers import pipeline\npipe = pipeline('text-generation', model='google/flan-t5-base')")
            
            model_code = st.text_area("Cole o código do modelo aqui:", height=100)
            if model_code:
                model_id = extract_model_id(model_code)
                if model_id:
                    st.session_state.hf_model_id = model_id
                    st.success(f"Model ID detectado: {model_id}")
                else:
                    st.error("Não foi possível detectar o Model ID no código. Certifique-se de colar o código completo da seção 'Use a pipeline as a high-level helper'")
            
            st.session_state.hf_token = st.text_input("Token de Acesso (Tipo Read):", type="password")
            st.markdown("**Nota:** O token deve ser do tipo **Read** para acesso à API")

        elif st.session_state.selected_provider == "Cohere":
            st.session_state.cohere_token = st.text_input("Chave API da Cohere:", type="password")
        
        elif st.session_state.selected_provider == "DeepInfra":
            st.session_state.deepinfra_token = st.text_input("API Key do DeepInfra:", type="password")
            st.session_state.deepinfra_model = st.text_input("Modelo do DeepInfra (ex: meta-llama/Llama-2-70b-chat):")
        
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
        provider = st.session_state.selected_provider
        
        if provider == "Hugging Face":
            required = ['hf_token', 'hf_model_id']
        elif provider == "Cohere":
            required = ['cohere_token']
        elif provider == "DeepInfra":
            required = ['deepinfra_token', 'deepinfra_model']
        
        for field in required:
            if not hasattr(st.session_state, field) or not getattr(st.session_state, field):
                config_valid = False
        
        if not config_valid:
            st.error("Configuração incompleta! Verifique todos os campos obrigatórios.")
            if st.button("Voltar para configuração"):
                st.session_state.current_page = "configure_provider"
                st.rerun()
            return
        
        prompt = st.text_area("Digite seu prompt:", height=150)
        
        if st.button("Requisitar Resposta"):
            with st.spinner("Processando..."):
                try:
                    if provider == "Hugging Face":
                        response = handle_huggingface(prompt)
                    elif provider == "Cohere":
                        response = handle_cohere(prompt)
                    elif provider == "DeepInfra":
                        response = handle_deepinfra(prompt)
                    else:
                        response = "Provedor não configurado"
                except Exception as e:
                    response = f"Erro crítico: {str(e)}"
                
                st.subheader("Resposta:")
                st.write(response)
        
        if st.button("Alterar Provedor"):
            st.session_state.current_page = "select_provider"
            st.rerun()

if __name__ == "__main__":
    main()
