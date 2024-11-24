from highrise import BaseBot, Position, User, CurrencyItem, Item
from highrise.__main__ import *
import time, json


class MazeBot(BaseBot):
    def __init__(self):
        super().__init__()

        ### VARIABLES ###

        ## WELCOME MESSAGE ##
        self.welcome_message_file = "welcome_message.json"  # File to store the welcome message
        self.load_welcome_message()

        ## TELEPORT POSITIONS ##
        self.bot_position_file = Position(3.5, 0, 0.5)
        self.player_position = Position(19.5, 1.0, 19.5)
        self.win_position = Position(2.5, 0.10000000149011612, 13.5)

        ## TIP AMOUNT ##

        self.tip_fee = 5

    ### SAVE AND LOAD FUNCTIONS ###

    def load_welcome_message(self):
        try:
            with open(self.welcome_message_file, "r") as file:
                data = json.load(file)
                self.welcome_message = data.get("welcome_message", "Welcome, {username}! Feel free to chat and participate in the activities.")
        except FileNotFoundError:
            self.welcome_message = "Welcome, {username}! Feel free to chat and participate in the activities."

    def save_welcome_message(self, new_message):
        try:
            with open(self.welcome_message_file, "w") as file:
                json.dump({"welcome_message": new_message}, file)
            self.load_welcome_message()  # Reload the welcome message after saving
        except OSError as e:
            print(f"Error saving welcome message: {e}")

    ###############################

    ##### MAIN CODE ####

    async def on_start(self, session_metadata):
        print("Armed and ready!")
        await self.highrise.teleport(self.highrise.my_id, self.bot_position_file)

    async def on_user_join(self, user: User, pos: Position) -> None:
        formatted_message = self.welcome_message.format(username=user.username)
        await self.highrise.chat(formatted_message)

    async def on_emote(self, user: User, emote_id: str, receiver: User | None,) -> None:

        # Add your logic to respond to user emotes here
        if emote_id == "emoji-thumbsup":

            # Get the list of users in the room
            users_won = (await self.highrise.get_room_users()).content

            for user, pos in users_won:

                # Check if the user is within a certain range of the winning position
                if (
                    abs(pos.x - self.win_position.x) < 0.5
                    and abs(pos.y - self.win_position.y) < 0.5
                    and abs(pos.z - self.win_position.z) < 0.5
                ):
                    await self.highrise.chat(f"You won {user.username}!")
                    await self.highrise.teleport(user.id, self.bot_position_file)

    async def on_tip(self, sender: User, receiver: User, tip: CurrencyItem | Item) -> None:

        print (f"{sender.username} tipped {receiver.username} an amount of {tip.amount}")

        if tip.amount == self.tip_fee and receiver.id == self.highrise.my_id:

            await self.highrise.teleport(sender.id, self.player_position)
            await self.highrise.chat(f"{sender.username} is entering the maze!")

    async def on_chat(self, user: User, message: str) -> None:

        if user.username == "DJ._.ZAMPA":

            if message.startswith("wallet"):
                wallet = (await self.highrise.get_wallet()).content
                await self.highrise.chat(f"The bot wallet contains {wallet[0].amount} {wallet[0].type}")

            if message.startswith("/wmessage"):
                # Extract the new welcome message from the command
                new_welcome_message = message[len("/wmessage"):].strip()
                self.save_welcome_message(new_welcome_message)
                await self.highrise.chat(f"Welcome message has been updated!")

            elif message.startswith("/botpos"):
                # Update bot position to the position of the user who used the command
                user_id = (await self.highrise.get_room_users()).content
                user_pos = next((info for info in user_id if info[0].id == user.id), None)

                if user_pos:
                    user_position = user_pos[1]
                    self.bot_position_file = Position(user_position.x, user_position.y, user_position.z)
                    await self.highrise.chat(f"Position updated!")

            elif message.startswith("/playerpos"):
                # Update bot position to the position of the user who used the command
                user_id = (await self.highrise.get_room_users()).content
                user_pos = next((info for info in user_id if info[0].id == user.id), None)

                if user_pos:
                    user_position = user_pos[1]
                    self.player_position = Position(user_position.x, user_position.y, user_position.z)
                    await self.highrise.chat(f"Position updated!")

            elif message.startswith("/winpos"):
                # Update bot position to the position of the user who used the command
                user_id = (await self.highrise.get_room_users()).content
                user_pos = next((info for info in user_id if info[0].id == user.id), None)

                if user_pos:
                    user_position = user_pos[1]
                    self.win_position = Position(user_position.x, user_position.y, user_position.z)
                    await self.highrise.chat(f"Position updated!")

            elif message.startswith("/tpplayer"):
                # Extract the target username from the command parameters
                target_username = message.split("/tpplayer", 1)[1].strip()

                # Get the list of users in the room
                room_users_response = await self.highrise.get_room_users()
                room_users = room_users_response.content

                # Find the user with the specified username
                target_user_tuple = next((user_tuple for user_tuple in room_users if user_tuple[0].username == target_username), None)

                if target_user_tuple:
                    target_user, _ = target_user_tuple
                    # Teleport the target user to the specified position
                    await self.highrise.teleport(target_user.id, self.player_position)
                    await self.highrise.chat(f"{target_username} is entering the maze!")
                else:
                    await self.highrise.chat(f"Player with username {target_username} not found.")



            elif message.startswith("/tpbot"):

                await self.highrise.teleport(self.highrise.my_id, self.bot_position_file)

            elif message.startswith("/changefee "):
                try:
                    # Extract the number from the message
                    new_fee = int(message[len("/changefee "):])

                    # Check if the new_fee is one of the allowed values
                    allowed_values = {1, 5, 10, 50, 100}
                    if new_fee in allowed_values:

                        # Update the tip_fee
                        self.tip_fee = new_fee
                        await self.highrise.chat(f"Maze fee has been changed to {new_fee}")
                    else:
                        await self.highrise.chat("Invalid input. Please choose from 1, 5, 10, 50, or 100.")
                except ValueError:
                    await self.highrise.chat("Invalid input. Please use /changefee <number> to change the tip fee.")

    async def on_user_move(self, user: User, pos: Position) -> None:
            print (f"{user.username} new pos updated to {pos}")

    async def userinfo (self: BaseBot, user: User, message: str) -> None:
        print(f"{self.highrise.my_id}")

##### BOT SETTINGS #####
room_id = "65a7cd002d4c283c61689cd5"
bot_token = "816fa979d29701fb2a4ee2c81c2ef4fba2715906586d58728fc70f1ecb42897f"
bot_file = "botfilename"
bot_class = "MazeBot"

if __name__ == "__main__":
    definitions = [
        BotDefinition(
            getattr(import_module(bot_file), bot_class)(),
            room_id,
            bot_token)]  # More BotDefinition classes can be added to the definitions list
    while True:
        try:
            arun(main(definitions))
        except Exception as e:
            # Print the full traceback for the exception
            import traceback
            print("Caught an exception:")
            traceback.print_exc()  # This will print the full traceback
            time.sleep(1)
            continue       
