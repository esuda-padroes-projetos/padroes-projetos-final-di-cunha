# Sistema de Gestão de Oficina Mecânica

Projeto para disciplinas de Padrões de Projetos de Softwares

## Tecnologias
- Backend: Python + Flask
- Frontend: HTML + CSS + JS (validações regex)
- Banco: SQLite (ou JSON via adapter)
- Padrões: Factory Method (criação de veículos), Adapter (persistência)

## Como Rodar
1. pip install -r requirements.txt
2. python app.py
3. Acesse http://127.0.0.1:5000/

## Padrões Aplicados
- Factory Method: factories/veiculo_factory.py
- Adapter: database/adapters/