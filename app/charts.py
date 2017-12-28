"""
Definition of charts
"""

from app.models import *

# Kiosk Type Data class to display pie chart on home page
class KioskTypeData(object):
    # definition function to get kiosk type information from the database
    def get_kioskTypes():
        kioskModels = KioskType.objects.all()
        kioskList = []

        # loop through kiosk types and append them to a list for graph rendering
        for kiosks in kioskModels:
            kioskList.append(kiosks.kiosk_type)

        # return the full kiosk type list
        return kioskList

# EXAMPLE CLASS
class testChartData(object):    
    def check_valve_data():
        data = {'serial numbers': [], 'mass': [],
                 'pressure drop': [], 'cracking pressure': [], 'reseat pressure': []}

        valves = CheckValve.objects.all()

        for unit in valves:
            data['serial numbers'].append(unit.serial_number)
            data['mass'].append(unit.mass)
            data['cracking pressure'].append(unit.cracking_pressure)
            data['pressure drop'].append(unit.pressure_drop)
            data['reseat pressure'].append(unit.reseat_pressure)

        return data   