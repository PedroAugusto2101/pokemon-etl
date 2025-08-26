# ETL no Databricks com Data Lakehouse — Guia Prático

> Este README organiza e complementa suas anotações para servir como um passo-a-passo didático de como construir uma pipeline ETL no Databricks usando a arquitetura Lakehouse (Delta Lake + governança).

---

## Sumário

- [Visão Geral](https://www.notion.so/hj-25a655c2069b801cb201e47937d7ea2c?pvs=21)
- [Arquitetura de Alto Nível](https://www.notion.so/hj-25a655c2069b801cb201e47937d7ea2c?pvs=21)
- [Conceitos Fundamentais](https://www.notion.so/hj-25a655c2069b801cb201e47937d7ea2c?pvs=21)
    - [Databricks vs Cloud Provider](https://www.notion.so/hj-25a655c2069b801cb201e47937d7ea2c?pvs=21)
    - [Compute (Clusters)](https://www.notion.so/hj-25a655c2069b801cb201e47937d7ea2c?pvs=21)
    - [Storage (Lake / Lakehouse)](https://www.notion.so/hj-25a655c2069b801cb201e47937d7ea2c?pvs=21)
    - [Delta Lake](https://www.notion.so/hj-25a655c2069b801cb201e47937d7ea2c?pvs=21)
    - [Unity Catalog (Governança)](https://www.notion.so/hj-25a655c2069b801cb201e47937d7ea2c?pvs=21)
    - [Volumes, Mounts e Buckets](https://www.notion.so/hj-25a655c2069b801cb201e47937d7ea2c?pvs=21)
- [Workspace, Repos e GitOps](https://www.notion.so/hj-25a655c2069b801cb201e47937d7ea2c?pvs=21)
- [Boas Práticas de Ingestão & Modelagem](https://www.notion.so/hj-25a655c2069b801cb201e47937d7ea2c?pvs=21)
- [Pipeline ETL Passo a Passo](https://www.notion.so/hj-25a655c2069b801cb201e47937d7ea2c?pvs=21)
    - [1) Preparar Ambiente](https://www.notion.so/hj-25a655c2069b801cb201e47937d7ea2c?pvs=21)
    - [2) Criar Catálogos e Schemas (Medallion)](https://www.notion.so/hj-25a655c2069b801cb201e47937d7ea2c?pvs=21)
    - [3) Criar Volumes para *raw*](https://www.notion.so/hj-25a655c2069b801cb201e47937d7ea2c?pvs=21)
    - [4) Ingestão *raw* (arquivos brutos)](https://www.notion.so/hj-25a655c2069b801cb201e47937d7ea2c?pvs=21)
    - [5) Tabelas Bronze](https://www.notion.so/hj-25a655c2069b801cb201e47937d7ea2c?pvs=21)
    - [6) Tabelas Silver](https://www.notion.so/hj-25a655c2069b801cb201e47937d7ea2c?pvs=21)
    - [7) Tabelas Gold](https://www.notion.so/hj-25a655c2069b801cb201e47937d7ea2c?pvs=21)
    - [8) Orquestração com Workflows (Jobs)](https://www.notion.so/hj-25a655c2069b801cb201e47937d7ea2c?pvs=21)
    - [9) Parametrização de Notebooks / Scripts](https://www.notion.so/hj-25a655c2069b801cb201e47937d7ea2c?pvs=21)
    - [10) Ingestão Incremental (Streaming)](https://www.notion.so/hj-25a655c2069b801cb201e47937d7ea2c?pvs=21)
    - [11) Exposição para BI (JDBC/ODBC)](https://www.notion.so/hj-25a655c2069b801cb201e47937d7ea2c?pvs=21)
- [Performance & Custo](https://www.notion.so/hj-25a655c2069b801cb201e47937d7ea2c?pvs=21)
- [Segurança & Governança](https://www.notion.so/hj-25a655c2069b801cb201e47937d7ea2c?pvs=21)
- [Monitoramento, Lineage e Auditoria](https://www.notion.so/hj-25a655c2069b801cb201e47937d7ea2c?pvs=21)
- [Estrutura de Pastas do Projeto](https://www.notion.so/hj-25a655c2069b801cb201e47937d7ea2c?pvs=21)
- [Snippets Úteis](https://www.notion.so/hj-25a655c2069b801cb201e47937d7ea2c?pvs=21)
- [Glossário Rápido](https://www.notion.so/hj-25a655c2069b801cb201e47937d7ea2c?pvs=21)

---

## Visão Geral

O **Databricks** é uma **plataforma de dados** que integra engenharia, ciência de dados, analytics e negócio num único lugar. Ele **não é** um cloud provider (como AWS/Azure/GCP). Em vez disso, roda **sobre** essas nuvens, utilizando as VMs e o storage delas. Você usa o navegador para desenvolver (sem instalar nada localmente) e a plataforma cuida de muito do que normalmente você teria de gerenciar: clusters, jobs, catálogos, lineage, etc.

A **arquitetura Lakehouse** combina a flexibilidade do data lake com recursos de banco de dados (ACID, time travel, governança) por meio do **Delta Lake** e do **Unity Catalog**.

---

## Arquitetura de Alto Nível

lua
Copiar
Editar
+------------------------- Plataforma Databricks -------------------------+
|                                                                          |
|  Workspace (Notebooks/.py)  |  Workflows (Jobs)  |  Unity Catalog        |
|                              |                    |  (Catálogo/Permissões)|
+------------------------+-----+--------------------+-----------------------+
|                                     ▲
v                                     │
[Compute / Clusters Spark]                       │
Driver + Workers (Autoscaling, Photon)           │
|                                     │
v                                     │
I/O (leitura e escrita)                         │
|                                     │
+-------------------------+---------------------------+         │
|                         |                           |         │
[AWS S3/GCP GCS/Azure Blob] (Volumes UC) (External Tables)| <= Storage na nuvem
+-------------------------+---------------------------+ │
| │
[Delta Lake] <---- Time Travel / Lineage / Governança

markdown
Copiar
Editar

---

## Conceitos Fundamentais

### Databricks vs Cloud Provider

- Databricks **orquestra** recursos **da** nuvem (VMs/Discos/Storage).
- Você **paga** pela infra do provedor (ex.: AWS EC2, S3) + custos da plataforma Databricks.
- Tudo é efêmero no **compute**: ao desligar o cluster, o que não está em storage **se perde** (por design).

### Compute (Clusters)

- Um **cluster** é um conjunto de VMs: 1 **driver** (orquestra) + **workers** (processam).
- **Databricks Runtime**: distribuição do Spark com otimizações e libs pré-instaladas (existem versões **LTS**).
- **Photon**: motor vetorizado que acelera SQL/DataFrames. Custa um pouco mais por hora, mas reduz tempo de execução.
- **Autoscaling (de nós)**: aumenta/diminui a **quantidade de workers** automaticamente.
    
    > Nota: há também “autoscaling de storage local”, que é específico para discos locais; não confundir.
    > 
- **On-Demand vs Spot/Preemptible**: *spot* é mais barato, porém pode sofrer preempção. Use *fallback* para on-demand.
- **Bibliotecas**:
    - **Cluster-scoped**: instaladas para todos os notebooks do cluster.
    - **Notebook-scoped**: `pip install` dentro do notebook (vale só para a sessão daquele notebook).

### Storage (Lake / Lakehouse)

- O dado **persistente** mora no storage da nuvem (S3, ADLS/Blob, GCS).
- Compute **processa**; storage **guarda**. O cluster lê/escreve (I/O) nesses storages.
- Lakehouse = Data Lake **+** Delta Lake **+** Governança (Unity Catalog).

### Delta Lake

- Formato transacional sobre arquivos **Parquet** com ***transaction log***.
- Recursos: **ACID**, **schema enforcement/evolution**, **UPDATE/DELETE/MERGE**, **time travel**, **otimizações**.
- Permite **upserts** eficientes e histórico nativo das alterações.

### Unity Catalog (Governança)

- Metastore unificado com **catálogos → schemas (databases) → tabelas / views / modelos**.
- **Managed vs External**:
    - **Managed**: Databricks gerencia a localização física; ao dropar a tabela, **apaga os arquivos**.
    - **External**: você aponta o caminho físico; o gerenciamento é seu.
- **Time Travel** e **History** já vêm prontos em tabelas Delta. `VACUUM` remove arquivos antigos (após retenção).
- **Lineage** (inclusive a nível de coluna): mostra **upstream/downstream**, notebooks, queries, workflows e dashboards.
- **Data discovery**: descrição, amostras, popularidade, tamanho, tags/Comentários (para dicionário de dados).
- **Permissões centralizadas** (GRANT) por catálogo/schema/tabela/coluna/linha (via *dynamic views*).

### Volumes, Mounts e Buckets

- **Bucket/Container**: “pasta raiz” no storage da nuvem.
- **Mounts (legado)**: montagem de um bucket em `/mnt/...`. Em ambientes UC, prefira **External Locations** e **Volumes**.
- **Volumes (Unity Catalog)**: espaços de arquivos gerenciados por UC, com path `/Volumes/<catalog>/<schema>/<volume>`.
Perfeitos para **dados brutos** (*landing*) antes de irem para tabelas Delta.

---

## Workspace, Repos e GitOps

- **Repos**: clone direto do GitHub/GitLab/Azure DevOps no Workspace.
Siga *feature branches* (`feat/minha_feature`), **Pull Request** e **code review** antes de **merge** na `main` (produção).
- **Notebooks vs .py**:
    - Notebooks são ótimos para exploração, mistura **SQL + Python** (ex.: *magic* `%%sql`) e visualizações rápidas.
    - Scripts `.py` favorecem **reprodutibilidade**, testes e CI/CD.
- **Execução**: notebooks/scripts executam no **cluster** configurado.
- **Dashboards**: crie visualizações no notebook e publique; compartilhe apenas a **URL** com o negócio.

> Dica SQL: algumas versões do Spark/Databricks suportam o atalho GROUP BY ALL, que agrupa por todas as colunas não agregadas do SELECT. Se não estiver disponível no seu runtime, liste as colunas explicitamente.
> 

---

## Boas Práticas de Ingestão & Modelagem

- **Desacople** extração de **persistência inicial**: salve o que veio (JSON/CSV/Parquet) **como chegou** (*raw/landing*), **antes** de transformar.
Isso evita que mudanças de schema na fonte **quebrem** o pipeline e facilita reprocessamentos.
- Use a **arquitetura Medallion**:
    - **raw/landing**: arquivos brutos em **Volumes**.
    - **bronze**: ingestão mínima, deduplicação leve, padronização.
    - **silver**: limpeza/normalização/joins, qualidade de dados.
    - **gold**: modelos analíticos para consumo (BI/serviços).
- **Particionamento** por colunas de alto *cardinality/time* (ex.: `ingestion_date`), quando fizer sentido.
- **Idempotência**: gravar de forma que reprocessar não duplique (ex.: `MERGE` por chave natural).
- **Convenções de nome**: `catalog.schema.tb_<domínio>_<entidade>`.
- **Carimbo de data/hora** nos arquivos *raw* (ex.: `extract_date=YYYY-MM-DD`).
- **Secrets** (tokens, chaves) via **Databricks Secrets**.

---

## Pipeline ETL Passo a Passo

### 1) Preparar Ambiente

1. Criar **metastore** do Unity Catalog e associar à workspace.
2. Conectar o **storage** (S3/ADLS/GCS) via **Storage Credentials** e **External Locations**.
3. Criar **cluster** (Runtime LTS quando possível). Ativar **Photon** para cargas SQL/DF intensivas.
4. Configurar **Auto Termination** (ex.: 60 min) para economizar.

### 2) Criar Catálogos e Schemas (Medallion)

- Catálogos sugeridos: `raw`, `bronze`, `silver`, `gold` (ou um catálogo por domínio e schemas por camadas).
- Dentro de cada catálogo, crie **schemas** por contexto de negócio/projeto (ex.: `raw.meu_projeto`).

### 3) Criar Volumes para *raw*

- Ex.: `CREATE VOLUME raw.meu_projeto.v_raw LOCATION 's3://.../landing/meu_projeto/';`
- Vai armazenar os **arquivos brutos** como chegaram.

### 4) Ingestão *raw* (arquivos brutos)

**Exemplo (notebook Python)**: salvar resposta de uma API em um Volume com *timestamp*:

```python
import json, datetime as dt, requests
run_ts = dt.datetime.utcnow().strftime("%Y-%m-%d_%H%M%S")
base_dir = f"/Volumes/raw/meu_projeto/v_raw/pokemon/extract_ts={run_ts}"

dbutils.fs.mkdirs(base_dir)
resp = requests.get("<https://pokeapi.co/api/v2/pokemon?limit=1000>", timeout=30)
dbutils.fs.put(f"{base_dir}/pokemon.json", json.dumps(resp.json()), overwrite=True)
Observação: instale requests no cluster ou no notebook conforme a política de libs.

5) Tabelas Bronze
Ingerir raw → Delta (bronze) com deduplicação mínima e carimbos técnicos:

python
Copiar
Editar
from pyspark.sql.functions import input_file_name, current_timestamp

raw_path = "/Volumes/raw/meu_projeto/v_raw/pokemon/*"
df_raw = spark.read.json(raw_path)

df_bronze = (
    df_raw
    .dropDuplicates()
    .withColumn("_ingestion_ts", current_timestamp())
    .withColumn("_source_file", input_file_name())
)

(df_bronze
 .coalesce(1)                       # opcional: poucos arquivos; avalie custo de shuffle
 .write
 .format("delta")
 .mode("overwrite")                  # ou 'append' conforme estratégia
 .saveAsTable("bronze.meu_projeto.tb_pokemon_list"))
6) Tabelas Silver
Limpezas, normalizações e upserts (ex.: MERGE por chave):

sql
Copiar
Editar
-- Exemplo (SQL) de tabela silver
CREATE TABLE IF NOT EXISTS silver.meu_projeto.tb_pokemon_clean
USING delta
AS
SELECT DISTINCT
  id,
  name,
  height,
  weight,
  _ingestion_ts
FROM bronze.meu_projeto.tb_pokemon_list;
Ou upsert contínuo:

sql
Copiar
Editar
MERGE INTO silver.meu_projeto.tb_pokemon_clean AS t
USING (
  SELECT id, name, height, weight, _ingestion_ts
  FROM bronze.meu_projeto.tb_pokemon_list
) AS s
ON t.id = s.id
WHEN MATCHED THEN UPDATE SET *
WHEN NOT MATCHED THEN INSERT *;
7) Tabelas Gold
Modelos analíticos para consumo (BI/serviços), já agregados e prontos para dashboard:

sql
Copiar
Editar
CREATE OR REPLACE TABLE gold.meu_projeto.vw_pokemon_metricas
AS
SELECT
  /* colunas de negócio/indicadores */
  height,
  weight,
  COUNT(*) AS qtd
FROM silver.meu_projeto.tb_pokemon_clean
GROUP BY height, weight;
8) Orquestração com Workflows (Jobs)
Jobs (Workflows) permitem criar um DAG: tarefas dependentes (por ex., raw → bronze → silver → gold).

Fonte do código: Git (provider + branch main — código revisado).

Para cada task:

Tipo: Notebook/Python script

Fonte: Git

Caminho: src/ingestion/etl_bronze.py etc.

Cluster: selecione um existente ou job cluster (sobe/sobe-desce por job)

Parâmetros: passe datas, caminhos, flags.

9) Parametrização de Notebooks / Scripts
Notebooks: dbutils.widgets.text("process_date","") e pegue com dbutils.widgets.get("process_date").

Scripts .py: use argparse e configure parâmetros no Job.

No Workflows, defina parâmetros por tarefa e reutilize em tarefas downstream.

10) Ingestão Incremental (Streaming)
Para ler apenas novos arquivos (Auto Loader) e escrever em Delta:

python
Copiar
Editar
(spark.readStream
 .format("cloudFiles")
 .option("cloudFiles.format", "json")
 .load("/Volumes/raw/meu_projeto/v_raw/pokemon/*")
 .writeStream
 .trigger(availableNow=True)  # executa como batch incremental
 .option("checkpointLocation", "/Volumes/raw/meu_projeto/v_raw/_checkpoints/pokemon_bronze")
 .toTable("bronze.meu_projeto.tb_pokemon_list"))
11) Exposição para BI (JDBC/ODBC)
Conexão via JDBC é possível direto ao cluster, mas recomenda-se usar um SQL Warehouse para Power BI/Tableau (pool dedicado, auto-scaling próprio e isolamento).

No Power BI, configure o driver Databricks e a URL JDBC fornecida pelo Warehouse/Cluster.

Performance & Custo
Photon para workloads SQL/DF pesados.

Autoscaling de nós para lidar com picos; ative Auto Termination.

Spot para batch tolerante a preempção; use fallback.

Delta:

OPTIMIZE <table> ZORDER BY (<col>) para melhorar pruning (quando fizer sentido).

Auto Optimize/Auto Compaction (se habilitado) ajudam a evitar muitos arquivos pequenos.

Particionamento e clustering conforme padrões de acesso.

Evite coalesce(1) em grandes volumes (gargalo); prefira partitioning e pruning.

Segurança & Governança
Unity Catalog centraliza GRANT/REVOKE (catálogo, schema, tabela, coluna).

Row/Column-level security via views dinâmicas.

Secrets para credenciais.

Managed vs External: escolha conforme governança e ciclo de vida do dado.

VACUUM para limpeza de arquivos antigos (respeite políticas de retenção/backup).

Monitoramento, Lineage e Auditoria
Lineage mostra origem/destino até nível de coluna (tabelas, notebooks, queries, jobs, dashboards).

History/Time Travel para auditoria de versões.

Workflows: métricas de execução, logs, alertas e retry.

Estrutura de Pastas do Projeto
bash
Copiar
Editar
.
├── README.md
├── src
│   ├── ingestion
│   │   ├── get_raw_from_api.py
│   │   └── bronze_from_raw.py
│   ├── transform
│   │   ├── silver_clean.py
│   │   └── gold_agg.py
│   └── utils
│       └── io.py
├── notebooks
│   ├── exploration.sql
│   ├── exploration.py
│   └── dashboards/...
├── workflows
│   └── job_definition.json   # export/import do job (opcional)
└── tests
    └── unit/...
Snippets Úteis
Escrever DataFrame em Delta (tabela gerenciada):

python
Copiar
Editar
(df.distinct()
   .coalesce(1)  # use com parcimônia
   .write
   .format("delta")
   .mode("overwrite")
   .saveAsTable("bronze.pokemon.tb_pokemon_list"))
Time Travel (consultar versão anterior):

sql
Copiar
Editar
SELECT * FROM silver.meu_projeto.tb_pokemon_clean VERSION AS OF 3;
-- ou por timestamp
SELECT * FROM silver.meu_projeto.tb_pokemon_clean TIMESTAMP AS OF '2025-08-20T10:00:00Z';
Limpeza de arquivos antigos (VACUUM):

sql
Copiar
Editar
VACUUM silver.meu_projeto.tb_pokemon_clean RETAIN 168 HOURS;
Lineage: abra a tabela no Catalog → guia Lineage para visualizar dependências.

Conectar Power BI via JDBC:

Crie um SQL Warehouse.

Copie a JDBC URL.

No Power BI, instale o Conector Databricks, cole a URL, configure token/SSO.

Multiprocessamento e barra de progresso em Python:

python
Copiar
Editar
from multiprocessing import Pool
from tqdm import tqdm

with Pool(processes=4) as p:
    list(tqdm(p.imap_unordered(get_and_save, urls), total=len(urls)))
Notebooks + SQL → DataFrame Python:

sql
Copiar
Editar
-- cell SQL
SELECT * FROM bronze.meu_projeto.tb_pokemon_list;
python
Copiar
Editar
# cell Python imediatamente após o SQL acima
df = _sqldf  # último resultado SQL como DataFrame Spark
Widgets (parâmetros) em notebook:

python
Copiar
Editar
dbutils.widgets.text("process_date", "")
process_date = dbutils.widgets.get("process_date")
Glossário Rápido
Driver / Workers: nós do cluster (coordenação vs execução).

Databricks Runtime (LTS): versão suportada por período estendido.

Photon: motor acelerado para SQL/DF.

Managed vs External Table: gerenciamento físico feito pelo Databricks vs pelo usuário.

Volume (UC): área de arquivos gerenciada pelo Unity Catalog.

Time Travel / History: consulta a versões anteriores de tabelas Delta.

VACUUM: coleta arquivos “órfãos” após o período de retenção.

Autoscaling: ajuste automático de número de workers.

On-Demand / Spot: tipos de instância (preço x disponibilidade).

I/O: operações de leitura/escrita (input/output).

Resumo: Com Databricks você usa compute efêmero da nuvem para processar dados que ficam persistidos no storage (S3/ADLS/GCS). O Delta Lake dá ACID/Time Travel, o Unity Catalog organiza/governa, e os Workflows orquestram. Estruture por raw → bronze → silver → gold, parametrize seus jobs e exponha via SQL Warehouse para BI.
```
