# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desired behavior.
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from __future__ import unicode_literals
from django.db import models

# create Client table; attributes to store client information
class Client(models.Model):
    name = models.CharField(unique=True, db_index=True, max_length=80)
    code = models.CharField(max_length=5, verbose_name='CTS Kiosk Code')
    notes = models.TextField(max_length=300, blank=True, null=True)

    # Meta class for Client table
    class Meta:
        db_table = 'Client'

    # return Client name instead of Client id
    def __str__(self):
        return self.name

# create ClientContact table; attributes to store contact information
class ClientContact(models.Model):
    client = models.ForeignKey(Client, db_index=True, db_column='Client_id')  # Field name made lowercase.
    first_name = models.CharField(max_length=30, verbose_name='First Name')
    last_name = models.CharField(max_length=30, verbose_name='Last Name')
    email = models.CharField(max_length=80)
    phone = models.CharField(max_length=12)
    title = models.CharField(max_length=80)
    eff_date = models.DateField(null=True, verbose_name='Effective Date')
    exp_date = models.DateField(null=True, verbose_name='Expiration Date')

    # Meta class for ClientContact table
    class Meta:        
        db_table = 'Client_Contact'

# create KioskType table; attributes to store the kiosk model and information
class KioskType(models.Model):
    kiosk_type = models.CharField(unique=True, db_index=True, max_length=50, verbose_name='Kiosk Model')
    cts_division = models.CharField(max_length=30, verbose_name='CTS Division')
    eff_date = models.DateField(null=True, verbose_name='Effective Date')
    exp_date = models.DateField(null=True, verbose_name='Expiration Date')

    # Meta class for KioskType table
    class Meta:
        db_table = 'Kiosk_Type'

    # return KioskType model instead of KioskType id
    def __str__(self):
        return self.kiosk_type

# create ClientKiosk table; attributes to store kiosk information
class ClientKiosk(models.Model):
    client = models.ForeignKey(Client, db_index=True, db_column='Client_id')  # Field name made lowercase.
    kiosk_type = models.ForeignKey(KioskType, db_index=True, db_column='Kiosk_Type_id', verbose_name='Kiosk Model')
    cts_kiosk_id = models.CharField(unique=True, db_index=True, max_length=12, verbose_name='CTS Kiosk ID')
    job_number = models.CharField(max_length=10, verbose_name='Job Number')
    notes = models.TextField(max_length=300, blank=True, null=True)
    eff_date = models.DateField(null=True, verbose_name='Effective Date')
    exp_date = models.DateField(null=True, verbose_name='Expiration Date')

    # Meta class for ClientKiosk table
    class Meta:        
        db_table = 'Client_Kiosk'

    # return ClientKiosk CTS kiosk id instead of ClientKiosk id
    def __str__(self):
        return self.cts_kiosk_id

# create ProdRlseGroup table; attributes store label information for Production Release From
class ProdRlseGroup(models.Model):
    name = models.CharField(max_length=80, unique=True, db_index=True)
    prod_descript = models.TextField(max_length=300, verbose_name='Description')
    eff_date = models.DateField(null=True, verbose_name='Effective Date')
    exp_date = models.DateField(null=True, verbose_name='Expiration Date')

    # Meta class for ProdRlseGroup table
    class Meta:
        db_table = 'Prod_Rlse_Group'

    # return ProdRlseGroup name instead of id
    def __str__(self):
        return self.name

# create KioskComponent table; attributes to store information about each type of equipment
class KioskComponent(models.Model):
    prod_rlse_group = models.ForeignKey(ProdRlseGroup, db_index=True, db_column='Prod_Rlse_Group_id', verbose_name='Production Release Group') # Field name made lowercase.
    name = models.CharField(max_length=80, unique=True, db_index=True)
    comp_descript = models.TextField(max_length=300, verbose_name='Description')
    display_type = models.CharField(max_length=20, blank=True, null=True, verbose_name='Display Field Type')
    eff_date = models.DateField(null=True, verbose_name='Effective Date')
    exp_date = models.DateField(null=True, verbose_name='Expiration Date')

    # Meta class for KioskComponent table
    class Meta:        
        db_table = 'Kiosk_Component'
        unique_together = (('prod_rlse_group', 'name'),)

    # return KioskComponent name instead of KioskComponent id
    def __str__(self):
        return self.name

# create SubequipGroup table; attributes to identify subequipment groups
class SubequipGroup(models.Model):
    name = models.CharField(max_length=80, unique=True, db_index=True)
    group_descript = models.TextField(max_length=300, verbose_name='Description')
    eff_date = models.DateField(null=True, verbose_name='Effective Date')
    exp_date = models.DateField(null=True, verbose_name='Expiration Date')

    # Meta class for SubequipGroup table
    class Meta:
        db_table = 'Subequip_Group'

    # return SubequipGroup name instead of SubequipGroup id
    def __str__(self):
        return self.name

# create Equip table; attributes to store information for each piece of equipment
class Equip(models.Model):
    kiosk_component = models.ForeignKey(KioskComponent, db_index=True, db_column='Kiosk_Component_id', verbose_name='Kiosk Component')  # Field name made lowercase.
    make = models.CharField(max_length=30)
    model = models.CharField(max_length=30)
    make_model = models.CharField(max_length=60, db_index=True, verbose_name='Make Model')
    cts_part_number = models.CharField(max_length=50, blank=True, null=True, verbose_name='CTS Part Number')
    manf_part_number = models.CharField(max_length=50, blank=True, null=True, verbose_name='Manufacturer Part Number')
    equip_descript = models.TextField(max_length=300, verbose_name='Description')
    eff_date = models.DateField(null=True, verbose_name='Effective Date')
    exp_date = models.DateField(null=True, verbose_name='Expiration Date')

    # Meta class for Equip table; create composite key for each Equip
    class Meta:        
        db_table = 'Equip'
        unique_together = (('kiosk_component', 'make', 'model'),)
        ordering = ['make', 'model']

    # return Equip make and model instead of ComponentEquip id
    def __str__(self):
        return self.make_model

# create Subequip table; attributes to store information for subequipment for each equipment attribute
class Subequip(models.Model):
    subequip_group = models.ForeignKey(SubequipGroup, db_index=True, blank=True, null=True, db_column='Subequip_Group_id', verbose_name='Subequipment Group')
    name = models.CharField(unique=True, db_index=True, max_length=80)
    cts_part_number = models.CharField(max_length=50, blank=True, null=True, verbose_name='CTS Part Number')
    manf_part_number = models.CharField(max_length=50, blank=True, null=True, verbose_name='Manufacturer Part Number')
    subequip_descript = models.TextField(max_length=300, verbose_name='Description')
    display_type = models.CharField(max_length=20, blank=True, null=True, verbose_name='Display Field Type')
    eff_date = models.DateField(null=True, verbose_name='Effective Date')
    exp_date = models.DateField(null=True, verbose_name='Expiration Date')

    # Meta class for Subequip table; create composite key for each equipment type attribute
    class Meta:        
        db_table = 'Subequip'

    # return Subequip name instead of Subequip id
    def __str__(self):
        return self.name

# create ClientKioskEquip table; attributes to store the information for each piece of kiosk equipment
class ClientKioskEquip(models.Model):
    client_kiosk = models.ForeignKey(ClientKiosk, db_index=True, db_column='Client_Kiosk_id')  # Field name made lowercase.
    equip = models.ForeignKey(Equip, db_column='Equip_id')  # Field name made lowercase.
    serial_number = models.CharField(max_length=50, blank=True, null=True, verbose_name='Serial Number')
    prod_rlse_rev = models.CharField(max_length=5, blank=True, null=True, verbose_name='Production Release Revision')
    retrofit_job_number = models.CharField(max_length=10, blank=True, null=True, verbose_name='Retrofit Job Number')
    eff_date = models.DateField(null=True, verbose_name='Effective Date')
    exp_date = models.DateField(null=True, verbose_name='Expiration Date')

    # Meta class for ClientKioskEquip table; create composite key for each specific piece of equipment
    class Meta:        
        db_table = 'Client_Kiosk_Equip'
        #unique_together = (('client_kiosk', 'equip', 'serial_number', 'prod_rlse_rev'),)

# create ClientKioskSubequip table; attributes to store the information for each specific subequip attribute for each piece of equipment
class ClientKioskSubequip(models.Model):
    client_kiosk_equip = models.ForeignKey(ClientKioskEquip, db_index=True, db_column='Client_Kiosk_Equip_id')  # Field name made lowercase.
    subequip = models.ForeignKey(Subequip, db_column='Subequip_id', verbose_name='Subequipment')  # Field name made lowercase.
    prod_rlse_rev = models.CharField(max_length=5, blank=True, null=True, verbose_name='Production Release Revision')
    retrofit_job_number = models.CharField(max_length=10, blank=True, null=True, verbose_name='Retrofit Job Number')
    display_text = models.CharField(max_length=50, blank=True, null=True)
    eff_date = models.DateField(null=True, verbose_name='Effective Date')
    exp_date = models.DateField(null=True, verbose_name='Expiration Date')

    # Meta class for ClientKioskSubequip table; create composite key for each specific attribute
    class Meta:        
        db_table = 'Client_Kiosk_Subequip'
        unique_together = (('client_kiosk_equip', 'subequip', 'prod_rlse_rev'),)

# create KioskTypeProdRlse table; attributes to store relationship between Kiosk Type and Production Release Groups
class KioskTypeProdRlse(models.Model):
    kiosk_type = models.ForeignKey(KioskType, db_column='Kiosk_Type_id', verbose_name='Kiosk Model') # Field name made lowercase.
    prod_rlse_group = models.ForeignKey(ProdRlseGroup, db_column='Prod_Rlse_Group_id', verbose_name='Production Release Group') # Field name made lowercase.
    eff_date = models.DateField(null=True, verbose_name='Effective Date')
    exp_date = models.DateField(null=True, verbose_name='Expiration Date')

    # Meta class for KioskTypeProdRlse table
    class Meta:
        db_table = 'Kiosk_Type_Prod_Rlse'

# create KioskTypeComponent table; attributes to store relationship between Kiosk Type and Kiosk Assembly Components
class KioskTypeComponent(models.Model):
    kiosk_type = models.ForeignKey(KioskType, db_column='Kiosk_Type_id', verbose_name='Kiosk Model') # Field name made lowercase.
    kiosk_component = models.ForeignKey(KioskComponent, db_column='Kiosk_Component_id', verbose_name='Kiosk Component') # Field name made lowercase.
    eff_date = models.DateField(null=True, verbose_name='Effective Date')
    exp_date = models.DateField(null=True, verbose_name='Expiration Date')

    # Meta class for KioskTypeComponent table
    class Meta:
        db_table = 'Kiosk_Type_Component'

# create KioskTypeEquip table; attributes to store relationship between Kiosk Type and Kiosk Equipment
class KioskTypeEquip(models.Model):
    kiosk_type = models.ForeignKey(KioskType, db_column='Kiosk_Type_id', verbose_name='Kiosk Model') # Field name made lowercase.
    equip = models.ForeignKey(Equip, db_column='Equip_id', verbose_name='Equipment') # Field name made lowercase.
    subassembly_num = models.CharField(max_length=30, blank=True, null=True, verbose_name='Subassembly Number')
    eff_date = models.DateField(null=True, verbose_name='Effective Date')
    exp_date = models.DateField(null=True, verbose_name='Expiration Date')

    # Meta class for Equip table
    class Meta:
        db_table = 'Kiosk_Type_Equip'

# create EquipSubequip table; attributes to store relationship between Equipment and Subequipment
class EquipSubequip(models.Model):
    equip = models.ForeignKey(Equip, db_index=True, db_column='Equip_id', verbose_name='Equipment') # Field name made lowercase.
    subequip = models.ForeignKey(Subequip, db_column='Subequip_id', verbose_name='Subequipment') # Field name made lowercase.
    subequip_included = models.CharField(max_length=5, blank=True, null=True, verbose_name='Subequipment Included')
    eff_date = models.DateField(null=True, verbose_name='Effective Date')
    exp_date = models.DateField(null=True, verbose_name='Expiration Date')

    # Meta class for EquipSubequip tablez
    class Meta:
        db_table = 'Equip_Subequip'

# create EquipRestriction table; attributes store restricted relationships between two pieces of Equipment
class EquipRestriction(models.Model):
    primaryEquip = models.ForeignKey(Equip, related_name='primary', verbose_name='Primary Equipment') # Field name made lowercase.
    secondaryEquip = models.ForeignKey(Equip, related_name='secondary', verbose_name='Secondary Equipment') # Field name made lowercase.
    eff_date = models.DateField(null=True, verbose_name='Effective Date')
    exp_date = models.DateField(null=True, verbose_name='Expiration Date')

    # Meta class for EquipRestriction table
    class Meta:
        db_table = 'Equip_Restriction'
        unique_together = (('primaryEquip', 'secondaryEquip'),)

# create ProdRlse table; attributes store information for each Production Release created
class ProdRlse(models.Model):
    client = models.ForeignKey(Client, db_index=True, db_column='Client_id')  # Field name made lowercase.
    prod_rlse_rev = models.CharField(max_length=5, blank=True, null=True, verbose_name='Production Release Revision')
    job_number = models.CharField(max_length=10, db_index=True, verbose_name='Job Number')
    sales_rep = models.CharField(max_length=60, verbose_name='Sales Rep')
    kiosk_quantity = models.IntegerField(verbose_name='Quantity')
    kiosk_range = models.CharField(max_length=20, blank=True, null=True, verbose_name='Unit ID(s)')
    po_number = models.CharField(max_length=20, verbose_name='PO Number')
    invoice_number = models.CharField(max_length=20, verbose_name='Invoice Number')
    release_date = models.DateField(null=True, verbose_name='Release Date')
    ship_date = models.DateField(null=True, verbose_name='Ship Date')
    go_live_date = models.DateField(null=True, verbose_name='Go-Live Date')
    image_support_fee = models.CharField(max_length=5, blank=True, null=True, verbose_name='Image Support Fee')
    it_contact = models.CharField(max_length=60, blank=True, null=True, verbose_name='IT Contact')
    it_email = models.CharField(max_length=80, blank=True, null=True, verbose_name='IT Contact Email')
    it_phone = models.CharField(max_length=12, blank=True, null=True, verbose_name='IT Phone Number')
    notes = models.TextField(max_length=300, blank=True, null=True)

    # Meta class for ProdRlse table; create unique composite key
    class Meta:
        db_table = 'Prod_Rlse'
        unique_together = (('job_number', 'prod_rlse_rev'),)

# create Quotes table; attributes to store each quote
class Quotes(models.Model):
    quote = models.TextField(max_length=300)

    # Meta class for Quotes table
    class Meta:
        db_table = 'Quotes'