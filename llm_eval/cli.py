"""Interface de linha de comando do llm-eval."""

import click


@click.group()
@click.version_option()
def main() -> None:
    """llm-eval: Framework para avaliação de confiabilidade de chatbots baseados em LLMs."""


if __name__ == "__main__":
    main()
