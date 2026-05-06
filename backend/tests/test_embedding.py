import pytest
from unittest.mock import MagicMock, patch
from services.embedding import get_embedding, get_embeddings_batch


def _mock_client(vectors):
    """Build a mock OpenAI client that returns given vectors."""
    client = MagicMock()
    items = [MagicMock(embedding=v, index=i) for i, v in enumerate(vectors)]
    client.embeddings.create.return_value = MagicMock(data=items)
    return client


def test_get_embedding_returns_vector():
    mock = _mock_client([[0.1, 0.2, 0.3]])
    result = get_embedding("hello", client=mock)
    assert result == [0.1, 0.2, 0.3]
    mock.embeddings.create.assert_called_once()


def test_batch_single_batch():
    vecs = [[float(i)] * 3 for i in range(5)]
    mock = _mock_client(vecs)
    result = get_embeddings_batch(["t"] * 5, client=mock, batch_size=10)
    assert len(result) == 5
    assert result[0] == [0.0, 0.0, 0.0]


def test_batch_multiple_batches():
    """Verify batching splits correctly."""
    vecs = [[float(i)] for i in range(6)]
    call_count = 0

    def fake_create(model, input):
        nonlocal call_count
        call_count += 1
        batch_vecs = vecs[call_count * 3 - 3 : call_count * 3]
        items = [MagicMock(embedding=v, index=j) for j, v in enumerate(batch_vecs)]
        return MagicMock(data=items)

    mock = MagicMock()
    mock.embeddings.create.side_effect = fake_create
    result = get_embeddings_batch(["t"] * 6, client=mock, batch_size=3)
    assert len(result) == 6
    assert mock.embeddings.create.call_count == 2


def test_batch_retry_on_failure():
    mock = MagicMock()
    items = [MagicMock(embedding=[1.0], index=0)]
    # Fail twice, succeed on third attempt
    mock.embeddings.create.side_effect = [
        Exception("rate limit"),
        Exception("rate limit"),
        MagicMock(data=items),
    ]
    result = get_embeddings_batch(["text"], client=mock, max_retries=3, retry_delay=0)
    assert result == [[1.0]]
    assert mock.embeddings.create.call_count == 3


def test_batch_raises_after_max_retries():
    mock = MagicMock()
    mock.embeddings.create.side_effect = Exception("always fails")
    with pytest.raises(RuntimeError, match="failed after"):
        get_embeddings_batch(["text"], client=mock, max_retries=2, retry_delay=0)