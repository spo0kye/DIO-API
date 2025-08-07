# Esse é o meu repositório do LAB de APIs em python com FastAPI da DIO

O arquivo docker-compose contém a configuração de um banco de dados PostgreSQL,
na qual será conectado pelo alembic

## Uso
### Instale os requerimentos com
```
pip install requeriments.txt
```

### Crie e ative o container do docker-compose
```
docker-compose up -d
```
Caso não tenha o docker instalado você pode baixar pelo site oficial: [docker.com](https://www.docker.com/)

### Crie as migrações do alembic com o comando
Linux:
```
make create_migrations
```

Windows:
```
alembic revision --autogenerate
```

### Aplique as migrações
Linux:
```
make run-migrations
```

Windows:
```
alembic upgrade head
```

### Inicie o servidor
```
python -m uvicorn workout_api.main:app --reload
```

## Extras
Ao iniciar o servidor você consegue acessar os endpoints e seus usos com descrições acessando localhost:5432/docs# no navegador

Os arquivos de configuração do alembic (alembic.ini) estão configurados para o padrão de conexão configurados no docker-compose (localhost:5432) com o nome do banco de dados, do usuário e da senha como "workout", se for alterar a configuração padrão, esteja ciente dessas modificações