import discord
from discord.ext import commands
from discord import app_commands
import os
from dotenv import load_dotenv

load_dotenv()

# Configuration des IDs (ceux fournis précédemment)
GUILD_ID = 1460284809455861875
PANEL_CHANNEL_ID = 1460998288361783518
CATEGORY_ID = 1460997839143567595
STAFF_ROLE_ID = 1495555149530140813

class TicketSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Aide", emoji="🆘", description="Besoin d'un coup de main ?"),
            discord.SelectOption(label="Question", emoji="❓", description="Une interrogation sur le serveur ?"),
            discord.SelectOption(label="Recrutements Staff", emoji="🛡️", description="Postuler pour l'équipe."),
            discord.SelectOption(label="Autre", emoji="⚙️", description="Tout autre demande.")
        ]
        # On ajoute un custom_id unique pour la persistance
        super().__init__(
            placeholder="Choisissez la raison du ticket...", 
            options=options, 
            custom_id="ticket_select_unique_id"
        )

    async def callback(self, interaction: discord.Interaction):
        guild = interaction.guild
        category = guild.get_channel(CATEGORY_ID)
        staff_role = guild.get_role(STAFF_ROLE_ID)

        if not category:
            return await interaction.response.send_message("Erreur : Catégorie introuvable.", ephemeral=True)

        # Permissions du salon
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            interaction.user: discord.PermissionOverwrite(view_channel=True, send_messages=True, attach_files=True),
            staff_role: discord.PermissionOverwrite(view_channel=True, send_messages=True)
        }

        # Création du salon
        channel = await guild.create_text_channel(
            name=f"ticket-{interaction.user.name}",
            category=category,
            overwrites=overwrites
        )

        await interaction.response.send_message(f"✅ Ticket créé : {channel.mention}", ephemeral=True)
        await channel.send(f"Bonjour {interaction.user.mention}, un membre du staff ({staff_role.mention}) va s'occuper de ta demande : **{self.values[0]}**.")

class TicketView(discord.ui.View):
    def __init__(self):
        # timeout=None est obligatoire pour un bouton persistant
        super().__init__(timeout=None)
        self.add_item(TicketSelect())

class Bot(commands.Bot):
    def __init__(self):
        # Activation des intents nécessaires
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        # Enregistre la vue pour qu'elle fonctionne après redémarrage
        self.add_view(TicketView())

bot = Bot()

@bot.event
async def on_ready():
    print(f"✅ Connecté en tant que {bot.user}")
    print(f"ID du Bot : {bot.user.id}")
    try:
        synced = await bot.tree.sync()
        print(f"📡 {len(synced)} commandes slash synchronisées.")
    except Exception as e:
        print(f"Erreur de synchro : {e}")

@bot.command()
@commands.has_permissions(administrator=True)
async def setup_ticket(ctx):
    embed = discord.Embed(
        title="Support - Ouverture de Ticket",
        description="Veuillez sélectionner le type de votre demande dans le menu déroulant ci-dessous.",
        color=discord.Color.blue()
    )
    embed.set_footer(text="Système de tickets automatique")
    
    view = TicketView()
    await ctx.send(embed=embed, view=view)

# Lancement du bot
token = os.getenv('TOKEN')
if token:
    bot.run(token)
else:
    print("❌ Erreur : Aucun token trouvé dans le fichier .env")