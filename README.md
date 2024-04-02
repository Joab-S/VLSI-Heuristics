## Como rodar o projeto

# Faça o download do CPLEX Studio 22.11 pelo link abaixo (cplex_studio2211.linux_x86_64.bin):
https://drive.google.com/uc?export=download&id=1fXyw6id8sfnEuveO5PwYbXUAYSNnl5oX
# Após o download pelo link direto, coloque o arquivo baixado no diretório 'docker/cplex/'

# Em um terminal faça: Iniciar o contêiner Docker
# (use o --build caso seja a primeira vez subindo o projeto) 
# Caso queria parar o container, pode usar Ctrl + c
docker-compose up --build

# Em outro terminal faça: abrir o terminal do container 
docker-compose exec cplex-container /bin/bash

# Nesse terminal do container faça: instalar as dependências do projeto
pip install -r docker/requirements.txt

# Agora fique a vontade para rodar o projeto
python main.py

# Use o comando abaixo para *parar* e *remover* os containers criados pelo 'up'
docker-compose down

# Use o comando abaixo para *parar* o container para ser reiniciado mais tarde:
docker-compose stop

# Para *iniciar* os containers novamente sem reconstruir:
docker-compose start
