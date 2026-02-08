import sys
import os

# Add project root to path
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT_DIR)

import json
import streamlit as st

from core.rag.loader import load_rules
from core.rag.cleaner import clean_text
from core.rag.chunker import chunk_text
from core.rag.embedder import Embedder
from core.rag.vector_store import VectorStore
from core.rag.retriever import Retriever
from core.agent.reporting_agent import ReportingAgent
from core.validators.corep_validator import CorepValidator
from core.tools.report_saver import ReportSaver


# ------------------ Backend Setup ------------------ #

@st.cache_resource
def setup_system():

    # Build RAG
    raw = load_rules("data/rules/demo_rules.txt")
    cleaned = clean_text(raw)
    chunks = chunk_text(cleaned)

    embedder = Embedder()
    vectors = embedder.embed(chunks)

    store = VectorStore(dim=len(vectors[0]))
    store.add(vectors)

    retriever = Retriever(embedder, store, chunks)

    # Load schema
    with open("core/schemas/c01_schema.json") as f:
        schema = json.load(f)

    # Init components
    agent = ReportingAgent(retriever, schema)
    validator = CorepValidator(schema)
    saver = ReportSaver()

    return agent, validator, saver


agent, validator, saver = setup_system()

# ------------------ UI ------------------ #

st.set_page_config(page_title="COREP AI Assistant", layout="centered")

st.title("🏦 COREP Regulatory Reporting Assistant")
st.markdown("LLM-powered reporting tool for Own Funds (C01.00)")

st.divider()

# Input Section
# ------------------ Query Section ------------------ #

st.subheader("📝 Regulatory Query")

question = st.text_area(
    "Ask your regulatory question",
    placeholder="e.g. How should I report CET1 and capital ratios?"
)

scenario = st.text_area(
    "Describe the reporting scenario",
    placeholder="e.g. UK consolidated bank, no deductions, GBP reporting"
)

st.divider()

# ------------------ Financial Inputs ------------------ #

st.subheader("📥 Input Financial Data")

cet1 = st.number_input("CET1 Capital", min_value=0.0, step=1.0)
at1 = st.number_input("AT1 Capital", min_value=0.0, step=1.0)
tier2 = st.number_input("Tier 2 Capital", min_value=0.0, step=1.0)

rwa = st.number_input("Risk Weighted Assets (RWA)", min_value=1.0, step=10.0)

currency = st.selectbox("Currency", ["GBP"])

st.divider()

generate = st.button("🚀 Generate Report", use_container_width=True)


# Output Section
if generate:

    user_data = {
        "question": question,
        "scenario": scenario,
        "cet1": cet1,
        "at1": at1,
        "tier2": tier2,
        "rwa": rwa,
        "currency": currency
    }

    with st.spinner("Generating report..."):

        result, errors = agent.run_with_retry(user_data, validator)

        path = saver.save(result, errors)

    st.divider()

    st.subheader("📄 Generated Report")

    st.code(json.dumps(result, indent=2), language="json")

    if errors:
        st.error("⚠️ Validation Errors")
        for e in errors:
            st.write("-", e)
    else:
        st.success("✅ Report Passed Validation")

    st.info(f"📁 Saved to: {path}")
