from app import db

class Beer(db.Model):
    __tablename__ = 'Beer'

    upc = db.Column(db.Integer, primary_key=True)
    brewery_id = db.Column(db.Integer, db.ForeignKey('Brewery.id'), nullable=False)

    def __init__(self, upc, brewery_id, style, beer_name, abv, ibu, year_created, stock, price, rating):
        self.upc = upc
        self.brewery_id = brewery_id
        self.style = style
        self.beer_name = beer_name
        self.abv = abv
        self.ibu = ibu
        self.year_created = year_created
        self.stock = stock
        self.price = price
        self.rating = rating
