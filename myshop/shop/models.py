from django.db import models
from django.urls import reverse

'''
    All models using in the project.
'''


class Category(models.Model):
    name = models.CharField(max_length=128)
    slug = models.SlugField(max_length=128, unique=True)

    # def get_absolute_url(self):
    #     return reverse('shop:product_list_by_category', args=[self.slug])

    def __str__(self):
        return self.name

    class Meta:
        ordering = ('name',)
        verbose_name = 'category'
        verbose_name_plural = 'categories'


class Product(models.Model):
    SEX = (
        ('M', 'Man'),
        ('W', 'Woman')
    )

    SIZE_PRODUCT = [
        ('Clothes', (
            ('S', 'S'),
            ('M', 'M'),
            ('L', 'L'),
            ('XL', 'XL'),
            ('XXL', 'XXL'),
            ('XXXL', 'XXXL'),
            )
        ),

        ('Shoes', (
            ('32', '32'),
            ('33', '33'),
            ('34', '34'),
            ('35', '35'),
            ('36', '36'),
            ('37', '37'),
            ('38', '38'),
            ('39', '39'),
            ('40', '40'),
            ('41', '41'),
            ('42', '42'),
            ('43', '43'),
            ('44', '44'),
            ('45', '45'),
            )),
        ('unknown', 'Unknown'),
    ]

    category = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE)
    name = models.CharField(max_length=128)
    slug = models.SlugField(max_length=128)
    image = models.ImageField(upload_to='products/%Y/%m/%d/%H/%M/%S', blank=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    available = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    sex = models.CharField(max_length=1, choices=SEX)
    size = models.CharField(max_length=7, choices=SIZE_PRODUCT)

    # def get_absolute_url(self):
    #     return reverse('shop:product_detail', args=[self.id, self.slug])

    class Meta:
        ordering = ('name',)
        index_together = (('id', 'slug'),)

    def __str__(self):
        return self.name


class Order(models.Model):
    first_name = models.CharField(max_length=64)
    last_name = models.CharField(max_length=64)
    email = models.EmailField()
    address = models.CharField(max_length=256)
    postal_code = models.CharField(max_length=20)
    city = models.CharField(max_length=128)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    paid = models.BooleanField(default=False)

    class Meta:
        ordering = ('-created',)

    def __str__(self):
        return f'Order {self.id}'

    def get_total_cost(self):
        return sum(item.get_cost() for item in self.items.all())


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name='order_items', on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f'Order {self.id}'

    def get_cost(self):
        return self.price * self.quantity
