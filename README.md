# Comunicacao TCP Cliente-Servidor

Projeto pratico do Grupo 5 para demonstrar uma comunicacao TCP cliente-servidor usando sockets em Python.

O sistema implementa um servidor TCP e um cliente TCP capazes de trocar mensagens de texto e transferir arquivos. A demonstracao evidencia conceitos como conexao, sockets, fluxo de bytes, confiabilidade, ordem de entrega e encerramento da comunicacao.

## Requisitos atendidos

| Requisito do trabalho | Como o projeto atende |
| --- | --- |
| Codigo ou configuracao executavel | Scripts Python em `src/server.py` e `src/client.py`, sem dependencias externas. |
| Instrucoes no README | Este arquivo explica execucao, comandos, protocolo, demonstracao e analise. |
| Demonstracao pratica | O cliente interativo permite enviar varias mensagens e arquivos para o servidor em tempo real. |
| Captura ou analise de trafego | A secao de Wireshark mostra filtro, passos e pontos de analise do trafego TCP. |
| Explicacao curta dos conceitos | A secao de conceitos conecta a pratica com TCP, sockets, ACKs, fluxo de bytes e ordem. |
| Limitacoes do experimento | A secao de limitacoes descreve ambiente local, poucos clientes, ausencia de seguranca real e simplificacoes. |

## Tecnologias

- Python 3
- Biblioteca padrao `socket`
- Biblioteca padrao `threading`
- Wireshark para captura e analise de trafego

Nao e necessario instalar bibliotecas Python externas.

## Estrutura do projeto

```text
.
|-- src/
|   |-- client.py
|   |-- protocol.py
|   `-- server.py
|-- exemplos/
|   `-- exemplo.txt
|-- README.md
|-- .gitignore
`-- recebidos/          # criada automaticamente quando arquivos sao recebidos
```

### Papel de cada arquivo

- `src/server.py`: inicia o servidor, escuta conexoes TCP, atende clientes em threads e salva arquivos recebidos.
- `src/client.py`: conecta ao servidor, envia mensagens, transfere arquivos e oferece modo interativo.
- `src/protocol.py`: concentra constantes e funcoes comuns usadas por cliente e servidor, como envio de texto, leitura de linhas e transferencia de arquivos em blocos.
- `exemplos/exemplo.txt`: arquivo simples usado para demonstrar a transferencia.
- `recebidos/`: pasta criada automaticamente pelo servidor para armazenar arquivos recebidos.

## Como executar

Abra dois terminais na pasta do projeto.

Se o comando `python` nao for reconhecido no Windows, instale o Python 3 e marque a opcao de adicionar ao PATH durante a instalacao.

### 1. Iniciar o servidor

No primeiro terminal:

```bash
python src/server.py
```

Saida esperada:

```text
[SERVIDOR] Aguardando conexoes em 127.0.0.1:5000
[SERVIDOR] Pressione Ctrl+C para parar.
```

O servidor permanece em execucao aguardando clientes. Para encerrar, pressione `Ctrl+C`.

### 2. Executar o cliente em modo interativo

No segundo terminal:

```bash
python src/client.py --interactive
```

Depois de conectar, digite mensagens diretamente:

```text
> primeira mensagem
> segunda mensagem
> /file exemplos/exemplo.txt
> /quit
```

No modo interativo:

- qualquer texto comum e enviado como mensagem `MSG`;
- `/file caminho/do/arquivo` envia um arquivo;
- `/quit` encerra a conexao com o servidor.

O servidor mantem a conexao interativa aberta por ate 5 minutos sem atividade. Se esse tempo for excedido, execute o cliente novamente.

### 3. Executar o cliente em modo rapido

Tambem e possivel enviar uma unica mensagem e encerrar automaticamente:

```bash
python src/client.py --message "Teste de comunicacao TCP"
```

Para enviar mensagem e arquivo na mesma execucao:

```bash
python src/client.py --message "Vou enviar um arquivo" --file exemplos/exemplo.txt
```

O servidor salva o arquivo recebido na pasta `recebidos/`. Se ja existir um arquivo com o mesmo nome, o servidor cria uma nova copia com sufixo numerico, como `exemplo_1.txt`.

### 4. Alterar host ou porta

O servidor e o cliente aceitam os parametros `--host` e `--port`.

Servidor:

```bash
python src/server.py --host 127.0.0.1 --port 5000
```

Cliente:

```bash
python src/client.py --host 127.0.0.1 --port 5000 --interactive
```

## Protocolo da aplicacao

TCP entrega um fluxo continuo de bytes. Ele nao separa mensagens automaticamente. Por isso, esta aplicacao define um protocolo textual simples sobre TCP:

```text
MSG texto_da_mensagem
FILE nome_do_arquivo tamanho_em_bytes
QUIT
```

- `MSG`: envia uma mensagem de texto terminada por quebra de linha.
- `FILE`: envia um cabecalho com nome e tamanho, seguido pelos bytes do arquivo.
- `QUIT`: solicita o encerramento organizado da conexao.
- `ACK`: resposta enviada pelo servidor quando um comando e processado com sucesso.
- `ERRO`: resposta enviada pelo servidor quando o comando recebido e invalido.

Exemplo de troca:

```text
Cliente -> Servidor: MSG Ola, servidor TCP!
Servidor -> Cliente: ACK MSG 18 bytes recebidos
Cliente -> Servidor: FILE exemplo.txt 36
Servidor -> Cliente: ACK FILE exemplo.txt 36 bytes recebidos
Cliente -> Servidor: QUIT
Servidor -> Cliente: ACK QUIT conexao encerrada
```

O limite padrao de arquivo e de 10 MB, definido em `src/protocol.py`.

## Demonstracao pratica

Um roteiro simples para apresentar o sistema:

1. Abrir o Wireshark e iniciar captura na interface de loopback.
2. Aplicar o filtro `tcp.port == 5000`.
3. Iniciar o servidor com `python src/server.py`.
4. Iniciar o cliente com `python src/client.py --interactive`.
5. Enviar duas mensagens comuns.
6. Enviar o arquivo com `/file exemplos/exemplo.txt`.
7. Encerrar com `/quit`.
8. Mostrar no servidor os logs de mensagem recebida, arquivo salvo e encerramento da conexao.
9. Mostrar no cliente as respostas `ACK`.
10. Mostrar no Wireshark o handshake, os segmentos com dados e o encerramento TCP.

## Captura e analise de trafego

### Filtro no Wireshark

```text
tcp.port == 5000
```

No Windows, a interface de captura costuma aparecer como `Adapter for loopback traffic capture` ou `Npcap Loopback Adapter`.

### Pontos observaveis na captura

- **Abertura da conexao:** pacotes `SYN`, `SYN, ACK` e `ACK`, formando o handshake de tres vias.
- **Troca de dados:** segmentos TCP com payload contendo comandos como `MSG`, `FILE` e `QUIT`.
- **Confiabilidade:** numeros de sequencia (`Seq`) e confirmacoes (`Ack`) mostrando o controle de entrega dos bytes.
- **Ordem:** os bytes enviados pelo cliente sao remontados na mesma ordem pelo servidor.
- **Encerramento:** pacotes `FIN` e `ACK`, indicando fechamento da conexao TCP.

## Conceitos demonstrados

- **Cliente-servidor:** o servidor fica em escuta e o cliente inicia a comunicacao.
- **Socket TCP:** interface usada pelos programas para enviar e receber dados pela rede.
- **Conexao:** antes de transmitir dados, TCP estabelece uma conexao entre cliente e servidor.
- **Fluxo de bytes:** TCP transporta bytes em sequencia; a aplicacao define onde cada comando termina.
- **Confiabilidade:** TCP usa ACKs, numeros de sequencia e retransmissoes quando necessario.
- **Ordem de entrega:** TCP entrega os bytes ao programa na mesma ordem em que foram enviados.
- **Porta:** a porta `5000` identifica o processo servidor que deve receber os dados.
- **Concorrencia:** o servidor cria uma thread para cada cliente aceito, permitindo mais de uma conexao ao mesmo tempo.

## Limitacoes do experimento

Este projeto foi desenvolvido para fins didaticos. As principais limitacoes sao:

- **Ambiente local:** a execucao padrao usa `127.0.0.1`, ou seja, cliente e servidor rodam na mesma maquina.
- **Rede simulada por loopback:** a captura mostra trafego local; nao ha roteadores, enlaces fisicos, perda real de pacotes ou latencia de uma rede externa.
- **Poucos clientes:** o servidor usa threads e aceita mais de um cliente, mas nao foi projetado para alto volume de conexoes.
- **Ausencia de seguranca real:** nao ha TLS, criptografia, autenticacao, controle de usuarios ou protecao contra clientes maliciosos.
- **Protocolo simples:** os comandos `MSG`, `FILE` e `QUIT` foram criados apenas para demonstrar TCP de forma clara.
- **Limite de arquivo:** arquivos acima de 10 MB sao recusados para manter o experimento controlado.
- **Sem verificacao criptografica:** o projeto nao calcula hash, assinatura digital ou validacao forte de integridade do arquivo.
- **Sem comparacao com UDP:** o foco e demonstrar TCP, nao comparar desempenho, perdas ou latencia com outros protocolos.
- **Timeout de inatividade:** clientes interativos inativos por mais de 5 minutos sao desconectados.

## Conclusao

O projeto demonstra uma comunicacao TCP completa em pequena escala: o servidor escuta, o cliente conecta, mensagens e arquivos sao enviados como fluxo de bytes, o servidor confirma recebimentos com `ACK`, e a conexao e encerrada de forma controlada. A captura no Wireshark permite relacionar a execucao do codigo aos mecanismos teoricos do TCP.
