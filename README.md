# ChockieMusicBot

ChockieMusicBot é um bot de música para Discord desenvolvido em Python, permitindo que os usuários reproduzam músicas diretamente em seus servidores Discord.

## Índice

- [Recursos](#recursos)
- [Pré-requisitos](#pré-requisitos)
- [Instalação](#instalação)
- [Configuração](#configuração)
- [Comandos](#comandos)
- [Contribuição](#contribuição)
- [Licença](#licença)

## Recursos

- Reproduz músicas de URLs do YouTube.
- Gerencia uma fila de músicas.
- Comandos para pular, pausar e retomar músicas.

## Pré-requisitos

- Python 3.8 ou superior.
- [FFmpeg](https://ffmpeg.org/) instalado e disponível no PATH do sistema.
- Uma conta no Discord e um servidor onde você tenha permissões para adicionar bots.

## Instalação

1. **Clone este repositório:**

   ```bash
   git clone https://github.com/joaopedrobn/chockiemusicbot.git
   ```

2. **Navegue até o diretório do projeto:**

   ```bash
   cd chockiemusicbot
   ```

3. **Crie um ambiente virtual (opcional, mas recomendado):**

   ```bash
   python -m venv env
   source env/bin/activate  # No Windows: env\Scripts\activate
   ```

4. **Instale as dependências:**

   ```bash
   pip install -r requirements.txt
   ```

5. **Instale o FFmpeg:**

   Execute o script de instalação do FFmpeg fornecido:

   ```bash
   ./install_ffmpeg.sh
   ```

   *Nota:* Certifique-se de que o FFmpeg esteja instalado e disponível no PATH do sistema.

## Configuração

1. **Crie um bot no Discord:**

   - Acesse o [Portal de Desenvolvedores do Discord](https://discord.com/developers/applications) e crie uma nova aplicação.
   - Adicione um bot à sua aplicação e copie o token.

2. **Configure variáveis de ambiente:**

   Crie um arquivo `.env` no diretório raiz do projeto e adicione o token do bot:

   ```
   DISCORD_TOKEN=seu_token_aqui
   ```

3. **Convide o bot para seu servidor:**

   Gere um link de convite com as permissões necessárias e adicione o bot ao seu servidor.

## Uso

Inicie o bot executando:

```bash
python bot.py
```

O bot agora está ativo e pronto para receber comandos no seu servidor Discord.

## Comandos

- **`!play <url>`**: Adiciona uma música à fila e começa a reproduzir.
- **`!skip`**: Pula a música atual.
- **`!pause`**: Pausa a música atual.
- **`!resume`**: Retoma a música pausada.
- **`!stop`**: Para a reprodução e limpa a fila.

## Contribuição

Contribuições são bem-vindas! Sinta-se à vontade para abrir issues e pull requests.

## Licença

Este projeto está licenciado sob a Licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.
