# Generated by Django 4.1.4 on 2023-07-04 12:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0008_listings_category'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='watchcounter',
            field=models.IntegerField(default=0),
        ),
    ]
