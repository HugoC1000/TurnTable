import random
import discord

card_values = {
    '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, '10': 10,
    'J': 10, 'Q': 10, 'K': 10, 'A': 11
}

class BlackjackGame(discord.ui.View):
    def __init__(self, ctx):
        super().__init__(timeout=30)
        self.ctx = ctx
        self.player_hand = [self.draw_card(), self.draw_card()]
        self.dealer_hand = [self.draw_card(), self.draw_card()]
        self.game_message = None

    def draw_card(self):
        return random.choice(list(card_values.keys()))

    def calculate_hand_value(self, hand):
        value = sum(card_values[card] for card in hand)
        ace_count = hand.count('A')
        while value > 21 and ace_count:
            value -= 10
            ace_count -= 1
        return value

    def format_hand(self, hand):
        return ', '.join(hand)

    async def update_embed(self):
        player_value = self.calculate_hand_value(self.player_hand)
        embed = discord.Embed(title="Blackjack", color=discord.Color.green())
        embed.add_field(name="Your Hand", value=f"{self.format_hand(self.player_hand)}\nValue: {player_value}", inline=False)
        embed.add_field(name="Dealer's Hand", value=f"{self.dealer_hand[0]}, ??", inline=False)
        embed.set_footer(text="Press the buttons below to play.")
        
        if self.game_message:
            await self.game_message.edit(embed=embed)
        else:
            self.game_message = await self.ctx.respond(embed=embed, view=self)
            
        #print("Finished update embed")

    @discord.ui.button(label="Hit", style=discord.ButtonStyle.green)
    async def hit(self, button: discord.ui.Button, interaction: discord.Interaction):
        self.player_hand.append(self.draw_card())
        player_value = self.calculate_hand_value(self.player_hand)
        dealer_value = self.calculate_hand_value(self.dealer_hand)
        await self.update_embed()
        await interaction.response.defer()

        #print("Entered hit")

        if player_value > 21:
            embed = discord.Embed(title="Blackjack", color=discord.Color.blue())
            embed.add_field(name="Your Hand", value=f"{self.format_hand(self.player_hand)}\nValue: {player_value}", inline=False)
            embed.add_field(name="Dealer's Hand", value=f"{self.format_hand(self.dealer_hand)}\nValue: {dealer_value}", inline=False)
            embed.add_field(name="Result", value=f"You busted!")
            await self.game_message.edit(embed=embed, view=None)
            self.stop()  # Stop the view

    @discord.ui.button(label="Stand", style=discord.ButtonStyle.red)
    async def stand(self, button: discord.ui.Button, interaction: discord.Interaction):
        await interaction.response.defer()

        dealer_value = self.calculate_hand_value(self.dealer_hand)

        while dealer_value < 17:
            self.dealer_hand.append(self.draw_card())
            dealer_value = self.calculate_hand_value(self.dealer_hand)

        player_value = self.calculate_hand_value(self.player_hand)
        
        embed = discord.Embed(title="Blackjack", color=discord.Color.blue())
        embed.add_field(name="Your Hand", value=f"{self.format_hand(self.player_hand)}\nValue: {player_value}", inline=False)
        embed.add_field(name="Dealer's Hand", value=f"{self.format_hand(self.dealer_hand)}\nValue: {dealer_value}", inline=False)

        if dealer_value > 21 or player_value > dealer_value:
            embed.add_field(name="Result", value="You win!", inline=False)
            embed.color = discord.Color.green()
        elif player_value < dealer_value:
            embed.add_field(name="Result", value="Dealer wins!", inline=False)
            embed.color = discord.Color.red()
        else:
            embed.add_field(name="Result", value="It's a tie!", inline=False)
            embed.color = discord.Color.gold()

        await self.game_message.edit(embed=embed, view=None)
        self.stop()
        


class RPSGame(discord.ui.View):
    def __init__(self, ctx):
        super().__init__(timeout=30)
        self.ctx = ctx
        self.result_message = None

    async def send_initial_embed(self):
        embed = discord.Embed(
            title="Rock-Paper-Scissors",
            description="Choose your move!",
            color=discord.Color.blue()
        )
        self.result_message = await self.ctx.respond(embed=embed, view=self)

    @discord.ui.button(label="Rock", style=discord.ButtonStyle.green, emoji="🪨")
    async def rock(self, button: discord.ui.Button, interaction: discord.Interaction):
        await self.play_game("Rock")

    @discord.ui.button(label="Paper", style=discord.ButtonStyle.green, emoji="📃")
    async def paper(self, button: discord.ui.Button, interaction: discord.Interaction):
        await self.play_game("Paper")

    @discord.ui.button(label="Scissors", style=discord.ButtonStyle.green, emoji="✂️")
    async def scissors(self, button: discord.ui.Button, interaction: discord.Interaction):
        await self.play_game("Scissors")

    async def play_game(self, user_choice):
        bot_choice = random.choice(["Rock", "Paper", "Scissors"])
        result = self.determine_winner(user_choice, bot_choice)

        embed = discord.Embed(
            title="Rock-Paper-Scissors Result",
            color=discord.Color.blue()
        )
        embed.add_field(name="Your Choice", value=user_choice, inline=True)
        embed.add_field(name="Bot's Choice", value=bot_choice, inline=True)
        embed.add_field(name="Result", value=result, inline=False)

        await self.result_message.edit(embed=embed, view=None)
        self.stop()  # Stop the view

    def determine_winner(self, user_choice, bot_choice):
        if user_choice == bot_choice:
            return "It's a tie!"
        elif (user_choice == "Rock" and bot_choice == "Scissors") or \
             (user_choice == "Paper" and bot_choice == "Rock") or \
             (user_choice == "Scissors" and bot_choice == "Paper"):
            return "You win!"
        else:
            return "You lose!"