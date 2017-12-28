"""
Definition of forms.
"""

from django import forms
from django.utils.translation import ugettext_lazy as _
from django.forms import ModelForm

from app.models import *

# create a search form by CTS Kiosk ID
class searchKioskIDForm(forms.Form):
    ctsKioskID = forms.CharField(label='CTS Kiosk ID')
    ctsKioskID.widget.attrs.update({'autofocus':'autofocus', 'placeholder':'AA-###'})

# create a search form by job number
class searchJobNumberForm(forms.Form):
    jobNumber = forms.CharField(label='Job Number')
    jobNumber.widget.attrs.update({'autofocus':'autofocus', 'placeholder':'######'})

# create a search form by a specific peripheral
class searchPeripheralForm(forms.Form):
    peripheralType = forms.ModelChoiceField(label='Peripheral', queryset=Equip.objects.all().order_by('kiosk_component', 'make', 'model'))

# create an input form to update the notes for each kiosk
class updateKioskNotesForm(forms.Form):
    notes = forms.CharField(widget=forms.Textarea(attrs={'class':'form-control', 'rows':5}), required=False)

# create a search form for a range of CTS Kiosk IDs
class retrofitKioskForm(forms.Form):
    retroNumber = forms.CharField(label='Retrofit Job Number')
    startKiosk = forms.CharField(label='CTS Kiosk ID')
    endKiosk = forms.CharField(label='through', required=False)
    retroNumber.widget.attrs.update({'autofocus':'autofocus', 'placeholder':'######'})
    startKiosk.widget.attrs.update({'placeholder':'AA-###'})
    endKiosk.widget.attrs.update({'placeholder':'AA-### or Leave Blank'})

# create a selection form for retrofit requests
class retrofitTypeForm(forms.Form):
    searchChoices = (('add', 'Add Peripheral'), ('replace', 'Replace Peripheral'), ('remove', 'Remove Peripheral'))
    changeType = forms.ChoiceField(label='Change Request Type', widget=forms.RadioSelect, choices=searchChoices)

# create an input form to get information to create a new production release
class newProdRlseForm(forms.Form):
    client = forms.ModelChoiceField(label='Client Name', queryset=Client.objects.all(), widget=forms.Select(attrs={'autofocus':'autofocus'}))
    kiosk_type = forms.ModelChoiceField(label='Kiosk Model', queryset=KioskType.objects.all())
    quantity = forms.IntegerField(label='Number of Kiosks', min_value=1, widget=forms.NumberInput(attrs={'placeholder':'###'}))
    sales_rep = forms.CharField(label='Sales Rep', widget=forms.TextInput(attrs={'placeholder':'Sandy Nix'}))
    po_number = forms.CharField(label='PO Number', widget=forms.TextInput(attrs={'placeholder':'481756'}), required=False)
    invoice_number = forms.CharField(label='Invoice Number', widget=forms.TextInput(attrs={'placeholder':'847512'}), required=False)
    release_date = forms.DateField(label='Release Date', widget=forms.TextInput(attrs={'type':'date'}), required=False)
    ship_date = forms.DateField(label='Ship Date', widget=forms.TextInput(attrs={'type':'date'}), required=False)
    go_live_date = forms.DateField(label='Go-Live Date', widget=forms.TextInput(attrs={'type':'date'}), required=False)
    image_support_fee = forms.ChoiceField(label='Image Support Fee', widget=forms.RadioSelect, choices=(('Yes', 'Yes'),('No','No')))
    it_contact = forms.CharField(label='IT Contact Name', widget=forms.TextInput(attrs={'placeholder':'Eric Truss'}), required=False)
    it_email = forms.EmailField(label='IT Email Address', widget=forms.EmailInput(attrs={'placeholder':'etruss@connectedts.com'}), required=False)
    it_phone = forms.CharField(label='IT Phone Number', widget=forms.TextInput(attrs={'placeholder':'800-372-5771'}), required=False)

# create an input form to update information for an existing production release; initial data is populated in form by the calling view function
class updateProdRlseForm(forms.Form):
    sales_rep = forms.CharField(label='Sales Rep', widget=forms.TextInput(attrs={'placeholder':'Sandy Nix'}))
    po_number = forms.CharField(label='PO Number', widget=forms.TextInput(attrs={'placeholder':'481756'}), required=False)
    invoice_number = forms.CharField(label='Invoice Number', widget=forms.TextInput(attrs={'placeholder':'847512'}), required=False)
    release_date = forms.DateField(label='Release Date', widget=forms.TextInput(attrs={'type':'date'}), required=False)
    ship_date = forms.DateField(label='Ship Date', widget=forms.TextInput(attrs={'type':'date'}), required=False)
    go_live_date = forms.DateField(label='Go-Live Date', widget=forms.TextInput(attrs={'type':'date'}), required=False)
    image_support_fee = forms.ChoiceField(label='Image Support Fee', widget=forms.RadioSelect, choices=(('Yes', 'Yes'),('No','No')))
    it_contact = forms.CharField(label='IT Contact Name', widget=forms.TextInput(attrs={'placeholder':'Eric Truss'}), required=False)
    it_email = forms.EmailField(label='IT Email Address', widget=forms.EmailInput(attrs={'placeholder':'etruss@connectedts.com'}), required=False)
    it_phone = forms.CharField(label='IT Phone Number', widget=forms.TextInput(attrs={'placeholder':'800-372-5771'}), required=False)

# create a Model form to add new clients to the database
class newClient_clientForm(ModelForm):
    class Meta:
        model = Client
        fields = ['name', 'code', 'notes']
        widgets = {'notes': forms.Textarea(attrs={'rows':5})}

# create a Model form to add new contacts to a client
class newContact_clientContactForm(ModelForm):
    class Meta:
        model = ClientContact
        fields = ['first_name','last_name', 'email', 'phone', 'title']

# create a Model form to add new kiosk to the database
class newMTKioskForm(ModelForm):
    quantity = forms.IntegerField(label='Number of Kiosks', min_value=1, widget=forms.NumberInput(attrs={'placeholder':'###'}))

    class Meta:
        model = ClientKiosk
        fields = ['client', 'kiosk_type', 'job_number', 'quantity', 'notes']
        widgets = {'notes': forms.Textarea(attrs={'rows':5})}

# create a Model form to add new equipment to the database
class newEquipForm(ModelForm):
    kioskTypes = forms.ModelMultipleChoiceField(queryset = KioskType.objects.filter(exp_date=None).order_by('cts_division', 'kiosk_type'),
                                                widget = forms.CheckboxSelectMultiple(),
                                                label='Select all the Kiosk Models this applies to:',)

    class Meta:
        model = Equip
        fields = ['kiosk_component', 'make', 'model', 'cts_part_number', 'manf_part_number', 'equip_descript', 'kioskTypes']
        widgets = {'kiosk_component': forms.Select(attrs={'autofocus':'autofocus'}),
                   'make': forms.TextInput(attrs={'placeholder':'Elo'}),
                   'model': forms.TextInput(attrs={'placeholder':'1939L'}),
                   'cts_part_number': forms.TextInput(attrs={'placeholder':'CTS1939'}),
                   'manf_part_number': forms.TextInput(attrs={'placeholder':'E328497'}),
                   'equip_descript': forms.Textarea(attrs={'placeholder':'Elo 19" Surface Acoustic Wave Touchscreen', 'rows':5})}

# create a Model form to add new subequip to a piece of equipment
class newSubequipForm(ModelForm):
    equipment = forms.ModelMultipleChoiceField(queryset = Equip.objects.filter(exp_date=None).order_by('kiosk_component', 'make', 'model'),
                                                widget = forms.CheckboxSelectMultiple(),
                                                label='Select all the Equipment this applies to:',)
    equipIncluded = forms.ModelMultipleChoiceField(queryset = Equip.objects.filter(exp_date=None).order_by('kiosk_component', 'make', 'model'),
                                                widget = forms.CheckboxSelectMultiple(),
                                                label='Select all the Equipment where this is included in the packaging:',
                                                required=False,)
    DISPLAY_CHOICES = [('dropdown', 'Dropdown Menu'), ('checkbox', 'Checkbox Select'), ('text', 'Text Field')]
    subequipDisplay = forms.ChoiceField(choices=DISPLAY_CHOICES, widget=forms.RadioSelect(), label='Display Field Type')

    class Meta:
        model = Subequip
        fields = ['name', 'subequip_group', 'subequipDisplay', 'cts_part_number', 'manf_part_number', 'subequip_descript']
        widgets = {'name': forms.TextInput(attrs={'autofocus':'autofocus','placeholder':'USB Cable'}),
                   'cts_part_number': forms.TextInput(attrs={'placeholder':'CTS6037'}),
                   'manf_part_number': forms.TextInput(attrs={'placeholder':'E005277'}),
                   'subequip_descript': forms.Textarea(attrs={'placeholder':'USB cable with A-B (male to male) connection','rows':5})}

# create a Model form to add new subequipment groups to existing subequipment
class newSubequipGroupForm(ModelForm):
    class Meta:
        model = SubequipGroup
        fields = ['name', 'group_descript']
        widgets = {'name': forms.TextInput(attrs={'autofocus':'autofocus','placeholder':'EMV Interface'}),
                   'group_descript': forms.Textarea(attrs={'placeholder':'Communication interface used on EMV devices', 'rows':5})}

# create a Model form to add new Kiosk components to the database
class newKioskComponentForm(ModelForm):
    kioskTypes = forms.ModelMultipleChoiceField(queryset = KioskType.objects.filter(exp_date=None).order_by('cts_division', 'kiosk_type'),
                                                widget = forms.CheckboxSelectMultiple(),
                                                label='Select all the Kiosk Models this applies to:',)
    DISPLAY_CHOICES = [('dropdown', 'Dropdown Menu'), ('checkbox', 'Checkbox Select')]#, ('text', 'Text Field')]
    compDisplay = forms.ChoiceField(choices=DISPLAY_CHOICES, widget=forms.RadioSelect(), initial='dropdown', label='Display Field Type')

    class Meta:
        model = KioskComponent
        fields = ['prod_rlse_group', 'name', 'compDisplay', 'comp_descript', 'kioskTypes']
        widgets = {'prod_rlse_group': forms.Select(attrs={'autofocus':'autofocus'}),
                   'name': forms.TextInput(attrs={'placeholder':'Touchscreen'}),
                   'comp_descript': forms.Textarea(attrs={'placeholder':'Touchscreen category for all types of touchscreens offered', 'rows':5})}

# create a Model form to add new Production Release Groups to the database
class newProdGroupForm(ModelForm):
    kioskTypes = forms.ModelMultipleChoiceField(queryset = KioskType.objects.filter(exp_date=None).order_by('cts_division', 'kiosk_type'),
                                                widget = forms.CheckboxSelectMultiple(),
                                                label='Select all the Kiosk Models this applies to:',)

    class Meta:
        model = ProdRlseGroup
        fields = ['name', 'prod_descript', 'kioskTypes']
        widgets = {'name': forms.TextInput(attrs={'autofocus':'autofocus','placeholder':'Equipment Configuration'}),
                   'prod_descript': forms.Textarea(attrs={'placeholder':'Equipment Configuration section on production release form; features kiosk components related to hardware','rows':5})}

# create a Model form to add new kiosk modesl to the database
class newKioskTypeForm(ModelForm):
    class Meta:
        model = KioskType
        fields = ['kiosk_type', 'cts_division']
        widgets = {'kiosk_type': forms.TextInput(attrs={'autofocus':'autofocus','placeholder':'PPE'}),
                   'cts_division': forms.TextInput(attrs={'placeholder':'CTS Healthcare'})}

# create a Model form to add equipment restrictions to existing kiosk equipment
class newEquipRestrictionForm(ModelForm):
    class Meta:
        model = EquipRestriction
        fields = ['primaryEquip', 'secondaryEquip']
        widgets = {'primaryEquip': forms.Select(attrs={'autofocus':'autofocus'})}