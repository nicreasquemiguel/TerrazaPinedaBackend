# Generated by Django 4.2.11 on 2025-01-11 19:30

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import shortuuid.django_fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('booking', '__first__'),
    ]

    operations = [
        migrations.CreateModel(
            name='BookingFAQ',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('product', models.CharField(max_length=1000)),
                ('question', models.CharField(max_length=1000)),
                ('answer', models.CharField(max_length=1000)),
                ('active', models.BooleanField(default=False)),
            ],
            options={
                'verbose_name_plural': 'Preguntas Frecuentes',
            },
        ),
        migrations.CreateModel(
            name='Tax',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('country', models.CharField(max_length=255)),
                ('rate', models.IntegerField(default=5, help_text='En porcentajes 5%')),
                ('active', models.BooleanField(default=True)),
                ('date', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name_plural': 'Taxes',
                'ordering': ['country'],
            },
        ),
        migrations.CreateModel(
            name='Review',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('review', models.TextField()),
                ('reply', models.TextField(blank=True, null=True)),
                ('rating', models.PositiveIntegerField(choices=[(1, '1 Estrella'), (2, '2 Estrellas'), (3, '3 Estrellas'), (4, '4 Estrellas'), (5, '5 Estrellas')], default=None)),
                ('active', models.BooleanField(default=False)),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='booking.event')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': 'Opinión de Eventos',
            },
        ),
        migrations.CreateModel(
            name='PaymentOrder',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('oid', shortuuid.django_fields.ShortUUIDField(alphabet='abcdefg12345', length=10, max_length=10, prefix='', unique=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('subtotal', models.DecimalField(decimal_places=2, default=0.0, max_digits=12)),
                ('tax_fee', models.DecimalField(decimal_places=2, default=0.0, max_digits=12)),
                ('total', models.DecimalField(decimal_places=2, default=0.0, max_digits=12)),
                ('linked', models.BooleanField(default=False)),
                ('payment_status', models.CharField(choices=[('pagado', 'Pagado'), ('pendiente', 'Pendiente'), ('procesando', 'Procesando'), ('cancelled', 'Cancelled')], default='pending', max_length=100)),
                ('payment_type', models.CharField(choices=[('stripe', 'Pago por Stripe'), ('deposito', 'Deposito Bancario'), ('transferencia', 'Transferncia Bancaria')], max_length=100)),
                ('stripe_session_id', models.CharField(blank=True, max_length=1000, null=True)),
                ('event', models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, to='booking.event')),
                ('payer', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='payer', to=settings.AUTH_USER_MODEL)),
                ('vendor', models.ForeignKey(blank=True, on_delete=django.db.models.deletion.PROTECT, related_name='vendor', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Coupon',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=1000)),
                ('discount', models.IntegerField(default=1)),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('active', models.BooleanField(default=True)),
                ('cid', shortuuid.django_fields.ShortUUIDField(alphabet='abcdefghijklmnopqrstuvxyz', length=10, max_length=25, prefix='')),
                ('used_by', models.ManyToManyField(blank=True, to=settings.AUTH_USER_MODEL)),
                ('vendor', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='coupon_vendor', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-id'],
            },
        ),
    ]
