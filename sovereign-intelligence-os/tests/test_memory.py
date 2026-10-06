from orchestrator.memory import ForeverMemory


def test_memory_add_query_count_and_dedup(tmp_path):
    memory = ForeverMemory(tmp_path / "memory")

    first_id = memory.add("alpha memory", metadata={"source": "test"})
    second_id = memory.add("alpha memory", metadata={"source": "test"})
    third_id = memory.add("beta memory", metadata={"source": "test"})

    assert first_id == second_id
    assert first_id != third_id
    assert memory.count() == 2

    results = memory.query("alpha", n_results=2)
    assert results
    assert any(item["document"] == "alpha memory" for item in results)

    preview = memory.peek(limit=5)
    assert len(preview) == 2
    assert {item["id"] for item in preview} == {first_id, third_id}
