FROM python:3.10

# Define o diretório de instalação do CPLEX (também especificado em install.properties)
ARG COSDIR=/opt/CPLEX

# Versão do Python (usada para instalação da API Python do CPLEX)
ARG CPX_PYVERSION=3.10

# Copia o instalador do CPLEX e o arquivo de propriedades do host para o contêiner
COPY docker/cplex/cplex.install.properties /tmp/install.properties
COPY docker/cplex/cplex_studio2211.linux_x86_64.bin /tmp/installer
RUN chmod u+x /tmp/installer

# Instala o Java Runtime Environment (JRE), necessário para o instalador
RUN apt-get update && apt-get install -y default-jre

# Executa o instalador do CPLEX
RUN /tmp/installer -f /tmp/install.properties

# Listar os diretórios após a instalação do CPLEX
RUN ls -l ${COSDIR}/cplex

# Remove o instalador, arquivos temporários e o JRE instalado
RUN rm -f /tmp/installer /tmp/install.properties
RUN apt-get remove -y --purge default-jre && apt-get -y autoremove

# Remove diretórios desnecessários, mantendo apenas a API Python do CPLEX
RUN rm -rf \
   ${COSDIR}/concert \
   ${COSDIR}/cpoptimizer \
   ${COSDIR}/doc \
   ${COSDIR}/opl \
   ${COSDIR}/python \
   ${COSDIR}/Uninstall \
   ${COSDIR}/cplex/bin \
   ${COSDIR}/cplex/examples \ 
   ${COSDIR}/cplex/include \
   ${COSDIR}/cplex/lib \
   ${COSDIR}/cplex/matlab \
   ${COSDIR}/cplex/readmeUNIX.html
RUN ls -d ${COSDIR}/cplex/python/* | grep -v ${CPX_PYVERSION} | xargs rm -rf

# Copia o projeto para o diretório de trabalho no container
COPY . /home/cplex
# Configura o ambiente Python
# Instala a API Python do CPLEX
RUN cd ${COSDIR}/cplex/python/${CPX_PYVERSION}/x86-64_linux && python setup.py install

# Define a versão do CPLEX Python como uma variável de ambiente
ENV CPX_PYVERSION=${CPX_PYVERSION}

# Configura o usuário padrão como 'cplex'
RUN adduser --disabled-password --gecos "" cplex
USER root

# Instala o tkinter
RUN apt-get update && \
    apt-get install -y python3-tk && \
    apt-get clean

# Muda de volta para o usuário cplex
USER cplex
WORKDIR /home/cplex

# guarda o endereço do executável do cplex
#ENV CPLEX_EXECUTABLE=${COSDIR}/cplex/python/${CPX_PYVERSION}/x86-64_linux/cplex