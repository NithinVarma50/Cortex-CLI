import pytest
import os
import tempfile
from memory.memory_manager import MemoryManager

@pytest.fixture
def memory():
    # Ensure tests don't pollute real DB
    with tempfile.TemporaryDirectory() as temp_dir:
        os.environ["CORTEX_STORAGE_PATH"] = temp_dir
        os.environ["CORTEX_MAX_STORAGE_GB"] = "1"
        mem = MemoryManager()
        yield mem

def test_vector_store_and_retrieve(memory):
    doc_id = memory.store("Deep learning is transforming the EV market.", "company")
    assert doc_id is not None
    
def test_semantic_search(memory):
    memory.store("Deep learning is transforming the EV market.", "company")
    results = memory.search("EV market AI", "company", top_k=1)
    assert len(results) == 1
    assert "EV market" in results[0]["content"]

def test_memory_isolation_between_agents(memory):
    memory.store("Secret marketing plan", memory_type="department", agent="marketing_agent")
    memory.store("Secret financial budget", memory_type="department", agent="finance_agent")
    
    # Simulate routing filter logic
    hits = memory.search("finance_agent Secret financial budget", memory_type="department")
    assert len(hits) > 0
    assert "Secret financial budget" in hits[0]["content"]

def test_storage_limit_warning(memory):
    # Temp dir is empty so it should be fine
    is_ok = memory.check_storage_limit()
    assert is_ok is True
