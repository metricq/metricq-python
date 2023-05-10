import pytest

from metricq import Agent

# Yes, the tests are fragile. But it's the only way to test this.
# We can remove it once the whole management_url fallback is gone


def test_agent_url() -> None:
    agent = Agent(token="test", url="amqps://test.invalid")
    assert agent._management_url == "amqps://test.invalid"


def test_agent_management_url() -> None:
    with pytest.warns(DeprecationWarning):
        agent = Agent(token="test", management_url="amqps://test.invalid")
        assert agent._management_url == "amqps://test.invalid"


def test_agent_url_and_management_url() -> None:
    with pytest.warns(DeprecationWarning):
        with pytest.raises(TypeError):
            Agent(
                token="test",
                url="amqps://test.invalid",
                management_url="amqps://test.invalid",
            )
