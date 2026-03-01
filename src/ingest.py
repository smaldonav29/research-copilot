"""
ingest.py — Run this ONCE to index all PDFs into ChromaDB.

Usage:
    python -m src.ingest
    python -m src.ingest --chunk-size 256
    python -m src.ingest --chunk-size 1024
    python -m src.ingest --reset
"""

from dotenv import load_dotenv
load_dotenv()

import json
import argparse
from pathlib import Path
from tqdm import tqdm
from loguru import logger

from src.ingestion.pdf_extractor import extract_text_from_pdf
from src.ingestion.text_cleaner import clean_extracted_text
from src.chunking.chunker import TokenChunker
from src.embedding.embedder import OpenAIEmbedder
from src.vectorstore.chroma_store import ChromaVectorStore


PAPERS_DIR = Path("papers")
CATALOG_PATH = PAPERS_DIR / "paper_catalog.json"
CHROMA_DIR = "./chroma_db"
COLLECTION_NAME = "papers"


# ---------------------------------------------------
# Metadata sanitizer (CRITICAL FIX)
# ---------------------------------------------------
def clean_metadata(meta: dict) -> dict:
    """
    Ensure metadata values are compatible with ChromaDB.
    Allowed types:
        str, int, float, bool, None
    Everything else is converted to string.
    """
    cleaned = {}

    for k, v in meta.items():
        # Convert numpy types safely
        try:
            if hasattr(v, "item"):
                v = v.item()
        except Exception:
            pass

        if isinstance(v, (str, int, float, bool)) or v is None:
            cleaned[k] = v
        else:
            cleaned[k] = str(v)

    return cleaned


def load_catalog() -> list[dict]:
    """Load paper metadata from catalog JSON."""
    with open(CATALOG_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data["papers"]


def ingest(chunk_size: int = 512, chunk_overlap: int = 50, reset: bool = False):
    logger.info(f"Starting ingestion | chunk_size={chunk_size} | overlap={chunk_overlap}")

    # 1. Load catalog
    papers = load_catalog()
    logger.info(f"Found {len(papers)} papers in catalog")

    # 2. Setup components
    chunker = TokenChunker(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    embedder = OpenAIEmbedder()
    vectorstore = ChromaVectorStore(persist_directory=CHROMA_DIR)

    # 3. Reset collection if requested
    if reset:
        logger.warning("Resetting ChromaDB collection...")
        try:
            vectorstore.client.delete_collection(COLLECTION_NAME)
            logger.info("Collection deleted")
        except Exception:
            pass

    vectorstore.create_collection(COLLECTION_NAME)

    # 4. Process each paper
    total_chunks = 0
    skipped = 0
    successful = 0

    for paper in tqdm(papers, desc="Ingesting papers"):
        pdf_path = PAPERS_DIR / paper["filename"]

        if not pdf_path.exists():
            logger.warning(f"PDF not found, skipping: {pdf_path}")
            skipped += 1
            continue

        try:
            # Extract text
            extracted = extract_text_from_pdf(str(pdf_path))
            raw_text = extracted["text"]
            clean_text = clean_extracted_text(raw_text)

            # -------------------------
            # Build paper metadata
            # -------------------------
            paper_metadata = {
                "paper_id": str(paper["id"]),
                "paper_title": str(paper["title"]),
                "authors": ", ".join(map(str, paper.get("authors", []))),
                "year": int(paper["year"]) if paper.get("year") else None,
                "venue": str(paper.get("venue", "")),
                "doi": str(paper.get("doi", "")),
                "section": str(paper.get("section", "")),
            }

            # Clean base metadata
            paper_metadata = clean_metadata(paper_metadata)

            # -------------------------
            # Chunk text
            # -------------------------
            chunks = chunker.chunk_text(clean_text, metadata=paper_metadata)

            ids = []
            documents = []
            embeddings_input = []
            metadatas = []

            for chunk in chunks:
                chunk_id = int(chunk["chunk_id"])
                token_count = int(chunk["token_count"])

                ids.append(f"{paper['id']}_chunk_{chunk_id:04d}")
                documents.append(chunk["text"])
                embeddings_input.append(chunk["text"])

                meta = {
                    **paper_metadata,
                    "chunk_id": chunk_id,
                    "token_count": token_count
                }

                meta = clean_metadata(meta)
                metadatas.append(meta)

            # -------------------------
            # Generate embeddings
            # -------------------------
            all_embeddings = []
            batch_size = 100

            for i in range(0, len(embeddings_input), batch_size):
                batch = embeddings_input[i:i + batch_size]
                batch_embeddings = embedder.embed_texts(batch)
                all_embeddings.extend(batch_embeddings)

            # -------------------------
            # Store in ChromaDB
            # -------------------------
            vectorstore.add_documents(
                ids=ids,
                documents=documents,
                embeddings=all_embeddings,
                metadatas=metadatas
            )

            total_chunks += len(chunks)
            successful += 1

            logger.success(
                f"✓ {paper['id']} — {paper['title'][:50]} ({len(chunks)} chunks)"
            )

        except Exception as e:
            logger.error(f"Failed to process {paper['filename']}: {e}")

    logger.info("─" * 60)
    logger.info("Ingestion complete!")
    logger.info(f"  Papers processed : {successful}/{len(papers)}")
    logger.info(f"  Papers skipped   : {skipped} (PDF not found)")
    logger.info(f"  Total chunks     : {total_chunks}")
    logger.info(f"  ChromaDB path    : {CHROMA_DIR}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ingest PDFs into ChromaDB")
    parser.add_argument("--chunk-size", type=int, default=512,
                        help="Token chunk size (default: 512)")
    parser.add_argument("--chunk-overlap", type=int, default=50,
                        help="Token overlap between chunks (default: 50)")
    parser.add_argument("--reset", action="store_true",
                        help="Delete and recreate ChromaDB collection")
    args = parser.parse_args()

    ingest(
        chunk_size=args.chunk_size,
        chunk_overlap=args.chunk_overlap,
        reset=args.reset
    )
