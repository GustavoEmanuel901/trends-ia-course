# trends-ia-course

## P0 — Classificador de dúvidas

Aplicação de terminal que envia uma dúvida a um serviço de linguagem compatível
com a API da OpenAI e apresenta a categoria e um resumo da resposta estruturada.
O serviço e o modelo são definidos por variáveis de ambiente.

### Requisitos

- Python 3.10 ou superior (testado em 3.13.3);
- credencial válida e acesso a um serviço compatível com a API da OpenAI;
- um modelo habilitado para a conta que aceite respostas estruturadas.


### Dependências Principais

| Biblioteca | Versão | Finalidade |
|-----------|--------|-----------|
| `openai` | 3.54.0 | Cliente da API OpenAI |
| `pydantic` | 2.14.3 | Validação de tipos e modelos |
| `python-dotenv` | 1.2.4 | Carregamento de variáveis de ambiente |
| `pytest` | 9.2.0 | Framework de testes |

**Versão do Python testada:** 3.13.3  
**Compatibilidade:** Python 3.10+

### Instalação

No terminal, a partir da raiz do repositório:

```bash
cd p0
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

No Windows PowerShell, ative o ambiente com:

```powershell
.\.venv\Scripts\Activate.ps1
```

### Configuração do acesso ao serviço

1. Crie uma chave de API na conta do provedor escolhido e confirme que ela tem
   permissão para usar o modelo desejado.
2. Copie `.env.example` para `.env`.
3. Preencha as três variáveis em `.env` com os valores fornecidos pelo provedor:

   ```dotenv
   LLM_API_KEY=sua_chave_de_api
   LLM_BASE_URL=https://url-base-do-provedor/v1
   LLM_MODEL=id-do-modelo-disponibilizado
   ```

`LLM_BASE_URL` deve ser uma URL HTTP ou HTTPS sem credenciais, parâmetros de
consulta ou fragmento. O endpoint deve ser compatível com o cliente OpenAI usado
pelo programa e aceitar a solicitação de resposta estruturada. A URL e o
identificador do modelo variam por provedor; consulte a documentação do serviço
para obter os valores corretos. A chave é secreta: mantenha-a somente no `.env`
local, que não deve ser compartilhado nem enviado ao repositório.

### Execução

Ainda dentro de `p0`, com o ambiente virtual ativado e o `.env` configurado:

```bash
python main.py
```

Digite a dúvida quando solicitado. Depois do resultado, responda `s` para
classificar outra dúvida ou qualquer outro valor para encerrar.

### Exemplo de entrada e saída

Exemplo ilustrativo — a classificação e o resumo são gerados pelo serviço e
podem variar:

```text
Qual sua dúvida ou problema? Meu computador não liga.

--- Resultado da Classificação ---
Categoria ID: 2
Categoria:  suporte_tecnico_hardware
Resumo:     Computador não liga
Deseja tirar mais dúvidas? (s/n): n
```

As categorias disponíveis são operacional (1), suporte técnico de hardware (2),
suporte técnico de software (3), vendas (4) e outros (5).

### Registros de Execução (Logging)

A aplicação registra informações sobre sua execução em tempo real, sem expor dados
sensíveis:

**Informações registradas:**
- Início e fim de cada classificação
- Carregamento de configuração (hostname do servidor, parâmetros de geração)
- Fluxo de execução (validação, conexão, processamento)
- Erros e exceções (com contexto, sem credenciais)

**Dados NÃO registrados (proteção de privacidade):**
- Chaves de API (`LLM_API_KEY`)
- URLs completas de endpoint (apenas hostname é registrado)
- Tokens de resposta da API
- Credenciais de autenticação
- Dados pessoais do usuário ou conteúdo específico das dúvidas

**Exemplo de log:**
```
2026-11-19 22:36:00 - text_classifier.main - INFO - Iniciando aplicação de classificação de texto
2026-11-19 22:36:05 - text_classifier.llm_params - INFO - Usando valores padrão do LLM: timeout=30.0, temperature=0.0, max_tokens=1024
2026-11-19 22:36:08 - text_classifier.classifier - INFO - Conectando ao servidor LLM: api.openai.com
2026-11-19 22:36:10 - text_classifier.classifier - INFO - Classificação completada com sucesso
```

### Testes reais e simulados

- **Execução real:** `python main.py` chama o endpoint configurado usando a
  chave e o modelo da conta. Requer conexão, pode consumir cota ou gerar custos,
  e a resposta depende do modelo.
- **Execução simulada:** os testes automatizados executam a lógica de
  classificação com mocks, sem chamar o serviço real. Isso permite validar o
  comportamento esperado, testar casos de erro e verificar a tratamento de
  exceções sem custos.

#### Rodando os testes

Dentro de `p0`, com o ambiente virtual ativado:

```bash
python -m pytest test/
```

Ou execute apenas os testes de um arquivo específico:

```bash
python -m pytest test/textClassifier_test.py -v
```

#### Cobertura de testes

O suite de testes valida:

**Entrada de dados (`getEntry`)**
- Captura correta de entrada do usuário
- Remoção de espaços em branco (`strip()`)
- Retorno de `None` para entrada vazia
- Tratamento de entrada apenas com espaços

**Parâmetros do LLM (`getLLMparams`)**
- Função `get_input`: conversão de valores float, uso de padrões
- Validação de entrada vazia e com espaços
- Tratamento de valores inválidos com fallback para padrão
- Parametrização com múltiplos valores (positivos, zero, negativos, grandes)
- Função `get_llm_params`: escolha de usar valores padrão ou customizados
- Case-insensitive na entrada do usuário
- Validação individual de timeout, temperature e max_tokens inválidos

**Total: 53 casos de teste** que cobrem:
- Entrada e validação de dados (6 testes)
- Parâmetros do LLM (17 testes)
- Classificação e tratamento de erros (30 testes)
