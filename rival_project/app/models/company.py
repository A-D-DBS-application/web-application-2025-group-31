class Company:
    def __init__(self, name, industry, location, description):
        self.name = name
        self.industry = industry
        self.location = location
        self.description = description

    def __repr__(self):
        return f"<Company {self.name}>"

    def get_info(self):
        return {
            "name": self.name,
            "industry": self.industry,
            "location": self.location,
            "description": self.description
        }