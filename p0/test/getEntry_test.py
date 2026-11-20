import pytest

from usecases.getEntry import get_entry


@pytest.fixture
def prompt():
    return "Digite algo: "


@pytest.mark.parametrize("entrada", ["alguma entrada", "outra entrada", "teste 123"])
def test_get_entry(monkeypatch, prompt, entrada):
    """Testa se get_entry retorna corretamente a entrada do usuário"""
    monkeypatch.setattr('builtins.input', lambda _: entrada)
    assert get_entry(prompt) == entrada


def test_get_entry_with_whitespace(monkeypatch, prompt):
    """Testa se get_entry remove espaços em branco da entrada"""
    monkeypatch.setattr('builtins.input', lambda _: "  texto com espaços  ")
    assert get_entry(prompt) == "texto com espaços"


def test_get_entry_empty(monkeypatch, prompt, capsys):
    """Testa se get_entry retorna None para entrada vazia"""
    monkeypatch.setattr('builtins.input', lambda _: "")
    result = get_entry(prompt)
    assert result is None
    captured = capsys.readouterr()
    assert "Entrada vazia" in captured.out


def test_get_entry_empty_with_spaces(monkeypatch, prompt):
    """Testa se get_entry trata entrada apenas com espaços como vazia"""
    monkeypatch.setattr('builtins.input', lambda _: "   ")
    assert get_entry(prompt) is None