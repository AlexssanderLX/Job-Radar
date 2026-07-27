# Job Radar

Aplicação local para pesquisar, comparar e acompanhar vagas usando múltiplos cargos, habilidades, stacks, perfis e fontes configuráveis.

## Executar no Windows

1. Instale Python 3.11+ e Node.js 20+.
2. Execute `start-all.bat`.
3. Abra `http://localhost:5173`.

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

A API FastAPI fica em `http://localhost:8000` e a documentação em `http://localhost:8000/docs`. O SQLite é criado localmente e não é versionado.
