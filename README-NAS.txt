SISTEMA ROMANEIO AMAZON - INSTALAÇÃO NO NAS

Este pacote usa Docker. O banco de dados fica na pasta data e continua salvo
mesmo quando o NAS for reiniciado ou o sistema for atualizado.

1. Extraia esta pasta em uma pasta do NAS, por exemplo:
   /docker/sistema-romaneio-amazon

2. No NAS, abra o Container Manager / Docker e execute nesta pasta:
   docker compose up -d --build

3. Acesse no navegador:
   http://IP_DO_NAS:8765

Todos na mesma rede poderão consultar pelo mesmo endereço.

ATUALIZAÇÃO

Substitua index.html e server.py por versões novas e execute novamente:
   docker compose up -d --build

BACKUP

Faça cópia da pasta data. O banco de dados é:
   data/romaneio.db

IMPORTANTE

Não compartilhe a porta 8765 para a internet. Use somente dentro da rede da
empresa, a menos que seja configurada autenticação e HTTPS.
