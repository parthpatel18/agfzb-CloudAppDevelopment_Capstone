from django.db import models
from django.utils.timezone import now


# Create your models here.

# <HINT> Create a Car Make model
class CarMake(models.Model):
    name = models.CharField('Name', max_length=30)
    description = models.CharField('Description', max_length=250)

    def __str__(self):
        return self.name

# <HINT> Create a Car Model model 
class CarModel(models.Model):
    car_type_choices = (
        ('HT', 'Hatchback'),
        ('PU', 'Pickup'),
        ('SD', 'Sedan'),
        ('SU', 'SUV'),
        ('WA', 'Wagon'),
    )

    car_make = models.ForeignKey(CarMake, on_delete=models.CASCADE)
    dealer_id = models.IntegerField('Dealer ID', default=0)
    name = models.CharField('Name', max_length=30)
    car_type = models.CharField('Type', max_length=2, choices=car_type_choices)
    year = models.DateField('Year')

    def __str__(self):
        return str(self.car_make) + ' ' + self.name

# <HINT> Create a plain Python class `CarDealer` to hold dealer data
class CarDealer:
    def __init__(self, address, city, full_name, id, lat, long, short_name, st, zip):
        self.address = address
        self.city = city
        self.full_name = full_name
        self.id = id
        self.lat = lat
        self.long = long
        self.short_name = short_name
        self.st = st
        self.zip = zip

        def __str__(self):
            return "Dealer name: " + self.full_name

# <HINT> Create a plain Python class `DealerReview` to hold review data
class DealerReview:
    def __init__(self, dealership, name, purchase, review, purchase_date, car_make, car_model, car_year, review_id):
        self.dealership = dealership
        self.name = name
        self.purchase = purchase
        self.review = review
        self.purchase_date = purchase_date
        self.car_make = car_make
        self.car_model = car_model
        self.car_year = car_year
        self.review_id = review_id

    def __str__(self):
        return "Dealer Review: " + self.review