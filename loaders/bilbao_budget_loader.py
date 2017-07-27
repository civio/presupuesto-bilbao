# -*- coding: UTF-8 -*-
from budget_app.models import *
from budget_app.loaders import SimpleBudgetLoader
from decimal import *
import csv
import os
import re

class BilbaoBudgetLoader(SimpleBudgetLoader):

    def parse_item(self, filename, line):
        # Although there's no change in the programme structure, there are some programmes in the 2015 budget that
        # change their code in later years
        programme_mapping_2015 = {
        # old programme: new programme
            '2371':'2318',  # Actividades de ocio para juventud -> Promoción y servicios a la juventud/infancia
            '2372':'2318',  # Actividades de ocio para infancia -> Promoción y servicios a la juventud/infancia
            '3391':'3344',  # Bandas municipales de música -> Bandas municipales de música
            '3291':'3262',  # Enseñanza de música -> Enseñanza de música
            '1691':'1632',  # Servicios generales del bienestar comunitario -> Servicios generales del bienestar comunitario
            '2391':'2319',  # Cooperación al desarrollo -> Ayudas a la cooperación desarrollo internacional
        }

        # Institutional code (all income go to the root node, and all expenses come from the root node too)
        ic_code = '000'

        # Type of data
        is_expense = (filename.find('gastos.csv')!=-1)
        is_actual = (filename.find('/ejecucion_')!=-1)

        # Expenses
        if is_expense:
            # Functional code
            fc_code = line[2].strip()

            # For year 2015 we check whether we need to amend the programme code
            year = re.search('municipio/(\d+)/', filename).group(1)
            if int(year) == 2015:
                fc_code = programme_mapping_2015.get(fc_code, fc_code)

            # Economic code
            full_ec_code = line[4].strip()

            # On economic codes we get the first three digits
            ec_code = full_ec_code[:3]

            # Item numbers are the last two digits from the economic codes (fourth and fifth digit)
            item_number = full_ec_code[-2:]

            # Description
            description = line[5].strip()

            # Parse amount
            amount = line[12 if is_actual else 9].strip()
            amount = self._parse_amount(amount)

            return {
                'is_expense': True,
                'is_actual': is_actual,
                'fc_code': fc_code,
                'ec_code': ec_code,
                'ic_code': ic_code,
                'item_number': item_number,
                'description': description,
                'amount': amount
            }

        # Income
        else:
            # Economic code
            full_ec_code = line[0].strip()

            # On economic codes we get the first three digits
            ec_code = full_ec_code[:3]

            # Item numbers are the last two digits from the economic codes (fourth and fifth digit)
            item_number = full_ec_code[-2:]

            # Description
            description = line[1].strip()

            # Parse amount
            amount = line[5 if is_actual else 2].strip()
            amount = self._parse_amount(amount)

            return {
                'is_expense': False,
                'is_actual': is_actual,
                'ec_code': ec_code,
                'ic_code': ic_code,
                'item_number': item_number,
                'description': description,
                'amount': amount
            }