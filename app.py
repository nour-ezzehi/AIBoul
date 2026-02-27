import streamlit as st
import requests

API_URL = "http://localhost:8000"

st.set_page_config(page_title="RAG Boulangerie", page_icon="🥖", layout="centered")

st.title("🥖 Assistant Fiches Techniques")
st.caption("Posez une question sur vos ingrédients et améliorants de panification")

question = st.text_input("Votre question", placeholder="Ex: Quel est le rôle de l'amylase ?")
use_llm = st.toggle("Générer une réponse avec le LLM", value=True)

if st.button("Rechercher", type="primary") and question:
    with st.spinner("Recherche en cours..."):
        try:
            resp = requests.post(
                f"{API_URL}/query",
                json={"question": question, "use_llm": use_llm},
                timeout=60,
            )
            resp.raise_for_status()
            data = resp.json()
        except requests.exceptions.ConnectionError:
            st.error("❌ Impossible de contacter l'API. Assurez-vous que `api.py` tourne sur le port 8000.")
            st.stop()
        except Exception as e:
            st.error(f"❌ Erreur : {e}")
            st.stop()

    if use_llm and data.get("answer"):
        st.subheader("💬 Réponse")
        st.success(data["answer"])

    st.subheader("📄 Fragments les plus proches")
    for i, frag in enumerate(data["fragments"], 1):
        with st.expander(f"Fragment {i} — Document #{frag['id_document']} · Similarité : {frag['similarity']}"):
            st.write(frag["texte_fragment"])
            