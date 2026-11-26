# Relatório de execução

## Evolução por nível

- **Básico:** aplicação de terminal que recebe uma dúvida e apresenta a categoria e um resumo gerados pelo modelo de linguagem.
- **Intermediário:** código separado em módulos, configuração do serviço por variáveis de ambiente, validação da resposta e tratamento de erros da API.
- **Avançado:** parâmetros do modelo configuráveis pelo usuário (timeout, temperatura e limite de tokens) e ampliação dos testes automatizados para entradas, configurações e falhas simuladas.

## Decisões principais

| Decisão tomada | Alternativa considerada | Justificativa |
|---|---|---|
| Solicitar resposta estruturada conforme um modelo Pydantic. | Receber texto livre e interpretar manualmente. | Facilita validar os campos e os tipos esperados para a classificação. |
| Criação de Enum para guardar mensagens | Deixar todas as mensagens hardcode | Facilita manutenção e evita strings hardcode duplicadas
| Perguntar as configurações do LLM a cada pergunta | Perguntar apenas uma vez durante a sessão | O usuário poderia ter que mudar configurações como o timeout durante a sessão, durante alguns testes com o Gemini o tempo de resposta aumentou

## Testes e resultados

| Teste, entrada ou situação | Resultado esperado | Resultado obtido |
|---|---|---|
| Classificação com resposta válida (API simulada) | Retornar categoria e resumo estruturados. | Aprovado: classificação simulada validada; suíte completa passou (54 testes). |
| Entrada vazia ou composta por espaços | Encerrar a captura sem encaminhar texto vazio. | Aprovado: casos de entrada vazia passaram na suíte (54 testes no total). |
| Variável de ambiente ausente ou URL inválida | Informar erro de configuração sem chamar a API. | Aprovado: casos de configuração ausente e URL inválida passaram na suíte (54 testes no total). |
| Falhas simuladas da API (timeout, autenticação, limite de requisições e resposta inválida) | Converter a falha em uma mensagem de erro tratada pela aplicação. | Aprovado: mapeamento de falhas simuladas passou na suíte (54 testes no total). |

## Falhas e limitações

- **Uso do LLM**: Para essa tarefa o uso de LLM pode ser considerado um OVERKILL, pois técnicas simples de aprendizado de máquina conseguem fazer a classificação de textos muito bem. O uso de um modelo de linguagem se justifica em falta de bases de dados iniciais para treinar o modelo, pensando em um empresa pequena onde não tem dados guardados ou não quer consideram o trabalho juridico de capturar os dados de seus clientes.
- **Modelos de LLM utilizados**: Foram testados dois modelos de LLM o gemini-4-hydrogen que trouxe bons resultados, porém tem limites rigidos da conta gratuita e começa a dar erros de timeout (esse tempo pode ser configurado pelo usuário). O outro modelo testado foi o phi4-mini:3.8b rodando o Ollama localmente, esse modelo responde muito rápido porém em alguns momentos suas respostas são equivocadas.
- **Erros com o texto do Enum**: Durante o desenvolvimento descobri que não era possivel acessar o texto do Enum como em outras linguagens, mas para isso foi desenvolvido a lógica do `classificationError.py`.
- **Remover todas as strings hardcode**: As mensagens de erro foram transformadas em um Enum, porém todas as strings poderiam estar fora do código com hardcode

## Uso de IA no desenvolvimento

- **Ferramenta utilizada:** Github Copilot
- **Tarefa:** analisar e revisar código, testes e documentação durante o processo de desenvolvimento
- **Resultado aproveitado:** alguns testes que eu não havia pensado e a ferramenta sugeriu e também a estuturação e revisão ortográfica da documentação
- **Correções ou alterações realizadas:** em alguns momentos a ferramenta propos testes ou funcionalidades que não agregavam muito ao projeto
- **Verificação:** foram feitos testes manuais e automatizados em boa parte do código

## Reflexão final

- **Principal aprendizado:** integrar um modelo de linguagem também exige validar a configuração e tratar respostas e falhas externas.
- **Competência mais desenvolvida:** modularização da aplicação e criação de testes simulados para diferentes resultados.
- **Aspecto a aprimorar:** escrita da documentação durante o desenvolvimento e integração com algum serviço com Whatsapp
