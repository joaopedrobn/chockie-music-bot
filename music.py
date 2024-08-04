import discord
from discord.ext import commands
import yt_dlp as youtube_dl
import logging
import asyncio

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.guild_data = {}  # Armazena dados específicos de cada servidor

        # Configuração de logs
        logging.basicConfig(level=logging.INFO, format='%(asctime)s:%(levelname)s:%(message)s')
        self.logger = logging.getLogger(__name__)

        # Definindo opções do yt_dlp
        self.ydl_opts = {
            'format': 'bestaudio/best',
            'noplaylist': 'True',
            'quiet': True,
        }

        self.ffmpeg_options = {
            'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
            'options': '-vn'
        }

    def get_guild_data(self, guild_id):
        if guild_id not in self.guild_data:
            self.guild_data[guild_id] = {
                'queue': [],
                'is_playing': False,
                'current': None,
                'voice_client': None,
                'volume': 0.5,
                'loop': False
            }
        return self.guild_data[guild_id]

    async def search_yt(self, query):
        self.logger.info(f"Buscando áudio para: {query}")
        ydl_opts = self.ydl_opts.copy()
        ydl_opts.update({'default_search': 'ytsearch', 'max_downloads': 1})
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            try:
                info = ydl.extract_info(query, download=False)
                # Verifica se é um único vídeo ou uma lista de vídeos
                if 'entries' in info:
                    video = info['entries'][0]
                else:
                    video = info
                return video['url'], video
            except Exception as e:
                self.logger.error(f"Erro ao buscar áudio: {e}")
                return None, None

    async def search_playlist(self, url):
        self.logger.info(f"Buscando playlist de {url}")
        ydl_opts = self.ydl_opts.copy()
        ydl_opts.update({'extract_flat': True, 'playlistend': 50})
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            try:
                info = ydl.extract_info(url, download=False)
                return info['entries']
            except Exception as e:
                self.logger.error(f"Erro ao buscar playlist: {e}")
                return None

    async def play_song(self, ctx):
        guild_data = self.get_guild_data(ctx.guild.id)

        if len(guild_data['queue']) > 0:
            guild_data['is_playing'] = True
            guild_data['current'] = guild_data['queue'].pop(0)
            m_url, info = await self.search_yt(guild_data['current']['url'])

            if m_url is None:
                await self.safe_send(ctx, "Não foi possível encontrar o áudio para essa URL.")
                guild_data['is_playing'] = False
                return

            self.logger.info(f"Tocando música: {guild_data['current']['title']} - URL: {m_url}")

            if ctx.voice_client is None:
                guild_data['voice_client'] = await ctx.author.voice.channel.connect()
                self.logger.info("Bot conectado ao canal de voz.")
            else:
                guild_data['voice_client'] = ctx.voice_client

            # Definindo o volume e iniciando a reprodução
            source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(m_url, **self.ffmpeg_options))
            source.volume = guild_data['volume']
            guild_data['voice_client'].play(source, after=lambda e: self.bot.loop.create_task(self.play_next(ctx)))

            embed = discord.Embed(
                title="Tocando agora",
                description=f"[{info['title']}]({guild_data['current']['url']})",
                color=discord.Color.blue()
            )
            embed.set_thumbnail(url=info['thumbnail'])
            await self.safe_send(ctx, embed=embed)
        else:
            guild_data['is_playing'] = False
            guild_data['current'] = None
            self.logger.info("Fila de música está vazia.")
            await self.safe_send(ctx, "Fila de música está vazia.")

    async def play_next(self, ctx):
        guild_data = self.get_guild_data(ctx.guild.id)

        if guild_data['loop']:
            guild_data['queue'].append(guild_data['current'])

        if len(guild_data['queue']) > 0:
            await self.play_song(ctx)
        else:
            guild_data['is_playing'] = False
            if guild_data['voice_client']:
                await guild_data['voice_client'].disconnect()
                self.logger.info("Bot desconectado do canal de voz.")
                await self.safe_send(ctx, "Todas as músicas da fila foram tocadas. Desconectando do canal de voz.")

    @commands.command(name="play", help="Toca uma música ou playlist do YouTube")
    async def play(self, ctx, *, query):
        guild_data = self.get_guild_data(ctx.guild.id)
        if 'playlist' in query:
            playlist = await self.search_playlist(query)
            if playlist:
                for entry in playlist:
                    guild_data['queue'].append({"title": entry['title'], "url": entry['url']})
                await self.safe_send(ctx, f"Playlist **{query}** adicionada à fila com {len(playlist)} músicas.")
        else:
            guild_data['queue'].append({"title": query, "url": query})
            await self.safe_send(ctx, f"Música **{query}** adicionada à fila.")

        self.logger.info(f"Adicionando à fila: {query}")
        if not guild_data['is_playing']:
            await self.play_song(ctx)

    @commands.command(name="skip", help="Pula para a próxima música na fila")
    async def skip(self, ctx):
        guild_data = self.get_guild_data(ctx.guild.id)

        if guild_data['voice_client'] and guild_data['voice_client'].is_playing():
            self.logger.info("Pulado para a próxima música.")
            await self.safe_send(ctx, "Pulando para a próxima música.")
            guild_data['voice_client'].stop()
        else:
            await self.safe_send(ctx, "Nenhuma música está sendo tocada no momento.")

    @commands.command(name="queue", help="Mostra a fila de músicas")
    async def queue_(self, ctx):
        guild_data = self.get_guild_data(ctx.guild.id)
        retval = "\n".join([f"{idx + 1}. {song['title']}" for idx, song in enumerate(guild_data['queue'])])
        if retval:
            embed = discord.Embed(
                title="Fila de músicas",
                description=retval,
                color=discord.Color.blue()
            )
            await self.safe_send(ctx, embed=embed)
        else:
            await self.safe_send(ctx, "A fila está vazia.")

    @commands.command(name="leave", help="Desconecta o bot do canal de voz")
    async def leave(self, ctx):
        guild_data = self.get_guild_data(ctx.guild.id)
        guild_data['queue'] = []
        if guild_data['voice_client']:
            await guild_data['voice_client'].disconnect()
            self.logger.info("Bot desconectado do canal de voz.")
            await self.safe_send(ctx, "Bot desconectado do canal de voz.")

    @commands.command(name="pause", help="Pausa a música atual")
    async def pause(self, ctx):
        guild_data = self.get_guild_data(ctx.guild.id)
        if guild_data['voice_client'] and guild_data['voice_client'].is_playing():
            guild_data['voice_client'].pause()
            self.logger.info("Música pausada.")
            await self.safe_send(ctx, "Música pausada.")
        else:
            await self.safe_send(ctx, "Nenhuma música está sendo tocada no momento.")

    @commands.command(name="resume", help="Retoma a música atual")
    async def resume(self, ctx):
        guild_data = self.get_guild_data(ctx.guild.id)
        if guild_data['voice_client'] and guild_data['voice_client'].is_paused():
            guild_data['voice_client'].resume()
            self.logger.info("Música retomada.")
            await self.safe_send(ctx, "Música retomada.")
        else:
            await self.safe_send(ctx, "Nenhuma música está pausada no momento.")

    @commands.command(name="volume", help="Ajusta o volume da música")
    async def volume(self, ctx, volume: int):
        guild_data = self.get_guild_data(ctx.guild.id)
        guild_data['volume'] = volume / 100
        if guild_data['voice_client'] and guild_data['voice_client'].source:
            guild_data['voice_client'].source.volume = guild_data['volume']
        await self.safe_send(ctx, f"Volume ajustado para {volume}%.")

    @commands.command(name="loop", help="Alterna o modo de repetição")
    async def loop(self, ctx):
        guild_data = self.get_guild_data(ctx.guild.id)
        guild_data['loop'] = not guild_data['loop']
        status = "ativado" if guild_data['loop'] else "desativado"
        await self.safe_send(ctx, f"Modo de repetição {status}.")

    async def safe_send(self, ctx, message=None, embed=None):
        try:
            if embed:
                await ctx.send(embed=embed)
            else:
                await ctx.send(message)
        except (discord.HTTPException, discord.Forbidden, discord.NotFound):
            self.logger.error(f"Falha ao enviar mensagem: {message}")

def setup(bot):
    bot.add_cog(Music(bot))