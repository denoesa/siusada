from django.contrib.auth import get_user_model
from django.db import models
from django.db.models.signals import pre_save
from django.shortcuts import reverse
from django.utils.text import slugify

User = get_user_model()


class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Address(models.Model):
    village = models.CharField(max_length=250)

    def __str__(self):
        return self.village


class Product(models.Model):
    title = models.CharField(max_length=150)
    slug = models.SlugField(unique=True)
    image = models.ImageField(upload_to='product_images')
    description = models.TextField()
    price = models.IntegerField(default=0)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    category = models.ManyToManyField(Category, related_name="products")
    owner = models.ForeignKey(
        User, related_name="products", on_delete=models.CASCADE)
    address = models.ManyToManyField(Address, related_name="productaddress")
    available = models.BooleanField(default=False)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("shop:product-detail", kwargs={'slug': self.slug})

    def get_update_url(self):
        return reverse("staff:product-update", kwargs={'pk': self.pk})

    def get_delete_url(self):
        return reverse("staff:product-delete", kwargs={'pk': self.pk})

    def get_price(self):
        return self.price

    def get_owner(self):
        return self.owner


class Order(models.Model):
    user = models.ForeignKey(
        User, related_name="orders", on_delete=models.CASCADE, blank=True, null=True)
    start_date = models.DateTimeField(auto_now_add=True)
    ordered_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.reference_number

    @property
    def reference_number(self):
        return f"ORDER-{self.pk}"

    def get_total(self):
        total = 0
        for order_item in self.items.all():
            total += order_item.get_total_item()
        return total


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(
        Product, related_name="items", on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    product_owner = models.ForeignKey(
        User, related_name="items", on_delete=models.CASCADE)
    product_total_price = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.product} x {self.quantity}"

    def get_total_item(self):
        return self.quantity * self.product.price

    def save(self):
        self.product_total_price = self.quantity * self.product.price
        self.product_owner = self.product.owner
        return super(OrderItem, self).save()


class Checkout(models.Model):
    name = models.CharField(max_length=100, blank=True, null=True)
    address = models.CharField(max_length=256, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    request = models.TextField(max_length=256, blank=True, null=True)
    order = models.ForeignKey(
        Order, related_name='checkout', on_delete=models.CASCADE)
    owner = models.ForeignKey(
        User, related_name="checkoutowner", on_delete=models.CASCADE, blank=True, null=True)
    totalpay = models.IntegerField(default=0)
    status = models.BooleanField(default=False)
    checkout_date = models.DateTimeField(
        auto_now_add=True, blank=True, null=True)
    user = models.ForeignKey(
        User, related_name="checkoutuser", on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return self.reference_number

    def save(self):
        super(Checkout, self).save()
        objs = [
            RealOrderItem(
                checkout=Checkout.objects.get(id=self.id),
                order=self.order,
                product=item.product,
                quantity=item.quantity,
                product_owner=item.product_owner,
                product_total_price=item.product_total_price
            )
            for item in self.order.items.filter(order__checkout__pk=self.id, order=self.order, product_owner=self.owner)
        ]
        if self.status == False:
            RealOrderItem.objects.bulk_create(objs)

    @property
    def reference_number(self):
        return f"CHECKOUT-{self.pk}"


class RealOrderItem(models.Model):
    checkout = models.ForeignKey(
        Checkout, related_name="real", on_delete=models.CASCADE)
    order = models.ForeignKey(
        Order, related_name='orders', on_delete=models.CASCADE)
    product = models.ForeignKey(
        Product, related_name="products", on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    product_owner = models.ForeignKey(
        User, related_name="owners", on_delete=models.CASCADE,)
    product_total_price = models.IntegerField(default=0)

    def __str__(self):
        return self.reference_number

    @property
    def reference_number(self):
        return f"ITEM-{self.pk} {self.product.title} X {self.quantity} - {self.checkout}"


class Payment(models.Model):
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name='payments')
    timestamp = models.DateTimeField(auto_now_add=True)
    receipt = models.FileField(
        upload_to='payment_receipt', blank=True, null=True)
    owner = models.ForeignKey(
        User, related_name="paymentowner", on_delete=models.CASCADE, blank=True, null=True)
    checkout = models.ForeignKey(
        Checkout, related_name="paymentcheckout", on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return self.reference_number

    @property
    def reference_number(self):
        return f"PAYMENT-{self.pk} - {self.checkout}"


def pre_save_product_receiver(sender, instance, *args, **kwargs):
    if not instance.slug:
        instance.slug = slugify(instance.title)


pre_save.connect(pre_save_product_receiver, sender=Product)
