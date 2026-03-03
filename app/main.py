import sys
import os

# --------------------------------------------------
# Add project root to path
# --------------------------------------------------
PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..")
)

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import streamlit as st
from src.rag_pipeline import RAGPipeline

# --------------------------------------------------
# Page Config
# --------------------------------------------------
st.set_page_config(
    page_title="Research Copilot",
    layout="wide"
)

st.title("📚 Mi asistente personal: Mr. Research Copilot")

# --------------------------------------------------
# Initialize Pipeline Once
# --------------------------------------------------
if "pipeline" not in st.session_state:
    st.session_state.pipeline = RAGPipeline()

# --------------------------------------------------
# Strategy Selector
# --------------------------------------------------
strategy = st.selectbox(
    "Select Prompt Strategy",
    [
        "v1_delimiters",
        "v2_json_output",
        "v3_few_shot",
        "v4_chain_of_thought"
    ]
)

# --------------------------------------------------
# User Input
# --------------------------------------------------
question = st.text_input("Ask a research question:")

result = None  # ✅ Prevent NameError

if st.button("Ask") and question.strip():

    with st.spinner("Processing..."):

        result = st.session_state.pipeline.query(
            question,
            strategy=strategy
        )

    # --------------------------------------------------
    # Show Answer
    # --------------------------------------------------
    st.subheader("Answer")
    st.write(result.get("answer"))

    # --------------------------------------------------
    # Show Citations
    # --------------------------------------------------
    if result.get("citations"):
        st.subheader("Citations")
        for citation in result["citations"]:
            st.markdown(citation)

# --------------------------------------------------
# Show Retrieved Sources ONLY if result exists
# --------------------------------------------------
if result:

    st.subheader("📚 Retrieved Sources")

    retrieved_chunks = result.get("retrieved_chunks", [])

    if retrieved_chunks:

        for i, chunk in enumerate(retrieved_chunks, 1):

            st.markdown(f"### Source {i}")

            doc = chunk.get("document", "No document text")
            metadata = chunk.get("metadata", {})

            st.markdown("**Document Text:**")
            st.write(doc)

            if metadata:
                st.markdown("**Metadata:**")
                st.json(metadata)

            st.markdown("---")

    else:
        st.info("No sources retrieved.")