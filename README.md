# Comunicacao TCP Cliente-Servidor

Projeto pratico do Grupo 5 para demonstrar uma comunicacao TCP cliente-servidor usando sockets em Python.

O sistema tem:

- um servidor TCP que escuta conexoes em `127.0.0.1:5000`;
- um cliente TCP que se conecta ao servidor;
- envio de mensagens de texto;
- envio opcional de arquivo;
- respostas de confirmacao do servidor;
- roteiro para inspecionar o trafego no Wireshark.

## Tecnologias

- Python 3
- Biblioteca padrao `socket`
- Wireshark para captura/analise de trafego

Nao e necessario instalar bibliotecas externas.

## Estrutura

```text
.
|-- src/
|   |-- client.py
|   `-- server.py
|-- docs/
|   `-- DOCUMENTO_TRABALHO.md
|-- exemplos/
|   `-- exemplo.txt
|-- evidencias/
|   `-- README.md
|-- README.md
`-- .gitignore
```

## Como executar

Abra dois terminais na pasta do projeto.

### 1. Iniciar o servidor

```bash
python src/server.py
```

Saida esperada:

```text
[SERVIDOR] Aguardando conexoes em 127.0.0.1:5000
[SERVIDOR] Pressione Ctrl+C para parar.
```

### 2. Executar o cliente

Em outro terminal:

```bash
python src/client.py
```

Saida esperada no cliente:

```text
[CLIENTE] Conectando em 127.0.0.1:5000
[CLIENTE] Servidor: Bem-vindo ao servidor TCP. Use MSG, FILE ou QUIT.
[CLIENTE] Resposta: ACK MSG 18 bytes recebidos
[CLIENTE] Resposta: ACK QUIT conexao encerrada
```

### 3. Enviar uma mensagem personalizada

```bash
python src/client.py --message "Teste de comunicacao TCP"
```

### 4. Enviar um arquivo

Crie um arquivo de teste:

```bash
echo "arquivo de teste via TCP" > exemplos/exemplo.txt
```

Execute o cliente com a opcao `--file`:

```bash
python src/client.py --message "Vou enviar um arquivo" --file exemplos/exemplo.txt
```

O servidor salva o arquivo recebido na pasta `recebidos/`.

## Analise de trafego

### Wireshark

1. Abra o Wireshark.
2. Inicie a captura na interface de loopback.
   - No Windows, normalmente aparece como `Adapter for loopback traffic capture`.
   - Em algumas instalacoes pode aparecer como `Npcap Loopback Adapter`.
3. Use o filtro:

```text
tcp.port == 5000
```

4. Inicie o servidor com `python src/server.py`.
5. Execute o cliente com `python src/client.py`.
6. Observe os pacotes capturados.

### O que observar

- Estabelecimento da conexao:
  - `SYN`
  - `SYN, ACK`
  - `ACK`
- Envio dos dados:
  - segmentos TCP com payload contendo `MSG`, `FILE` ou `QUIT`;
  - numeros de sequencia (`Seq`);
  - confirmacoes (`Ack`).
- Encerramento:
  - pacotes `FIN` e `ACK`, quando a conexao e finalizada.

## Conceitos demonstrados

- **Cliente-servidor:** o servidor espera conexoes e o cliente inicia a comunicacao.
- **Socket TCP:** interface usada pelo programa para enviar e receber dados pela rede.
- **Conexao:** antes dos dados, o TCP estabelece uma conexao com handshake de tres vias.
- **Fluxo de bytes:** TCP envia bytes em sequencia; por isso o programa define comandos terminados por `\n`.
- **Confiabilidade:** o protocolo usa confirmacoes, numeros de sequencia e retransmissoes quando necessario.
- **Ordem:** os bytes chegam ao programa na mesma ordem em que foram enviados.
- **Porta:** o servidor usa a porta `5000`, permitindo que o sistema operacional entregue os dados ao processo correto.

## Limitacoes

- O experimento roda em `localhost`, sem trafego em uma rede real.
- O servidor atende um cliente por vez.
- Nao ha criptografia, autenticacao ou TLS.
- O protocolo da aplicacao e simples e criado apenas para fins didaticos.
- Nao ha comparacao de desempenho com UDP.
- Arquivos grandes nao foram o foco do teste.

## Roteiro rapido para apresentacao

1. Mostrar o codigo do servidor em `src/server.py` e explicar `bind`, `listen` e `accept`.
2. Mostrar o codigo do cliente em `src/client.py` e explicar `connect` e `sendall`.
3. Executar `python src/server.py`.
4. Executar `python src/client.py`.
5. Mostrar a resposta `ACK` no cliente e os logs no servidor.
6. Repetir enviando um arquivo com `--file`.
7. Abrir o Wireshark com filtro `tcp.port == 5000`.
8. Apontar o handshake, os pacotes com dados e o encerramento da conexao.
