# 🦇 Wayne Industries — Sistema de Controle de Segurança

Aplicação web full stack desenvolvida como projeto final do curso **Dev Full Stack**.

---

## 🗂️ Estrutura do Projeto

```
wayne-industries/
├── app.py              # Aplicação Flask (rotas e lógica)
├── database.py         # Camada de dados (SQLite + funções CRUD)
├── requirements.txt    # Dependências Python
├── wayne.db            # Banco de dados (gerado automaticamente)
├── templates/
│   ├── base.html       # Layout base com sidebar
│   ├── login.html      # Página de login
│   ├── dashboard.html  # Painel de controle com gráficos
│   ├── resources.html  # Gestão de recursos (CRUD)
│   └── users.html      # Gestão de usuários (CRUD) — somente admin
└── static/
    ├── css/style.css   # Tema escuro Wayne Industries
    └── js/main.js      # JavaScript: modais, API calls, gráficos
```

---

## 🚀 Como rodar

### 1. Instale as dependências

```bash
pip install -r requirements.txt
```

### 2. Inicie a aplicação

```bash
python app.py
```

### 3. Acesse no navegador

```
http://localhost:5000
```

---

## 👤 Contas pré-cadastradas

| Nome              | E-mail               | Senha      | Perfil      |
|-------------------|----------------------|------------|-------------|
| Bruce Wayne       | bruce@wayne.com      | batman123  | **Admin**   |
| Alfred Pennyworth | alfred@wayne.com     | butler456  | Gerente     |
| Lucius Fox        | lucius@wayne.com     | tech789    | Gerente     |
| Dick Grayson      | dick@wayne.com       | robin101   | Funcionário |

---

## 🔐 Sistema de Permissões

| Ação                        | Admin | Gerente | Funcionário |
|-----------------------------|:-----:|:-------:|:-----------:|
| Ver dashboard               | ✅    | ✅      | ✅          |
| Ver recursos                | ✅    | ✅      | ✅          |
| Adicionar / Editar recursos | ✅    | ✅      | ❌          |
| Remover recursos            | ✅    | ❌      | ❌          |
| Gerenciar usuários          | ✅    | ❌      | ❌          |

---

## 📋 Funcionalidades

### Dashboard
- Cards com totais: recursos, operacionais, em manutenção, usuários ativos
- Gráfico de donuts: distribuição por tipo (veículo, equipamento, dispositivo)
- Gráfico de barras: recursos por status
- Gráfico de barras: usuários por perfil
- Feed de atividade recente (logs de auditoria)

### Gestão de Recursos
- Listagem de todos os recursos com busca em tempo real
- Adição de novos recursos (admin/gerente)
- Edição de recursos existentes (admin/gerente)
- Remoção de recursos (somente admin)
- Tipos: Veículo, Equipamento, Dispositivo de Segurança
- Status: Operacional, Em Manutenção, Inativo

### Gestão de Usuários *(somente admin)*
- Listagem de usuários com busca
- Criação de novos usuários com perfil
- Edição de dados e troca de senha
- Ativação/desativação de contas
- Remoção de usuários

### Logs de Auditoria
- Registro automático de: login, logout, adição/edição/remoção de recursos
- Exibidos no dashboard em tempo real

---

## 🛠️ Stack Tecnológica

| Camada     | Tecnologia                   |
|------------|------------------------------|
| Backend    | Python 3 + Flask             |
| Banco      | SQLite (via módulo `sqlite3`) |
| Frontend   | HTML5 + CSS3 + JavaScript ES6|
| Gráficos   | Chart.js 4 (CDN)             |
| Auth       | Flask Sessions + SHA-256     |

---

## 📌 Notas de Desenvolvimento

- Senhas armazenadas com hash SHA-256
- Controle de acesso via decoradores (`@roles_required`)
- API REST para CRUD com respostas JSON
- Logs de auditoria automáticos em todas as operações
- Interface responsiva com sidebar colapsável
- Dados de demonstração pré-carregados automaticamente

---

*Desenvolvido para o Projeto Final — Infinity School · Dev Full Stack*
