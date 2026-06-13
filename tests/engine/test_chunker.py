from langchain_core.documents import Document
from engine.ingestion.chunker import chunk_documents


def test_chunk_documents_empty():
    result = chunk_documents([])
    assert result == []


def test_chunk_documents_single_short():
    doc = Document(
        page_content="Short text.",
        metadata={"filename": "test.pdf", "page_number": 1},
    )
    chunks = chunk_documents([doc], chunk_size=100, chunk_overlap=20)
    assert len(chunks) >= 1
    assert chunks[0].metadata["filename"] == "test.pdf"
    assert chunks[0].metadata["page_number"] == 1
    assert chunks[0].metadata["chunk_index"] == 0


def test_chunk_documents_splits_long_text():
    long_text = "Word " * 200
    doc = Document(
        page_content=long_text,
        metadata={"filename": "long.pdf", "page_number": 3},
    )
    chunks = chunk_documents([doc], chunk_size=100, chunk_overlap=20)
    assert len(chunks) > 1
    for i, chunk in enumerate(chunks):
        assert chunk.metadata["chunk_index"] == i
        assert chunk.metadata["filename"] == "long.pdf"


def test_chunk_documents_preserves_metadata():
    doc = Document(
        page_content="Some legal text about contracts and liability.",
        metadata={"filename": "contract.pdf", "page_number": 5, "extra": "data"},
    )
    chunks = chunk_documents([doc], chunk_size=1000, chunk_overlap=0)
    assert chunks[0].metadata["extra"] == "data"
    assert chunks[0].metadata["page_number"] == 5


def test_chunk_documents_multiple_docs():
    docs = [
        Document(page_content="First document content.", metadata={"filename": "a.pdf", "page_number": 1}),
        Document(page_content="Second document content.", metadata={"filename": "b.pdf", "page_number": 1}),
    ]
    chunks = chunk_documents(docs, chunk_size=1000, chunk_overlap=0)
    assert len(chunks) == 2
    assert chunks[0].metadata["chunk_index"] == 0
    assert chunks[1].metadata["chunk_index"] == 1
