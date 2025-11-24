# Sistema de Gestão de Oficina Mecânica 🚗🔧

Este projeto é uma aplicação web completa para gerenciamento de uma oficina mecânica, desenvolvida como requisito para a disciplina de **Padrões de Projetos de Software**.

O sistema aplica conceitos de Arquitetura MVC, Clean Code e Design Patterns clássicos (GoF) para resolver problemas reais de negócio.

---

## 🚀 Principais Funcionalidades

### 📊 Dashboard Operacional
- **Tela Inicial:** Visão geral imediata com indicadores de performance.
- **KPIs:** Total de clientes, Ordens em aberto e Faturamento total acumulado.

### 👥 Gestão de Clientes
- **Cadastro Completo:** Validação de dados obrigatórios.
- **UX Aprimorada:** Máscara de CPF automática (adiciona pontos e traço) e trava de 11 dígitos.
- **Histórico:** Visualização dos veículos vinculados a cada cliente na listagem.
- **Edição:** Permite corrigir dados cadastrais facilmente.

### 🚙 Gestão de Veículos (Frota)
- **Vínculo com Proprietário:** Cada veículo é amarrado a um cliente existente.
- **Seleção Inteligente (Cascading Dropdown):** Ao escolher o tipo (Carro/Moto), o sistema carrega as Marcas e, em seguida, os Modelos correspondentes.
- **Padronização:** Máscara de Placa automática (converte para maiúsculo e adiciona traço).
- **Proteção de Integridade:** Impede a exclusão de veículos que possuem histórico de Ordens de Serviço.

### 🛠️ Gestão de Serviços e Ordens (OS)
- **Catálogo Dinâmico:** Cadastro de novos tipos de serviços e preços.
- **Criação de OS:** - Filtro dinâmico de veículos (mostra apenas os carros do cliente selecionado).
  - Seleção múltipla de serviços via *Checkboxes*.
- **Controle Granular:** Possibilidade de finalizar itens da ordem individualmente (Status Parcial) ou finalizar a ordem completa com um clique.
- **Financeiro:** Formatação monetária padrão PT-BR (R$ 1.200,00).

---

## 🏗️ Arquitetura e Padrões de Projeto

O diferencial deste projeto é a aplicação prática de Design Patterns para desacoplar o código e facilitar a manutenção:

### 1. Chain of Responsibility 🔗
**Onde foi usado:** No processo de validação de cadastro de Usuários.
**Objetivo:** Criamos uma cadeia de validadores (`ValidadorCamposObrigatorios` -> `ValidadorCPF`). Se uma regra falha, a cadeia é interrompida e o erro retornado, evitando `ifs` aninhados complexos nas rotas.

### 2. Factory Method 🏭
**Onde foi usado:** Na criação de objetos `Veiculo`.
**Objetivo:** A classe `VeiculoFactory` encapsula a lógica de instanciação, garantindo que todo veículo criado tenha um proprietário válido e os dados corretos antes de chegar ao banco.

### 3. Adapter 🔌
**Onde foi usado:** Na camada de persistência de dados (`database/adapters`).
**Objetivo:** O sistema foi desenhado para ser agnóstico ao banco de dados. Atualmente usamos o `SQLiteAdapter`, mas a estrutura permite trocar para `JSONAdapter` ou `PostgresAdapter` sem alterar uma linha da regra de negócio.

---

## 🛠️ Tecnologias Utilizadas

- **Linguagem:** Python 3.x
- **Framework Web:** Flask
- **Front-end:** HTML5, CSS3, JavaScript (Fetch API para carregamento assíncrono).
- **Banco de Dados:** SQLite.
- **Testes:** Unittest (Python nativo).

---

## ▶️ Como Rodar o Projeto

1. **Clone o repositório ou baixe os arquivos.**

2. **Instale as dependências:**
   ```bash
   pip install -r requirements.txt