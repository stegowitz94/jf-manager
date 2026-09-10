from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies=[("core","0002_externallink_dashboardpreference")]
    operations=[
        migrations.AddField(model_name="appsettings",name="short_name",field=models.CharField(blank=True,default="JF-Manager",max_length=60,verbose_name="Kurzbezeichnung")),
        migrations.AddField(model_name="appsettings",name="logo",field=models.ImageField(blank=True,null=True,upload_to="organisation/",verbose_name="Logo")),
        migrations.AddField(model_name="dashboardpreference",name="show_attendance_trend",field=models.BooleanField(default=True,verbose_name="Anwesenheitsentwicklung")),
        migrations.AddField(model_name="dashboardpreference",name="show_favorite_links",field=models.BooleanField(default=True,verbose_name="Favoriten")),
        migrations.AddField(model_name="dashboardpreference",name="widget_order",field=models.JSONField(blank=True,default=list,verbose_name="Widget-Reihenfolge")),
    ]
