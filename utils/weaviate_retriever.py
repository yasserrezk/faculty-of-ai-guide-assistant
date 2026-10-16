import configparser
import json
from pathlib import Path

import weaviate
from tqdm.auto import tqdm
from weaviate.classes.config import Configure, DataType, Property
from weaviate.classes.query import MetadataQuery

ROOT = Path(__file__).resolve().parent.parent
COLLECTION = "FAI_Guide"
OLLAMA_URL = "http://ollama:11434"

cfg = configparser.ConfigParser()
if not cfg.read(ROOT / "config.conf"):
    raise FileNotFoundError(f"Config file not found: {ROOT / 'config.conf'}")
w = cfg["weaviate"]


def connect():
    return weaviate.connect_to_custom(
        http_host=w["http_host"],
        http_port=w.getint("http_port"),
        http_secure=w.getboolean("http_secure"),
        grpc_host=w["grpc_host"],
        grpc_port=w.getint("grpc_port"),
        grpc_secure=w.getboolean("grpc_secure"),
    )


def load_chunks(path):
    file = ROOT / path
    if not file.is_file():
        raise FileNotFoundError(f"Chunks file not found: {file}")
    return json.loads(file.read_text(encoding="utf-8"))


def create_collection():
    with connect() as client:
        if client.collections.exists(COLLECTION):
            print("Collection already exists.")
            return
        client.collections.create(
            name=COLLECTION,
            description="A collection of student guide information",
            properties=[
                Property(
                    name="chunk_id", data_type=DataType.TEXT, skip_vectorization=True
                ),
                Property(name="page_number", data_type=DataType.INT),
                Property(name="main", data_type=DataType.TEXT),
                Property(name="content", data_type=DataType.TEXT),
            ],
            vector_config=Configure.Vectors.text2vec_ollama(
                api_endpoint=OLLAMA_URL,
                model="embeddinggemma:latest",
            ),
        )
        print("Collection created.")


def ingest(chunks):
    with connect() as client:
        col = client.collections.get(COLLECTION)
        with col.batch.dynamic() as batch:
            for c in tqdm(chunks, desc="Ingesting", unit="chunk"):
                batch.add_object(
                    properties={
                        "chunk_id": str(c["chunk_id"]),
                        "page_number": int(c["page_number"]),
                        "main": c["main"],
                        "content": c["content"],
                    }
                )
        if col.batch.failed_objects:
            print(f"Failed: {len(col.batch.failed_objects)}")
            print(col.batch.failed_objects[0])
        print("Total objects:", col.aggregate.over_all(total_count=True).total_count)


def query(q, alpha=0.5, limit=5):
    with connect() as client:
        res = client.collections.get(COLLECTION).query.hybrid(
            query=q,
            alpha=alpha,
            limit=limit,
            return_metadata=MetadataQuery(score=True),
        )
        return [
            f"[صفحة {o.properties['page_number']}]\n{o.properties['content']}"
            for o in res.objects
        ]
