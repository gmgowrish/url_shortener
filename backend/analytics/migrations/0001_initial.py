# Generated migration for analytics app with geolocation support

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('links', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='DeviceInfo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ip_address', models.GenericIPAddressField()),
                ('device_model', models.CharField(blank=True, default='Unknown', max_length=255)),
                ('device_type', models.CharField(choices=[('mobile', 'Mobile'), ('tablet', 'Tablet'), ('desktop', 'Desktop'), ('unknown', 'Unknown')], default='unknown', max_length=50)),
                ('user_agent', models.CharField(blank=True, max_length=500)),
                ('country', models.CharField(blank=True, default='Unknown', max_length=100)),
                ('country_code', models.CharField(blank=True, default='', max_length=2)),
                ('city', models.CharField(blank=True, default='Unknown', max_length=100)),
                ('region', models.CharField(blank=True, default='', max_length=100)),
                ('latitude', models.FloatField(blank=True, null=True)),
                ('longitude', models.FloatField(blank=True, null=True)),
                ('timezone', models.CharField(blank=True, default='', max_length=50)),
                ('isp', models.CharField(blank=True, default='', max_length=255)),
                ('first_access', models.DateTimeField(auto_now_add=True)),
                ('last_access', models.DateTimeField(auto_now=True)),
                ('access_count', models.PositiveIntegerField(default=1)),
                ('link', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='device_accesses', to='links.link')),
            ],
            options={
                'ordering': ['-last_access'],
            },
        ),
        migrations.CreateModel(
            name='DailyStats',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('clicks', models.PositiveIntegerField(default=0)),
                ('unique_clicks', models.PositiveIntegerField(default=0)),
                ('link', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='daily_stats', to='links.link')),
            ],
            options={
                'ordering': ['-date'],
                'unique_together': {('link', 'date')},
            },
        ),
        migrations.CreateModel(
            name='ClickEvent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('clicked_at', models.DateTimeField(auto_now_add=True)),
                ('ip_address', models.GenericIPAddressField(blank=True, null=True)),
                ('user_agent', models.CharField(blank=True, default='', max_length=500)),
                ('referer', models.URLField(blank=True, null=True)),
                ('country', models.CharField(blank=True, default='', max_length=2)),
                ('city', models.CharField(blank=True, default='', max_length=100)),
                ('link', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='click_events', to='links.link')),
            ],
            options={
                'ordering': ['-clicked_at'],
            },
        ),
        migrations.AddIndex(
            model_name='deviceinfo',
            index=models.Index(fields=['link', '-last_access'], name='analytics_d_link_id_idx'),
        ),
        migrations.AddIndex(
            model_name='deviceinfo',
            index=models.Index(fields=['country_code'], name='analytics_d_country_code_idx'),
        ),
        migrations.AddIndex(
            model_name='clickevent',
            index=models.Index(fields=['link', '-clicked_at'], name='analytics_c_link_id_clicked_at_idx'),
        ),
        migrations.AddIndex(
            model_name='clickevent',
            index=models.Index(fields=['clicked_at'], name='analytics_c_clicked_at_idx'),
        ),
        migrations.AlterUniqueTogether(
            name='deviceinfo',
            unique_together={('link', 'ip_address')},
        ),
    ]
