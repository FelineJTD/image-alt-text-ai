import json
import uuid
from pprint import pprint
from graph import run_graph
# from rag_graph import update_vectorstore

def generate_alt_text(data):
    try:
        # Generate random thread ID
        data['thread_id'] = str(uuid.uuid4())
        result = run_graph(data, data.get('thread_id'))
        return result
    except Exception as e:
        return str(e)

pprint(generate_alt_text({
    "context": "test",
}))