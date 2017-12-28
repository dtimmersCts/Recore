"""
Definition of tables
"""

import django_tables2 as tables

from app.forms import *
from app.models import *

# create table from ClientKiosk model
class ClientKioskTable(tables.Table):
    # create two custome columns of hyperlinks to redirect to edit/view pages for kiosk
    viewKiosk = tables.TemplateColumn('<a href="/searchRecoreResults?ctsKioskID={{ record.cts_kiosk_id }}">View Kiosk</a>', verbose_name='View Kiosk')
    editKiosk = tables.TemplateColumn('<a href="/updateKiosk?ctsKioskID={{ record.cts_kiosk_id }}">Edit Kiosk</a>', verbose_name='Edit Kiosk')

    # use Meta class; ClientKiosk model; exclude 'id' model field; add custom columns; specify django_tables2 CSS table attrs
    class Meta:
        model = ClientKiosk
        exclude = {'id'}
        sequence = ('viewKiosk','editKiosk','...')
        attrs = {'class':'paleblue'}

# create table from ClientKioskEquip model
class ClientKioskEquipTable(tables.Table):
    # use Meta class; ClientKioskEquip model; exclude 'id' and 'client_kiosk' model fields; specify django_tables2 CSS table attrs
    class Meta:
        model = ClientKioskEquip
        exclude = {'id', 'client_kiosk'}
        attrs = {'class':'paleblue'}

# create table from ClientContact model
class ClientContactTable(tables.Table):
    # use Meta class; ClientContact model; exclude 'id' and 'client' model fields; specify django_tables2 CSS table attrs
    class Meta:
        model = ClientContact
        exclude = {'id', 'client'}
        attrs = {'class':'paleblue'}

# create table from EquipSubequip model
class EquipSubequipTable(tables.Table):
    # use Mega class; EquipSubequip model; exlude 'id', 'eff_date', and 'exp_date' model fields; specify django_tables2 CSS table attrs
    class Meta:
        model = EquipSubequip
        exclude = {'id', 'eff_date', 'exp_date'}
        attrs = {'class':'paleblue'}

# create table from the Equip model
class EquipTable(tables.Table):
    # use Meta class; Equip model; exlude 'id' and 'make_model'; specify django_tables2 CSS table attrs
    class Meta:
        model = Equip
        exclude = {'id', 'make_model'}
        sequence = ('make','model','kiosk_component','...')
        attrs = {'class':'paleblue'}

# create table from the Subequip model
class SubequipTable(tables.Table):
    # use Meta class; Subequip model; exlude 'id'; specify django_tables2 CSS table attrs
    class Meta:
        model = Subequip
        exclude = {'id'}
        sequence = ('name', 'cts_part_number', 'manf_part_number', 'subequip_group', 'display_type', '...')
        orderable = False
        attrs = {'class':'paleblue'}

# create table from the Subequip model; specifically for Production Release subequipment view
class SubequipPRTable(tables.Table):
    # use Meta class; Subequip model; exlude 'id', 'subequip_group', and 'display_type' model fields; specify django_tables2 CSS table attrs
    class Meta:
        model = Subequip
        exclude = {'id', 'subequip_group', 'display_type'}
        sequence = ('name', 'cts_part_number', 'manf_part_number', '...')
        orderable = False
        attrs = {'class':'paleblue'}

# create table from SubequipGroup model
class SubequipGroupTable(tables.Table):
    # use Meta class; SubequipGroup model; exlude 'id'; specify django_tables2 CSS table attrs
    class Meta:
        model = SubequipGroup
        exclude = {'id'}
        attrs = {'class':'paleblue'}

# create table from the KioskComponent model
class KioskComponentTable(tables.Table):
    # use Meta class; KioskComponent model; exlude 'id'; specify django_tables2 CSS table attrs
    class Meta:
        model = KioskComponent
        exclude = {'id'}
        sequence = ('name', 'prod_rlse_group', '...')
        attrs = {'class':'paleblue'}

# create table from the ProdRlseGroupTable model
class ProdRlseGroupTable(tables.Table):
    # use Meta class; ProdRlseGroup model; exlude 'id'; specify django_tables2 CSS table attrs
    class Meta:
        model = ProdRlseGroup
        exclude = {'id'}
        attrs = {'class':'paleblue'}

# create table from the KioskType model
class KioskTypeTable(tables.Table):
    # use Meta class; KioskType model; exlude 'id'; specify django_tables2 CSS table attrs
    class Meta:
        model = KioskType
        exclude = {'id'}
        attrs = {'class':'paleblue'}

# create table from the EquipRestrictionTable model
class EquipRestrictionTable(tables.Table):
    # use Meta class; EquipRestriction model; exlude 'id'; specify django_tables2 CSS table attrs
    class Meta:
        model = EquipRestriction
        exclude = {'id'}
        attrs = {'class':'paleblue'}