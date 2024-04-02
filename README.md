# Como rodar o projeto

## Faça o download do CPLEX Studio 22.11 pelo link abaixo (cplex_studio2211.linux_x86_64.bin):
https://drive.google.com/uc?export=download&id=1fXyw6id8sfnEuveO5PwYbXUAYSNnl5oX
## Após o download pelo link direto, coloque o arquivo baixado no diretório 'docker/cplex/'

## Iniciar o contêiner Docker
<p>
Em um terminal faça:
```docker-compose up --build```
(use o --build caso seja a primeira vez subindo o projeto) 
Caso queria parar o container, pode usar Ctrl + c
</p>


## Abrir o terminal do container 
<p>
Em outro terminal faça: abrir o terminal do container 
```docker-compose exec cplex-container /bin/bash```
</p>

## Instalar as dependências do projeto
<p>
Nesse terminal do container faça:
```pip install -r docker/requirements.txt```
</p>

## Rodar o projeto
<p>
```python main.py```
</p>

## Use o comando abaixo para *parar* e *remover* os containers criados pelo 'up'
docker-compose down

## Use o comando abaixo para *parar* o container para ser reiniciado mais tarde:
docker-compose stop

## Para *iniciar* os containers novamente sem reconstruir:
docker-compose start
