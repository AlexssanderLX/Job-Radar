# Job Radar

Aplicação local para pesquisar, comparar e acompanhar vagas usando múltiplos cargos, habilidades, stacks, perfis e fontes configuráveis.

## Executar no Windows

1. Instale Python 3.11+ e Node.js 20+.
2. Execute `start-all.bat`.
3. Abra `http://localhost:5174`.

Também é possível iniciar separadamente com `start-backend.bat` e `start-frontend.bat`.

## Desenvolvimento

```powershell
cd backend
python -m pip install -r requirements.txt
python -m pytest

cd ..\frontend
npm install
npm run dev
```

A API FastAPI fica em `http://localhost:8010` e a documentação em `http://localhost:8010/docs`. O SQLite é criado localmente e não é versionado. O frontend usa `http://localhost:5174`, evitando conflito com o Lead Finder em `http://localhost:8000`.

## Pesquisa web indexada (opcional)

Os conectores públicos funcionam sem chave. Para também transformar resultados indexados de LinkedIn, Lever, Gupy e Greenhouse em vagas individuais, copie `backend/.env.example` para `backend/.env` e configure:

```env
WEB_SEARCH_PROVIDER=serper
WEB_SEARCH_API_KEY=sua-chave
```

A chave permanece somente no backend. Sem configuração, a aplicação continua funcional e apresenta as pesquisas externas como fallback.

## Privacidade

O histórico de links registra apenas vagas e pesquisas abertas por botões dentro do Job Radar. Ele fica no SQLite local; o aplicativo não lê o histórico geral do navegador, cookies ou credenciais.
