import click
import click_repl


@click.group(invoke_without_command=True)
@click.pass_context
def cli(ctx):
    if ctx.invoked_subcommand is None:
        ctx.invoke(repl)


@cli.command()
@click.argument('what')
@click.option('--deamon', is_flag=True)
@click.option('--check', is_flag=True)
def run(what, deamon, check):
    """ application entry point """
    if check:
        from database.database_manupulation import create_all
        create_all()
    if what == 'bot':
        if deamon:
            import subprocess
            with open('bot_log', 'w') as fd:
                p = subprocess.Popen(['python', 'manage.py', 'run', 'bot'],
                                     cwd=".",
                                     stdout=subprocess.DEVNULL,
                                     stderr=fd)
                print(p.pid)
        else:
            from bots.telegram_bot import main
            main()
    elif what == 'flask':
        if deamon:
            import subprocess
            with open('flask_log', 'w') as fd:
                p = subprocess.Popen(['python', 'manage.py', 'run', 'flask'],
                                     cwd=".",
                                     stdout=subprocess.DEVNULL,
                                     stderr=fd)
                print(p.pid)
        else:
            from stella_api.app import app
            app.run(host='0.0.0.0', port=5000)
    elif what == 'all':
        import subprocess
        with open('bot_log', 'w') as fd:
            p1 = subprocess.Popen(['python', 'manage.py', 'run', 'bot'],
                                  cwd=".",
                                  stdout=subprocess.DEVNULL,
                                  stderr=fd)
        with open('flask_log', 'w') as fd:
            p2 = subprocess.Popen(['python', 'manage.py', 'run', 'flask'],
                                  cwd=".",
                                  stdout=subprocess.DEVNULL,
                                  stderr=fd)
        if not deamon:
            print('running')
            p1.wait()
            p2.wait()
        else:
            print(p1.pid)
            print(p2.pid)
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
def fixture():
    """fixture"""
    from database.models import Fuel, FuelCompany
    from database.queries import session_scope
    with session_scope() as session:
        for company_name in ['Юкон', 'Брсм']:
            session.add(FuelCompany(fuel_company_name=company_name))
            session.commit()
        for fuel, is_premium in [('95+', False),
                                 ('95E', True),
                                 ('92', False),
                                 ('ДП+', False),
                                 ('ДП', False),
                                 ('ГАЗ', False),
                                 ('95', False)]:
            session.add(Fuel(fuel_type=fuel, is_premium=is_premium))
            session.commit()


@cli.command()
@click.option('--all', is_flag=True)
@click.option('--tables')
def truncate(all, tables):
    """ truncates table(s) """
    if all:
        from database.database_manupulation import truncate_all_tables
        truncate_all_tables()
    elif tables:
        from database.database_manupulation import truncate_tables
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


@cli.command()
def fake():
    """ create fake instances in database """
    import random
    from itertools import chain
    from faker import Faker
    from database.queries import get_or_create
    from database.db_connection import session_maker
    from database.models import (User, FuelCompany, Fuel, GasStation, Images,
                                 Price)

    fake = Faker()
    session = session_maker()

    tg_uids = random.sample(list(range(10_000)), 5)
    users = [get_or_create(session, User, tg_id=uid) for uid in tg_uids]

    fuel_company_names = [fake.company() for _ in range(3)]
    companies = [get_or_create(session, FuelCompany, fuel_company_name=n)
                 for n in fuel_company_names]

    fuel_marks = ['92', '98', '95', '80']
    fuels = [get_or_create(session, Fuel, fuel_type=f, is_premium=False)
             for f in fuel_marks]

    addresses = [fake.address() for _ in range(10)]
    gas_stations = [get_or_create(session, GasStation, address=a,
                                  fuel_company_id=random.choice(companies).id)
                    for a in addresses]

    links = [fake.image_url(width=500, height=400) for _ in range(10)]
    recognized = [fake.pybool() for _ in range(10)]
    metadata = [fake.pybool() for _ in range(10)]
    images = [get_or_create(session, Images, link=l, is_recognized=r,
                            is_from_metadata=m)
              for l, r, m in zip(links, recognized, metadata)]

    prices = [get_or_create(session, Price, price=random.uniform(0, 99),
                            gas_station_id=random.choice(gas_stations).id,
                            fuel_id=random.choice(fuels).id,
                            images_id=i.id)
              for i in images]

    for entity in chain(users, companies, fuels, gas_stations, images, prices):
        session.add(entity)

    session.commit()


@cli.command()
def repl():
    click_repl.repl(click.get_current_context())


@cli.command()
def help():
    print('run - runs apllication\n'
          'show-schema - describes database schema\n'
          'create - creates table(s)\n'
          'truncate - truncates table(s)\n'
          'drop - drops table(s)\n'
          'fake - fill database with fake records')


if __name__ == '__main__':
    cli(obj={})
