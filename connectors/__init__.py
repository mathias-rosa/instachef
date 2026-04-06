from typing import Protocol


class InstachefConnector(Protocol):
    """Base interface for all InstaChef connectors."""

    async def run(self) -> None:
        """Run the connector."""
