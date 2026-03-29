# Mapa iterativo de transportes portugueses

Contém sobretudo transportes lisboetas, mas também alguns portuenses.

## Base de dados

O projeto usa uma base de dados em postgres, mas também alguns ficheiros locais.

### Prepara base de dados

TODO: Explicar como criar a base de dados

Para fazer login:

```bash
pgcli -d public_transport
```

### Migrações de dados

Correr scripts que estão na pasta `sql`.

## Atualizar

### Métodos a correr

#### Preparar dados

Para preparar os dados:
```bash
./prepare.py -h
```

#### Fazer um mapa

Para fazer o mapa:
```bash
./map.py -h
```
e para o ver:
```bash
firefox *.html
```

#### Correr servidor para as posições

Correr o servidor de posições em tempo real:

```bash
flask --app vehicles_real_time run --port 5000
```
E para correr a simulação:
```bash
flask --app vehicles_simulate run --port 5001
```

### Qualidade de dados

#### Dados de origem

| Operadora | Cidade | Tipo | GTFS | Atualização | API |
| -- | -- | -- | -- | -- | -- |
| Carris | Lisboa | 🚌 Autocarros | ✅ Sim | 2024/04/30 | ❔ Talvez |
| Carris Metropolitana | Lisboa | 🚌 Autocarros | ✅ Sim | 2024/05/05 | ✅ Sim |
| MobiCascais | Lisboa | 🚌 Autocarros | ✅ Sim | 2024/03/26 | ❌ Não |
| TCBarreiro | Lisboa | 🚌 Autocarros | ✅ Sim | 2021/11/15❗ | ❔ Possível |
| Soflusa - Transtejo | Lisboa | 🚢 Barcos | ✅ Sim | 2024/01/04 | ❌ Não |
| Metro de Lisboa | Lisboa | 🚇 Metro | ✅ Sim | 2024/05/05 | ❌ Não |
| Metro Sul do Tejo | Lisboa | 🚇 Metro | ❌ Não | | ❌ Não |
| CP Lisboa | Lisboa | 🚂 Comboio |  ✅ Sim | 2022/12/09❗ | ❌ Não |
| Fertagus | Lisboa | 🚂 Comboio | ✅ Sim | 2024/05/05 | ❌ Não | 
| STCP | Porto | 🚌 Autocarros | ✅ Sim | 2023/10/23 | ❔ Talvez |
| UNIR | Porto | 🚌 Autocarros | ❌ Não | | ❌ Não |
| Metro do Porto | Porto | 🚇 Metro | ✅ Sim | 2024/05/06 | ❌ Não |
| CP Porto | Porto | 🚂 Comboio | ❌ Não | | ❌ Não

#### Dados calculados

##### Dados principais

| Operadora | Rotas | Paragens | Veículos | Veiculos a Tempo Real | 
| -- | -- | -- | -- | -- |
| Carris | ✅ | ✅ | ❌ | ❌ |
| Carris Metropolitana | ✅ | ✅ | ❗ | ✅ |
| MobiCascais | ✅ | ✅ | ❌ | ❌ |
| TCBarreiro | ✅ | ✅ | ❌ | ❌ |
| Soflusa - Transtejo | ✅ | ✅ | ❌ | ❌ |
| Metro de Lisboa | ✅ | ✅ | ❌ | ❌ |
| CP Lisboa | ✅ | ✅ | ❌ | ❌ |
| Fertagus | ✅ | ✅ | ❌ | ❌ |
| STCP | ✅ | ✅ | ❌ | ❌ |
| Metro do Porto | ✅ | ✅ | ❌ | ❌ |

##### Dados para desenhar paragens

| Operadora | Mapa | Nomes | Rotas | 
| -- | -- | -- | -- |
| Carris | ✅ | ✅ | |
| Carris Metropolitana | ✅ | ✅ | |
| MobiCascais | ✅ | ✅ | |
| TCBarreiro | ✅ | ✅ | |
| Soflusa - Transtejo | ✅ | ✅ | |
| Metro de Lisboa | ✅ | ✅ | |
| CP Lisboa | ✅ | ✅ | |
| Fertagus | ✅ | ✅ | |
| STCP | ✅ | ✅ | |
| Metro do Porto | ✅ | ✅ | |

##### Dados para desenhar rotas

| Operadora | Mapa | Códigos | Nomes | Cores | 
| -- | -- | -- | -- | -- |
| Carris | ✅ | ✅ | ✅ | ✅ |
| Carris Metropolitana | ✅ | ✅ | ✅ | ✅ |
| MobiCascais | ✅ | ✅ | ✅ | ✅ |
| TCBarreiro | ✅ | ✅ | ✅ | ✅ |
| Soflusa - Transtejo | ❗✅ | ✅ | ✅ | ✅ |
| Metro de Lisboa | ❗✅ | ✅ | ✅ | ✅ |
| CP Lisboa | ❗✅ | ✅ | ✅ | ✅ |
| Fertagus | ❗✅ | ✅ | ✅ | ✅ |
| STCP | ✅ | ✅ | ✅ | ✅ |
| Metro do Porto | ❗✅ | ✅ | ✅ | ✅ |

##### Dados complementares para veículos

| Operadora | Cores | Códigos | Nomes | Letreiros | 
| -- | -- | -- | -- | -- |
| Carris | ✅ | ✅ | ✅ | ❌ |
| Carris Metropolitana | ✅ | ✅ | ✅ | ✅ |
| MobiCascais | ✅ | ✅ | ✅ | ❌ |
| TCBarreiro | ✅ | ✅ | ✅ | ❌ |
| Soflusa - Transtejo | ❌ | ❌ | ❗ | ❌ |
| Metro de Lisboa | ❌ | ❌ | ❗ | ❌ |
| CP Lisboa | ❌ | ❌ | ❌ | ❌ |
| Fertagus | ❌ | ❔ | ✅ | ❌ |
| STCP | ✅ | ✅ | ✅ | ✅ |
| Metro do Porto | ✅ | ✅ | ❌ | ✅ |

##### Dados usados para simular posição dos veículos

Ainda não comecei

### Dados da Carris Metropolitana

Existe um github com os dados de **gtfs** da Carris Metropolitana.

E existe também uma api pública da Carris Metropolitana.

Para atualizar os dados **gtfs**, na pasta `CarrisMetropolitana`:
```shell
wget https://api.carrismetropolitana.pt/gtfs -O CarrisMetropolitana.zip
```

E por fim, para extrair os ficheiros, na pasta `CarrisMetropolitana`:
```shell
unzip -o CarrisMetropolitana.zip -d data
```

### Dados da Carris

Existe uma api onde se encontra o ficheiro **gtfs**. Na pasta `Carris`:
```shell
curl https://gateway.carris.pt/gateway/gtfs/api/v2.8/GTFS --output Carris.zip
```

e depois para extrair os ficheiros:
```shell
unzip -o Carris.zip -d data
```

Existe também uma api para ir buscar dados em tempo real, mas os dados estão num formato estranho.

As cores das carreiras foram retiradas diretamente da wikipedia: `https://pt.wikipedia.org/wiki/Lista_de_carreiras_da_Carris`. Sacar a tabela como csv para criar um mapa, e colocá-lo em `Carris/wikipedia_list.csv`.

Correr:
```shell
./create_carris_colors.py
```

### Dados da MobiCascais

Ir buscar os dados em
```
https://dadosabertos.cascais.pt/dataset/gtfs-mobicascais
```

Colocá-los na pasta `MobiCascais` e depois extraí-los:
```shell
unzip -o cascais.zip -d data
```

### Dados dos Transportes Coletivos do Barreiro

Não encontrei nada de oficial, mas no site `www.transit.land` tem uma cópia. Ir buscar os dados em
```
https://www.transit.land/feeds/f-transportes~colectivos~do~barreiro~pt
```

Colocá-los na pasta `Barreiro` e depois extraí-los:
```shell
unzip -o barreiro.zip -d data
```

Estes dados são da antiga Transpolis e parecem estar desatualizados...

### Dados da CP Lisboa

Não encontrei nada de oficial, mas no site `https://transitfeeds.com` tem uma cópia. Ir buscar os dados em
```
https://transitfeeds.com/p/comboios-de-portugal/1004/latest
```

Colocá-los na pasta `CpLisboa` e depois extraí-los:
```shell
unzip -o gtfs.zip -d data
```

Estes dados são da antiga Transpolis e parecem estar desatualizados...

### Dados da Fertagus

Não encontrei nada de oficial, mas no site `www.transit.land` tem uma cópia. Ir buscar os dados em
```
https://www.transit.land/operators/o-eyce-fertagus
```

Colocá-los na pasta `Fertagus` e depois extraí-los:
```shell
unzip -o Fertagus.zip -d data
```

Estes dados são da antiga Transpolis e parecem estar desatualizados...

### Dados da Transtejo / Soflusa

Encontrei dados em `transitfeeds.com`. Ir buscar os dados em
```
https://transitfeeds.com/p/transtejo/1006
```

Colocá-los na pasta `Transtejo` e depois extraí-los:
```shell
unzip -o gtfs.zip -d data
```

Estes dados são da antiga Transpolis e parecem estar desatualizados...

### Dados do Metro de Lisboa

Não encontrei nada de oficial, mas no site `www.transit.land` tem uma cópia. Ir buscar os dados em
```
https://www.transit.land/operators/o-eyckr-metrodelisboa
```

Colocá-los na pasta `MetroLisboa` e depois extraí-los:
```shell
unzip -o Metro.zip -d data
```

Estes dados são da antiga Transpolis e parecem estar desatualizados...

### Dados do Metro Sul do Tejo

Não encontrei nenhum gtfs.

### Dados do Metro de Porto

Encontrei os dados no site de dados abertos do Porto `https://opendata.porto.digital`. Mais precisamente em
```
https://opendata.porto.digital/dataset/horarios-paragens-e-rotas-em-formato-gtfs
```

Encontrei-os também no site da própria `Metro do Porto`, mais atuais.
Mais precisamente em `Download > Outros`.

Colocá-los na pasta `MetroPorto` e depois extraí-los:
```shell
unzip -o gtfs_mdp_11_09_2023.zip -d data
```

No caso dos dados sacados do próprio site, precisamos de correr o 
```shell
./fix_metro_porto.py
```

Não estão atualizados, mas devem ser melhores do que os da Transpolis.

### Dados da STCP

Encontrei os dados no site de dados abertos do Porto `https://opendata.porto.digital`. Mais precisamente em
```
https://opendata.porto.digital/dataset/horarios-paragens-e-rotas-em-formato-gtfs-stcp
```

Colocá-los na pasta `STCP` e depois extraí-los:
```shell
unzip -o gtfs-stcp-2023-09.zip -d data
```

Não estão atualizados, mas devem ser melhores do que os da Transpolis.

Deve-se conseguir ir buscar mais informação dos autocarros em _real time_ em :
```
https://opendata.porto.digital/organization/sociedade-de-transportes-colectivos-do-porto-stcp
```

### Dados da UNIR

Não encontrei nenhum gtfs.