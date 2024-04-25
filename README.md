# PUCRS-LabRedes-1

1 - Registrar: /REG nickname
2 - Enviar mensagem: /MSG recipient "message"
3 - Enviar arquivo: /FILE recipient file_name "message"
4 - Sair: /OFF

Inicialmente o código tinha o objetivo de ter apenas um código de aplicação e a implementação de UDP e TCP como interfaces, porém, com o desenvolvimento do trabalho isso se mostrou mais difícil do que o planeja, por isso, os códigos foram separados, sendo assin, todo código relativo ao TCP está localizado na pasta tcp e o código UDP está dentro da pasta udp + app_client.py e app_server.py.

Código UDP:
- app_client.py
- udp_client.py
- app_server.py
- udp_server.py

Código TCP:
- tcp_client.py
- tcp_server.py