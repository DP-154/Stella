
class Database:
    def __init__(self):
        self.companies = ['Okko', 'WOG', 'Sky', 'Socar', 'Avias']
        self.stations = ['Okko, Panikahi str. 18', 'Wog, Zap. road 64']
        self.request = {
            'companies' :[]
        }

    def get_companies(self):
        return self.companies

    def get_stations(self):
        return self.stations

    def add_company(self, name):
        self.companies.append(name)
        return 'Success!'

