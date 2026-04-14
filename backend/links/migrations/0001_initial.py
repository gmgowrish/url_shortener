# links app initial migration

from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings
import links.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Link',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('original_url', models.URLField(max_length=2048)),
                ('short_code', models.CharField(db_index=True, max_length=20, unique=True)),
                ('title', models.CharField(blank=True, default='', max_length=200)),
                ('description', models.TextField(blank=True, default='')),
                ('is_active', models.BooleanField(default=True)),
                ('expires_at', models.DateTimeField(blank=True, null=True)),
                ('custom_slug', models.CharField(blank=True, max_length=50, null=True, unique=True)),
                ('click_count', models.PositiveIntegerField(default=0)),
                ('unique_clicks', models.PositiveIntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('last_clicked_at', models.DateTimeField(blank=True, null=True)),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='links', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.AddIndex(
            model_name='link',
            index=models.Index(fields=['short_code'], name='links_l_short_code_idx'),
        ),
        migrations.AddIndex(
            model_name='link',
            index=models.Index(fields=['owner', '-created_at'], name='links_l_owner_created_at_idx'),
        ),
    ]
