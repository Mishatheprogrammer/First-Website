from .models import Category
def menu_links(request): # Here we are going to fetch all the categories from the database
    links = Category.objects.all()
    return {'links': links}
