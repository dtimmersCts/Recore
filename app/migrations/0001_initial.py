# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2017-12-29 15:33
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Client',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(db_index=True, max_length=80, unique=True)),
                ('code', models.CharField(max_length=5, verbose_name='CTS Kiosk Code')),
                ('notes', models.TextField(blank=True, max_length=300, null=True)),
            ],
            options={
                'db_table': 'Client',
            },
        ),
        migrations.CreateModel(
            name='ClientContact',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=30, verbose_name='First Name')),
                ('last_name', models.CharField(max_length=30, verbose_name='Last Name')),
                ('email', models.CharField(max_length=80)),
                ('phone', models.CharField(max_length=12)),
                ('title', models.CharField(max_length=80)),
                ('eff_date', models.DateField(null=True, verbose_name='Effective Date')),
                ('exp_date', models.DateField(null=True, verbose_name='Expiration Date')),
                ('client', models.ForeignKey(db_column='Client_id', on_delete=django.db.models.deletion.CASCADE, to='app.Client')),
            ],
            options={
                'db_table': 'Client_Contact',
            },
        ),
        migrations.CreateModel(
            name='ClientKiosk',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cts_kiosk_id', models.CharField(db_index=True, max_length=12, unique=True, verbose_name='CTS Kiosk ID')),
                ('job_number', models.CharField(max_length=10, verbose_name='Job Number')),
                ('notes', models.TextField(blank=True, max_length=300, null=True)),
                ('eff_date', models.DateField(null=True, verbose_name='Effective Date')),
                ('exp_date', models.DateField(null=True, verbose_name='Expiration Date')),
                ('client', models.ForeignKey(db_column='Client_id', on_delete=django.db.models.deletion.CASCADE, to='app.Client')),
            ],
            options={
                'db_table': 'Client_Kiosk',
            },
        ),
        migrations.CreateModel(
            name='ClientKioskEquip',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('serial_number', models.CharField(blank=True, max_length=50, null=True, verbose_name='Serial Number')),
                ('prod_rlse_rev', models.CharField(blank=True, max_length=5, null=True, verbose_name='Production Release Revision')),
                ('retrofit_job_number', models.CharField(blank=True, max_length=10, null=True, verbose_name='Retrofit Job Number')),
                ('eff_date', models.DateField(null=True, verbose_name='Effective Date')),
                ('exp_date', models.DateField(null=True, verbose_name='Expiration Date')),
                ('client_kiosk', models.ForeignKey(db_column='Client_Kiosk_id', on_delete=django.db.models.deletion.CASCADE, to='app.ClientKiosk')),
            ],
            options={
                'db_table': 'Client_Kiosk_Equip',
            },
        ),
        migrations.CreateModel(
            name='ClientKioskSubequip',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('prod_rlse_rev', models.CharField(blank=True, max_length=5, null=True, verbose_name='Production Release Revision')),
                ('retrofit_job_number', models.CharField(blank=True, max_length=10, null=True, verbose_name='Retrofit Job Number')),
                ('display_text', models.CharField(blank=True, max_length=50, null=True)),
                ('eff_date', models.DateField(null=True, verbose_name='Effective Date')),
                ('exp_date', models.DateField(null=True, verbose_name='Expiration Date')),
                ('client_kiosk_equip', models.ForeignKey(db_column='Client_Kiosk_Equip_id', on_delete=django.db.models.deletion.CASCADE, to='app.ClientKioskEquip')),
            ],
            options={
                'db_table': 'Client_Kiosk_Subequip',
            },
        ),
        migrations.CreateModel(
            name='Equip',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('make', models.CharField(max_length=30)),
                ('model', models.CharField(max_length=30)),
                ('make_model', models.CharField(db_index=True, max_length=60, verbose_name='Make Model')),
                ('cts_part_number', models.CharField(blank=True, max_length=50, null=True, verbose_name='CTS Part Number')),
                ('manf_part_number', models.CharField(blank=True, max_length=50, null=True, verbose_name='Manufacturer Part Number')),
                ('equip_descript', models.TextField(max_length=300, verbose_name='Description')),
                ('eff_date', models.DateField(null=True, verbose_name='Effective Date')),
                ('exp_date', models.DateField(null=True, verbose_name='Expiration Date')),
            ],
            options={
                'db_table': 'Equip',
                'ordering': ['make', 'model'],
            },
        ),
        migrations.CreateModel(
            name='EquipRestriction',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('eff_date', models.DateField(null=True, verbose_name='Effective Date')),
                ('exp_date', models.DateField(null=True, verbose_name='Expiration Date')),
                ('primaryEquip', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='primary', to='app.Equip', verbose_name='Primary Equipment')),
                ('secondaryEquip', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='secondary', to='app.Equip', verbose_name='Secondary Equipment')),
            ],
            options={
                'db_table': 'Equip_Restriction',
            },
        ),
        migrations.CreateModel(
            name='EquipSubequip',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('subequip_included', models.CharField(blank=True, max_length=5, null=True, verbose_name='Subequipment Included')),
                ('eff_date', models.DateField(null=True, verbose_name='Effective Date')),
                ('exp_date', models.DateField(null=True, verbose_name='Expiration Date')),
                ('equip', models.ForeignKey(db_column='Equip_id', on_delete=django.db.models.deletion.CASCADE, to='app.Equip', verbose_name='Equipment')),
            ],
            options={
                'db_table': 'Equip_Subequip',
            },
        ),
        migrations.CreateModel(
            name='KioskComponent',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(db_index=True, max_length=80, unique=True)),
                ('comp_descript', models.TextField(max_length=300, verbose_name='Description')),
                ('display_type', models.CharField(blank=True, max_length=20, null=True, verbose_name='Display Field Type')),
                ('eff_date', models.DateField(null=True, verbose_name='Effective Date')),
                ('exp_date', models.DateField(null=True, verbose_name='Expiration Date')),
            ],
            options={
                'db_table': 'Kiosk_Component',
            },
        ),
        migrations.CreateModel(
            name='KioskType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('kiosk_type', models.CharField(db_index=True, max_length=50, unique=True, verbose_name='Kiosk Model')),
                ('cts_division', models.CharField(max_length=30, verbose_name='CTS Division')),
                ('eff_date', models.DateField(null=True, verbose_name='Effective Date')),
                ('exp_date', models.DateField(null=True, verbose_name='Expiration Date')),
            ],
            options={
                'db_table': 'Kiosk_Type',
            },
        ),
        migrations.CreateModel(
            name='KioskTypeComponent',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('eff_date', models.DateField(null=True, verbose_name='Effective Date')),
                ('exp_date', models.DateField(null=True, verbose_name='Expiration Date')),
                ('kiosk_component', models.ForeignKey(db_column='Kiosk_Component_id', on_delete=django.db.models.deletion.CASCADE, to='app.KioskComponent', verbose_name='Kiosk Component')),
                ('kiosk_type', models.ForeignKey(db_column='Kiosk_Type_id', on_delete=django.db.models.deletion.CASCADE, to='app.KioskType', verbose_name='Kiosk Model')),
            ],
            options={
                'db_table': 'Kiosk_Type_Component',
            },
        ),
        migrations.CreateModel(
            name='KioskTypeEquip',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('subassembly_num', models.CharField(blank=True, max_length=100, null=True, verbose_name='Subassembly Number')),
                ('eff_date', models.DateField(null=True, verbose_name='Effective Date')),
                ('exp_date', models.DateField(null=True, verbose_name='Expiration Date')),
                ('equip', models.ForeignKey(db_column='Equip_id', on_delete=django.db.models.deletion.CASCADE, to='app.Equip', verbose_name='Equipment')),
                ('kiosk_type', models.ForeignKey(db_column='Kiosk_Type_id', on_delete=django.db.models.deletion.CASCADE, to='app.KioskType', verbose_name='Kiosk Model')),
            ],
            options={
                'db_table': 'Kiosk_Type_Equip',
            },
        ),
        migrations.CreateModel(
            name='KioskTypeProdRlse',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('eff_date', models.DateField(null=True, verbose_name='Effective Date')),
                ('exp_date', models.DateField(null=True, verbose_name='Expiration Date')),
                ('kiosk_type', models.ForeignKey(db_column='Kiosk_Type_id', on_delete=django.db.models.deletion.CASCADE, to='app.KioskType', verbose_name='Kiosk Model')),
            ],
            options={
                'db_table': 'Kiosk_Type_Prod_Rlse',
            },
        ),
        migrations.CreateModel(
            name='ProdRlse',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('prod_rlse_rev', models.CharField(blank=True, max_length=5, null=True, verbose_name='Production Release Revision')),
                ('job_number', models.CharField(db_index=True, max_length=10, verbose_name='Job Number')),
                ('sales_rep', models.CharField(max_length=60, verbose_name='Sales Rep')),
                ('kiosk_quantity', models.IntegerField(verbose_name='Quantity')),
                ('kiosk_range', models.CharField(blank=True, max_length=20, null=True, verbose_name='Unit ID(s)')),
                ('po_number', models.CharField(max_length=20, verbose_name='PO Number')),
                ('invoice_number', models.CharField(max_length=20, verbose_name='Invoice Number')),
                ('release_date', models.DateField(null=True, verbose_name='Release Date')),
                ('ship_date', models.DateField(null=True, verbose_name='Ship Date')),
                ('go_live_date', models.DateField(null=True, verbose_name='Go-Live Date')),
                ('image_support_fee', models.CharField(blank=True, max_length=5, null=True, verbose_name='Image Support Fee')),
                ('it_contact', models.CharField(blank=True, max_length=60, null=True, verbose_name='IT Contact')),
                ('it_email', models.CharField(blank=True, max_length=80, null=True, verbose_name='IT Contact Email')),
                ('it_phone', models.CharField(blank=True, max_length=12, null=True, verbose_name='IT Phone Number')),
                ('notes', models.TextField(blank=True, max_length=300, null=True)),
                ('client', models.ForeignKey(db_column='Client_id', on_delete=django.db.models.deletion.CASCADE, to='app.Client')),
            ],
            options={
                'db_table': 'Prod_Rlse',
            },
        ),
        migrations.CreateModel(
            name='ProdRlseGroup',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(db_index=True, max_length=80, unique=True)),
                ('prod_descript', models.TextField(max_length=300, verbose_name='Description')),
                ('eff_date', models.DateField(null=True, verbose_name='Effective Date')),
                ('exp_date', models.DateField(null=True, verbose_name='Expiration Date')),
            ],
            options={
                'db_table': 'Prod_Rlse_Group',
            },
        ),
        migrations.CreateModel(
            name='Quotes',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quote', models.TextField(max_length=300)),
            ],
            options={
                'db_table': 'Quotes',
            },
        ),
        migrations.CreateModel(
            name='Subequip',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(db_index=True, max_length=80, unique=True)),
                ('cts_part_number', models.CharField(blank=True, max_length=50, null=True, verbose_name='CTS Part Number')),
                ('manf_part_number', models.CharField(blank=True, max_length=50, null=True, verbose_name='Manufacturer Part Number')),
                ('subequip_descript', models.TextField(max_length=300, verbose_name='Description')),
                ('display_type', models.CharField(blank=True, max_length=20, null=True, verbose_name='Display Field Type')),
                ('eff_date', models.DateField(null=True, verbose_name='Effective Date')),
                ('exp_date', models.DateField(null=True, verbose_name='Expiration Date')),
            ],
            options={
                'db_table': 'Subequip',
            },
        ),
        migrations.CreateModel(
            name='SubequipGroup',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(db_index=True, max_length=80, unique=True)),
                ('group_descript', models.TextField(max_length=300, verbose_name='Description')),
                ('eff_date', models.DateField(null=True, verbose_name='Effective Date')),
                ('exp_date', models.DateField(null=True, verbose_name='Expiration Date')),
            ],
            options={
                'db_table': 'Subequip_Group',
            },
        ),
        migrations.AddField(
            model_name='subequip',
            name='subequip_group',
            field=models.ForeignKey(blank=True, db_column='Subequip_Group_id', null=True, on_delete=django.db.models.deletion.CASCADE, to='app.SubequipGroup', verbose_name='Subequipment Group'),
        ),
        migrations.AddField(
            model_name='kiosktypeprodrlse',
            name='prod_rlse_group',
            field=models.ForeignKey(db_column='Prod_Rlse_Group_id', on_delete=django.db.models.deletion.CASCADE, to='app.ProdRlseGroup', verbose_name='Production Release Group'),
        ),
        migrations.AddField(
            model_name='kioskcomponent',
            name='prod_rlse_group',
            field=models.ForeignKey(db_column='Prod_Rlse_Group_id', on_delete=django.db.models.deletion.CASCADE, to='app.ProdRlseGroup', verbose_name='Production Release Group'),
        ),
        migrations.AddField(
            model_name='equipsubequip',
            name='subequip',
            field=models.ForeignKey(db_column='Subequip_id', on_delete=django.db.models.deletion.CASCADE, to='app.Subequip', verbose_name='Subequipment'),
        ),
        migrations.AddField(
            model_name='equip',
            name='kiosk_component',
            field=models.ForeignKey(db_column='Kiosk_Component_id', on_delete=django.db.models.deletion.CASCADE, to='app.KioskComponent', verbose_name='Kiosk Component'),
        ),
        migrations.AddField(
            model_name='clientkiosksubequip',
            name='subequip',
            field=models.ForeignKey(db_column='Subequip_id', on_delete=django.db.models.deletion.CASCADE, to='app.Subequip', verbose_name='Subequipment'),
        ),
        migrations.AddField(
            model_name='clientkioskequip',
            name='equip',
            field=models.ForeignKey(db_column='Equip_id', on_delete=django.db.models.deletion.CASCADE, to='app.Equip'),
        ),
        migrations.AddField(
            model_name='clientkiosk',
            name='kiosk_type',
            field=models.ForeignKey(db_column='Kiosk_Type_id', on_delete=django.db.models.deletion.CASCADE, to='app.KioskType', verbose_name='Kiosk Model'),
        ),
        migrations.AlterUniqueTogether(
            name='prodrlse',
            unique_together=set([('job_number', 'prod_rlse_rev')]),
        ),
        migrations.AlterUniqueTogether(
            name='kioskcomponent',
            unique_together=set([('prod_rlse_group', 'name')]),
        ),
        migrations.AlterUniqueTogether(
            name='equiprestriction',
            unique_together=set([('primaryEquip', 'secondaryEquip')]),
        ),
        migrations.AlterUniqueTogether(
            name='equip',
            unique_together=set([('kiosk_component', 'make', 'model')]),
        ),
        migrations.AlterUniqueTogether(
            name='clientkiosksubequip',
            unique_together=set([('client_kiosk_equip', 'subequip', 'prod_rlse_rev')]),
        ),
    ]
