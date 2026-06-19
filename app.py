import streamlit as st
import tempfile
import os

from pdf_reader import read_pdf
from chunker import create_chunks
from summary import generate_summary
from vector_store import build_index, retrieve
from llm import ask_llm

st.set_page_config(
    page_title="PDF Chatbot",
    page_icon="📄"
)

st.markdown("""
<style>

/* Main app */
.stApp {
    background-color: #0E1117;
}

/* Buttons */
.stButton > button {
    border-radius: 12px;
    height: 3rem;
    font-weight: 600;
}

/* Text input */
.stTextInput input {
    border-radius: 12px;
}
if st.button("🗑️ Clear Chat"):

    st.session_state.chat_history = []

    st.rerun()

/* Summary container */
[data-testid="stVerticalBlockBorderWrapper"] {
    border-radius: 15px;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    border-right: 1px solid #30363D;
}

</style>
""", unsafe_allow_html=True)

if "summary" not in st.session_state:
    st.session_state.summary = None

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "last_pdf_name" not in st.session_state:
    st.session_state.last_pdf_name = None

if "pdf_text" not in st.session_state:
    st.session_state.pdf_text = None

if "vectorstore" not in st.session_state:
    st.session_state.vectorstore = None


st.markdown("""
# 📄 AI PDF Assistant

### Summarize documents • Ask questions • Retrieve answers with RAG
""")

with st.sidebar:

    st.title("📄 PDF Assistant")

    st.markdown("---")

    st.write(
        "Upload a PDF and ask questions using RAG."
    )

    st.markdown("---")

    st.subheader("Tech Stack")

    st.write("🤖 Groq")
    st.write("🔗 LangChain")
    st.write("🗂️ FAISS")
    st.write("🎨 Streamlit")

    st.markdown("---")

   


uploaded_file = st.file_uploader(
    "Upload a PDF",
    type=["pdf"]
)
if uploaded_file:

        st.success(
            f"Loaded: {uploaded_file.name}"
        )

if uploaded_file is not None:

    if uploaded_file.name != st.session_state.last_pdf_name:

        st.session_state.summary = None
        st.session_state.pdf_text = None
        st.session_state.vectorstore = None

        st.session_state.last_pdf_name = uploaded_file.name
question = st.text_input(
    "Ask a question about the document",
    placeholder="e.g. What are the advantages of Machine Learning?"
)
col1, col2 = st.columns(2)

with col1:

    answer_button = st.button(
        "🤖 Get Answer",
        use_container_width=True
    )

with col2:

    summary_button = st.button(
        "📋 Generate Summary",
        use_container_width=True
    )
if answer_button:

    if uploaded_file is None:

        st.warning(
            "Please upload a PDF"
        )

    elif question.strip() == "":

        st.warning(
            "Please enter a question"
        )

    else:

        with st.spinner(
            "Processing..."
        ):
            if st.session_state.pdf_text is None:

                with tempfile.NamedTemporaryFile(
                    delete=False,
                    suffix=".pdf"
                ) as tmp_file:

                    tmp_file.write(
                        uploaded_file.getvalue()
                    )

                    pdf_path = tmp_file.name

                st.session_state.pdf_text = read_pdf(
                    pdf_path
                )

                os.remove(
                    pdf_path
                )

            text = st.session_state.pdf_text
            word_count = len(
            st.session_state.pdf_text.split()
)
            chunk_count = len(
            create_chunks(
            st.session_state.pdf_text
                            )
            )
            col1, col2 = st.columns(2)
            with col1:

                st.metric(
        "📄 Words",
        word_count
    )

            with col2:

                st.metric(
        "🧩 Chunks",
        chunk_count
    )

            if st.session_state.vectorstore is None:

                chunks = create_chunks(text)

                st.session_state.vectorstore = build_index(
                    chunks
                )
            
            vectorstore = st.session_state.vectorstore

            context = retrieve(
    question,
    vectorstore
)

            answer = ask_llm(
    context,
    question
)
        st.success(
            "Answer Generated"
        )
        st.session_state.chat_history.append(
    {
        "question": question,
        "answer": answer
    }
)   

        with st.chat_message("user"):

            st.write(question)

        with st.chat_message("assistant"):

            st.write(answer)

        with st.expander(
    "🔍 Retrieved Context"
):

            st.code(
        context,
        language=None
        )
if summary_button:

    if uploaded_file is None:

        st.warning(
            "Please upload a PDF"
        )

    else:

        if st.session_state.pdf_text is None:

            with tempfile.NamedTemporaryFile(
                delete=False,
                suffix=".pdf"
            ) as tmp_file:

                tmp_file.write(
                    uploaded_file.getvalue()
                )

                pdf_path = tmp_file.name

            st.session_state.pdf_text = read_pdf(
                pdf_path
            )

            os.remove(
                pdf_path
            )
        if st.session_state.summary is None:

            with st.spinner(
                "Generating Summary..."
            ):

                st.session_state.summary = generate_summary(
                    st.session_state.pdf_text
                )
with st.container(border=True):

    st.markdown("## 📋 Document Summary")

    if st.session_state.summary:

        st.write(
            st.session_state.summary
        )

    else:

        st.info(
            "Click 'Generate Summary' to create a document summary."
        )

st.markdown(
    """
    ## 💬 Chat History

    Previous questions and answers from this document.
    """
)
with st.container(border=True):

    st.markdown(
        f"## 💬 Chat History ({len(st.session_state.chat_history)} Messages)"
    )

    if not st.session_state.chat_history:

        st.info(
            "Ask a question to start a conversation."
        )

    else:

        for message in st.session_state.chat_history:

            with st.chat_message("user"):
                st.write(
                    message["question"]
                )

            with st.chat_message("assistant"):
                st.write(
                    message["answer"]
                )