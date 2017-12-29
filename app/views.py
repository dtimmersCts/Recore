"""
Definition of views
"""

# import all other Recore classes
from app.forms import *
from app.models import *
from app.tables import *
from app.charts import *

# import classes for Django response
from django.shortcuts import render, redirect, render_to_response
from django.http import HttpRequest, HttpResponse, Http404
from django.template import RequestContext
from django_tables2 import RequestConfig
from datetime import datetime
from random import randint
from functools import partial
import subprocess
import re

# import social and Django authorization classes for Google SSO
from social_core.utils import setting_name, module_member, get_strategy
from social_core.exceptions import MissingBackend
from social_core.backends.utils import get_backend
from django.contrib.auth import login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required

# import PDF design classes from the ReportLAB PDF generator package
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.units import inch, cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import BaseDocTemplate, SimpleDocTemplate, PageTemplate, Paragraph, Frame, ListFlowable, ListItem, Table, TableStyle
from io import StringIO, BytesIO

# Renders Recore Home page view
@login_required
def home(request):
    """Renders the Home page"""
    
    # query the database for kiosk types and build a list
    kioskTypes = KioskTypeData.get_kioskTypes()
    totalList = []

    # loop through the kiosk type list and get the number of kiosks per kiosk type
    for i in range(len(kioskTypes)):
        tempKiosk = KioskType.objects.get(kiosk_type=kioskTypes[i])
        totalList.append({"name": kioskTypes[i], "y": ClientKiosk.objects.filter(kiosk_type=tempKiosk).count()},)

    # create the variables and assign the values for the pie chart
    chartID = 'chart_ID'
    chart = {"renderTo": 'chart_ID', "type": 'pie',}  
    chartTitle = {"text": 'Kiosk Models'}
    series = [{
            "type": 'pie',
            "name": 'Kiosk',
            "data": totalList
    }]

    # return render view with variables
    return render(
        request,
        'app/index.html',
        {
            'title':'Home',
            'inspiration':inspirationalQuote(),
            'year': datetime.now().year,
            'chartID': chartID,
            'chart': chart,
            'chartTitle': chartTitle, 
            'series': series,
        }
    )

# Renders Search Recore page view
@login_required
def searchRecore(request):
    """Renders the Search Recore page"""
    assert isinstance(request, HttpRequest)

    # return render view with variables
    return render(
        request,
        'app/searchRecore.html',
        {
            'title':'Search Recore',
            'inspiration':inspirationalQuote(),
            'year': datetime.now().year,
            'message':'Choose from the following search options',
        }
    )

# Renders the form used for the Search Recore page view
@login_required
def getSearchForm(request):
    """Renders the Search Recore form page"""
    assert isinstance(request, HttpRequest)

    # get the form type from the GET request
    formType = request.GET.get('formType')
    searchType = "Search by " + formType

    # initialize the possible forms to render
    formOptions = {'CTS Kiosk ID':searchKioskIDForm,
                   'Job Number':searchJobNumberForm,
                   'Peripheral':searchPeripheralForm,
                   }

    # return render view with variables
    return render(
        request,
        'app/searchRecore/getSearchForm.html',
        {
            'searchType':searchType,
            'searchForm':formOptions[formType],
        }
    )

# Renders the Search Recore Results page view
@login_required
def searchRecoreResults(request):
    """Renders the Search Recore Results page"""
    assert isinstance(request, HttpRequest)

    # initialize all the variables for the view
    errorMessage = None
    searchTitle = None
    clientInfo = None
    contactInfo = None
    kioskInfo = None
    equipInfo = None
    kiosksTable = None
    noResultsMessage = None

    # assign the GET request values from the previous view
    ctsKioskID = request.GET.get('ctsKioskID',None)
    jobNumber = request.GET.get('jobNumber',None)
    peripheralType = request.GET.get('peripheralType',None)

    # check for a CTS Kiosk ID search
    if ctsKioskID is not None:
        # run the function to check and correct the CTS Kiosk ID format
        ctsKioskID = checkKioskID(ctsKioskID)

        # try/except to handle an empty return from the database query
        try:
            # query the databases for all the kiosk information
            kioskInfo = ClientKiosk.objects.get(cts_kiosk_id=ctsKioskID)
            equipQuery = ClientKioskEquip.objects.filter(client_kiosk=kioskInfo).order_by('equip__kiosk_component', '-eff_date', 'exp_date')

            # create the table view for the previous kiosk equipment
            equipInfo = ClientKioskEquipTable(equipQuery)
            RequestConfig(request, paginate=False).configure(equipInfo)
            
            # query the database for the client contact information for the kiosk search
            clientInfo = Client.objects.get(name=kioskInfo.client)
            contactQuery = ClientContact.objects.filter(client=kioskInfo.client)
            
            # create the table view for the contact information if it exists
            if contactQuery.exists():
                contactInfo = ClientContactTable(ClientContact.objects.filter(client=kioskInfo.client))
                RequestConfig(request, paginate=False).configure(contactInfo)

            else:
                noResultsMessage = 'There is no contact information for this client'

            # kiosk search message for user
            searchTitle =  'CTS Kiosk ID: ' + ctsKioskID

        # sets a user message if the kiosk does not exist
        except:
            kioskInfo = None
            noResultsMessage = 'This kiosk is not in the database'
        
    # checks for a Job Number search
    elif jobNumber is not None:
        # query the database for all kiosks for the job number
        jobKiosks = ClientKiosk.objects.filter(job_number=jobNumber).prefetch_related('client', 'kiosk_type')

        # creates a table if the query returned results
        if jobKiosks.exists():
            kiosksTable = ClientKioskTable(jobKiosks)
            RequestConfig(request, paginate=False).configure(kiosksTable)
            searchTitle = "Job Number: " + jobNumber

        # creates an error message if the job number does not exist in the database
        else:
            kiosksTable = None
            noResultsMessage = 'This job number is not in the database'

    # checks for a Peripheral Type search
    elif peripheralType is not None:
        # query the database for all kiosks that have the peripheral that is searched
        peripheralSearch = ClientKiosk.objects.filter(clientkioskequip__equip=peripheralType).prefetch_related('client', 'kiosk_type').order_by('client', 'cts_kiosk_id',)

        # creates a table if the query returned results
        if peripheralSearch.exists():
            kiosksTable = ClientKioskTable(peripheralSearch)
            RequestConfig(request, paginate=False).configure(kiosksTable)
            searchTitle = "Peripheral: " + Equip.objects.get(id=peripheralType).make_model

        # creates an error message if the peripheral search returns no kiosks
        else:
            kiosksTable = None
            noResultsMessage = 'There are no kiosks with this peripheral in the database'

    # sets a full page error message to be displayed if the search parameters are not met
    else:
        errorMessage = True

    # return render view with variables
    return render(
        request,
        'app/searchRecore/searchRecoreResults.html',
        {
            'title':'Search Results',
            'inspiration':inspirationalQuote(),
            'year': datetime.now().year,
            'message':'The results of your search are listed below',
            'searchTitle':searchTitle,
            'clientInfo':clientInfo,
            'contactInfo':contactInfo,
            'kioskInfo':kioskInfo,
            'equipInfo':equipInfo,
            'kiosksTable':kiosksTable,
            'errorMessage':errorMessage,
            'noResultsMessage':noResultsMessage
        }
    )

# Renders Client List page view
@login_required
def clientList(request):
    """Renders the Client List page"""
    assert isinstance(request, HttpRequest)

    # return render view with variables; include database query of all clients
    return render(
        request,
        'app/clientList.html',
        {
            'title':'Client List',
            'inspiration':inspirationalQuote(),
            'year': datetime.now().year,
            'message':'Select a Client to view a list of their kiosks',
            'clients': Client.objects.all().order_by('name'),
        }
    )

# Renders Kiosk List page view from client selection
@login_required
def clientKioskList(request, client_id):
    """Renders the Kiosk List page from the Client List page"""
    assert isinstance(request, HttpRequest)

    # query the database from the client selected on the previous page
    clientQuery = ClientKiosk.objects.filter(client=client_id).prefetch_related('client', 'kiosk_type')

    # query the database for the contacts from the current client
    contactQuery = ClientContact.objects.filter(client=client_id)
    
    # creates a table of kiosks if the query returned results
    if clientQuery.exists():
        noResultsMessage = None
        clientTable = ClientKioskTable(clientQuery)
        RequestConfig(request, paginate=False).configure(clientTable)

    else:
        clientTable = None
        noResultsMessage = 'This client does not have any kiosks in the database'

    # creates a table of client contacts if the query returned results
    if contactQuery.exists():
        noContactsMessage = None
        contactTable = ClientContactTable(contactQuery)
        RequestConfig(request, paginate=False).configure(contactTable)

    else:
        contactTable = None
        noContactsMessage = 'This client does not have any contact information available'
    
    # return render view with variables; include client name from GET request
    return render(
        request,
        'app/clientList/clientKioskList.html',
        {
            'title':request.GET.get('clientName',None),
            'inspiration':inspirationalQuote(),
            'year': datetime.now().year,
            'message':'Select a kiosk to view or edit',
            'clientTable':clientTable,
            'contactTable':contactTable,
            'noResultsMessage':noResultsMessage,
            'noContactsMessage':noContactsMessage

        }
    )

# Renders Update Kiosk page view
@login_required
def updateKiosk(request):
    """Renders the Update Kiosk page"""
    assert isinstance(request, HttpRequest)

    # initialize variables for view
    kioskInfo = None
    kioskEquip = None
    kioskSubequip = None
    notesForm = None
    successMessage = None
    noResultsMessage = None

    # checks if the submitted request was a POST
    if request.method == 'POST':
        # initialize variables with information from POST request
        equipName = request.POST.getlist('equipName[]')
        equipSerial = request.POST.getlist('equipSerial[]')
        attrName = request.POST.getlist('attrName[]')
        attrValue = request.POST.getlist('attrValue[]')
        notes = request.POST.get('notes')
        currentKiosk = ClientKiosk.objects.get(kioskequip__id=equipName[0])

        # get notes from current kiosk, save new notes from POST request
        currentKiosk.notes = notes
        currentKiosk.save()

        # loop through all the equipment for the kiosk
        for i in range(len(equipName)):
            # query the database for all information on the current piece of equipment
            currentEquip = ClientKioskEquip.objects.get(id=equipName[i])

            # checks if the serial number from the database is different from the submitted form
            if currentEquip.serial_number != equipSerial[i]:
                # checks if the equipment exists in the database; checks that it is a new entry and not a replacement
                if currentEquip.serial_number != '':
                    # equipment already exists; expire current equipment
                    currentEquip.exp_date = datetime.now()
                    currentEquip.save()

                    # create a new piece of equipment with the same attributes as the expired equipment
                    newEquip = ClientKioskEquip(client_kiosk=currentEquip.client_kiosk, equip=currentEquip.equip, eff_date=datetime.now(), serial_number=equipSerial[i])
                    newEquip.save()

                    # loop through all the attributes for the expired equipment
                    for j in range(len(attrName)):
                        # query the database for all information on the current attribute
                        currentAttr = KioskEquipAttr.objects.get(id=attrName[j])

                        # checks if the attribute belongs to the current piece of equipment
                        if currentAttr.kiosk_equip == currentEquip:
                            # attribute already exists; expire current attribute
                            currentAttr.exp_date = datetime.now()
                            currentAttr.save()

                            # create a new attribute for the new piece of equipment
                            newAttr = KioskEquipAttr(kiosk_equip=newEquip, equip_type_attr=currentAttr.equip_type_attr, code_value=True, eff_date=datetime.now())
                            newAttr.save()

                # if the equipment does not have a serial number in the database
                else:
                    # set the serial number for the current piece of equipment; save to database
                    currentEquip.serial_number = equipSerial[i]
                    currentEquip.eff_date = datetime.now()
                    currentEquip.save()

        # loop through all the attributes for the kiosk
        for i in range(len(attrName)):
            # query the database for all information on the current attribute
            currentAttr = KioskEquipAttr.objects.get(id=attrName[i])

            # checks the attribute value from the from against the database; save new value to database
            if currentAttr.code_value is not attrValue[i]:
                currentAttr.code_value = attrValue[i]
                currentAttr.save()

        # redirect to current view as a GET request; redisplays the new form already completed
        return redirect("/updateKiosk?ctsKiosk=" + currentKiosk.cts_kiosk_id + "&success=True")
    
    # gets the current kiosk ID from the submitted GET request
    currentKiosk = request.GET.get('ctsKioskID',None)
    successKiosk = request.GET.get('success',None)

    # checks for a kiosk ID from the GET request
    if currentKiosk is not None:
        # initialize the form with results from GET request
        searchForm = searchKioskIDForm(request.GET)

        # call function to check CTS Kiosk ID string format
        currentKiosk = checkKioskID(currentKiosk)

        # try/except to handle an empty return from the database query
        try:
            # query database for kiosk information from submitted form
            kioskInfo = ClientKiosk.objects.get(cts_kiosk_id=currentKiosk)
            currentProdRlse = ProdRlse.objects.filter(job_number=kioskInfo.job_number).order_by('-prod_rlse_rev').first()
            kioskEquip = ClientKioskEquip.objects.filter(client_kiosk=kioskInfo, prod_rlse_rev=currentProdRlse.prod_rlse_rev, exp_date__isnull=True).order_by('equip__kiosk_component')

            # creates form for kiosk notes update
            notesForm = updateKioskNotesForm(initial={'notes': kioskInfo.notes})
        
        # creates a display message for user if no results are found
        except:
            kioskInfo = None
            kioskEquip = None
            noResultsMessage = 'This kiosk is not in the database'
        
    # creates a blank search form if the GET request was empty
    else:
        searchForm = searchKioskIDForm

    if successKiosk is not None:
        successMessage = 'This kiosk was successfully updated'

    # return render view with variables
    return render(
        request,
        'app/updateKiosk.html',
        {
            'title':'Update Kiosk',
            'inspiration':inspirationalQuote(),
            'year':datetime.now().year,
            'message':'Enter the CTS Kiosk ID',
            'searchForm':searchForm,
            'kioskInfo':kioskInfo,
            'kioskEquip':kioskEquip,
            'kioskSubequip':kioskSubequip,
            'notesForm':notesForm,
            'successMessage':successMessage,
            'noResultsMessage':noResultsMessage,
        }
    )

# Renders the Production Release page view
@login_required
def productionRelease(request):
    """Renders the Production Release page"""
    assert isinstance(request, HttpRequest)
    
    # get the job number from the GET request
    jobNumber = request.GET.get('jobNumber',None)

    # checks that a job number exists
    if jobNumber is not None:
        # redirect to the existing production release page
        if ProdRlse.objects.filter(job_number=jobNumber).exists():
            return redirect("/existProdRlse?jobNumber=" + jobNumber)

        # redirect to the new production release page
        else:
            return redirect("/newProdRlse?jobNumber=" + jobNumber)

    # initialize the job number search form
    else:
        jobForm = searchJobNumberForm

    # return render view with variables
    return render(
        request,
        'app/productionRelease.html',
        {
            'title':'Production Release',
            'inspiration':inspirationalQuote(),
            'year':datetime.now().year,
            'message':'Enter a new or existing job number',
            'jobForm':jobForm,
        }
    )

# Renders the New Production Release page view
@login_required
def newProdRlse(request):
    """Renders the New Production Release page"""
    assert isinstance(request, HttpRequest)
    
    # handles the POST request from the template
    if request.method == 'POST':
        # get the job number and form from the POST request
        jobNumber = request.POST.get('jobNumber',None)
        prodRlseForm = newProdRlseForm(request.POST)

        # check that all fields in the form have been completed
        if prodRlseForm.is_valid():
            # create a new production release in the database
            ProdRlse.objects.create(client=prodRlseForm.cleaned_data['client'], prod_rlse_rev=0, job_number=jobNumber, sales_rep=prodRlseForm.cleaned_data['sales_rep'], kiosk_quantity=prodRlseForm.cleaned_data['quantity'],
                                    po_number=prodRlseForm.cleaned_data['po_number'], invoice_number=prodRlseForm.cleaned_data['invoice_number'], release_date=prodRlseForm.cleaned_data['release_date'],
                                    ship_date=prodRlseForm.cleaned_data['ship_date'], go_live_date=prodRlseForm.cleaned_data['go_live_date'], image_support_fee=prodRlseForm.cleaned_data['image_support_fee'],
                                    it_contact=prodRlseForm.cleaned_data['it_contact'], it_email=prodRlseForm.cleaned_data['it_email'], it_phone=prodRlseForm.cleaned_data['it_phone'])

            # get the client code from the database; get the last entry for that client
            clientCode = Client.objects.get(name=prodRlseForm.cleaned_data['client'])
            lastKiosk = ClientKiosk.objects.filter(client=prodRlseForm.cleaned_data['client']).prefetch_related('client', 'kiosk_type').order_by('-cts_kiosk_id').first()

            # gets the number of the last kiosk for the client
            if lastKiosk:
                kioskNumber = lastKiosk.cts_kiosk_id.split('-')[1]

            # sets the last kiosk number to zero if no kiosks exist
            else:
                kioskNumber = 0

            # creates a counter for adding multiple kiosks per job number
            counter = int(kioskNumber)
            
            # loop through the number of kiosks entered from the form
            for i in range(prodRlseForm.cleaned_data['quantity']):
                counter += 1
                # create the kiosk ID for each kiosk
                tempKioskID = clientCode.code + '-' + str(counter).zfill(3)

                # create the kiosk object in the database
                ClientKiosk.objects.create(client=prodRlseForm.cleaned_data['client'], kiosk_type=prodRlseForm.cleaned_data['kiosk_type'], cts_kiosk_id=tempKioskID, job_number=jobNumber, eff_date=datetime.now())

            # get the first kiosk created for the new job number
            currentKiosks = ClientKiosk.objects.filter(job_number=jobNumber).order_by('cts_kiosk_id')

            # gets the range of kiosks that were created to be stored with the production release form database object
            if len(currentKiosks) > 1:
                kioskRange = currentKiosks[0].cts_kiosk_id + ' - ' + currentKiosks[len(currentKiosks) - 1].cts_kiosk_id

            else:
                kioskRange = currentKiosks[0].cts_kiosk_id

            # get the current production release form for the job number and save the kiosk range to the object
            currentProdRlse = ProdRlse.objects.filter(job_number=jobNumber).first()
            currentProdRlse.kiosk_range = kioskRange
            currentProdRlse.save()

            # get the production release group, the kiosk components, the equipment, and the kiosk type for the current job number
            prodList = ProdRlseGroup.objects.filter(exp_date=None, kiosktypeprodrlse__kiosk_type=prodRlseForm.cleaned_data['kiosk_type'], kiosktypeprodrlse__exp_date=None)
            compList = list(KioskComponent.objects.filter(exp_date=None, kiosktypecomponent__kiosk_type=prodRlseForm.cleaned_data['kiosk_type'], kiosktypecomponent__exp_date=None))
            equipList = Equip.objects.filter(exp_date=None, kiosktypeequip__kiosk_type=prodRlseForm.cleaned_data['kiosk_type'], kiosktypeequip__exp_date=None, kiosk_component=compList[0])
            kioskType = prodRlseForm.cleaned_data['kiosk_type']
            
            # for each kiosk component; generate the kiosk component that follows to allow the configurator to build restrictions as a production release is built
            for i in range(len(compList)):
                if i == (len(compList) - 1):
                    compList[i].nextComp = None

                else:
                    compList[i].nextComp = compList[i+1].id

    # initialize all variables for the view when a GET request is returned to the view
    else:
        jobNumber = request.GET.get('jobNumber',None)
        prodRlseForm = newProdRlseForm
        prodList = None
        compList = None
        equipList = None
        kioskType = None

    # return render view with variables
    return render(
        request,
        'app/productionRelease/newProdRlse.html',
        {
            'title':'Production Release',
            'inspiration':inspirationalQuote(),
            'year':datetime.now().year,
            'message':'Create a new Production Release for Job Number ' + jobNumber,
            'jobNumber':jobNumber,
            'prodRlseForm':prodRlseForm,
            'prodList':prodList,
            'compList':compList,
            'equipList':equipList,
            'kioskType':kioskType,
        }
    )

# Renders the New Production Release Equipment page view
@login_required
def newProdRlseEquip(request):
    """Renders the New Production Release Equipment page"""
    assert isinstance(request, HttpRequest)

    # get the variables from the GET request
    equipList = request.GET.getlist('equipList',None)
    compList = request.GET.getlist('compList',None)
    currentComp = request.GET.get('nextComp',None)
    kioskType = request.GET.get('kioskType',None)

    # strip the first character from the next component variable
    currentComp = currentComp[1:]

    # remove the 'None' values from the equipment list
    equipList = [value for value in equipList if value != 'None']

    # check that the next component exists
    if currentComp != 'None':
        # get the equipment and restrictions for the next component to be rendered
        getComp = KioskComponent.objects.get(id=currentComp)
        getType = KioskType.objects.get(kiosk_type=kioskType)
        getEquip = Equip.objects.filter(id__in=equipList)
        getRestrictions = EquipRestriction.objects.filter(exp_date=None)

        # get the available equipment for user selection
        equipOptions = list(Equip.objects.filter(exp_date=None, kiosk_component=getComp, kiosktypeequip__kiosk_type=getType, kiosktypeequip__exp_date=None))

        # check the restrictions of the available equipment for the next component
        for equip in getEquip:
            restriction = False

            # check the secondary equipment for a restriction list
            for option in equipOptions:

                # loop through all available restrictions
                for restrict in getRestrictions:
                    # set the restriction flag to True if a restriction is found
                    if ((restrict.primaryEquip == equip) and (restrict.secondaryEquip == option) and (restrict.exp_date == None)) or ((restrict.primaryEquip == option) and (restrict.secondaryEquip == equip) and (restrict.exp_date == None)):
                        restriction = True
                        break

                # remove the equipment from the available equipment list if a restriction is found
                if restriction == True:
                    equipOptions.remove(option)
                    restriction = False

        # assign the next component to the current component list that is generated
        for i in range(len(compList)):
            if int(compList[i]) == getComp.id:
                if i == (len(compList) - 1):
                    nextComp = None

                else:
                    nextComp = compList[i + 1]

        # create the current component kiosk component object to render database information for template
        currentCompObject = KioskComponent.objects.get(id=currentComp)

    # initialize the variables if a GET request is received by the view
    else:
        currentCompObject = None
        nextComp = None
        equipOptions = None

    # return render view with variables
    return render(
        request,
        'app/productionRelease/newProdRlseEquip.html',
        {
            'currentCompObject':currentCompObject,
            'nextComp':nextComp,
            'kioskType':kioskType,
            'equipOptions':equipOptions,
        }
    )

# Renders the Subequipment page view for the selected equipment
@login_required
def getSubEquip(request):
    """Renders the Subequipment page"""
    assert isinstance(request, HttpRequest)

    # initialize variables and assign values from GET request
    currentEquip = request.GET.get('currentEquip',None)
    subEquipDiv = request.GET.get('subEquipDiv',None)
    reqSubTable = None
    subequipChoices = None
    subequipGroups = None
    textSubequip = None
    subEquipDiv = subEquipDiv[1:]

    # check that the current equipment exists
    if currentEquip != 'None':
        # get the current equipment database object
        getEquip = Equip.objects.get(id=currentEquip)
        
        # get the subequipment for the current equipment based on subequipment group, display type, and subequipment that is required by the equipment
        reqSubEquip = Subequip.objects.filter(subequip_group=None, exp_date=None, equipsubequip__equip=getEquip, equipsubequip__exp_date=None).exclude(display_type='text')
        textSubequip = Subequip.objects.filter(exp_date=None, subequip_group=None, display_type='text', equipsubequip__equip=getEquip, equipsubequip__exp_date=None)
        subequipChoices = Subequip.objects.filter(subequip_group__isnull=False, exp_date=None, equipsubequip__equip=getEquip, equipsubequip__exp_date=None)
        subequipGroups = SubequipGroup.objects.filter(exp_date=None, id__in=subequipChoices.values('subequip_group_id'))

        # renders the required subequipment table if it exists
        if reqSubEquip.exists():
            reqSubTable = SubequipPRTable(reqSubEquip)
            RequestConfig(request, paginate=False).configure(reqSubTable)

    # return render view with variables
    return render(
        request,
        'app/productionRelease/getSubEquip.html',
        {
            'subEquipDiv':subEquipDiv,
            'reqSubTable':reqSubTable,
            'subequipChoices':subequipChoices,
            'subequipGroups':subequipGroups,
            'textSubequip':textSubequip,
        }
    )

# Renders the Reset Production Release page view
@login_required
def resetProdRlse(request):
    """Renders the Reset Production Release page"""
    assert isinstance(request, HttpRequest)

    # assign the values from the GET request
    currentDiv = request.GET.get('currentDiv',None)
    currentDiv = currentDiv[1:]

    # return render view with variables
    return render(
        request,
        'app/productionRelease/resetProdRlse.html',
        {
            'currentDiv':currentDiv,
        }
    )

# Renders the Create Production Release view
@login_required
def createProdRlse(request):
    """Renders the Create Production Release view"""
    assert isinstance(request, HttpRequest)

    # assign values from POST request
    jobNumber = request.POST.get('jobNumber',None)
    kioskType = KioskType.objects.get(kiosk_type=request.POST.get('kioskType',None))

    # initialize lists to create the new production release
    equipList = []
    subequipList = []
    equipSubList = []

    # get the kiosks, kiosk components, and subequipment groups to create the production release and all the equipment for each kiosk
    kioskList = ClientKiosk.objects.filter(job_number=jobNumber)
    compList = KioskComponent.objects.filter(kiosktypecomponent__kiosk_type=kioskType)
    subequipGroups = SubequipGroup.objects.filter(exp_date=None)
    
    # loop through all the components in the kiosk component list that are returned to the view from the template
    for comp in compList:
        # get the current equipment from the POST request
        currentEquip = request.POST.get(str(comp.id),None)

        # check the equipment is not 'None' or NULL
        if (currentEquip != 'None' and currentEquip is not None):
            # create a temporary equipment object and append it to an equipment list for new kiosk equipment creation
            tempEquip = Equip.objects.get(id=int(currentEquip))
            equipList.append(tempEquip)

            # get all the subequipment groups related to the current equipment
            allSubequipGroups = list(SubequipGroup.objects.filter(exp_date=None, subequip__exp_date=None, subequip__equipsubequip__exp_date=None, subequip__equipsubequip__equip=tempEquip))
            finalGroups = []

            # check for subequipment groups for the current equipment and append the group to the current equipment if it exists
            for allGroups in allSubequipGroups:
                if allGroups not in finalGroups:
                    finalGroups.append(allGroups)

            # loop through the final list of groups to create subequipment
            for group in finalGroups:
                # check the current div from the template and get the subequipment from the POST request
                subequipDiv = str(group.id) + 'B'
                currentSubequip = request.POST.get(subequipDiv,None)

                # check that the subequipment exists
                if currentSubequip is not None:
                    # create a temporary subequipment object and append it to the subequpment list for kiosk equipment creation
                    tempSubequip = Subequip.objects.get(id=currentSubequip)
                    subequipList.append(tempSubequip)
                    equipSubList.append(tempEquip)

        # get the kiosk component equipment list if the POST request sends the component back as a list and not an individual value
        else:
            tempName = str(comp.id) + '[]'
            currentEquipList = request.POST.getlist(tempName,None)
            
            # check that the current kiosk equipment has an equipment list
            if currentEquipList is not None:
                # loop through all the kiosk equipment in the equipment list
                for equip in currentEquipList:
                    # create a temporary equipment object and append it to a final equipment list for kiosk equipment creation
                    tempEquip = Equip.objects.get(id=int(equip))
                    equipList.append(tempEquip)

                    # check the current equipment for any subequipment that belongs to a subequipment group
                    allSubequipGroups = list(SubequipGroup.objects.filter(exp_date=None, subequip__exp_date=None, subequip__equipsubequip__exp_date=None, subequip__equipsubequip__equip=tempEquip))
                    finalGroups = []

                    # loop through all subequipment groups
                    for allGroups in allSubequipGroups:
                        # check the current equipment subequipment groups against all the subequipment groups
                        if allGroups not in finalGroups:
                            # append the subequipment group to a final subequipment group list for kiosk equipment creation
                            finalGroups.append(allGroups)

                    # loop through all the groups in the final subquipment group list
                    for group in finalGroups:
                        # get the subequipment variable from the template div if it exists
                        subequipDiv = str(group.id) + 'B'
                        currentSubequip = request.POST.get(subequipDiv,None)

                        # if the subequipment exists
                        if currentSubequip is not None:
                            # create a temporary subequipment object and append it to a final subequipment list for kiosk equipment creation
                            tempSubequip = Subequip.objects.get(id=currentSubequip)
                            subequipList.append(tempSubequip)
                            equipSubList.append(tempEquip)
            
    # loop through all the new kiosks to create kiosk equipment and subequipment relations
    for i in range(len(kioskList)):

        # loop through each piece of equipment to create the database entry for that equipment related to the current kiosk
        for j in range(len(equipList)):
            # create the equipment and save it to the database
            newEquip = ClientKioskEquip(client_kiosk=kioskList[i], equip=equipList[j], prod_rlse_rev=0, eff_date=datetime.now())
            newEquip.save()

            # assign the most recent created equipment to a temporary equipment object
            tempEquip = ClientKioskEquip.objects.all().order_by('-id')[0]

            # get the required subequipment for temporary equipment
            reqSubEquip = Subequip.objects.filter(exp_date=None, equipsubequip__equip=tempEquip.equip, equipsubequip__exp_date=None, subequip_group__isnull=True)

            # loop through the required subequipment for the current kiosk equipment
            for k in range(len(reqSubEquip)):
                # get the required subequipment that have display text to store with the subequipment database entry
                if str(reqSubEquip[k].display_type) == 'text':
                    subequipTextDiv = str(reqSubEquip[k].id) + 'C'
                    getSubequipText = request.POST.get(subequipTextDiv,None)

                    # create the subequipment database entry
                    newSubequip = ClientKioskSubequip(client_kiosk_equip=tempEquip, subequip=reqSubEquip[k], prod_rlse_rev=0, eff_date=datetime.now(), display_text=getSubequipText)
                    newSubequip.save()

                # create all subequipment database entries that do not have display text to stroe
                else:
                    newSubequip = ClientKioskSubequip(client_kiosk_equip=tempEquip, subequip=reqSubEquip[k], prod_rlse_rev=0, eff_date=datetime.now())
                    newSubequip.save()

            # loop through all subequipment that belongs to a subequipment group
            for k in range(len(subequipList)):
                # create the subequipment databse entry for grouped subequipment
                if tempEquip.equip == equipSubList[k]:
                    tempSubequip = ClientKioskSubequip(client_kiosk_equip=tempEquip, subequip=subequipList[k], prod_rlse_rev=0, eff_date=datetime.now())
                    tempSubequip.save()

    # returns the user to the existing production release page after the production release, kiosks, equipment, and subequipment have all been created in the databse
    return redirect("/existProdRlse?jobNumber=" + jobNumber)

# Renders the Existing Production Release page view
@login_required
def existProdRlse(request):
    """Renders the Existing Production Release page"""
    assert isinstance(request, HttpRequest)

    # assign the job number from the GET request
    jobNumber = request.GET.get('jobNumber',None)

    # assign the form values from the POST request
    if request.method == 'POST':
        prodRlseForm = updateProdRlseForm(request.POST)
        jobNumber = request.POST.get('jobNumber')

        # query the database for the current production release and kiosk for the job number
        currentProdRlse = ProdRlse.objects.filter(job_number=jobNumber).order_by('-prod_rlse_rev').first()
        currentKiosk = ClientKiosk.objects.filter(job_number=jobNumber).order_by('cts_kiosk_id').first()

        # check that the submitted form values are valid; make changes to the job information for the production release
        if prodRlseForm.is_valid():
            # check the submitted form values against the database values to check for changes
            if ((prodRlseForm.cleaned_data['sales_rep'] != currentProdRlse.sales_rep) or (prodRlseForm.cleaned_data['po_number'] != currentProdRlse.po_number) or (prodRlseForm.cleaned_data['invoice_number'] != currentProdRlse.invoice_number) or
                (prodRlseForm.cleaned_data['release_date'] != currentProdRlse.release_date) or (prodRlseForm.cleaned_data['ship_date'] != currentProdRlse.ship_date) or (prodRlseForm.cleaned_data['go_live_date'] != currentProdRlse.go_live_date) or 
                (prodRlseForm.cleaned_data['image_support_fee'] != currentProdRlse.image_support_fee) or (prodRlseForm.cleaned_data['it_contact'] != currentProdRlse.it_contact) or (prodRlseForm.cleaned_data['it_phone'] != currentProdRlse.it_phone) or 
                (prodRlseForm.cleaned_data['it_email'] != currentProdRlse.it_email)):
                    # increase the production release revision number when a change is found
                    newProdRev = int(currentProdRlse.prod_rlse_rev) + 1
                    # create a new production release revision in the database
                    ProdRlse.objects.create(client=currentProdRlse.client, prod_rlse_rev=str(newProdRev), job_number=currentProdRlse.job_number, sales_rep=prodRlseForm.cleaned_data['sales_rep'], kiosk_quantity=currentProdRlse.kiosk_quantity,
                                    kiosk_range=currentProdRlse.kiosk_range, po_number=prodRlseForm.cleaned_data['po_number'], invoice_number=prodRlseForm.cleaned_data['invoice_number'], release_date=prodRlseForm.cleaned_data['release_date'],
                                    ship_date=prodRlseForm.cleaned_data['ship_date'], go_live_date=prodRlseForm.cleaned_data['go_live_date'], image_support_fee=prodRlseForm.cleaned_data['image_support_fee'],
                                    it_contact=prodRlseForm.cleaned_data['it_contact'], it_email=prodRlseForm.cleaned_data['it_email'], it_phone=prodRlseForm.cleaned_data['it_phone'])

                    # get the new production release, kiosks, and kiosk equipment from the database
                    currentProdRlse = ProdRlse.objects.filter(job_number=jobNumber).order_by('-prod_rlse_rev').first()
                    clientKioskList = ClientKiosk.objects.filter(job_number=currentProdRlse.job_number)
                    clientEquipList = ClientKioskEquip.objects.filter(client_kiosk_id__in=clientKioskList.values('id'))
                    clientSubequipList = ClientKioskSubequip.objects.filter(client_kiosk_equip_id__in=clientEquipList.values('id'))

                    # loop through the kiosks for the current job number
                    for i in range(len(clientKioskList)):
                        # loop through the equipment for each kiosk
                        for j in range(len(clientEquipList)):
                            # check the current equipment against the current kiosk
                            if clientEquipList[j].client_kiosk == clientKioskList[i]:
                                # create an equipment database entry for the new production release revision
                                newEquip = ClientKioskEquip(client_kiosk=clientKioskList[i], equip=clientEquipList[j].equip, prod_rlse_rev=currentProdRlse.prod_rlse_rev, eff_date=datetime.now())
                                newEquip.save()

                                # get the most recently created kiosk equipment
                                tempEquip = ClientKioskEquip.objects.all().order_by('-id')[0]

                                # loop through the subequipment for the equipment that was just created; create a new subequipment database entry for the production release revision
                                for k in range(len(clientSubequipList)):
                                    if clientSubequipList[k].client_kiosk_equip == clientEquipList[j]:
                                        newSubequip = ClientKioskSubequip(client_kiosk_equip=tempEquip, subequip=clientSubequipList[k].subequip, prod_rlse_rev=currentProdRlse.prod_rlse_rev, display_text=clientSubequipList[k].display_text, eff_date=datetime.now())
                                        newSubequip.save()

        # make changes to the equipment set for the current job number
        else:
            # increase the production release revision number; create a new production release database entry for the new revision
            newProdRev = int(currentProdRlse.prod_rlse_rev) + 1
            ProdRlse.objects.create(client=currentProdRlse.client, prod_rlse_rev=str(newProdRev), job_number=currentProdRlse.job_number, sales_rep=currentProdRlse.sales_rep, kiosk_quantity=currentProdRlse.kiosk_quantity,
                            kiosk_range=currentProdRlse.kiosk_range, po_number=currentProdRlse.po_number, invoice_number=currentProdRlse.invoice_number, release_date=currentProdRlse.release_date,
                            ship_date=currentProdRlse.ship_date, go_live_date=currentProdRlse.go_live_date, image_support_fee=currentProdRlse.image_support_fee,
                            it_contact=currentProdRlse.it_contact, it_email=currentProdRlse.it_email, it_phone=currentProdRlse.it_phone)

            # get the newly created production release
            currentProdRlse = ProdRlse.objects.filter(job_number=jobNumber).order_by('-prod_rlse_rev').first()

            # get the kiosk type from the POST request
            kioskType = KioskType.objects.get(kiosk_type=request.POST.get('kioskType',None))

            # initialize empty lists to be used for production release equipment changes
            equipList = []
            subequipList = []
            equipSubList = []

            # get the kiosks, kiosk components, and subequipment groups from databas; used to render template
            kioskList = ClientKiosk.objects.filter(job_number=jobNumber)
            compList = KioskComponent.objects.filter(kiosktypecomponent__kiosk_type=kioskType)
            subequipGroups = SubequipGroup.objects.filter(exp_date=None)
    
            # loop through the kiosk components to get the values from the template
            for comp in compList:
                currentEquip = request.POST.get(str(comp.id),None)

                # check that the equipment value exists; append the equipment to a list for database entry
                if (currentEquip != 'None' and currentEquip is not None):
                    tempEquip = Equip.objects.get(id=int(currentEquip))
                    equipList.append(tempEquip)

                    # get all the subequipment groups from the database to compare to the equipment submitted in the tempalte
                    allSubequipGroups = list(SubequipGroup.objects.filter(exp_date=None, subequip__exp_date=None, subequip__equipsubequip__exp_date=None, subequip__equipsubequip__equip=tempEquip))
                    finalGroups = []

                    # check the subequipment for a group value; if it exists then append the subequipment group to a list for database entry
                    for allGroups in allSubequipGroups:
                        if allGroups not in finalGroups:
                            finalGroups.append(allGroups)

                    # loop through the subequipment groups list to get subequipment values from template
                    for group in finalGroups:
                        # get subequipment DIV values from the POST request
                        subequipDiv = str(group.id) + 'B'
                        currentSubequip = request.POST.get(subequipDiv,None)

                        # check that the subequipment exists from the POST request; append the subequipment to a list for database entry
                        if currentSubequip is not None:
                            tempSubequip = Subequip.objects.get(id=currentSubequip)
                            subequipList.append(tempSubequip)
                            equipSubList.append(tempEquip)

                # get the equipment from the POST request that is passed as a list
                else:
                    tempName = str(comp.id) + '[]'
                    currentEquipList = request.POST.getlist(tempName,None)

                    # check that an equipment list exists from the POST request
                    if currentEquipList is not None:
                        # append the equipment to a list for database entry
                        for equip in currentEquipList:
                            tempEquip = Equip.objects.get(id=int(equip))
                            equipList.append(tempEquip)

                            # get all the subequipment groups for the current equipment
                            allSubequipGroups = list(SubequipGroup.objects.filter(exp_date=None, subequip__exp_date=None, subequip__equipsubequip__exp_date=None, subequip__equipsubequip__equip=tempEquip))
                            finalGroups = []

                            # add the subequipment group to a list for database entry
                            for allGroups in allSubequipGroups:
                                if allGroups not in finalGroups:
                                    finalGroups.append(allGroups)

                            # loop through the subequipment group list
                            for group in finalGroups:
                                # get the subequipment DIV and value from the POST request
                                subequipDiv = str(group.id) + 'B'
                                currentSubequip = request.POST.get(subequipDiv,None)

                                # check that the POST request returned a value from the template; append the subequipment to a list for database entry
                                if currentSubequip is not None:
                                    tempSubequip = Subequip.objects.get(id=currentSubequip)
                                    subequipList.append(tempSubequip)
                                    equipSubList.append(tempEquip)
            
            # loop through all kiosks for the current production release
            for i in range(len(kioskList)):

                # loop through all the equipment for each kiosk
                for j in range(len(equipList)):
                    # create a new equipment database entry for the new production release revision
                    newEquip = ClientKioskEquip(client_kiosk=kioskList[i], equip=equipList[j], prod_rlse_rev=newProdRev, eff_date=datetime.now())
                    newEquip.save()

                    # get the newly created equipment
                    tempEquip = ClientKioskEquip.objects.all().order_by('-id')[0]

                    # get the subequipment required for the current equipment
                    reqSubEquip = Subequip.objects.filter(exp_date=None, equipsubequip__equip=tempEquip.equip, equipsubequip__exp_date=None, subequip_group__isnull=True)

                    # loop through the subequipment for the current equipment
                    for k in range(len(reqSubEquip)):
                        # create new subequipment database entry for display type text and store text value
                        if str(reqSubEquip[k].display_type) == 'text':
                            subequipTextDiv = str(reqSubEquip[k].id) + 'C'
                            getSubequipText = request.POST.get(subequipTextDiv,None)

                            newSubequip = ClientKioskSubequip(client_kiosk_equip=tempEquip, subequip=reqSubEquip[k], prod_rlse_rev=newProdRev, eff_date=datetime.now(), display_text=getSubequipText)
                            newSubequip.save()

                        # create new subequipment databse entry for all other subequipment display types
                        else:
                            newSubequip = ClientKioskSubequip(client_kiosk_equip=tempEquip, subequip=reqSubEquip[k], prod_rlse_rev=newProdRev, eff_date=datetime.now())
                            newSubequip.save()

                    # loop through subequipment that is part of a subequipment group; create subequipment database entry
                    for k in range(len(subequipList)):
                        if tempEquip.equip == equipSubList[k]:
                            tempSubequip = ClientKioskSubequip(client_kiosk_equip=tempEquip, subequip=subequipList[k], prod_rlse_rev=newProdRev, eff_date=datetime.now())
                            tempSubequip.save()

    # get current production release, kiosks, and equipment set
    currentKiosk = ClientKiosk.objects.filter(job_number=jobNumber).order_by('cts_kiosk_id').first()
    currentProdRlse = ProdRlse.objects.filter(job_number=jobNumber).order_by('-prod_rlse_rev').first()
    currentEquip = ClientKioskEquip.objects.filter(client_kiosk=currentKiosk, prod_rlse_rev=currentProdRlse.prod_rlse_rev)

    # get the production release groups and kiosk components for template view render
    prodList = ProdRlseGroup.objects.filter(kiosktypeprodrlse__kiosk_type=currentKiosk.kiosk_type, kiosktypeprodrlse__exp_date=None)
    compList = list(KioskComponent.objects.filter(exp_date=None, kiosktypecomponent__kiosk_type=currentKiosk.kiosk_type, kiosktypecomponent__exp_date=None))
    allProdRlse = ProdRlse.objects.filter(job_number=jobNumber).order_by('-prod_rlse_rev')

    # return render view with variables
    return render(
        request,
        'app/productionRelease/existProdRlse.html',
        {
            'title':'Existing Production Release',
            'inspiration':inspirationalQuote(),
            'year':datetime.now().year,
            'message':'Make changes below to create a new revision for Production Release Job ' + jobNumber,
            'allProdRlse':allProdRlse,
            'currentKiosk':currentKiosk,
            'currentProdRlse':currentProdRlse,
            'currentEquip':currentEquip,
            'prodList':prodList,
            'compList':compList,
        }
    )

# Renders the Edit Production Release Information page view
@login_required
def editProdRlseInfo(request):
    """Renders the Edit Production Release Information page"""
    assert isinstance(request, HttpRequest)

    # get the job number from the GET request
    jobNumber = request.GET.get('jobNumber')
    currentProdRlse = ProdRlse.objects.filter(job_number=jobNumber).order_by('-prod_rlse_rev').first()

    # create the update production release form; loaded with the initial values from the database
    prodRlseForm = updateProdRlseForm(initial={'sales_rep': currentProdRlse.sales_rep,
                                                   'po_number': currentProdRlse.po_number,
                                                   'invoice_number': currentProdRlse.invoice_number,
                                                   'release_date': currentProdRlse.release_date,
                                                   'ship_date': currentProdRlse.ship_date,
                                                   'go_live_date': currentProdRlse.go_live_date,
                                                   'image_support_fee': currentProdRlse.image_support_fee,
                                                   'it_contact': currentProdRlse.it_contact,
                                                   'it_phone': currentProdRlse.it_phone,
                                                   'it_email': currentProdRlse.it_email,})

    # return render view with variables
    return render(
        request,
        'app/productionRelease/editProdRlseInfo.html',
        {
            'jobNumber':jobNumber,
            'prodRlseForm':prodRlseForm,
        }
    )

# Renders the Edit Production Release Equipment page view
@login_required
def editProdRlseEquip(request):
    """Renders the Edit Production Release Equipment page"""
    assert isinstance(request, HttpRequest)

    # get the job number from the GET request
    jobNumber = request.GET.get('jobNumber')

    # query the database for current production release revision and equipment
    currentProdRlse = ProdRlse.objects.filter(job_number=jobNumber).order_by('-prod_rlse_rev').first()
    currentKiosk = ClientKiosk.objects.filter(job_number=jobNumber).first()
    currentEquip = ClientKioskEquip.objects.filter(client_kiosk=currentKiosk, prod_rlse_rev=currentProdRlse.prod_rlse_rev)
    currentSubequip = ClientKioskSubequip.objects.filter(client_kiosk_equip_id__in=currentEquip.values('id'), prod_rlse_rev=currentProdRlse.prod_rlse_rev)

    # query the database for the kiosk equipment, kiosk components, and production release groups
    equipList = Equip.objects.filter(id__in=currentEquip.values('equip_id'))
    compList = KioskComponent.objects.filter(id__in=equipList.values('kiosk_component_id'))
    prodList = ProdRlseGroup.objects.filter(id__in=compList.values('prod_rlse_group_id'))

    # query the database for all kiosk model equipment, components, and production release groups
    fullEquipList = list(Equip.objects.filter(kiosktypeequip__kiosk_type=currentKiosk.kiosk_type, exp_date=None).order_by('kiosk_component'))
    fullCompList = list(KioskComponent.objects.filter(kiosktypecomponent__kiosk_type=currentKiosk.kiosk_type, exp_date=None).order_by('id'))
    fullProdList = ProdRlseGroup.objects.filter(kiosktypeprodrlse__kiosk_type=currentKiosk.kiosk_type, exp_date=None)

    # get all the equipment restrictions available
    getRestrictions = EquipRestriction.objects.filter(exp_date=None)

    # loop through the equipment list at the first level for restriction comparison
    for firstEquip in equipList:
        # reset the restriction flag to false
        restriction = False

        # loop through the equipment list at the second level for restriction comparison
        for secondEquip in fullEquipList:
            # loop through all the available restrictions
            for restrict in getRestrictions:
                # check if a restriction exists between the equipment at the first and second loop level
                if ((restrict.primaryEquip == firstEquip) and (restrict.secondaryEquip == secondEquip) and (restrict.exp_date == None)) or ((restrict.primaryEquip == secondEquip) and (restrict.secondaryEquip == firstEquip) and (restrict.exp_date == None)):
                    # set the restriction flag to true and break the second level loop
                    restriction = True
                    break

            # remove the second level equipment if the restriction flag is true; reset restriction flag
            if restriction == True:
                fullEquipList.remove(secondEquip)
                restriction = False
    
    # loop through the entire component list for the kiosk model and set next kiosk component value; for page rendering
    for i in range(len(fullCompList)):
                if i == (len(fullCompList) - 1):
                    fullCompList[i].nextComp = None

                else:
                    fullCompList[i].nextComp = fullCompList[i+1].id

    # return render view with variables
    return render(
        request,
        'app/productionRelease/editProdRlseEquip.html',
        {
            'currentEquip':currentEquip,
            'currentSubequip':currentSubequip,
            'prodList':prodList,
            'compList':compList,
            'equipList':equipList,
            'fullProdList':fullProdList,
            'fullCompList':fullCompList,
            'fullEquipList':fullEquipList,
            'jobNumber':jobNumber,
            'kioskType':currentKiosk.kiosk_type,
        }
    )

# Renders the Check Existing Equipment Restriction page view
@login_required
def checkExistEquipRestrict(request):
    """Renders the Check Existing Equipment Restriction on page"""
    assert isinstance(request, HttpRequest)

    # get the current equipment from the GET request
    currentEquip = request.GET.get('equip',None)

    # create binary value for variable to be passed to Javascript function
    restrictionsExist = 0

    # check that the equipment exists
    if currentEquip != 'None' and currentEquip is not None:
        equip = Equip.objects.get(id=currentEquip)
        allRestrictions = EquipRestriction.objects.filter(exp_date=None)

        # loop through all restrictions
        for restrict in allRestrictions:
            # check if the current restriction in the loop relates to the current equipment; set binary value to 1 if the relation exists
            if restrict.primaryEquip == equip or restrict.secondaryEquip == equip:
                restrictionsExist = 1
                break

    # return the binary value as an HTTP response to the Javascript function that made the call
    return HttpResponse(int(restrictionsExist))

# Renders the Existing Subequipment page view
@login_required
def existingSubequip(request):
    """Renders the Existing Subequipment on page"""
    assert isinstance(request, HttpRequest)

    # get the current equipment from the GET request
    equipID = request.GET.get('currentEquip')
    # strip the first character from the equipment GET request; first character used for page rendering in previous Javascript function
    equipID = equipID[1:]
    # query database for equipment and subequipment for current equipment
    currentEquip = ClientKioskEquip.objects.get(id=equipID)
    subequipQuery = Subequip.objects.filter(clientkiosksubequip__client_kiosk_equip=currentEquip).exclude(display_type='text').order_by('name')
    subequipText = ClientKioskSubequip.objects.filter(client_kiosk_equip=currentEquip, prod_rlse_rev=currentEquip.prod_rlse_rev, subequip__display_type='text')
    subTable = None

    # check that subequipment exists for the current equipment; call Tables class to render table for display
    if subequipQuery.exists():
        subTable = SubequipPRTable(subequipQuery)
        RequestConfig(request, paginate=False).configure(subTable)

    # return render view with variables
    return render(
        request,
        'app/productionRelease/existingSubequip.html',
        {
            'subTable':subTable,
            'subequipText':subequipText,
            'equipID':equipID,
        }
    )

# Renders the Edit Existing Subequipment page view
@login_required
def editExistSubequip(request):
    """Renders the Edit Existing Subequipment on page"""
    assert isinstance(request, HttpRequest)

    # get the equipment and component from the GET request
    equip = request.GET.get('equip')
    comp = request.GET.get('comp')
    jobNumber = request.GET.get('jobNumber')
    # strip the first character from the GET request; first character is used for page rendering
    comp = comp[1:]

    # check that the equipment exists from the GET request
    if equip != 'None':
        # query the database for the kiosk, kiosk equipment, and subequipment
        currentKiosk = ClientKiosk.objects.filter(job_number=jobNumber).first()
        currentEquip = ClientKioskEquip.objects.filter(client_kiosk=currentKiosk, equip_id=equip).order_by('-prod_rlse_rev').first()
        subequipQuery = ClientKioskSubequip.objects.filter(client_kiosk_equip=currentEquip, prod_rlse_rev=currentEquip.prod_rlse_rev)

        # get the subequipment and subequipment groups from the database; get the subequipment related to the kiosk equipment
        tempSubequipGroup = ClientKioskSubequip.objects.filter(id__in=subequipQuery.values('id'), subequip__subequip_group__isnull=False, display_text__isnull=True)
        subequipGroup = Subequip.objects.filter(id__in=tempSubequipGroup.values('subequip_id'))
        tempSubequipReq = ClientKioskSubequip.objects.filter(id__in=subequipQuery.values('id'), subequip__subequip_group__isnull=True, display_text__isnull=True)
        subequipReq = Subequip.objects.filter(id__in=tempSubequipReq.values('subequip_id'))
        subequipText = ClientKioskSubequip.objects.filter(id__in=subequipQuery.values('id'), display_text__isnull=False)

        # get all the subequipment and subequipment groups from the database
        allSubGroup = SubequipGroup.objects.filter(id__in=subequipGroup.values('subequip_group_id'))
        allSubequipGroup = Subequip.objects.filter(subequip_group__in=allSubGroup.values('id'))

        subTable = None

        # check if the equipment has required subequipment; create table for display if the subequipment exists
        if subequipReq.exists():
            subTable = SubequipPRTable(subequipReq)
            RequestConfig(request, paginate=False).configure(subTable)

    # if the equipment does not exist from the GET request; initialize all variables to None for page render
    else:
        subTable = None
        subequipGroup = None
        subequipText = None
        allSubGroup = None
        allSubequipGroup = None

    # return render view with variables
    return render(
        request,
        'app/productionRelease/editExistSubequip.html',
        {
            'subTable':subTable,
            'subequipGroup':subequipGroup,
            'subequipText':subequipText,
            'allSubGroup':allSubGroup,
            'allSubequipGroup':allSubequipGroup,
            'comp':comp,
        }
    )

# Renders New Kiosk page view
@login_required
def newKiosk(request):
    """Renders the New Kiosk page"""
    assert isinstance(request, HttpRequest)

    # initialize variables for view
    form = newMTKioskForm
    resultsMessage = None
    kioskTable = None
    jobNumber = None
    prodList = None
    compList = None
    equipList = None

    # checks if submitted request was a POST
    if request.method == 'POST':
        # get form information from POST request
        form = newMTKioskForm(request.POST)

        # checks if the submitted form has valid entries
        if form.is_valid():
            # checks to see if the job number submitted by the form already exists in the database
            if ClientKiosk.objects.filter(job_number=form.cleaned_data['job_number']).exists():
                # create an error message for existing job number; query the existing job number; create a table with the kiosks for the existing job number
                resultsMessage = 'This job number already exists in the database with the following kiosks'
                kioskList = ClientKiosk.objects.filter(job_number=form.cleaned_data['job_number']).prefetch_related('client', 'kiosk_type')
                kioskTable = ClientKioskTable(kioskList)
                RequestConfig(request, paginate=False).configure(kioskTable)

            # create the new job number with the submitted information
            else:
                # get the client code from the database; get the last entry for that client
                clientCode = Client.objects.get(name=form.cleaned_data['client'])
                lastKiosk = ClientKiosk.objects.filter(client=form.cleaned_data['client']).prefetch_related('client', 'kiosk_type').order_by('-cts_kiosk_id').first()

                # gets the number of the last kiosk for the client
                if lastKiosk:
                    kioskNumber = lastKiosk.cts_kiosk_id.split('-')[1]

                # sets the last kiosk number to zero if no kiosks exist
                else:
                    kioskNumber = 0

                # creates a counter for adding multiple kiosks per job number
                counter = int(kioskNumber)
            
                # loop through the number of kiosks entered from the form
                for i in range(form.cleaned_data['quantity']):
                    counter += 1
                    # create the kiosk ID for each kiosk
                    tempKioskID = clientCode.code + '-' + str(counter).zfill(3)

                    # copy the form data from the submitted form; do not save to the database
                    newKioskForm = form.save(commit=False)
                    # add the new kiosk ID to the form
                    newKioskForm.cts_kiosk_id = tempKioskID

                    # create the new kiosk object in the database from the form data
                    ClientKiosk.objects.create(client=newKioskForm.client, kiosk_type=newKioskForm.kiosk_type, cts_kiosk_id=tempKioskID, job_number=newKioskForm.job_number, notes=newKioskForm.notes, eff_date=datetime.now())

                # create message for user
                resultsMessage = 'Select the type of kiosk equipment for this job from the list below to continue:'

                # store the job number and create the equipment type list for the user
                jobNumber = form.cleaned_data['job_number']

                # create production release groups, kiosk components, and kiosk equipment for user selection
                prodList = ProdRlseGroup.objects.filter(exp_date=None)
                compList = KioskComponent.objects.filter(exp_date=None)
                equipList = Equip.objects.filter(exp_date=None)

    # return render view with variables
    return render(
        request,
        'app/newKiosk.html',
        {
            'title':'New Kiosk',
            'inspiration':inspirationalQuote(),
            'year':datetime.now().year,
            'message':'Fill out the following form to create a new job and associated kiosks',
            'form':form,
            'resultsMessage':resultsMessage,
            'kioskTable':kioskTable,
            'jobNumber':jobNumber,
            'prodList':prodList,
            'compList':compList,
            'equipList':equipList,
        }
    )

# Renders the MT New Kiosk Equipment page view
@login_required
def newKioskEquip(request):
    """Renders the MT New Kiosk Equipment view"""
    assert isinstance(request, HttpRequest)

    # assign values from POST request
    jobNumber = request.POST.get('jobNumber',None)
    kioskEquip = request.POST.getlist('equip[]',None)

    # get the kiosks and subequipment groups to create all the equipment for each kiosk
    kioskList = ClientKiosk.objects.filter(job_number=jobNumber)
    subequipGroups = SubequipGroup.objects.filter(exp_date=None)
    currentClient = kioskList[0].client

    # initialize lists to create the new equipment
    equipList = []
    subequipList = []
    equipSubList = []

    for equip in kioskEquip:
        # create a temporary equipment object and append it to an equipment list for new kiosk equipment creation
        tempEquip = Equip.objects.get(id=int(equip))
        equipList.append(tempEquip)

        # get all the subequipment groups related to the current equipment
        allSubequipGroups = list(SubequipGroup.objects.filter(exp_date=None, subequip__exp_date=None, subequip__equipsubequip__exp_date=None, subequip__equipsubequip__equip=tempEquip))
        finalGroups = []

        # check for subequipment groups for the current equipment and append the group to the current equipment if it exists
        for allGroups in allSubequipGroups:
            if allGroups not in finalGroups:
                finalGroups.append(allGroups)

        # loop through the final list of groups to create subequipment
        for group in finalGroups:
            # check the current div from the template and get the subequipment from the POST request
            subequipDiv = str(group.id) + 'B'
            currentSubequip = request.POST.get(subequipDiv,None)

            # check that the subequipment exists
            if currentSubequip is not None:
                # create a temporary subequipment object and append it to the subequpment list for kiosk equipment creation
                tempSubequip = Subequip.objects.get(id=currentSubequip)
                subequipList.append(tempSubequip)
                equipSubList.append(tempEquip)
            
    # loop through all the new kiosks to create kiosk equipment and subequipment relations
    for i in range(len(kioskList)):

        # loop through each piece of equipment to create the database entry for that equipment related to the current kiosk
        for j in range(len(equipList)):
            # create the equipment and save it to the database
            newEquip = ClientKioskEquip(client_kiosk=kioskList[i], equip=equipList[j], prod_rlse_rev=0, eff_date=datetime.now())
            newEquip.save()

            # assign the most recent created equipment to a temporary equipment object
            tempEquip = ClientKioskEquip.objects.all().order_by('-id')[0]

            # get the required subequipment for temporary equipment
            reqSubEquip = Subequip.objects.filter(exp_date=None, equipsubequip__equip=tempEquip.equip, equipsubequip__exp_date=None, subequip_group__isnull=True)

            # loop through the required subequipment for the current kiosk equipment
            for k in range(len(reqSubEquip)):
                # get the required subequipment that have display text to store with the subequipment database entry
                if str(reqSubEquip[k].display_type) == 'text':
                    subequipTextDiv = str(reqSubEquip[k].id) + 'C'
                    getSubequipText = request.POST.get(subequipTextDiv,None)

                    # create the subequipment database entry
                    newSubequip = ClientKioskSubequip(client_kiosk_equip=tempEquip, subequip=reqSubEquip[k], prod_rlse_rev=0, eff_date=datetime.now(), display_text=getSubequipText)
                    newSubequip.save()

                # create all subequipment database entries that do not have display text to stroe
                else:
                    newSubequip = ClientKioskSubequip(client_kiosk_equip=tempEquip, subequip=reqSubEquip[k], prod_rlse_rev=0, eff_date=datetime.now())
                    newSubequip.save()

            # loop through all subequipment that belongs to a subequipment group
            for k in range(len(subequipList)):
                # create the subequipment databse entry for grouped subequipment
                if tempEquip.equip == equipSubList[k]:
                    tempSubequip = ClientKioskSubequip(client_kiosk_equip=tempEquip, subequip=subequipList[k], prod_rlse_rev=0, eff_date=datetime.now())
                    tempSubequip.save()

    # returns the user to the existing production release page after the production release, kiosks, equipment, and subequipment have all been created in the database
    return redirect("/clientList/" + str(currentClient.id) + "/?clientName=" + currentClient.name)

# Renders New Client page view
@login_required
def newClient(request):
    """Renders the New Client page"""
    assert isinstance(request, HttpRequest)

    # initialize variables for view
    successMessage = None
    errorMessage = None
    contactForm = None
    currentClient = None

    # checks if the submitted request was a POST
    if request.method == 'POST':
        # get the form information from the POST request
        clientForm = newClient_clientForm(request.POST)
        
        # check that the form information is valid
        if clientForm.is_valid():
            # create an error message if the client name is already being used
            if Client.objects.filter(name=clientForm.cleaned_data['name']):
                errorMessage = 'This client already exists in the database'
            # creates an error message if the client code is already being used
            elif Client.objects.filter(code=clientForm.cleaned_data['code']):
                errorMessage = 'This client code is already in use'
            # all new client checks have passed; create the client in the database
            else:
                # prevents the form from saving on commit; turns the Client Code upper case; saves form data
                hiddenFieldForm = clientForm.save(commit=False)
                hiddenFieldForm.code = clientForm.cleaned_data['code'].upper()
                hiddenFieldForm.save()
                successMessage = 'Client successfully added to the database'
                currentClient = request.POST.get('name')
                
                # create the client contact form
                contactForm = newContact_clientContactForm()

        # set error message for user; generate a new empty form
        else:
            errorMessage = 'That Client and/or Kiosk Code already exists'
            clientForm = newClient_clientForm()

    # create a new client form
    else:
        clientForm = newClient_clientForm()

    # return render view with variables
    return render(
        request,
        'app/newClient.html',
        {
            'title':'New Client',
            'inspiration':inspirationalQuote(),
            'year': datetime.now().year,
            'message':'Enter the name and code to be used for the new client',
            'clientForm':clientForm,
            'errorMessage':errorMessage,
            'successMessage':successMessage,
            'currentClient':currentClient,
            'contactForm':contactForm
        }
    )

# Renders Add Contact page view
@login_required
def newClient_addContact(request):
    """Renders the Add Contact page"""
    assert isinstance(request, HttpRequest)

    # initialize variables for view
    successMessage = None
    errorMessage = None
    contactForm = None
    contactTable = None
    currentClient = None

    # checks if the submitted request was a POST
    if request.method == 'POST':
        # get the form information from the POST request
        contactForm = newContact_clientContactForm(request.POST)

        # check if the submitted form has valid entries
        if contactForm.is_valid():
            # save the form values to a new form but do not save to database; allows hidden fields from user to be updated
            hiddenFieldForm = contactForm.save(commit=False)
            # get the current client from the database; client name from POST request
            currentClient = Client.objects.get(name=request.POST.get('clientName'))

            # create a new object in the database using the input from the POST request form
            ClientContact.objects.create(client=currentClient, first_name=hiddenFieldForm.first_name, last_name=hiddenFieldForm.last_name, email=hiddenFieldForm.email, phone=hiddenFieldForm.phone, title=hiddenFieldForm.title, eff_date=datetime.now())
            successMessage = 'Contact information has been added to the client'

            # create a new contact form for the view
            contactForm = newContact_clientContactForm()

        # create new contact form for view and get the current client name from POST request
        else:
            contactForm = newContact_clientContactForm()
            currentClient = request.POST.get('clientName')

        # query the database for the client contacts
        checkQuery = ClientContact.objects.filter(client=Client.objects.get(name=currentClient)).prefetch_related('client')

        # create a table if the client contact query returned any results
        if checkQuery.exists():
            contactTable = ClientContactTable(checkQuery)
            RequestConfig(request, paginate=False).configure(contactTable)

        # set table to None if query did not return any results
        else:
            contactTable = None

    # create a new contact form for a GET request
    else:
        contactForm = newContact_clientContactForm()
        successMessage = 'Fill the form out to add a new contact'

    # return render view with variables
    return render(
        request,
        'app/newClient/newClient_addContact.html',
        {
            'title':currentClient,
            'inspiration':inspirationalQuote(),
            'year': datetime.now().year,
            'message':'Add another contact for this client',
            'errorMessage':errorMessage,
            'successMessage':successMessage,
            'contactForm':contactForm,
            'contactTable':contactTable,
            'currentClient':currentClient
        }
    )

# Renders Retrofit Kiosk page view
@login_required
def retrofitKiosk(request):
    """Renders the Retrofit Kiosk page"""
    assert isinstance(request, HttpRequest)

    # initialize the forms for the view
    searchForm = retrofitKioskForm
    changeForm = retrofitTypeForm

    # return render view with variables
    return render(
        request,
        'app/retrofitKiosk.html',
        {
            'title':'Retrofit Kiosk',
            'inspiration':inspirationalQuote(),
            'year': datetime.now().year,
            'message':'Fill out the form to create a new retrofit job',
            'searchForm':searchForm,
            'changeForm':changeForm,
        }
    )
    
# Renders Retrofit equipment page view
@login_required
def retrofitEquip(request):
    """Renders the Retrofit Equipment view"""
    assert isinstance(request, HttpRequest)

    # initialize variables for view
    addMessage = None
    changeMessage = None
    noResultsMessage = None
    addEquip = None
    removeEquip = None

    # assign variable values from GET request
    retroNumber = request.GET.get('retroNumber', None)
    startKiosk = request.GET.get('startKiosk', None)
    endKiosk = request.GET.get('endKiosk', None)
    changeType = request.GET.get('changeType', None)
        
    # checks if there is multiple kiosks
    if endKiosk == '':
        endKiosk = None

    # catches an error when the search criteria does not exist
    try:
        # checks if the request has a starting kiosk ID
        if startKiosk:
            # checks user input is appropriate format; corrects the format
            startKiosk = checkKioskID(startKiosk)

            # creates a message for the user
            addMessage = 'kiosk ' + startKiosk

            # gets the kiosks that need to be updated
            currentKiosk = ClientKiosk.objects.get(cts_kiosk_id=startKiosk)

        # checks if the request has an end kiosk ID; indicates multiple kiosks to be altered
        if endKiosk:
            # checks user input is appropriate format; corrects the format
            endKiosk = checkKioskID(endKiosk)

            # creates a message for the user
            addMessage = 'kiosk range ' + startKiosk + ' through ' + endKiosk

        # displays instructions to the user based on the change type submitted
        if changeType == 'add':
            changeMessage = 'Select a peripheral to add to ' + addMessage
            
            # gets all the available equipment that can be added
            addEquip = Equip.objects.exclude(clientkioskequip__client_kiosk=currentKiosk, clientkioskequip__exp_date__isnull=False).order_by('kiosk_component')

        elif changeType == 'replace':
            changeMessage = 'Select the peripherals to remove and replace for ' + addMessage

            # gets all the current equipment that can be removed; gets all the current equipment that can be added
            removeEquip = Equip.objects.filter(clientkioskequip__client_kiosk=currentKiosk, clientkioskequip__exp_date__isnull=True).order_by('kiosk_component')
            addEquip = Equip.objects.exclude(clientkioskequip__client_kiosk=currentKiosk, clientkioskequip__exp_date__isnull=False).order_by('kiosk_component')

            # gets all the current equipment that can be removed
        elif changeType == 'remove':
            changeMessage = 'Select the peripheral to remove from ' + addMessage

            removeEquip = Equip.objects.filter(clientkioskequip__client_kiosk=currentKiosk, clientkioskequip__exp_date__isnull=True).order_by('kiosk_component')

    # displays a custom error message to the user that their search criteria failed
    except:
        noResultsMessage = 'Your search criteria is not in the database'

    # return render view with variables
    return render(
        request,
        'app/retrofitKiosk/retrofitEquip.html',
        {
            'title':'Retrofit Kiosk',
            'inspiration':inspirationalQuote(),
            'year': datetime.now().year,
            'message':'Select the peripherals for the retrofit job',
            'changeMessage':changeMessage,
            'noResultsMessage':noResultsMessage,
            'addEquip':addEquip,
            'removeEquip':removeEquip,
            'retroNumber':retroNumber,
            'startKiosk':startKiosk,
            'endKiosk':endKiosk,
        }
    )

# Renders the Retrofit Kiosk Complete view
@login_required
def retrofitKioskComplete(request):
    """Renders the Retrofit Complete page"""
    assert isinstance(request, HttpRequest)

    # get the variable values from the GET request
    removeType = request.GET.get('removeType', None)
    addType = request.GET.get('addType', None)
    retroNumber = request.GET.get('retroNumber', None)
    startKiosk = request.GET.get('startKiosk', None)
    endKiosk = request.GET.get('endKiosk', None)

    # initialize the variables
    equipRemove = None
    equipAdd = None

    # check the GET request variables for "None" text and assign None value
    if startKiosk == 'None':
        startKiosk = None

    if endKiosk == 'None':
        endKiosk = None

    if retroNumber == 'None':
        retroNumber = None

    # check if the request is submitted via kiosk ID
    if startKiosk:
        kioskList = []

        # create kiosk list to be used for retrofit
        kioskList.append(ClientKiosk.objects.get(cts_kiosk_id=startKiosk))
        changeMessage = 'kiosk ' + startKiosk

        # check if the retrofit has to cover a range of kiosk IDs
        if endKiosk:
            startNum = int(startKiosk.split('-')[1]) + 1
            endNum = int(endKiosk.split('-')[1]) + 1
            currentCode = startKiosk.split('-')[0]

            # loop through the range submitted; add each kiosk to the kiosk list
            for i in range(endNum - startNum):
                currentID = currentCode + '-' + str(startNum + i).zfill(3)
                kioskList.append(ClientKiosk.objects.get(cts_kiosk_id=currentID))

            # create user message
            changeMessage = 'kiosks in range ' + startKiosk + ' through ' + endKiosk

        # assign kiosk list to a queryset for better manipulation
        currentKiosks = ClientKiosk.objects.filter(id__in=[i.id for i in kioskList])

    # checks the type of alteration needed
    if removeType:
        # get the specific equipment that must be altered
        equipRemove = Equip.objects.get(id=removeType)
            
        # get the kiosk equipment and attributes to be changed
        removeEquip = ClientKioskEquip.objects.filter(client_kiosk__in=currentKiosks.values('id'), equip=equipRemove)
        removeAttr = ClientKioskSubequip.objects.filter(client_kiosk_equip__in=removeEquip.values('id'))

        # expire attributes for equipment
        for i in range(len(removeAttr)):
            tempAttr = removeAttr[i]
            tempAttr.exp_date=datetime.now()
            tempAttr.save()

        # expire equipment for kiosks
        for i in range(len(removeEquip)):
            tempEquip = removeEquip[i]
            tempEquip.exp_date=datetime.now()
            tempEquip.save()

    # initialize lists for subequipment
    finalGroups = []
    subequipList = []
    equipSubList = []

    # checks the type of alteration method
    if addType:
        # get the specific equipment that must be altered
        equipAdd = Equip.objects.get(id=addType)

        # get all the subequipment groups related to the current equipment
        allSubequipGroups = list(SubequipGroup.objects.filter(exp_date=None, subequip__exp_date=None, subequip__equipsubequip__exp_date=None, subequip__equipsubequip__equip=equipAdd))

        # check for subequipment groups for the current equipment and append the group to the current equipment if it exists
        for allGroups in allSubequipGroups:
            if allGroups not in finalGroups:
                finalGroups.append(allGroups)

        # loop through the final list of groups to create subequipment
        for group in finalGroups:
            # check the current div from the template and get the subequipment from the POST request
            subequipDiv = str(group.id) + 'B'
            currentSubequip = request.POST.get(subequipDiv,None)

            # check that the subequipment exists
            if currentSubequip is not None:
                # create a temporary subequipment object and append it to the subequpment list for kiosk equipment creation
                tempSubequip = Subequip.objects.get(id=currentSubequip)
                subequipList.append(tempSubequip)
                equipSubList.append(tempEquip)

        # loop through the kiosk queryset to alter kiosks
        for i in range(len(currentKiosks)):

            # add the equipment with retrofit number if it is changed by kiosk ID
            newEquip = ClientKioskEquip(client_kiosk=currentKiosks[i], equip=equipAdd, serial_number=None, prod_rlse_rev=None, retrofit_job_number=retroNumber, eff_date=datetime.now())
            newEquip.save()

            # assign the most recent created equipment to a temporary equipment object
            tempEquip = ClientKioskEquip.objects.all().order_by('-id')[0]

            # get the required subequipment for temporary equipment
            reqSubEquip = Subequip.objects.filter(exp_date=None, equipsubequip__equip=tempEquip.equip, equipsubequip__exp_date=None, subequip_group__isnull=True)

            # loop through the required subequipment for the current kiosk equipment
            for k in range(len(reqSubEquip)):
                # get the required subequipment that have display text to store with the subequipment database entry
                if str(reqSubEquip[k].display_type) == 'text':
                    subequipTextDiv = str(reqSubEquip[k].id) + 'C'
                    getSubequipText = request.POST.get(subequipTextDiv,None)

                    # create the subequipment database entry
                    newSubequip = ClientKioskSubequip(client_kiosk_equip=tempEquip, subequip=reqSubEquip[k], prod_rlse_rev=None, retrofit_job_number=retroNumber, eff_date=datetime.now(), display_text=getSubequipText)
                    newSubequip.save()

                # create all subequipment database entries that do not have display text to stroe
                else:
                    newSubequip = ClientKioskSubequip(client_kiosk_equip=tempEquip, subequip=reqSubEquip[k], prod_rlse_rev=None, retrofit_job_number=retroNumber, eff_date=datetime.now())
                    newSubequip.save()

            # loop through all subequipment that belongs to a subequipment group
            for k in range(len(subequipList)):
                # create the subequipment databse entry for grouped subequipment
                if tempEquip.equip == equipSubList[k]:
                    tempSubequip = ClientKioskSubequip(client_kiosk_equip=tempEquip, subequip=subequipList[k], prod_rlse_rev=None, retrofit_job_number=retroNumber, eff_date=datetime.now())
                    tempSubequip.save()

    # create the table object for the view
    kioskTable = ClientKioskTable(currentKiosks)
    RequestConfig(request, paginate=False).configure(kioskTable)

    # return render view with variables
    return render(
        request,
        'app/retrofitKiosk/retrofitKioskComplete.html',
        {
            'title':'Successful Change',
            'inspiration':inspirationalQuote(),
            'year':datetime.now().year,
            'message':'Successful update for ' + changeMessage,
            'equipRemove':equipRemove,
            'equipAdd':equipAdd,
            'retroNumber':retroNumber,
            'kioskTable':kioskTable,
        }
    )

"""
    # Remove kiosk is a full database removal tool.  Executing actions on this page does not expire database entries from Recore, it permanently deletes the database entry.
    # This feature was commented out from the production code base per request from Paul Stroede, deemed unnecessary as entries should be expired instead of deleted.
    # The code is left in the code base as a comment in the event it is deemed appropriate in the future.
    # To activate this code:
        # - Remove the comment characters for the removeKiosk and associated functions in this file, the views.py file
        # - Remove the comment characters for the removeKiosk menu option in the layout.html file
        # - Remove the comment characters for the removeKiosk and associated URL options in the urls.py file

# Renders Remove Kiosk page view
@login_required
def removeKiosk(request):
    # Renders the Remove Kiosk page
    assert isinstance(request, HttpRequest)
    
    deleteForm = None

    # get the type of delete being performed or set to None
    deleteType = request.GET.get('delete',None)

    # check the type of delete submitted from user; initialize form for delete type
    if deleteType == 'Delete Kiosk':
        deleteForm = kioskID_searchForm()

    elif deleteType == 'Delete Job Number':
        deleteForm = jobNumber_searchForm()

    elif deleteType == 'Delete Client':
        deleteForm = client_searchForm()

    # return render view with variables
    return render(
        request,
        'app/removeKiosk.html',
        {
            'title':'Remove Kiosk',
            'inspiration':inspirationalQuote(),
            'year':datetime.now().year,
            'message':'WARNING - Deleting data from the database CANNOT be undone',
            'deleteType':deleteType,
            'deleteForm':deleteForm
        }
    )

# Renders Remove Kiosk page after delete has been performed view
@login_required
def removeKiosk_deleteKiosk(request):
    # Renders the Remove Kiosk page
    assert isinstance(request, HttpRequest)

    # initialize message to None
    userMessage = None

    # get the delete type information from the submitted form
    kioskID = request.GET.get('ctsKiosk',None)
    jobNumber = request.GET.get('jobNumber',None)
    clientName = request.GET.get('clientName',None)

    # check if the delete type is by CTS Kiosk ID
    if kioskID is not None:
        # call function to check CTS Kiosk ID string format
        kioskID = checkKioskID(kioskID)

        # try/except to handle an empty return from the database query
        try:
            # get the kiosk for deletion from the database; delete corresponding kiosk data
            currentKiosk = ClientKiosk.objects.get(cts_kiosk_id=kioskID)
            kioskEquip = KioskEquip.objects.filter(client_kiosk=currentKiosk)
            KioskEquipAttr.objects.filter(kiosk_equip__in=kioskEquip.values('id')).delete()
            kioskEquip.delete()
            currentKiosk.delete()

            # success message for user
            userMessage = 'The kiosk was successfully deleted'

        # sets a user message if the kiosk does not exist
        except:
            userMessage = 'This kiosk is not in the database'

    # check if the delete type is by job number
    elif jobNumber is not None:
        # checks if the job number has any kiosks in the database
        if ClientKiosk.objects.filter(job_number=jobNumber).count() > 0:
            # get the kiosks for deletion; delete the corresponding kiosk data
            kioskSet = ClientKiosk.objects.filter(job_number=jobNumber)
            kioskEquip = KioskEquip.objects.filter(client_kiosk__in=kioskSet.values('id'))
            KioskEquipAttr.objects.filter(kiosk_equip__in=kioskEquip.values('id')).delete()
            kioskEquip.delete()
            kioskSet.delete()

            # success message for user
            userMessage = 'The job number was successfully deleted'

        # sets a user message if the kiosk does not exist
        else:
            userMessage = 'This job number is not in the database'

    # checks if the delete type is by client
    elif clientName is not None:
        # try/except to handle an empty return from the database query
        try:
            # checks if the client exists in the database
            currentClient = Client.objects.get(id=clientName)

            # delete all client information; contacts, kiosk data, and kiosks
            ClientContact.objects.filter(client=currentClient).delete()
            kioskSet = ClientKiosk.objects.filter(client=currentClient)
            kioskEquip = KioskEquip.objects.filter(client_kiosk__in=kioskSet.values('id'))
            KioskEquipAttr.objects.filter(kiosk_equip__in=kioskEquip.values('id')).delete()
            kioskEquip.delete()
            kioskSet.delete()
            currentClient.delete()

            # success message for user
            userMessage = 'The client was successfully deleted'

        # sets a user message if the kiosk does not exist
        except:
            userMessage = 'This client is not in the database'

    # return render view with variables
    return render(
        request,
        'app/removeKiosk.html',
        {
            'title':'Remove Kiosk',
            'inspiration':inspirationalQuote(),
            'year':datetime.now().year,
            'message':'WARNING - Deleting data from the database CANNOT be undone',
            'userMessage':userMessage,
        }
    )
    # End removeKiosk and associated functions
"""

# Renders Update Database page view
@login_required
def updateDatabase(request):
    """Renders the Equipment Sets page"""
    assert isinstance(request, HttpRequest)

    # initialize the variables for the view
    currentForm = None
    currentKioskType = None
    prodList = None
    compList = None
    equipList = None
    errorMessage = None

    # checks if the submitted request was a POST
    if request.method == 'POST':

        # check which form was submitted; validate input against form object; save form object as new database entry
        if newEquipForm(request.POST).is_valid():
            currentForm = newEquipForm(request.POST)
            
            # create temporary form with submitted form data; set default fields; save object to the database
            addFieldForm = currentForm.save(commit=False)
            addFieldForm.make_model = currentForm.cleaned_data['make'] + ' ' + currentForm.cleaned_data['model']
            addFieldForm.eff_date = datetime.now()
            addFieldForm.save()

            # get the kiosk models list from the POST request; query the database for the kiosk models and associated equipment
            typeList = request.POST.getlist('kioskTypes')          
            kioskTypes = KioskType.objects.filter(id__in=typeList)
            currentEquip = Equip.objects.get(make_model=addFieldForm.make_model)

            # loop through the kiosk models; create new equipment to kiosk relation for each kiosk model
            for i in range(len(kioskTypes)):
                newRelation = KioskTypeEquip(kiosk_type=kioskTypes[i], equip=currentEquip, eff_date=datetime.now())
                newRelation.save()

        # checks if the subequipment form was submitted and is valid
        elif newSubequipForm(request.POST).is_valid():
            currentForm = newSubequipForm(request.POST)

            # create temporary form with submitted form data; save object to the database
            addFieldForm = currentForm.save(commit=False)
            addFieldForm.display_type = request.POST.get('subequipDisplay')
            addFieldForm.eff_date = datetime.now()
            addFieldForm.save()

            # get the equipment list and the included subequipment list from the POST request
            equipList = request.POST.getlist('equipment')
            inclList = request.POST.getlist('equipIncluded')

            # query the database for the POST request list database objects
            equipTypes = Equip.objects.filter(id__in=equipList)
            inclTypes = Equip.objects.filter(id__in=inclList)
            currentSubequip = Subequip.objects.get(name=addFieldForm.name)

            # loop through the equipment to create equipment to subequipment relationships
            for i in range(len(equipTypes)):
                newRelation = EquipSubequip(equip=equipTypes[i], subequip=currentSubequip, eff_date=datetime.now())
                newRelation.save()

                # get the most recently created subequipment to create relation type between equipment to subequipment
                tempRelation = EquipSubequip.objects.all().order_by('-id')[0]
                for j in range(len(inclTypes)):
                    # check if the subequipment is included in the equipment packaging; set attribute accordingly
                    if inclTypes[j] == tempRelation.equip:
                        tempRelation.subequip_included = 'Yes'
                        tempRelation.save()

        # check if the subequipment group form was submitted and is valid
        elif newSubequipGroupForm(request.POST).is_valid():
            currentForm = newSubequipGroupForm(request.POST)

            # create temporary form with submitted form data; save object to the database
            addFieldForm = currentForm.save(commit=False)
            addFieldForm.eff_date = datetime.now()
            addFieldForm.save()

        # check if the new kiosk component form was submitted and is valid
        elif newKioskComponentForm(request.POST).is_valid():
            currentForm = newKioskComponentForm(request.POST)

            # create temporary form with submitted form data; save object to the database
            addFieldForm = currentForm.save(commit=False)
            addFieldForm.display_type = request.POST.get('compDisplay')
            addFieldForm.eff_date = datetime.now()
            addFieldForm.save()

            # get the kiosk types list from the POST request; query database for all kiosk components
            typeList = request.POST.getlist('kioskTypes')          
            kioskTypes = KioskType.objects.filter(id__in=typeList)
            currentComponent = KioskComponent.objects.get(name=addFieldForm.name)

            # loop through the kiosk types; create kiosk component to kiosk model relationships
            for i in range(len(kioskTypes)):
                newRelation = KioskTypeComponent(kiosk_type=kioskTypes[i], kiosk_component=currentComponent, eff_date=datetime.now())
                newRelation.save()

        # check if the new production release group form was submitted and is valid
        elif newProdGroupForm(request.POST).is_valid():
            currentForm = newProdGroupForm(request.POST)

            # create temporary form with submitted form data; save object to the database
            addFieldForm = currentForm.save(commite=False)
            addFieldForm.eff_date = datetime.now()
            addFieldForm.save()

            # get the kiosk types from the POST request; query database for all production release groups
            typeList = request.POST.getlist('kioskTypes')          
            kioskTypes = KioskType.objects.filter(id__in=typeList)
            currentGroup = ProdRlseGroup.objects.get(name=request.POST.get('name'))

            # loop through the kiosk types; create production release group to kiosk model relationships
            for i in range(len(kioskTypes)):
                newRelation = KioskTypeProdRlse(kiosk_type=kioskTypes[i], prod_rlse_group=currentGroup, eff_date=datetime.now())
                newRelation.save()

        # check if the new kiosk type form was submitted and is valid
        elif newKioskTypeForm(request.POST).is_valid():
            currentForm = newKioskTypeForm(request.POST)
            
            # create temporary form with submitted form data; save object to the database
            addFieldForm = currentForm.save(commit=False)
            addFieldForm.eff_date = datetime.now()
            addFieldForm.save()

            # get all the production release groups, kiosk components, and equipment from the database
            currentKioskType = addFieldForm.kiosk_type
            prodList = ProdRlseGroup.objects.filter(exp_date=None)
            compList = KioskComponent.objects.filter(exp_date=None)
            equipList = Equip.objects.filter(exp_date=None)

        # check if the equipment restriction form was submitted and is valid
        elif newEquipRestrictionForm(request.POST).is_valid():
            currentForm = newEquipRestrictionForm(request.POST)

            # create temporary form with submitted form data; save object to the database
            addFieldForm = currentForm.save(commit=False)
            addFieldForm.eff_date = datetime.now()
            addFieldForm.save()

        # mark the error message boolean to True if no valid form is submitted; allows page to render the error message
        else:
            errorMessage = True

    # return render view with variables
    return render(
        request,
        'app/updateDatabase.html',
        {
            'title':'Update Database',
            'inspiration':inspirationalQuote(),
            'year':datetime.now().year,
            'message':'Use this page to add new kiosk options and features to the database',
            'currentForm':currentForm,
            'currentKioskType':currentKioskType,
            'prodList':prodList,
            'compList':compList,
            'equipList':equipList,
            'errorMessage':errorMessage,
        }
    )

# Renders Get Database Form page view
@login_required
def getDatabaseForm(request):
    """Renders the Get Database Form page"""
    assert isinstance(request, HttpRequest)

    # get the form type variable from the GET request
    formType = request.GET.get('formType')
    # create the form title for display
    formName = formType + " Form"

    # create dictionary of all possible forms for the Update Database views
    formOptions = {'Equipment':newEquipForm,
                   'Subequipment':newSubequipForm,
                   'Subequipment Group':newSubequipGroupForm,
                   'Kiosk Component':newKioskComponentForm,
                   'Production Release Group':newProdGroupForm,
                   'Kiosk Model':newKioskTypeForm,
                   'Equipment Restriction':newEquipRestrictionForm,
                   }

    # create dictionary of all the possible tables to display of existing database information
    currentData = {'Equipment':EquipTable(Equip.objects.all().order_by('kiosk_component','make','model')),
                   'Subequipment':SubequipTable(Subequip.objects.all().order_by('name')),
                   'Subequipment Group':SubequipGroupTable(SubequipGroup.objects.all().order_by('name')),
                   'Kiosk Component':KioskComponentTable(KioskComponent.objects.all().order_by('prod_rlse_group','name')),
                   'Production Release Group':ProdRlseGroupTable(ProdRlseGroup.objects.all().order_by('name')),
                   'Kiosk Model':KioskTypeTable(KioskType.objects.all().order_by('cts_division','kiosk_type')),
                   'Equipment Restriction':EquipRestrictionTable(EquipRestriction.objects.all().order_by('primaryEquip')),
                   }

    # create the table corresponding to the selected form
    RequestConfig(request, paginate=False).configure(currentData[formType])

    # return render view with variables
    return render(
        request,
        'app/updateDatabase/getDatabaseForm.html',
        {
            'formName':formName,
            'databaseForm':formOptions[formType],
            'tableData':currentData[formType],
        }
    )

# Renders New Kiosk Equipment page view
@login_required
def kioskModelNewEquip(request):
    """Renders the New Kiosk Equipment page"""
    assert isinstance(request, HttpRequest)

    # get the production release group, the kiosk component, and the display DIV from the GET request
    currentProd = ProdRlseGroup.objects.get(id=(request.GET.get('prod')))
    currentComp = KioskComponent.objects.get(id=(request.GET.get('comp')))
    equipDiv = request.GET.get('equipDiv')

    # strip the first character from the DIV; first character used for page display
    equipDiv = equipDiv[1:]

    # return render view with variables
    return render(
        request,
        'app/updateDatabase/kioskModelNewEquip.html',
        {
            'currentProd':currentProd,
            'currentComp':currentComp,
            'equipDiv':equipDiv,
        }
    )

# Renders Create New Kiosk Equipment page view
@login_required
def kioskModelCreateEquip(request):
    """Renders the Create New Kiosk Equipment page"""
    assert isinstance(request, HttpRequest)

    # get the production release group and kiosk component from the GET request
    currentProd = ProdRlseGroup.objects.get(id=(request.GET.get('prod')))
    currentComp = KioskComponent.objects.get(id=(request.GET.get('comp')))

    # get the equipment details from the GET request
    equipMake = request.GET.get('make')
    equipModel = request.GET.get('model')
    equipDescript = request.GET.get('equip_descript')
    ctsNum = request.GET.get('ctsNumber',None)
    manfNum = request.GET.get('manfNumber',None)

    # create a new kiosk equipment database entry with the submitted user information
    Equip.objects.create(kiosk_component=currentComp, equip_descript=equipDescript, make=equipMake, model=equipModel, make_model=equipMake + " " + equipModel, cts_part_number=ctsNum,
                         manf_part_number=manfNum, eff_date=datetime.now())

    # query the database for all the production release groups, kiosk components, and kiosk equipment for page display
    prodList = ProdRlseGroup.objects.filter(exp_date=None)
    compList = KioskComponent.objects.filter(exp_date=None)
    equipList = Equip.objects.filter(exp_date=None)

    # return render view with variables
    return render(
        request,
        'app/updateDatabase/createKioskRelations.html',
        {
            'prodList':prodList,
            'compList':compList,
            'equipList':equipList,
        }
    )

# Renders New Kiosk Component page view
@login_required
def kioskModelNewComp(request):
    """Renders the New Kiosk Component page"""
    assert isinstance(request, HttpRequest)

    # query the database for all the production release groups; get the current kiosk component DIV
    currentProd = ProdRlseGroup.objects.get(id=(request.GET.get('prod')))
    compDiv = request.GET.get('compDiv')

    # return render view with variables
    return render(
        request,
        'app/updateDatabase/kioskModelNewComp.html',
        {
            'currentProd':currentProd,
            'compDiv':compDiv,
        }
    )

# Renders Create Kiosk Component page view
@login_required
def kioskModelCreateComp(request):
    """Renders the Create Kiosk Component page"""
    assert isinstance(request, HttpRequest)

    # get the current production release group from the GET request
    currentProd = ProdRlseGroup.objects.get(id=(request.GET.get('prod')))
    # get the kiosk component information from the submitted GET request
    compName = request.GET.get('name')
    displayType = request.GET.get('display_type')
    compDescript = request.GET.get('comp_descript')

    # create a new kiosk component in the database with the submitted kiosk component information
    KioskComponent.objects.create(prod_rlse_group=currentProd, name=compName, display_type=displayType, comp_descript=compDescript, eff_date=datetime.now())

    # query the database for all the production release groups, kiosk components, and equipment; used for page dispay and user selection
    prodList = ProdRlseGroup.objects.filter(exp_date=None)
    compList = KioskComponent.objects.filter(exp_date=None)
    equipList = Equip.objects.filter(exp_date=None)

    # return render view with variables
    return render(
        request,
        'app/updateDatabase/createKioskRelations.html',
        {
            'prodList':prodList,
            'compList':compList,
            'equipList':equipList,
        }
    )

# Renders New Production Release Group page view
@login_required
def kioskModelNewProd(request):
    """Renders the New Production Release Group page"""
    assert isinstance(request, HttpRequest)

    # return render view with variables
    return render(
        request,
        'app/updateDatabase/kioskModelNewProd.html',
        {
            # generates production release group view; no variables to pass
        }
    )

# Renders Create Production Release Group page view
@login_required
def kioskModelCreateProd(request):
    """Renders the Create Production Release Group page"""
    assert isinstance(request, HttpRequest)

    # get the production release group and description from the GET request
    prodName = request.GET.get('name')
    equipDescript = request.GET.get('prod_descript')

    # create production release group with the submitted information
    ProdRlseGroup.objects.create(name=prodName, prod_descript=equipDescript, eff_date=datetime.now())

    # query the database for all production release groups, kiosk components, and equipment; used for page rendering and user selection
    prodList = ProdRlseGroup.objects.filter(exp_date=None)
    compList = KioskComponent.objects.filter(exp_date=None)
    equipList = Equip.objects.filter(exp_date=None)

    # return render view with variables
    return render(
        request,
        'app/updateDatabase/createKioskRelations.html',
        {
            'prodList':prodList,
            'compList':compList,
            'equipList':equipList,
        }
    )

# Renders the Cancel Database form page view
@login_required
def cancelDatabaseForm(request):
    """Renders the Cancel Database page"""
    assert isinstance(request, HttpRequest)

    # query the database for the production release group, kiosk components, and kiosk equipment
    prodList = ProdRlseGroup.objects.filter(exp_date=None)
    compList = KioskComponent.objects.filter(exp_date=None)
    equipList = Equip.objects.filter(exp_date=None)

    # return render view with variables
    return render(
        request,
        'app/updateDatabase/createKioskRelations.html',
        {
            'prodList':prodList,
            'compList':compList,
            'equipList':equipList,
        }
    )

# Renders the New Equipment Relations page view
@login_required
def newEquipRelations(request):
    """Renders the New Equipment Relations page"""
    assert isinstance(request, HttpRequest)

    # get the full equipment list from the GET request; get the kiosk type from the GET request
    newEquipList = request.GET.getlist('equipRelations[]')
    subassemblyList = request.GET.getlist('subassemblyRelation[]')
    currentKioskType = KioskType.objects.filter(kiosk_type=request.GET.get('currentKioskType')).first()

    # query the database for the kiosk equipment, kiosk components, and production release groups based on the submitted kiosk equipment
    currentEquip = Equip.objects.filter(id__in=newEquipList)
    currentComp = KioskComponent.objects.filter(id__in=currentEquip.values('kiosk_component_id'))
    currentProd = ProdRlseGroup.objects.filter(id__in=currentComp.values('prod_rlse_group_id'))
    
    # loop through the submitted equipment; create equipment to kiosk type relations in the database
    for i in range(len(currentEquip)):

        # check that a subassembly number was entered; if there is no subassembly number then set the attribute to None
        if subassemblyList[i] == '':
            KioskTypeEquip.objects.create(kiosk_type=currentKioskType, equip=currentEquip[i], subassembly_num=None, eff_date=datetime.now())
        else:
            KioskTypeEquip.objects.create(kiosk_type=currentKioskType, equip=currentEquip[i], subassembly_num=subassemblyList[i], eff_date=datetime.now())

    # loop through the submitted kiosk components; create kiosk component to kiosk type relations in the database
    for i in range(len(currentComp)):
        KioskTypeComponent.objects.create(kiosk_type=currentKioskType, kiosk_component=currentComp[i], eff_date=datetime.now())

    # loop through the submitted production release groups; create the production release group to kiosk type relations in the database
    for i in range(len(currentProd)):
        KioskTypeProdRlse.objects.create(kiosk_type=currentKioskType, prod_rlse_group=currentProd[i], eff_date=datetime.now())

    # query the database for the all (including the newly created) production release groups, kiosk components, and kiosk equipment; used for display
    prodList = ProdRlseGroup.objects.filter(kiosktypeprodrlse__kiosk_type=currentKioskType)
    compList = KioskComponent.objects.filter(kiosktypecomponent__kiosk_type=currentKioskType)
    equipList = Equip.objects.filter(kiosktypeequip__kiosk_type=currentKioskType)

    # return render view with variables
    return render(
        request,
        'app/updateDatabase/newEquipRelations.html',
        {
            'currentKioskType':currentKioskType,
            'prodList':prodList,
            'compList':compList,
            'equipList':equipList,
            'currentProd':currentProd,
            'currentComp':currentComp,
            'currentEquip':currentEquip,
        }
    )

# Renders Error page view
@login_required
def error(request):
    """Renders the Error page"""
    assert isinstance(request, HttpRequest)

    # return render view with variables
    return render(
        request,
        'app/error.html',
        {
            'title':'I know...computers are hard',
            'inspiration':inspirationalQuote(),
            'year':datetime.now().year,
            'message':'A team of highly trained monkeys has been dispatched to deal with this situation'
        }
    )

# Create the Production Release PDF for download
def generatePDF(request):
    # get the job number and production release revision
    jobNumber = request.GET.get('jobNumber')
    prodRlseRev = request.GET.get('prodRlseRev')

    # query the database for the production release information
    prodRlse = ProdRlse.objects.get(job_number=jobNumber, prod_rlse_rev=prodRlseRev)
    kioskList = ClientKiosk.objects.filter(job_number=jobNumber).order_by('cts_kiosk_id')
    currentKiosk = ClientKiosk.objects.filter(job_number=jobNumber).first()
    kioskType = kioskList[0].kiosk_type
    
    # create the display title and release name for the PDF
    kioskHeader = kioskType.kiosk_type + " Production Release"
    releaseName = 'Production Release Job ' + str(prodRlse.job_number) + ' Rev ' + str(prodRlse.prod_rlse_rev) + '.pdf'

    # set the font metrics for PDF generation
    pdfmetrics.registerFont(TTFont('Calibri', 'Calibri.ttf'))
    pdfmetrics.registerFont(TTFont('Calibri-Bold', 'Calibrib.ttf'))
    styles = getSampleStyleSheet()
    sNormal = styles['Normal']
    sTitle = styles['Heading3']
    sSubtitle = styles['Heading5']
    sTable = styles['BodyText']
    sTable.wordWrap = 'CJK'

    # create empty story to append PDF elements to for generation
    prodRlseStory = []

    # create the response type for PDF download
    response = HttpResponse(content_type='application/pdf')
    pdf_name = releaseName
    response['Content-Disposition'] = 'attachment; filename=%s' % pdf_name
    buff = BytesIO()
    
    # create the document template; assign margins
    doc = SimpleDocTemplate(buff, pagesize=letter, rightMargin=0.5*inch, leftMargin=0.5*inch, topMargin=0.8*inch, bottomMargin=0.8*inch)
    prodRlseStory.append(Paragraph("General Information", sTitle))

    # create the production release information to be displayed in columns on the PDF
    prodFields = [['Client: ' + str(prodRlse.client), 'Quantity: ' + str(kioskList.count()), 'Release Date: ' + str(prodRlse.release_date)],
            ['Job Number: ' + str(prodRlse.job_number), 'Unit ID(s): ' + str(prodRlse.kiosk_range), 'Ship Date: ' + str(prodRlse.ship_date)],
            ['Sales Rep: ' + str(prodRlse.sales_rep), 'P.O. #: ' + str(prodRlse.po_number), 'Go-Live Date: ' + str(prodRlse.go_live_date)],
            ['Production Release Rev #: ' + str(prodRlse.prod_rlse_rev), 'Invoice #: ' + str(prodRlse.invoice_number)],]

    # set the table information, margins, and style
    tableProdFields = [[Paragraph(cell, sTable) for cell in row] for row in prodFields]
    prodTable = Table(tableProdFields, colWidths='*')
    prodTable.setStyle(TableStyle([('LEFTPADDING', (0,0), (-1,-1), 0),
                                   ('RIGHTPADDING', (0,0), (-1,-1), 0),
                                   ('BOTTOMPADDING', (0,0), (-1,-1), 1),
                                   ('TOPPADDING', (0,0), (-1,-1), 1)]))
    
    # append the production release information table to the PDF story
    prodRlseStory.append(prodTable)
    prodRlseStory.append(Paragraph('Notes', sTitle))

    # check for an image support fee and display image support fee in form of table if it exists
    if prodRlse.image_support_fee == 'Yes':
        itFields = [['Image Support Fee Selected'],
                    ['IT Contact: ' + str(prodRlse.it_contact), 'IT Phone Number: ' + str(prodRlse.it_phone)],
                    ['IT Email: ' + str(prodRlse.it_email)],]
        tableItFields = [[Paragraph(cell, sTable) for cell in row] for row in itFields]
        itTable = Table(tableItFields, colWidths='*')
        itTable.setStyle(TableStyle([('LEFTPADDING', (0,0), (-1,-1), 0),
                                     ('RIGHTPADDING', (0,0), (-1,-1), 0),
                                     ('BOTTOMPADDING', (0,0), (-1,-1), 1),
                                     ('TOPPADDING', (0,0), (-1,-1), 1)]))

        # append the image support fee to the PDF story
        prodRlseStory.append(itTable)

    # check for additional notes and appends them to the PDF story if they exist
    if prodRlse.notes is not None:
        prodRlseStory.append(Paragraph('Additional Notes: ' + str(prodRlse.notes), sNormal))

    # query the database for the equipment and production release groups associated to the current production release revision
    currentEquip = ClientKioskEquip.objects.filter(client_kiosk=currentKiosk, prod_rlse_rev=prodRlse.prod_rlse_rev)
    prodGroups = ProdRlseGroup.objects.filter(kiosktypeprodrlse__kiosk_type=kioskType)

    # loop through the production release groups; appending the title to the PDF story as each production release group loops through kiosk equipment
    for group in prodGroups:
        prodRlseStory.append(Paragraph(str(group.name), sTitle))
      
        # loop through all the equipment for the current production release revision
        for item in currentEquip:
            # if the current equipment is part of the current production release revision; display the kiosk component for that equipment
            if item.equip.kiosk_component.prod_rlse_group == group:
                # check the equipment for a CTS part number; if it exists also display the part number
                if (item.equip.cts_part_number is not None) and (item.equip.cts_part_number != ''):
                    currentInfo = str(item.equip.kiosk_component.name) + ': ' + str(item.equip.make_model) + ' (#' + str(item.equip.cts_part_number) + ')'
                else:
                    currentInfo = str(item.equip.kiosk_component.name) + ': ' + str(item.equip.make_model)
                
                # append the current equipment to the production release story
                prodRlseStory.append(ListFlowable([ListItem(Paragraph(currentInfo, sNormal), value='disc')], bulletType='bullet',start='disc'))

                # query the database for the current kiosk equipment's subequipment
                includedSubequip = Subequip.objects.filter(equipsubequip__equip=item.equip, equipsubequip__subequip_included='Yes', exp_date=None)
                currentInclSubequip = ClientKioskSubequip.objects.filter(client_kiosk_equip=item, subequip_id__in=includedSubequip)
                
                # loop through the subequipment included with the current kiosk equipment
                for subItem in currentInclSubequip:
                    # if the subequipment has a CTS part number, display that part number
                    if (subItem.subequip.cts_part_number is not None) and (subItem.subequip.cts_part_number != ''):
                        subequipInfo = str(subItem.subequip.name) + ' (#' + str(subItem.subequip.cts_part_number) + ')'
                    else:
                        subequipInfo = str(subItem.subequip.name)

                    # check if the subequipment has text to be displayed; display the text if it exists
                    if subItem.display_text is not None:
                        subequipInfo = subequipInfo + ': ' + subItem.display_text

                    # append the subequipment to the PDF story
                    prodRlseStory.append(ListFlowable([ListItem(Paragraph(subequipInfo, sNormal), leftIndent=50, value='diamondwx')], bulletType='bullet',start='diamondwx'))
                
                # query the database for the remaining subequipment for the current kiosk equipment
                otherSubequip = Subequip.objects.filter(equipsubequip__equip=item.equip, equipsubequip__subequip_included=None, exp_date=None)
                currentOtherSubequip = ClientKioskSubequip.objects.filter(client_kiosk_equip=item, subequip_id__in=otherSubequip)

                # loop through the remaining subequipment
                for subItem in currentOtherSubequip:
                    # check the subequipment for a CTS part number; if it exists also display the part number
                    if (subItem.subequip.cts_part_number is not None) and (subItem.subequip.cts_part_number != ''):
                        subequipInfo = str(subItem.subequip.name) + ' (#' + str(subItem.subequip.cts_part_number) + ')'
                    else:
                        subequipInfo = str(subItem.subequip.name)

                    # check if the subequipment has text to be displayed; display the text if it exists
                    if subItem.display_text is not None:
                        subequipInfo = subequipInfo + ': ' + subItem.display_text

                    # append the current subequipment to the PDF story
                    prodRlseStory.append(ListFlowable([ListItem(Paragraph(subequipInfo, sNormal), leftIndent=50, value='blackstar')], bulletType='bullet',start='blackstar'))
    
    # build the PDF document using the PDF story list
    doc.build(prodRlseStory, onFirstPage=partial(allPages, content=kioskHeader), onLaterPages=partial(allPages, content=kioskHeader))

    # write the PDF to the buffer; close the buffer; return the PDF as the function response
    response.write(buff.getvalue())
    buff.close()
    return response

# Create the header and footer for Production Release PDF
def allPages(canvas, doc, content):
    # create the canvas to write to; set the style; write the header and footer to the current canvas
    canvas.saveState()
    width, height = letter
    canvas.setFont('Calibri-Bold',18)
    canvas.drawCentredString(0.5*width, height-(0.5*inch), content)
    canvas.line(0.5*inch, height-(0.75*inch), width-(0.5*inch), height-(0.75*inch))
    canvas.setFont('Calibri', 9)
    canvas.drawRightString(width-(0.5*inch), (0.5*inch), datetime.now().strftime("%B") + " " + str(datetime.now().year))
    canvas.restoreState()

# Checks the CTS Kiosk ID for appropriate character format and entry
def checkKioskID(currentKiosk):
    # try/except to handle an invalid search entry
        try:
            # checks user input is appropriate format; corrects the format
            if '-' not in currentKiosk:
                tempKiosk = re.match(r"([a-z]+)([0-9]+)",currentKiosk)
                currentKiosk = ''
                currentKiosk = tempKiosk.group(1).upper() + '-' + tempKiosk.group(2)
       
            else:
                tempKiosk = currentKiosk.split('-')
                currentKiosk = tempKiosk[0].upper() + '-' + tempKiosk[1]

        # sets the return variable to Nonetype if the search entry is invalid
        except:
            currentKiosk = None

        # return the variable with the CTS Kiosk ID or Nonetype
        return currentKiosk

# Get super inspirational quotes and facts from database
def inspirationalQuote():
    # query the database for a random quote or fact and return for inspirational user support and motivation
    # FACT: Dave is pretty much the best there is
    try:
        currentQuote = Quotes.objects.get(id = randint(1,Quotes.objects.count())).quote
    except:
        currentQuote = 'The toughest part about being the smartest person in the room is pretending that you are not. - Dave'

    return currentQuote