# 🍀 Meoo Daily

**Créditos de login diário do Meoo · script único para várias contas · resultados JSONL**

[简体中文](../README.md) · [English](README.en.md) · [繁體中文](README.zh-Hant.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · [Português (BR)](README.pt-BR.md)

> [!WARNING]
> `--status` envia a mesma requisição `GET /api/mc/entitlement/init` do modo normal. Essa requisição concede os créditos de login diário. `--status` altera apenas o modo e o texto do relatório; não é uma consulta somente leitura.

## O que faz

O script chama:

```http
GET https://meoo.com/api/mc/entitlement/init
Cookie: <Cookie completo do navegador>
```

Ele verifica `dailyLoginGranted`, `dailyLoginSkipReason`, `dailyLoginGrantAmount` e `dailyLoginBalanceAfter`; HTTP 200 sozinho não é tratado como sucesso.

## Início rápido

```powershell
python -m pip install -r requirements.txt
$env:MEOO_COOKIE = "sessionid=REPLACE_WITH_COOKIE; other_cookie=REPLACE_ME"
python .\meoo_daily.py
```

Para várias contas, use `MEOO_COOKIES` com um par `nota|Cookie` por linha:

```text
principal|sessionid=REPLACE_WITH_COOKIE
secundaria|sessionid=REPLACE_WITH_ANOTHER_COOKIE
```

`MEOO_COOKIES` tem prioridade sobre `MEOO_COOKIE`. As notificações opcionais usam `PUSHPLUS_TOKEN` e `QYWX_WEBHOOK`.

## Qinglong

1. Envie `meoo_daily.py`.
2. Adicione `MEOO_COOKIES` ou `MEOO_COOKIE` nas variáveis de ambiente.
3. Instale `requests`.
4. Crie uma tarefa diária com o comando `task meoo_daily.py`.

## GitHub Actions

Faça Fork / Import do repositório, adicione o Cookie como Actions Secret e execute o workflow manualmente uma vez. O [workflow](../.github/workflows/meoo.yml) incluído roda testes em `push`, executa uma vez por dia em `schedule`, converte o JSONL do console em uma matriz JSON e envia os dois formatos de relatório como artifact.

## Critérios de sucesso

- `GRANTED`: os créditos foram concedidos nesta requisição.
- `ALREADY_GRANTED`: o servidor retornou `ALREADY_GRANTED_TODAY`.
- Qualquer erro de autenticação, redirecionamento, rede, HTTP, JSON ou formato de resposta faz `SUMMARY.ok` ser false.

## Uso e privacidade

O repositório oficial é gratuito. Revenda, cobrança pelo acesso, implantação paga, personificação do autor e remoção de avisos de copyright são proibidas. Consulte [NOTICE.md](../NOTICE.md).

Cookies são credenciais de login. Mantenha-os em variáveis de ambiente ou GitHub Secrets. Não faça commit de Cookies reais, números de telefone, relatórios, logs ou arquivos locais de autenticação.

Mantido originalmente por L0NE-6.
