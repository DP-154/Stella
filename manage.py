"""
this file will manage main app and telegram bot
"click" library will be used
"""
import click


@click.group()
def cli():
    pass


@cli.command()
@click.argument('what')
@click.option('--deamon', is_flag=True)
def run(what, deamon):
    """ application entry point """
    if what == 'bot':
        if deamon:
            import subprocess
            subprocess.Popen(['python', 'manage.py', 'run', 'bot'],
                             cwd="/",
                             stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT)
        else:
            from bots.telegram_bot import main
            main()
    else:
        print(f'option not recognized: {what}')


@cli.command()
def show_schema():
    """ describes database schema """
    from database.models import Base
    for table in Base.metadata.tables.values():
        print(table.name)
        fks = Base.metadata.tables[table.name].foreign_keys
        fks = {i.target_fullname.replace('.', '_'): i.column for i in fks}
        for column in table.c:
            if column.name in fks:
                print(' ', column.name, 'foreign key to', fks[column.name])
            else:
                print(' ', column.name, column.type)
        print()


@cli.command()
def create():
    """ creates table(s) """
    from database.database_manupulation import create_all
    create_all()


@cli.command()
@click.option('--all', is_flag=True)
@click.option('--tables')
def truncate(all, tables):
    """ truncates table(s) """
    if all:
        from database.database_manupulation import truncate_all_tables
        truncate_all_tables()
    elif tables:
        from dataclasses.database_manupulation import truncate_tables
        truncate_tables(*tables.split(','))


@cli.command()
@click.option('--all', is_flag=True)
@click.option('--tables')
def drop(all, tables):
    """ drops table(s) """
    if all:
        from database.database_manupulation import drop_all_tables
        drop_all_tables()
    elif tables:
        from database.database_manupulation import drop_tables
        drop_tables(*tables.split(','))


if __name__ == '__main__':
    cli()
