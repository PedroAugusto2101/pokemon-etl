# ETL no Databricks com Data Lakehouse — Guia Prático

> 📚 Guia completo e didático para construir pipelines ETL no Databricks usando a arquitetura Lakehouse (Delta Lake + Unity Catalog)

[![Databricks](https://img.shields.io/badge/Databricks-FF3621?style=flat&logo=databricks&logoColor=white)](https://databricks.com/)
[![Delta Lake](https://img.shields.io/badge/Delta%20Lake-00ADD8?style=flat&logo=deltalake&logoColor=white)](https://delta.io/)
[![Apache Spark](https://img.shields.io/badge/Apache%20Spark-E25A1C?style=flat&logo=apachespark&logoColor=white)](https://spark.apache.org/)

---

## 📖 Sumário

- [🔍 Visão Geral](#-visão-geral)
- [🏗️ Arquitetura de Alto Nível](#️-arquitetura-de-alto-nível)
- [🧠 Conceitos Fundamentais](#-conceitos-fundamentais)
- [💻 Workspace e GitOps](#-workspace-e-gitops)
- [✅ Boas Práticas](#-boas-práticas)
- [🚀 Pipeline ETL - Passo a Passo](#-pipeline-etl---passo-a-passo)
- [⚡ Performance e Custo](#-performance-e-custo)
- [🔒 Segurança e Governança](#-segurança-e-governança)
- [📊 Monitoramento e Auditoria](#-monitoramento-e-auditoria)
- [📁 Estrutura do Projeto](#-estrutura-do-projeto)
- [🔧 Snippets Úteis](#-snippets-úteis)
- [📚 Glossário](#-glossário)

---

## 🔍 Visão Geral

### O que é o Databricks?

O **Databricks** é uma **plataforma unificada de dados** que integra:

- 🔧 **Engenharia de Dados**
- 🧪 **Ciência de Dados**
- 📊 **Analytics**
- 💼 **Business Intelligence**

### Características Principais

| Aspecto           | Descrição                                                |
| ----------------- | -------------------------------------------------------- |
| **Arquitetura**   | Roda **sobre** clouds (AWS/Azure/GCP), não é um provedor |
| **Interface**     | Desenvolvimento via navegador, sem instalação local      |
| **Gerenciamento** | Automatiza clusters, jobs, catálogos e lineage           |
| **Lakehouse**     | Combina flexibilidade de data lake + recursos de banco   |

> 💡 **Lakehouse** = Data Lake + Delta Lake + Unity Catalog (governança)

---

## 🏗️ Arquitetura de Alto Nível

```text
┌─────────────────────── Plataforma Databricks ───────────────────────┐
│                                                                     │
│ ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐         │
│ │   Workspace     │ │   Workflows     │ │ Unity Catalog   │         │
│ │ (Notebooks/.py) │ │    (Jobs)       │ │ (Governança)    │         │
│ └─────────────────┘ └─────────────────┘ └─────────────────┘         │
│                              │                                      │
└──────────────────────────────┼──────────────────────────────────────┘
                               ▼
              ┌─────────────────────────────────┐
              │     Compute / Clusters Spark    │
              │      Driver + Workers           │
              │   (Autoscaling, Photon)         │
              └─────────────────────────────────┘
                               │
                               ▼
              ┌─────────────────────────────────┐
              │      I/O Operations             │
              │   (Read/Write Storage)          │
              └─────────────────────────────────┘
                               │
           ┌───────────────────┴────────────────────┐
           ▼                                        ▼
┌─────────────────────┐                  ┌─────────────────────┐
│   Cloud Storage     │ ◄────────────► │     Delta Lake      │
│ S3/ADLS/GCS        │                  │ Time Travel/ACID    │
│ (Volumes/Tables)    │                  │    Governance       │
└─────────────────────┘                  └─────────────────────┘
```

---

## 🧠 Conceitos Fundamentais

### 🏢 Databricks vs Cloud Provider

| Aspecto           | Databricks         | Cloud Provider         |
| ----------------- | ------------------ | ---------------------- |
| **Função**        | Orquestra recursos | Fornece infraestrutura |
| **Cobrança**      | Plataforma + Infra | Apenas infraestrutura  |
| **Gerenciamento** | Automatizado       | Manual                 |
| **Compute**       | Efêmero (se perde) | Persistente            |

### ⚙️ Compute (Clusters)

#### Componentes

- **Driver**: Nó coordenador (1 por cluster)
- **Workers**: Nós de processamento (escaláveis)

#### Tipos de Runtime

| Runtime      | Descrição         | Uso Recomendado           |
| ------------ | ----------------- | ------------------------- |
| **Standard** | Spark padrão      | Workloads gerais          |
| **LTS**      | Long Term Support | Produção                  |
| **Photon**   | Motor vetorizado  | SQL/DataFrames intensivos |

#### Estratégias de Custo

```text
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   On-Demand     │    │      Spot       │    │  Auto-Scaling   │
│                 │    │                 │    │                 │
│ ✅ Disponível   │    │ ✅ Mais barato  │    │ ✅ Dinâmico     │
│ ❌ Mais caro    │    │ ❌ Preemptível  │    │ ⚡ Baseado em   │
│                 │    │                 │    │    demanda      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### 💾 Storage (Data Lake/Lakehouse)

#### Separação de Responsabilidades

- **Compute**: Processa dados (efêmero)
- **Storage**: Armazena dados (persistente)

#### Evolução: Lake → Lakehouse

```text
Data Lake          +          Database Features          =          Lakehouse
────────────────────────────────────────────────────────────────────────────────
• Flexibilidade    +    • ACID Transactions           =    • Melhor de ambos
• Baixo custo      +    • Schema enforcement          =    • Delta Lake
• Escalabilidade   +    • Time Travel                 =    • Unity Catalog
• Formato aberto   +    • Governança                  =    • Performance
```

### 🔺 Delta Lake

#### Características Principais

| Recurso                 | Benefício             |
| ----------------------- | --------------------- |
| **ACID**                | Transações confiáveis |
| **Time Travel**         | Histórico de versões  |
| **Schema Evolution**    | Evolução segura       |
| **MERGE/UPDATE/DELETE** | Operações DML         |
| **Otimizações**         | Z-Order, compactação  |

#### Transaction Log

```text
📁 tabela_delta/
├── 📄 part-00000.parquet
├── 📄 part-00001.parquet
└── 📁 _delta_log/
    ├── 📄 00000000000000000000.json  ← Transação 0
    ├── 📄 00000000000000000001.json  ← Transação 1
    └── 📄 00000000000000000002.json  ← Transação 2
```

### 🏛️ Unity Catalog (Governança)

#### Hierarquia

```text
🏢 Metastore
├── 📚 Catalog A
│   ├── 📂 Schema 1
│   │   ├── 📋 Table X
│   │   └── 👁️ View Y
│   └── 📂 Schema 2
└── 📚 Catalog B
    └── 📂 Schema 3
```

#### Managed vs External Tables

| Tipo         | Gerenciamento | Ao Dropar       | Uso Recomendado      |
| ------------ | ------------- | --------------- | -------------------- |
| **Managed**  | Databricks    | Apaga arquivos  | Dados internos       |
| **External** | Usuário       | Mantém arquivos | Dados compartilhados |

### 📦 Volumes, Mounts e Buckets

#### Evolução dos Padrões

```text
Legacy (Mounts)          →          Modern (Unity Catalog)
─────────────────────────────────────────────────────────────
/mnt/bucket-name/        →          /Volumes/catalog/schema/volume/

• Sem governança         →          • Governança integrada
• Permissões complexas   →          • Permissões Unity Catalog
• Deprecated             →          • Recomendado
```

---

## 💻 Workspace e GitOps

### 🔄 Integração com Git

#### Workflow Recomendado

```text
1. 🌿 Feature Branch     →     2. 💻 Desenvolvimento     →     3. 🔍 Code Review
   feat/nova-feature            Notebooks/Scripts               Pull Request
           │                           │                           │
           ▼                           ▼                           ▼
4. ✅ Aprovação         →     5. 🔄 Merge Main         →     6. 🚀 Deploy
   Code Review                 Branch Principal              Produção
```

### 📝 Notebooks vs Scripts

| Aspecto               | Notebooks         | Scripts (.py) |
| --------------------- | ----------------- | ------------- |
| **Exploração**        | ✅ Excelente      | ❌ Limitado   |
| **Visualização**      | ✅ Integrada      | ❌ Externa    |
| **SQL + Python**      | ✅ Magic commands | ❌ Separado   |
| **Reprodutibilidade** | ⚠️ Moderada       | ✅ Excelente  |
| **Testes**            | ❌ Difícil        | ✅ Fácil      |
| **CI/CD**             | ⚠️ Complexo       | ✅ Simples    |

### 🎯 Dicas de Produtividade

```python
# Magic commands úteis
%sql SELECT * FROM tabela LIMIT 10
%fs ls /Volumes/catalog/schema/volume/
%sh pip install requests

# SQL → DataFrame Python
# Cell SQL
SELECT * FROM bronze.projeto.tabela;

# Cell Python (próxima)
df = _sqldf  # Último resultado SQL
```

---

## ✅ Boas Práticas

### 🏗️ Arquitetura Medallion

```text
🗂️ Raw/Landing     →     🥉 Bronze     →     🥈 Silver     →     🥇 Gold
────────────────────────────────────────────────────────────────────────
📁 Arquivos         →    📋 Tabelas    →    📋 Tabelas    →    📋 Tabelas
   Brutos                 Mínimas           Limpas            Analíticas

• Como chegou       →    • Deduplicação →   • Joins        →   • Agregações
• JSON/CSV/Parquet  →    • Timestamps   →   • Validações   →   • KPIs
• Volumes           →    • Schema basic →   • Normalização →   • Dashboards
```

### 🔄 Princípios de Design

#### 1. Desacoplamento

```text
❌ Extração + Transformação Acoplada
┌─────────────────────────────────────┐
│ API → Transform → Save              │  ← Se API muda, quebra tudo
└─────────────────────────────────────┘

✅ Extração Desacoplada
┌─────────┐    ┌─────────┐    ┌─────────┐
│ API →   │ →  │ Raw →   │ →  │ Bronze  │
│ Save    │    │ Bronze  │    │ Silver  │
└─────────┘    └─────────┘    └─────────┘
```

#### 2. Idempotência

```sql
-- ❌ Não idempotente
INSERT INTO tabela SELECT * FROM fonte;

-- ✅ Idempotente
MERGE INTO tabela AS t
USING fonte AS s ON t.id = s.id
WHEN MATCHED THEN UPDATE SET *
WHEN NOT MATCHED THEN INSERT *;
```

### 📝 Convenções de Nomenclatura

| Elemento        | Padrão                | Exemplo              |
| --------------- | --------------------- | -------------------- |
| **Catalog**     | `ambiente`            | `dev`, `prod`        |
| **Schema**      | `dominio_projeto`     | `vendas_ecommerce`   |
| **Tabela**      | `tb_dominio_entidade` | `tb_vendas_pedidos`  |
| **Volume**      | `v_tipo`              | `v_raw`, `v_staging` |
| **Arquivo Raw** | `entidade_YYYY-MM-DD` | `pedidos_2024-01-15` |

### 🔒 Segurança

```python
# ✅ Use Databricks Secrets
token = dbutils.secrets.get("key-vault", "api-token")

# ❌ Nunca hardcode credentials
token = "abc123..."  # NUNCA FAÇA ISSO!
```

---

## 🚀 Pipeline ETL - Passo a Passo

### 📋 Pré-requisitos

#### Checklist de Ambiente

- [ ] ✅ Metastore Unity Catalog criado
- [ ] ✅ Storage Credentials configurado
- [ ] ✅ External Locations criadas
- [ ] ✅ Cluster com Runtime LTS
- [ ] ✅ Photon habilitado (se aplicável)
- [ ] ✅ Auto Termination configurado

### 1️⃣ Preparar Ambiente

#### 1.1 Configurar Unity Catalog

```sql
-- Verificar metastore
SHOW METASTORES;

-- Verificar external locations
SHOW EXTERNAL LOCATIONS;
```

#### 1.2 Configurar Cluster

| Configuração         | Valor Recomendado       |
| -------------------- | ----------------------- |
| **Runtime**          | LTS (Latest)            |
| **Photon**           | Enabled (SQL workloads) |
| **Auto Termination** | 60 minutos              |
| **Workers**          | 2-8 (com autoscaling)   |

### 2️⃣ Criar Catálogos e Schemas

```sql
-- Estrutura Medallion
CREATE CATALOG IF NOT EXISTS raw;
CREATE CATALOG IF NOT EXISTS bronze;
CREATE CATALOG IF NOT EXISTS silver;
CREATE CATALOG IF NOT EXISTS gold;

-- Schemas por projeto
CREATE SCHEMA IF NOT EXISTS raw.meu_projeto;
CREATE SCHEMA IF NOT EXISTS bronze.meu_projeto;
CREATE SCHEMA IF NOT EXISTS silver.meu_projeto;
CREATE SCHEMA IF NOT EXISTS gold.meu_projeto;
```

### 3️⃣ Criar Volumes para Raw

```sql
-- Volume para arquivos brutos
CREATE VOLUME IF NOT EXISTS raw.meu_projeto.v_raw
LOCATION 's3://meu-bucket/landing/meu_projeto/';

-- Verificar criação
SHOW VOLUMES IN raw.meu_projeto;
```

### 4️⃣ Ingestão Raw (Arquivos Brutos)

#### Script de Ingestão API

```python
# Notebook: ingestion/01_raw_api_ingestion
import json
import datetime as dt
import requests

# Configurações
API_URL = "https://pokeapi.co/api/v2/pokemon?limit=1000"
run_ts = dt.datetime.utcnow().strftime("%Y-%m-%d_%H%M%S")
base_dir = f"/Volumes/raw/meu_projeto/v_raw/pokemon/extract_ts={run_ts}"

# Criar diretório
dbutils.fs.mkdirs(base_dir)

# Extrair dados
try:
    response = requests.get(API_URL, timeout=30)
    response.raise_for_status()

    # Salvar como chegou
    file_path = f"{base_dir}/pokemon.json"
    dbutils.fs.put(file_path, json.dumps(response.json()), overwrite=True)

    print(f"✅ Dados salvos em: {file_path}")

except Exception as e:
    print(f"❌ Erro na ingestão: {e}")
    raise
```

### 5️⃣ Tabelas Bronze

#### Processamento Bronze

```python
# Notebook: transform/02_bronze_processing
from pyspark.sql.functions import (
    input_file_name,
    current_timestamp,
    regexp_extract
)

# Ler dados raw
raw_path = "/Volumes/raw/meu_projeto/v_raw/pokemon/*/*.json"
df_raw = spark.read.option("multiline", "true").json(raw_path)

# Adicionar metadados técnicos
df_bronze = (
    df_raw
    .dropDuplicates()
    .withColumn("_ingestion_ts", current_timestamp())
    .withColumn("_source_file", input_file_name())
    .withColumn("_extract_date",
                regexp_extract(input_file_name(), r"extract_ts=(\d{4}-\d{2}-\d{2})", 1))
)

# Salvar como tabela Delta
(df_bronze
 .write
 .format("delta")
 .mode("overwrite")
 .option("mergeSchema", "true")
 .saveAsTable("bronze.meu_projeto.tb_pokemon_raw"))

print("✅ Tabela Bronze criada com sucesso!")
```

### 6️⃣ Tabelas Silver

#### Limpeza e Normalização

```sql
-- Notebook: transform/03_silver_processing

-- Criar tabela Silver inicial
CREATE OR REPLACE TABLE silver.meu_projeto.tb_pokemon_clean
USING DELTA
AS
SELECT
  -- Dados de negócio
  explode(results) as pokemon_data,
  _ingestion_ts,
  _extract_date
FROM bronze.meu_projeto.tb_pokemon_raw;

-- Normalizar estrutura
CREATE OR REPLACE TABLE silver.meu_projeto.tb_pokemon_list
USING DELTA
AS
SELECT
  pokemon_data.name as pokemon_name,
  pokemon_data.url as pokemon_url,
  regexp_extract(pokemon_data.url, r'/(\d+)/', 1)::int as pokemon_id,
  _ingestion_ts,
  _extract_date,
  current_timestamp() as _silver_processed_ts
FROM silver.meu_projeto.tb_pokemon_clean
WHERE pokemon_data.name IS NOT NULL;
```

#### Upsert Pattern

```sql
-- Merge incremental (idempotente)
MERGE INTO silver.meu_projeto.tb_pokemon_list AS target
USING (
  SELECT DISTINCT
    pokemon_name,
    pokemon_url,
    pokemon_id,
    _ingestion_ts,
    _extract_date,
    current_timestamp() as _silver_processed_ts
  FROM silver.meu_projeto.tb_pokemon_clean
  WHERE _extract_date = current_date()
) AS source
ON target.pokemon_id = source.pokemon_id
WHEN MATCHED THEN
  UPDATE SET *
WHEN NOT MATCHED THEN
  INSERT *;
```

### 7️⃣ Tabelas Gold

#### Modelos Analíticos

```sql
-- Notebook: transform/04_gold_analytics

-- Métricas de negócio
CREATE OR REPLACE TABLE gold.meu_projeto.vw_pokemon_metrics
USING DELTA
AS
SELECT
  COUNT(*) as total_pokemon,
  COUNT(DISTINCT _extract_date) as total_extractions,
  MIN(_ingestion_ts) as first_ingestion,
  MAX(_ingestion_ts) as last_ingestion,
  current_timestamp() as _gold_processed_ts
FROM silver.meu_projeto.tb_pokemon_list;

-- Análise temporal
CREATE OR REPLACE TABLE gold.meu_projeto.vw_pokemon_daily_stats
USING DELTA
AS
SELECT
  _extract_date,
  COUNT(*) as pokemon_count,
  COUNT(DISTINCT pokemon_name) as unique_pokemon,
  MIN(_ingestion_ts) as batch_start,
  MAX(_ingestion_ts) as batch_end
FROM silver.meu_projeto.tb_pokemon_list
GROUP BY _extract_date
ORDER BY _extract_date DESC;
```

### 8️⃣ Orquestração com Workflows

#### Configuração do Job

```json
{
  "name": "pokemon_etl_pipeline",
  "description": "Pipeline ETL completo para dados Pokemon",
  "git_source": {
    "git_provider": "github",
    "git_url": "https://github.com/usuario/projeto",
    "git_branch": "main"
  },
  "tasks": [
    {
      "task_key": "raw_ingestion",
      "description": "Ingestão de dados brutos da API",
      "notebook_task": {
        "notebook_path": "src/ingestion/01_raw_api_ingestion"
      },
      "job_cluster_key": "etl_cluster"
    },
    {
      "task_key": "bronze_processing",
      "description": "Processamento Bronze",
      "depends_on": [{ "task_key": "raw_ingestion" }],
      "notebook_task": {
        "notebook_path": "src/transform/02_bronze_processing"
      },
      "job_cluster_key": "etl_cluster"
    },
    {
      "task_key": "silver_processing",
      "description": "Processamento Silver",
      "depends_on": [{ "task_key": "bronze_processing" }],
      "sql_task": {
        "file": {
          "path": "src/transform/03_silver_processing.sql"
        }
      },
      "job_cluster_key": "etl_cluster"
    },
    {
      "task_key": "gold_analytics",
      "description": "Criação de modelos Gold",
      "depends_on": [{ "task_key": "silver_processing" }],
      "sql_task": {
        "file": {
          "path": "src/transform/04_gold_analytics.sql"
        }
      },
      "job_cluster_key": "etl_cluster"
    }
  ],
  "job_clusters": [
    {
      "job_cluster_key": "etl_cluster",
      "new_cluster": {
        "cluster_name": "",
        "spark_version": "13.3.x-scala2.12",
        "node_type_id": "i3.xlarge",
        "num_workers": 2,
        "autoscale": {
          "min_workers": 1,
          "max_workers": 4
        }
      }
    }
  ],
  "schedule": {
    "quartz_cron_expression": "0 0 6 * * ?",
    "timezone_id": "UTC"
  }
}
```

### 9️⃣ Parametrização

#### Notebooks com Widgets

```python
# Criar parâmetros
dbutils.widgets.text("process_date", "")
dbutils.widgets.dropdown("environment", "dev", ["dev", "staging", "prod"])

# Usar parâmetros
process_date = dbutils.widgets.get("process_date")
environment = dbutils.widgets.get("environment")

# Validação
if not process_date:
    process_date = datetime.now().strftime("%Y-%m-%d")

print(f"Processando data: {process_date} no ambiente: {environment}")
```

#### Scripts Python com ArgumentParser

```python
# src/utils/config.py
import argparse
from datetime import datetime

def get_config():
    parser = argparse.ArgumentParser(description='ETL Pokemon Pipeline')
    parser.add_argument('--process-date',
                       default=datetime.now().strftime("%Y-%m-%d"),
                       help='Data de processamento (YYYY-MM-DD)')
    parser.add_argument('--environment',
                       choices=['dev', 'staging', 'prod'],
                       default='dev',
                       help='Ambiente de execução')
    return parser.parse_args()

# Uso no script
if __name__ == "__main__":
    config = get_config()
    print(f"Executando para {config.process_date} em {config.environment}")
```

### 🔟 Ingestão Incremental (Streaming)

#### Auto Loader Pattern

```python
# Configuração do stream
checkpoint_path = "/Volumes/raw/meu_projeto/v_raw/_checkpoints/pokemon_bronze"
source_path = "/Volumes/raw/meu_projeto/v_raw/pokemon"

# Stream de leitura com Auto Loader
stream_df = (spark.readStream
             .format("cloudFiles")
             .option("cloudFiles.format", "json")
             .option("cloudFiles.schemaLocation", f"{checkpoint_path}/schema")
             .option("cloudFiles.inferColumnTypes", "true")
             .load(source_path))

# Adicionar metadados de streaming
stream_processed = (stream_df
                   .withColumn("_stream_ingestion_ts", current_timestamp())
                   .withColumn("_source_file", input_file_name()))

# Escrever como stream
query = (stream_processed.writeStream
         .format("delta")
         .outputMode("append")
         .option("checkpointLocation", checkpoint_path)
         .trigger(availableNow=True)  # Batch incremental
         .toTable("bronze.meu_projeto.tb_pokemon_stream"))

# Aguardar conclusão
query.awaitTermination()
print("✅ Stream processado com sucesso!")
```

### 1️⃣1️⃣ Exposição para BI

#### SQL Warehouse Setup

```sql
-- Criar view otimizada para BI
CREATE OR REPLACE VIEW gold.meu_projeto.pokemon_dashboard AS
SELECT
  pokemon_name,
  pokemon_id,
  _extract_date as data_coleta,
  CASE
    WHEN pokemon_id <= 151 THEN 'Geração 1'
    WHEN pokemon_id <= 251 THEN 'Geração 2'
    ELSE 'Outras'
  END as geracao,
  _silver_processed_ts as ultima_atualizacao
FROM silver.meu_projeto.tb_pokemon_list
ORDER BY pokemon_id;

-- Grant de acesso para grupo BI
GRANT SELECT ON gold.meu_projeto.pokemon_dashboard TO `bi-team`;
```

#### Power BI Connection

```text
📋 Checklist Power BI:
1. ✅ Criar SQL Warehouse no Databricks
2. ✅ Copiar Server Hostname e HTTP Path
3. ✅ Instalar Databricks Connector no Power BI
4. ✅ Configurar autenticação (Token/OAuth)
5. ✅ Testar conexão
6. ✅ Criar relatórios
```

---

## ⚡ Performance e Custo

### 🚀 Otimizações de Performance

#### Delta Lake Optimizations

```sql
-- Compactação e Z-Ordering
OPTIMIZE silver.meu_projeto.tb_pokemon_list
ZORDER BY (pokemon_id, _extract_date);

-- Auto Optimize (configuração de tabela)
ALTER TABLE silver.meu_projeto.tb_pokemon_list
SET TBLPROPERTIES (
  'delta.autoOptimize.optimizeWrite' = 'true',
  'delta.autoOptimize.autoCompact' = 'true'
);

-- Particionamento por data
CREATE TABLE silver.meu_projeto.tb_pokemon_partitioned
USING DELTA
PARTITIONED BY (_extract_date)
AS SELECT * FROM silver.meu_projeto.tb_pokemon_list;
```

#### Cluster Optimizations

| Configuração         | Impacto   | Recomendação            |
| -------------------- | --------- | ----------------------- |
| **Photon**           | 🚀 High   | SQL/DataFrame workloads |
| **Autoscaling**      | 💰 Medium | Min=1, Max=8 workers    |
| **Spot Instances**   | 💰 High   | Batch tolerante         |
| **Auto Termination** | 💰 High   | 30-60 minutos           |

### 💰 Estratégias de Custo

#### Compute Cost Optimization

```text
💡 Dicas de Economia:

1. 🎯 Right-sizing
   ├── Use clusters menores para desenvolvimento
   ├── Autoscaling baseado em demanda
   └── Job clusters vs All-purpose clusters

2. ⏰ Scheduling
   ├── Jobs em horários de menor demanda
   ├── Auto-termination agressivo
   └── Pause clusters não utilizados

3. 💾 Storage
   ├── Lifecycle policies (S3/ADLS)
   ├── VACUUM regulares
   └── Compactação automática
```

#### Monitoring de Custos

```python
# Verificar métricas de cluster
cluster_metrics = spark.sql("""
  SELECT
    cluster_id,
    cluster_name,
    uptime_hours,
    cost_estimate
  FROM system.compute.clusters
  WHERE cluster_name LIKE '%meu_projeto%'
""")

display(cluster_metrics)
```

---

## 🔒 Segurança e Governança

### 🛡️ Unity Catalog Security

#### Modelo de Permissões

```sql
-- Criar grupos
CREATE GROUP data_engineers;
CREATE GROUP data_analysts;
CREATE GROUP bi_users;

-- Permissões por camada
-- Bronze: Apenas Data Engineers
GRANT SELECT, INSERT, UPDATE, DELETE ON CATALOG bronze TO data_engineers;

-- Silver: Data Engineers + Data Analysts
GRANT SELECT, INSERT, UPDATE, DELETE ON CATALOG silver TO data_engineers;
GRANT SELECT ON CATALOG silver TO data_analysts;

-- Gold: Todos os grupos
GRANT SELECT, INSERT, UPDATE, DELETE ON CATALOG gold TO data_engineers;
GRANT SELECT ON CATALOG gold TO data_analysts;
GRANT SELECT ON CATALOG gold TO bi_users;
```

#### Row-Level Security

```sql
-- View com filtro dinâmico
CREATE VIEW gold.meu_projeto.pokemon_filtered AS
SELECT *
FROM gold.meu_projeto.vw_pokemon_daily_stats
WHERE CASE
  WHEN is_member('admin') THEN TRUE
  WHEN is_member('data_analysts') THEN _extract_date >= current_date() - 30
  ELSE _extract_date >= current_date() - 7
END;
```

### 🔐 Secrets Management

```python
# Configurar secrets scope
# CLI: databricks secrets create-scope --scope "api-keys"

# Usar secrets no código
def get_api_credentials():
    return {
        'api_key': dbutils.secrets.get("api-keys", "pokemon-api-key"),
        'base_url': dbutils.secrets.get("api-keys", "pokemon-base-url")
    }

# ❌ NUNCA faça isso:
# api_key = "hardcoded-key-123"  # VULNERABILIDADE!
```

### 📊 Data Quality

#### Validações Automáticas

```python
# src/utils/data_quality.py
from pyspark.sql.functions import col, count, when, isnan, isnull

def run_data_quality_checks(df, table_name):
    """Executa verificações de qualidade de dados"""

    total_rows = df.count()

    # Verificações básicas
    quality_checks = {}

    for column in df.columns:
        null_count = df.filter(col(column).isNull()).count()
        null_percentage = (null_count / total_rows) * 100

        quality_checks[column] = {
            'null_count': null_count,
            'null_percentage': round(null_percentage, 2)
        }

    # Log resultados
    print(f"📊 Quality Check para {table_name}:")
    print(f"   Total de registros: {total_rows}")

    for col_name, metrics in quality_checks.items():
        if metrics['null_percentage'] > 10:  # Threshold
            print(f"   ⚠️  {col_name}: {metrics['null_percentage']}% nulls")
        else:
            print(f"   ✅ {col_name}: {metrics['null_percentage']}% nulls")

    return quality_checks

# Uso
quality_results = run_data_quality_checks(df_silver, "tb_pokemon_list")
```

---

## 📊 Monitoramento e Auditoria

### 📈 Data Lineage

#### Visualização Automática

```sql
-- Verificar lineage via SQL
SHOW LINEAGE TABLE silver.meu_projeto.tb_pokemon_list;

-- Histórico de alterações
DESCRIBE HISTORY silver.meu_projeto.tb_pokemon_list;
```

#### Lineage Programático

```python
# Capturar informações de lineage
def log_lineage(source_table, target_table, transformation_type):
    lineage_info = {
        'source': source_table,
        'target': target_table,
        'transformation': transformation_type,
        'timestamp': datetime.now(),
        'user': spark.sql("SELECT current_user()").collect()[0][0],
        'notebook': dbutils.notebook.entry_point.getDbutils().notebook().getContext().notebookPath().get()
    }

    # Log em tabela de auditoria
    lineage_df = spark.createDataFrame([lineage_info])
    (lineage_df.write
     .format("delta")
     .mode("append")
     .saveAsTable("system.audit.lineage_log"))

# Uso
log_lineage("bronze.projeto.tb_raw", "silver.projeto.tb_clean", "cleaning")
```

### 🔍 Time Travel e Auditoria

#### Consultas Históricas

```sql
-- Ver todas as versões
DESCRIBE HISTORY silver.meu_projeto.tb_pokemon_list;

-- Consultar versão específica
SELECT COUNT(*) as registros_v0
FROM silver.meu_projeto.tb_pokemon_list VERSION AS OF 0;

-- Consultar por timestamp
SELECT *
FROM silver.meu_projeto.tb_pokemon_list
TIMESTAMP AS OF '2024-01-15T10:00:00Z'
LIMIT 10;

-- Comparar versões
WITH v0 AS (
  SELECT COUNT(*) as count_v0
  FROM silver.meu_projeto.tb_pokemon_list VERSION AS OF 0
),
current AS (
  SELECT COUNT(*) as count_current
  FROM silver.meu_projeto.tb_pokemon_list
)
SELECT
  count_v0,
  count_current,
  count_current - count_v0 as difference
FROM v0 CROSS JOIN current;
```

#### Restore e Rollback

```sql
-- Restaurar versão anterior
RESTORE silver.meu_projeto.tb_pokemon_list VERSION AS OF 2;

-- Ou por timestamp
RESTORE silver.meu_projeto.tb_pokemon_list
TIMESTAMP AS OF '2024-01-15T09:00:00Z';
```

### 📋 Monitoring Dashboard

#### Métricas de Pipeline

```sql
-- View de monitoramento
CREATE OR REPLACE VIEW system.monitoring.pipeline_health AS
SELECT
  'pokemon_pipeline' as pipeline_name,
  -- Métricas Bronze
  (SELECT COUNT(*) FROM bronze.meu_projeto.tb_pokemon_raw) as bronze_count,
  (SELECT MAX(_ingestion_ts) FROM bronze.meu_projeto.tb_pokemon_raw) as bronze_last_update,

  -- Métricas Silver
  (SELECT COUNT(*) FROM silver.meu_projeto.tb_pokemon_list) as silver_count,
  (SELECT MAX(_silver_processed_ts) FROM silver.meu_projeto.tb_pokemon_list) as silver_last_update,

  -- Métricas Gold
  (SELECT COUNT(*) FROM gold.meu_projeto.vw_pokemon_daily_stats) as gold_count,

  -- Health check
  CASE
    WHEN (SELECT MAX(_ingestion_ts) FROM bronze.meu_projeto.tb_pokemon_raw) > current_timestamp() - INTERVAL 1 DAY
    THEN 'Healthy'
    ELSE 'Stale'
  END as pipeline_status,

  current_timestamp() as check_timestamp;
```

#### Alertas Automáticos

```python
# src/monitoring/alerts.py
def check_pipeline_health():
    """Verifica saúde do pipeline e envia alertas"""

    health_df = spark.sql("SELECT * FROM system.monitoring.pipeline_health")
    health_data = health_df.collect()[0]

    # Verificações
    alerts = []

    # Data freshness
    if health_data.bronze_last_update < datetime.now() - timedelta(hours=25):
        alerts.append({
            'type': 'DATA_FRESHNESS',
            'message': f'Bronze data stale: {health_data.bronze_last_update}',
            'severity': 'HIGH'
        })

    # Data quality
    bronze_count = health_data.bronze_count
    silver_count = health_data.silver_count

    if silver_count < bronze_count * 0.95:  # 5% tolerance
        alerts.append({
            'type': 'DATA_QUALITY',
            'message': f'Significant data loss: Bronze({bronze_count}) vs Silver({silver_count})',
            'severity': 'MEDIUM'
        })

    # Enviar alertas (implementar webhook/email)
    if alerts:
        send_alerts(alerts)

    return alerts

def send_alerts(alerts):
    """Enviar alertas via webhook/email/Slack"""
    # Implementar integração
    for alert in alerts:
        print(f"🚨 ALERT [{alert['severity']}]: {alert['message']}")
```

---

## 📁 Estrutura do Projeto

### 🗂️ Layout Recomendado

```text
📦 databricks-pokemon-etl/
├── 📋 README.md
├── 📋 requirements.txt
├── 📋 setup.py
├── 📋 .gitignore
├── 📋 .databricks-cli
│
├── 📁 src/
│   ├── 📁 ingestion/
│   │   ├── 📄 01_raw_api_ingestion.py
│   │   ├── 📄 02_raw_file_ingestion.py
│   │   └── 📄 __init__.py
│   │
│   ├── 📁 transform/
│   │   ├── 📄 02_bronze_processing.py
│   │   ├── 📄 03_silver_processing.sql
│   │   ├── 📄 04_gold_analytics.sql
│   │   └── 📄 __init__.py
│   │
│   ├── 📁 utils/
│   │   ├── 📄 config.py
│   │   ├── 📄 data_quality.py
│   │   ├── 📄 io_helpers.py
│   │   └── 📄 __init__.py
│   │
│   └── 📁 monitoring/
│       ├── 📄 alerts.py
│       ├── 📄 metrics.py
│       └── 📄 __init__.py
│
├── 📁 notebooks/
│   ├── 📁 exploration/
│   │   ├── 📓 01_data_exploration.py
│   │   ├── 📓 02_schema_analysis.sql
│   │   └── 📓 03_quality_checks.py
│   │
│   ├── 📁 development/
│   │   ├── 📓 prototype_bronze.py
│   │   ├── 📓 prototype_silver.py
│   │   └── 📓 prototype_gold.py
│   │
│   └── 📁 dashboards/
│       ├── 📓 pokemon_metrics.py
│       └── 📓 pipeline_monitoring.py
│
├── 📁 workflows/
│   ├── 📄 pokemon_etl_dev.json
│   ├── 📄 pokemon_etl_prod.json
│   └── 📄 monitoring_job.json
│
├── 📁 sql/
│   ├── 📄 setup_catalogs.sql
│   ├── 📄 setup_permissions.sql
│   └── 📄 setup_monitoring.sql
│
├── 📁 tests/
│   ├── 📁 unit/
│   │   ├── 📄 test_data_quality.py
│   │   ├── 📄 test_transformations.py
│   │   └── 📄 __init__.py
│   │
│   ├── 📁 integration/
│   │   ├── 📄 test_pipeline_e2e.py
│   │   └── 📄 __init__.py
│   │
│   └── 📄 conftest.py
│
├── 📁 config/
│   ├── 📄 dev.yaml
│   ├── 📄 staging.yaml
│   ├── 📄 prod.yaml
│   └── 📄 secrets.yaml.template
│
└── 📁 docs/
    ├── 📄 setup.md
    ├── 📄 deployment.md
    ├── 📄 troubleshooting.md
    └── 📁 images/
        └── 🖼️ architecture.png
```

### ⚙️ Configuração de Ambiente

#### requirements.txt

```text
# Databricks runtime já inclui muitas libs
# Adicione apenas o que é específico do projeto

requests>=2.31.0
pyyaml>=6.0
pytest>=7.0.0
databricks-cli>=0.17.0

# Para desenvolvimento local (opcional)
pyspark>=3.4.0
delta-spark>=2.4.0
```

#### config/dev.yaml

```yaml
# Configuração para ambiente de desenvolvimento
environment: dev

catalogs:
  raw: raw_dev
  bronze: bronze_dev
  silver: silver_dev
  gold: gold_dev

storage:
  base_path: 's3://mybucket/dev/'
  checkpoints: 's3://mybucket/dev/_checkpoints/'

cluster:
  runtime: '13.3.x-scala2.12'
  node_type: 'i3.xlarge'
  min_workers: 1
  max_workers: 2
  photon: true
  auto_termination: 30

api:
  pokemon_base_url: 'https://pokeapi.co/api/v2'
  timeout: 30

monitoring:
  alerts_enabled: false
  webhook_url: null
```

---

## 🔧 Snippets Úteis

### 💾 Operações Delta Lake

#### Escrita e Leitura

```python
# Escrever DataFrame como tabela Delta
(df.write
 .format("delta")
 .mode("overwrite")  # append, overwrite, ignore, error
 .option("mergeSchema", "true")  # Evolução automática de schema
 .option("overwriteSchema", "true")  # Para mode overwrite
 .saveAsTable("catalog.schema.table"))

# Ler tabela Delta
df = spark.table("catalog.schema.table")

# Ler com filtros
df = spark.table("catalog.schema.table").filter("date >= '2024-01-01'")
```

#### MERGE (Upsert)

```sql
-- Template MERGE genérico
MERGE INTO {target_table} AS target
USING (
  SELECT DISTINCT *
  FROM {source_table}
  WHERE {incremental_filter}
) AS source
ON {join_condition}
WHEN MATCHED THEN
  UPDATE SET *
WHEN NOT MATCHED THEN
  INSERT *;
```

#### Otimizações

```sql
-- Compactação com Z-Order
OPTIMIZE catalog.schema.table
ZORDER BY (column1, column2);

-- Vacuum (limpeza de arquivos antigos)
VACUUM catalog.schema.table RETAIN 168 HOURS;

-- Estatísticas (opcional, para cost-based optimizer)
ANALYZE TABLE catalog.schema.table COMPUTE STATISTICS FOR ALL COLUMNS;
```

### 🔍 Debugging e Monitoramento

#### Informações de Tabela

```sql
-- Informações gerais
DESCRIBE EXTENDED catalog.schema.table;

-- Histórico de operações
DESCRIBE HISTORY catalog.schema.table;

-- Detalhes de arquivos
DESCRIBE DETAIL catalog.schema.table;

-- Schema evolution
SHOW COLUMNS IN catalog.schema.table;
```

#### Performance Analysis

```python
# Análise de partições
spark.sql("""
  SELECT
    input_file_name() as file_path,
    COUNT(*) as row_count,
    MAX(_ingestion_ts) as max_timestamp
  FROM catalog.schema.table
  GROUP BY input_file_name()
  ORDER BY row_count DESC
""").display()

# Estatísticas de execução
query = spark.sql("SELECT COUNT(*) FROM large_table")
query.explain(True)  # Plano de execução detalhado
```

### 📊 Utilitários de Databricks

#### dbutils Essentials

```python
# Sistema de arquivos
dbutils.fs.ls("/Volumes/catalog/schema/volume/")
dbutils.fs.cp("source_path", "dest_path", recurse=True)
dbutils.fs.rm("/path/to/delete", recurse=True)

# Informações do cluster/notebook
dbutils.notebook.entry_point.getDbutils().notebook().getContext().notebookPath().get()
spark.sql("SELECT current_user() as user, current_database() as db").display()

# Secrets (sempre via secrets)
api_key = dbutils.secrets.get("scope-name", "key-name")

# Widgets para parametrização
dbutils.widgets.text("param_name", "default_value", "Parameter Description")
param_value = dbutils.widgets.get("param_name")
```

#### SQL Magic Commands

```python
# SQL em célula Python
result_df = spark.sql("""
  SELECT COUNT(*) as total
  FROM catalog.schema.table
""")

# Magic command (notebook)
# %%sql
# SELECT * FROM catalog.schema.table LIMIT 10;

# Capturar resultado do SQL magic
# df = _sqldf  # Resultado da última célula %%sql
```

### 🌊 Streaming Patterns

#### Auto Loader Template

```python
def create_auto_loader_stream(source_path, target_table, checkpoint_path, file_format="json"):
    """Template para Auto Loader stream"""

    stream_df = (spark.readStream
                 .format("cloudFiles")
                 .option("cloudFiles.format", file_format)
                 .option("cloudFiles.schemaLocation", f"{checkpoint_path}/schema")
                 .option("cloudFiles.inferColumnTypes", "true")
                 .option("cloudFiles.maxFilesPerTrigger", 1000)
                 .load(source_path))

    # Adicionar metadados
    stream_processed = (stream_df
                       .withColumn("_stream_ts", current_timestamp())
                       .withColumn("_source_file", input_file_name()))

    # Configurar escrita
    query = (stream_processed.writeStream
             .format("delta")
             .outputMode("append")
             .option("checkpointLocation", checkpoint_path)
             .trigger(availableNow=True)  # Batch mode
             .toTable(target_table))

    return query

# Uso
query = create_auto_loader_stream(
    source_path="/Volumes/raw/project/landing/",
    target_table="bronze.project.streaming_table",
    checkpoint_path="/Volumes/raw/project/_checkpoints/streaming"
)
query.awaitTermination()
```

### 🔗 Conectividade e APIs

#### HTTP Requests com Retry

```python
import requests
from time import sleep
from typing import Dict, Any

def api_request_with_retry(url: str, headers: Dict[str, str] = None,
                          max_retries: int = 3, timeout: int = 30) -> Dict[Any, Any]:
    """Faz requisição HTTP com retry automático"""

    for attempt in range(max_retries):
        try:
            response = requests.get(url, headers=headers, timeout=timeout)
            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            if attempt == max_retries - 1:  # Último attempt
                raise Exception(f"Failed after {max_retries} attempts: {e}")

            wait_time = 2 ** attempt  # Backoff exponencial
            print(f"Attempt {attempt + 1} failed. Retrying in {wait_time}s...")
            sleep(wait_time)

# Uso
pokemon_data = api_request_with_retry(
    url="https://pokeapi.co/api/v2/pokemon/1",
    headers={"User-Agent": "Databricks-ETL/1.0"}
)
```

#### Multiprocessing para APIs

```python
from multiprocessing import Pool
from functools import partial
import json

def fetch_pokemon_data(pokemon_id: int, base_url: str) -> dict:
    """Busca dados de um Pokemon específico"""
    url = f"{base_url}/pokemon/{pokemon_id}"
    data = api_request_with_retry(url)

    return {
        'pokemon_id': pokemon_id,
        'data': data,
        'extracted_at': datetime.utcnow().isoformat()
    }

def parallel_pokemon_extraction(pokemon_ids: list, base_url: str, workers: int = 4):
    """Extração paralela de dados de Pokemon"""

    fetch_func = partial(fetch_pokemon_data, base_url=base_url)

    with Pool(processes=workers) as pool:
        results = list(tqdm(
            pool.imap_unordered(fetch_func, pokemon_ids),
            total=len(pokemon_ids),
            desc="Extracting Pokemon data"
        ))

    return results

# Uso
pokemon_ids = range(1, 151)  # Primeira geração
results = parallel_pokemon_extraction(pokemon_ids, "https://pokeapi.co/api/v2")
```

---

## 📚 Glossário

### 🔤 Termos Técnicos

| Termo                  | Definição                                                                  | Exemplo/Contexto              |
| ---------------------- | -------------------------------------------------------------------------- | ----------------------------- |
| **ACID**               | Atomicity, Consistency, Isolation, Durability - propriedades de transações | Delta Lake garante ACID       |
| **Auto Loader**        | Funcionalidade de ingestão incremental automática                          | `cloudFiles` format           |
| **Autoscaling**        | Ajuste automático de recursos baseado na demanda                           | Min/Max workers               |
| **Checkpoint**         | Ponto de controle para streams, garante exactly-once                       | `/path/_checkpoints/`         |
| **Cluster**            | Conjunto de VMs para processamento distribuído                             | Driver + Workers              |
| **Delta Lake**         | Formato de storage transacional sobre Parquet                              | `.delta` tables               |
| **Driver**             | Nó coordenador do cluster Spark                                            | Orquestra Workers             |
| **External Location**  | Configuração UC para acessar storage externo                               | S3/ADLS/GCS paths             |
| **Idempotente**        | Operação que pode ser repetida sem efeitos colaterais                      | MERGE operations              |
| **Job Cluster**        | Cluster efêmero criado apenas para execução de job                         | Cost-effective                |
| **Lakehouse**          | Arquitetura que combina data lake + warehouse                              | Delta + UC + Compute          |
| **Lineage**            | Rastreamento de origem e transformações dos dados                          | Upstream/Downstream           |
| **LTS**                | Long Term Support - versão com suporte estendido                           | Runtime LTS                   |
| **Medallion**          | Arquitetura Bronze/Silver/Gold para data quality                           | raw → bronze → silver → gold  |
| **Metastore**          | Catálogo central de metadados                                              | Unity Catalog component       |
| **Photon**             | Motor de execução vetorizado da Databricks                                 | SQL/DataFrame acceleration    |
| **Runtime**            | Versão do Spark com otimizações Databricks                                 | 13.3.x-scala2.12              |
| **Schema Evolution**   | Capacidade de evoluir schema automaticamente                               | Add/rename columns            |
| **Spot Instance**      | VM com preço reduzido mas preemptível                                      | Cost optimization             |
| **Storage Credential** | Credenciais para acessar storage externo                                   | IAM roles, Service principals |
| **Time Travel**        | Consulta a versões históricas de tabelas Delta                             | VERSION AS OF                 |
| **Unity Catalog**      | Sistema de governança e catalog da Databricks                              | Permissions, lineage          |
| **VACUUM**             | Operação de limpeza de arquivos antigos em Delta                           | Garbage collection            |
| **Volume**             | Área de arquivos gerenciada pelo Unity Catalog                             | `/Volumes/cat/schema/vol`     |
| **Widget**             | Parâmetro de entrada em notebooks                                          | `dbutils.widgets`             |
| **Worker**             | Nó de processamento no cluster Spark                                       | Executes tasks                |
| **Workflow**           | Orquestração de tarefas (DAG)                                              | Databricks Jobs               |
| **Z-Order**            | Técnica de clustering para otimizar queries                                | `ZORDER BY (col)`             |

### 🏗️ Padrões de Arquitetura

| Padrão                     | Descrição                                         | Benefícios             |
| -------------------------- | ------------------------------------------------- | ---------------------- |
| **Medallion Architecture** | Bronze (raw) → Silver (clean) → Gold (business)   | Qualidade progressiva  |
| **Lambda Architecture**    | Batch + Stream processing paralelos               | Real-time + historical |
| **Kappa Architecture**     | Apenas stream processing                          | Simplicidade           |
| **Data Mesh**              | Domínios descentralizados com governança federada | Scalability            |
| **ELT vs ETL**             | Extract-Load-Transform vs Extract-Transform-Load  | Cloud-native approach  |

### 📊 Formatos e Protocolos

| Formato/Protocolo | Uso                   | Características      |
| ----------------- | --------------------- | -------------------- |
| **Parquet**       | Storage columnar      | Compressão, schemas  |
| **Delta**         | Transactional storage | ACID, time travel    |
| **JSON**          | Semi-structured data  | Human readable       |
| **Avro**          | Schema evolution      | Backwards compatible |
| **JDBC/ODBC**     | Database connectivity | BI tools integration |
| **REST API**      | Web services          | HTTP-based           |

### 🔧 Ferramentas e Integrações

| Ferramenta         | Categoria              | Integração Databricks   |
| ------------------ | ---------------------- | ----------------------- |
| **Power BI**       | Business Intelligence  | SQL Warehouse connector |
| **Tableau**        | Data Visualization     | JDBC/ODBC               |
| **Apache Airflow** | Workflow Orchestration | REST API integration    |
| **dbt**            | Analytics Engineering  | Databricks adapter      |
| **MLflow**         | ML Lifecycle           | Native integration      |
| **Git**            | Version Control        | Repos integration       |
| **Terraform**      | Infrastructure as Code | Databricks provider     |

---

## 🎯 Resumo Executivo

### 🚀 Quick Start Checklist

```text
📋 Para começar com Databricks + Lakehouse:

1. 🏗️ Setup Inicial
   ├── ✅ Criar workspace Databricks
   ├── ✅ Configurar Unity Catalog
   ├── ✅ Conectar storage (S3/ADLS/GCS)
   └── ✅ Criar primeiro cluster

2. 📊 Dados e Governança
   ├── ✅ Criar estrutura Medallion (Bronze/Silver/Gold)
   ├── ✅ Configurar volumes para raw data
   ├── ✅ Definir permissões Unity Catalog
   └── ✅ Implementar data quality checks

3. 🔄 Pipeline ETL
   ├── ✅ Ingestão raw (APIs, files)
   ├── ✅ Transformações Bronze → Silver → Gold
   ├── ✅ Orquestração com Workflows
   └── ✅ Monitoring e alertas

4. 📈 Analytics e BI
   ├── ✅ SQL Warehouse para BI
   ├── ✅ Dashboards Databricks
   ├── ✅ Conexão Power BI/Tableau
   └── ✅ Exposição via REST APIs
```

### 💡 Principais Benefícios

| Benefício             | Descrição                                        | Impacto             |
| --------------------- | ------------------------------------------------ | ------------------- |
| **🏃‍♂️ Time-to-Market** | Desenvolvimento mais rápido sem gerenciar infra  | Weeks → Days        |
| **💰 Custo**          | Pay-per-use, autoscaling, spot instances         | 30-50% economia     |
| **🔒 Governança**     | Unity Catalog centralizado, lineage automático   | Compliance          |
| **⚡ Performance**    | Photon, Delta optimizations, intelligent caching | 2-5x faster         |
| **🔧 Produtividade**  | Notebooks colaborativos, Git integration         | Developer happiness |

### 🎯 Casos de Uso Ideais

```text
✅ Databricks é ideal para:
├── 📊 Analytics e BI em grande escala
├── 🤖 Machine Learning end-to-end
├── 🌊 Streaming real-time + batch
├── 🏗️ Data engineering complexo
├── 🔄 ETL/ELT com governança
└── 🏢 Multi-cloud data platforms

⚠️ Considere alternativas para:
├── 💾 OLTP transactional systems
├── 📱 Aplicações de baixa latência (<100ms)
├── 🏠 On-premises only requirements
└── 💸 Very small datasets (<1GB)
```

---

**🎉 Parabéns!** Você agora tem um guia completo para implementar pipelines ETL robustas no Databricks usando a arquitetura Lakehouse.

> 💡 **Próximos Passos**:
>
> 1. Clone este repositório
> 2. Configure seu ambiente seguindo o passo-a-passo
> 3. Adapte os exemplos para seus dados específicos
> 4. Implemente monitoring e alertas
> 5. Scale conforme necessário

**Happy Data Engineering!** 🚀📊

---

_Última atualização: Janeiro 2024 | Versão: 2.0_
