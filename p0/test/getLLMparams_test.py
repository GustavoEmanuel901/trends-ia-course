import pytest

from usecases.getLLMparams import get_llm_params, get_input
from models.llmParams import LLMParams


class TestGetInput:
    def test_get_input_valid_value(self, monkeypatch):
        monkeypatch.setattr('builtins.input', lambda _: "5.5")
        result = get_input("Digite um valor: ", 1.0)
        assert result == 5.5

    def test_get_input_empty_uses_default(self, monkeypatch):
        monkeypatch.setattr('builtins.input', lambda _: "")
        result = get_input("Digite um valor: ", 10.0)
        assert result == 10.0

    def test_get_input_whitespace_uses_default(self, monkeypatch):
        monkeypatch.setattr('builtins.input', lambda _: "   ")
        result = get_input("Digite um valor: ", 15.0)
        assert result == 15.0

    def test_get_input_invalid_value_uses_default(self, monkeypatch, capsys):
        monkeypatch.setattr('builtins.input', lambda _: "abc")
        result = get_input("Digite um valor: ", 20.0)
        assert result == 20.0
        captured = capsys.readouterr()
        assert "Valor inválido" in captured.out

    @pytest.mark.parametrize("value,expected", [
        ("3.14", 3.14),
        ("0", 0.0),
        ("100.5", 100.5),
        ("-5.5", -5.5),
    ])
    def test_get_input_various_floats(self, monkeypatch, value, expected):
        monkeypatch.setattr('builtins.input', lambda _: value)
        result = get_input("Digite um valor: ", 1.0)
        assert result == expected


class TestGetLLMParams:

    def test_get_llm_params_use_defaults(self, monkeypatch):
        inputs = iter(["n"])
        monkeypatch.setattr('builtins.input', lambda _: next(inputs))
        
        result = get_llm_params()
        
        assert isinstance(result, LLMParams)
        assert result.timeout == 30.0
        assert result.temperature == 0.0
        assert result.max_tokens == 1024

    def test_get_llm_params_use_defaults_case_insensitive(self, monkeypatch):
        inputs = iter(["N"])
        monkeypatch.setattr('builtins.input', lambda _: next(inputs))
        
        result = get_llm_params()
        
        assert result.timeout == 30.0
        assert result.temperature == 0.0
        assert result.max_tokens == 1024

    def test_get_llm_params_custom_values(self, monkeypatch):
        inputs = iter([
            "s",          
            "60.5",       
            "0.8",        
            "2048"      
        ])
        monkeypatch.setattr('builtins.input', lambda _: next(inputs))
        
        result = get_llm_params()
        
        assert result.timeout == 60.5
        assert result.temperature == 0.8
        assert result.max_tokens == 2048

    def test_get_llm_params_temperature_invalid_uses_default(self, monkeypatch, capsys):
        inputs = iter([
            "s",           
            "30.0",      
            "abc",         
            "1024"       
        ])
        monkeypatch.setattr('builtins.input', lambda _: next(inputs))
        
        result = get_llm_params()
        
        assert result.temperature == 0.0  
        captured = capsys.readouterr()
        assert "Valor inválido" in captured.out

    def test_get_llm_params_timeout_invalid_uses_default(self, monkeypatch, capsys):
      
        inputs = iter([
            "s",          
            "invalid",   
            "0.5",        
            "512"         
        ])
        monkeypatch.setattr('builtins.input', lambda _: next(inputs))
        
        result = get_llm_params()
        
        assert result.timeout == 30.0 
        captured = capsys.readouterr()
        assert "Valor inválido" in captured.out

    def test_get_llm_params_max_tokens_invalid_uses_default(self, monkeypatch, capsys):
        inputs = iter([
            "s",           
            "45.0",       
            "0.6",         
            "not_a_number" 
        ])
        monkeypatch.setattr('builtins.input', lambda _: next(inputs))
        
        result = get_llm_params()
        
        assert result.max_tokens == 1024  
        captured = capsys.readouterr()
        assert "Valor inválido" in captured.out

    def test_get_llm_params_zero_values(self, monkeypatch):
    
        inputs = iter([
            "s",           
            "0",           
            "0",           
            "0"           
        ])
        monkeypatch.setattr('builtins.input', lambda _: next(inputs))
        
        result = get_llm_params()
        
        assert result.timeout == 0.0
        assert result.temperature == 0.0
        assert result.max_tokens == 0

    def test_get_llm_params_negative_values(self, monkeypatch):
        inputs = iter([
            "s",           
            "-1.5",       
            "-0.5",       
            "-100"        
        ])
        monkeypatch.setattr('builtins.input', lambda _: next(inputs))
        
        result = get_llm_params()
        
        assert result.timeout == -1.5
        assert result.temperature == -0.5
        assert result.max_tokens == -100

    def test_get_llm_params_large_values(self, monkeypatch):
        inputs = iter([
            "s",          
            "1000.5",     
            "2.0",         
            "100000"       
        ])
        monkeypatch.setattr('builtins.input', lambda _: next(inputs))
        
        result = get_llm_params()
        
        assert result.timeout == 1000.5
        assert result.temperature == 2.0
        assert result.max_tokens == 100000