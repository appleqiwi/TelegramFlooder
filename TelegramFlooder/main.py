
from telethon import TelegramClient

import configparser
import asyncio
import os



asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


class Flooder():
    def __init__(
            self,
            session_name: str,
            api_id: int | str,
            api_hash: str,
            phone: str,
            password: str,
            check_dialog: int | bool = True,
    ):
        self.check_dialog = check_dialog
        self.phone = phone
        self.password = password if password.strip() else None
        self.client = TelegramClient(session_name, api_id, api_hash)

    async def connect(self):
        await self.client.connect()
        if not await self.client.is_user_authorized():
            await self.client.send_code_request(self.phone)
            await self.client.sign_in(self.phone, input('Please enter your code: '), password=self.password)

    async def get_chat_members(self, chat: str | int):
        chat_data = await self.client.get_entity(chat)
        return await self.client.get_participants(chat_data)

    async def send_message(self, user: str | int, text: str):
        if self.check_dialog:
            user_messages = await self.client.get_messages(user)
            total_messages = user_messages.total
            if total_messages != 0:
                return
        await self.client.send_message(user, text)
        return True

    async def send_messages(self, chat: str | int, text: str, limit=120):
        chat_members = list(await self.get_chat_members(chat))
        allowed_members = []
        count = 0
        for member in chat_members:
            if limit and count == limit:
                break
            if not member.bot and not member.is_self and not vars(member.participant).get('admin_rights'):
                allowed_members.append(member.id)
                count += 1
        tasks = [asyncio.create_task(self.send_message(member, text)) for member in allowed_members]
        response = list(await asyncio.gather(*tasks))
        return response.count(True)


if __name__ == '__main__':
    config = configparser.ConfigParser()
    config.read(os.path.abspath('config.cfg'))
    api_id = config['Telegram']['api_id']
    api_hash = config['Telegram']['api_hash']
    phone = config['Telegram']['phone']
    password = config['Telegram']['password']
    session_name = config['Telegram']['session_name']

    check_dialog = int(config['Settings']['check_dialog'])

    if any(not v for v in [api_id, api_hash, phone, session_name]):
        print('-* Error: Append data in config.cfg')
        os._exit(0)
    chat = input('-* [1] Enter chat id or url or name: ')
    limit = int(input('-* [2] Enter messages limit: '))
    text = input('-* [3] Enter messages text: ')

    async def main():
        flooder = Flooder(session_name, api_id, api_hash, phone, password, check_dialog)
        await flooder.connect()
        count = await flooder.send_messages(chat, text, limit)
        return count
    users_count = asyncio.run(main())
    print(f'-* Text successfully sent to {users_count} users')