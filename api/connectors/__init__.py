from typing import Protocol


class CookachuConnector(Protocol):
    """Base interface for all Cookachu connectors."""

    async def run(self) -> None:
        """Run the connector."""
