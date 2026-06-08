import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djangoproj.settings')
django.setup()

from djangoapp.models import CarMake, CarModel

def populate():
    # Clear existing
    CarModel.objects.all().delete()
    CarMake.objects.all().delete()

    # Create Makes
    toyota = CarMake.objects.create(name="Toyota", description="Japanese multinational automotive manufacturer")
    ford = CarMake.objects.create(name="Ford", description="American multinational automobile manufacturer")
    honda = CarMake.objects.create(name="Honda", description="Japanese multinational manufacturer of automobiles and motorcycles")
    nissan = CarMake.objects.create(name="Nissan", description="Japanese multinational automobile manufacturer")

    # Create Models
    CarModel.objects.create(car_make=toyota, name="Camry", type="SEDAN", year=2023)
    CarModel.objects.create(car_make=toyota, name="RAV4", type="SUV", year=2022)
    CarModel.objects.create(car_make=ford, name="Mustang", type="COUPE", year=2021)
    CarModel.objects.create(car_make=ford, name="Explorer", type="SUV", year=2023)
    CarModel.objects.create(car_make=honda, name="Civic", type="SEDAN", year=2022)
    CarModel.objects.create(car_make=nissan, name="Altima", type="SEDAN", year=2023)

    print("Database populated successfully with Car Makes and Models!")

if __name__ == '__main__':
    populate()
