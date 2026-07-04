# TCP_Cliente_Servidor# Comunicação TCP Cliente-Servidor

## Descrição

Este projeto implementa uma comunicação básica cliente-servidor utilizando o protocolo TCP em Python. O objetivo é demonstrar, de forma prática, conceitos fundamentais de redes de computadores, como estabelecimento de conexão, transmissão confiável de dados e controle de fluxo.

O sistema consiste em um servidor TCP que aguarda conexões e um cliente TCP que se conecta ao servidor para enviar mensagens e receber respostas.

---

## Tecnologias Utilizadas

* Python 3
* Biblioteca padrão `socket`
* Wireshark (para análise de tráfego)

---

## Como Executar

### 1. Pré-requisitos

* Python 3 instalado

### 2. Executando o servidor

```bash
python server.py
```

### 3. Executando o cliente

Em outro terminal:

```bash
python client.py
```

---

## Demonstração

O cliente estabelece uma conexão com o servidor e envia uma mensagem. O servidor recebe a mensagem e responde com uma confirmação.

---

## Análise de Tráfego (Wireshark)

Para analisar a comunicação TCP:

### Filtro utilizado:

```
tcp.port == 5000
```

### O que observar:

* **Handshake TCP (3-way handshake):**

  * SYN
  * SYN-ACK
  * ACK

* **Transmissão de dados:**

  * Pacotes com payload
  * Números de sequência (SEQ)
  * Confirmações (ACK)

* **Encerramento da conexão:**

  * FIN
  * ACK

---

## Conceitos Envolvidos

* **TCP (Transmission Control Protocol):**
  Protocolo orientado à conexão que garante entrega confiável e ordenada de dados.

* **Conexão:**
  Estabelecida através do handshake de três vias.

* **Fluxo de bytes:**
  Os dados são transmitidos como um fluxo contínuo, sem delimitação de mensagens.

* **Confiabilidade:**
  Garantida por mecanismos de retransmissão e confirmação (ACK).

* **Ordem:**
  Mantida através de números de sequência (SEQ).

* **Sockets:**
  Interface de programação utilizada para comunicação entre cliente e servidor.

---

## Limitações

* Execução em ambiente local (localhost)
* Suporte a apenas um cliente por vez
* Não há criptografia (sem TLS)
* Não há tratamento robusto de erros
* Não há controle explícito de congestionamento
* Comunicação simples (texto)

---

## Estrutura do Projeto

```
.
├── server.py
├── client.py
└── README.md
```

