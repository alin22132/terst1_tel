from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=100)
    image = models.TextField(default='def_category_img')  # Storing image URLs as text

    def __str__(self):
        return self.name


class Brand(models.Model):
    name = models.CharField(max_length=100)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='brands', default='default_category')

    def __str__(self):
        return self.name


class Model(models.Model):
    name = models.CharField(max_length=100)
    Brand = models.ForeignKey(Brand, on_delete=models.CASCADE, related_name='models', default='default_brand')

    def __str__(self):
        return self.name


class Item_list(models.Model):
    name = models.CharField(max_length=100)
    image = models.TextField(default='def_item_img')
    Model = models.ForeignKey(Model, on_delete=models.CASCADE, related_name='items', default='default_model')
    price = models.FloatField(default=0.00)
    desc = models.TextField(default='def_description')
    art_nr = models.CharField(max_length=100, default='N/A')
    descr = models.TextField(default='N/A')
    avlbl = models.BooleanField(default=False)

    def __str__(self):
        return self.name
