from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('carts', '0003_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cart',
            name='amount',
            field=models.IntegerField(default=1, verbose_name='수량'),
        ),
    ]