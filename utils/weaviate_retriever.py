import configparser
import json
import os
import time
from pathlib import Path

import dotenv
import weaviate
from google.genai import types, errors, Client
from weaviate.classes.config import Property, DataType, Configure


def connect():

    client = weaviate.connect_to_custom(
        http_host=w["http_host"],
        http_port=w.getint("http_port"),
        http_secure=w.getboolean("http_secure"),
        grpc_host=w["grpc_host"],
        grpc_port=w.getint("grpc_port"),
        grpc_secure=w.getboolean("grpc_secure"),
    )
    client.connect()
    return client


def create_collection():

    client = connect()

    try:
        client.collections.create(
            name="FAI_Guide",
            description="A collection of student guide information",
            properties=[
                Property(name="chunk_id", data_type=DataType.TEXT),
                Property(name="page_number", data_type=DataType.INT),
                Property(name="main", data_type=DataType.TEXT),
                Property(name="content", data_type=DataType.TEXT),
            ],
            vector_config=Configure.Vectors.self_provided(),
        )
        print(
            """\x1b[32;47mSuccess Mesage:\n--> Collection created successfully!\x1b[0m"""
        )
    except:
        print(
            """\x1b[30;41mInternal Error:\n--> The Weaviate VectorDB already exists.\x1b[0m"""
        )
    finally:
        client.close()


def embed_texts(texts, task, batch=10, pause=4):

    try:
        gclient = Client(api_key=os.environ["GEMINI_API_KEY"])
    except:
        if not dotenv.load_dotenv():
            raise FileNotFoundError(
                f"Environment file doesn't exists please create it."
            )
        elif os.environ["GEMINI_API_KEY"] == None:
            raise KeyError(f"Gemini API Key not found.")

    out = []
    for i in range(0, len(texts), batch):
        chunk = texts[i : i + batch]
        for attempt in range(6):
            try:
                res = gclient.models.embed_content(
                    model="gemini-embedding-001",
                    contents=chunk,
                    config=types.EmbedContentConfig(
                        task_type=task, output_dimensionality=768
                    ),
                )
                out.extend(e.values for e in res.embeddings)
                break
            except errors.ClientError as e:
                if e.code == 429:
                    time.sleep(20 * (attempt + 1))
                else:
                    raise
        else:
            raise RuntimeError(f"Gave up at batch starting {i}")
        time.sleep(pause)
    return out


def batch_text_vec(chunks, texts):

    client = connect()
    col = client.collections.get("FAI_Guide")
    vecs = embed_texts(texts, "RETRIEVAL_DOCUMENT")

    try:
        assert len(chunks) == len(vecs), (len(chunks), len(vecs))

        with col.batch.dynamic() as batch:
            for c, v in zip(chunks, vecs):
                batch.add_object(
                    properties={
                        "chunk_id": str(c["chunk_id"]),
                        "page_number": int(c["page_number"]),
                        "main": c["main"],
                        "content": c["content"],
                    },
                    vector=v,
                )

        failed = col.batch.failed_objects
        if failed:
            print(f"Failed: {len(failed)}")
            print(failed[0])

        print("Count:", col.aggregate.over_all(total_count=True).total_count)
    finally:
        client.close()


def query(q):
    
    client = connect()
    col = client.collections.get("FAI_Guide")
    query_vec = embed_texts([q], "RETRIEVAL_QUERY")
    
    results = 


dotenv.load_dotenv()

cfg = configparser.ConfigParser()

try:
    cfg.read("faculty-of-ai-guide-assistant/config.conf")
    w = cfg["weaviate"]  # weaviate configuration
except:
    path = Path("config.conf")
    if not path.is_file():
        raise FileNotFoundError(f"Config file not found: {path.resolve()}")

    if "weaviate" not in cfg:
        raise KeyError(f"Missing [weaviate] section in {path}")
