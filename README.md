# Documentação do Projeto: Autocuidado - TeaTime
## 1. Visão Geral

### Tecnologia Utilizada:
- Python  
- FastAPI  
- Uvicorn  
- JSON  

**Descrição:** Implementação de uma API backend que oferece funcionalidades de autocuidado, como gestão de hábitos saudáveis, registros diários e frases motivacionais.   
**Objetivo:** Criar uma plataforma digital para promover o bem-estar dos utilizadores através da organização e incentivo à prática de hábitos saudáveis.

---

## 2. Descrição Detalhada do Projeto

### O que é o projeto?
Plano de Autocuidado é uma plataforma web moderna e responsiva voltada para o bem-estar e equilíbrio emocional, permitindo ao utilizador acompanhar seus hábitos diários, metas e progresso pessoal, com funcionalidades de gamificação e mensagens motivacionais.

### 2.1 Funcionalidades Principais
- **Funcionalidade 01:** Criar e gerenciar hábitos personalizados (ex:hidratação, exercícios, skincare).  
- **Funcionalidade 02:** Registrar práticas diárias de autocuidado. 
- **Funcionalidade 03:** Acompanhar progresso semanal e histórico com gráficos e conquistas.  
- **Funcionalidade 04:** Receber mensagens motivacionais diárias, com temas positivos e sugestôes por IA.  
- **Funcionalidade 05:** Acesso ao ranking semanal com os utilizadores mais consistentes, promovendo motivação e engajamento através da gamificação.

### 2.2 Arquitetura do Código
```plaintext
teatime/
├── main.py                         
├── models.py          
├── schemas.py         
├── database.py  
├── Dockerfile
├── requirements.txt     
├── data/
|   |── users.json         
|   |── habits.json          
|   |── logs.json          
```

## 3. Etapas de Entrega (Cronograma Detalhado)

### Etapa 1:
- Levantamento de requisitos
- Definição do escopo inicial
- Criação do repositório e estrutura inicial do projeto

### Etapa 2:
- Implementação da estrutura base com FastAPI
- Definição dos modelos Pydantic
- Primeiros testes locais com Uvicorn

### Etapa 3:
- Desenvolvimento das funcionalidades principais
- Testes unitários e de integração
- Validação com stakeholders

### Etapa 4:
- Otimizações e refatorações
- Documentação técnica (README, endpoints da API, etc.)
- Preparação para deploy

### Etapa 5:
- Deploy em ambiente de produção
- Monitorização e correções pós-lançamento
- Encerramento do projeto e relatório final
