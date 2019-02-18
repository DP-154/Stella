"""
this file will manage main app and telegram bot
"click" library will be used
"""
import click

from bots.telegram_bot import main


def run_bot():
    main()

@click.command()
@click.option('-b', '--runbot', is_flag=True, help="Run Telegram bot")
def execute(runbot):
    if runbot:
        run_bot()


if __name__ == '__main__':
    execute()
