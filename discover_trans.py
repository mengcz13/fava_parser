import os
import sys
import csv
from datetime import datetime
from argparse import ArgumentParser

from utils import FavaJounralEntry


def parse_discover_merchant(description):
    if description.startswith('TARGET'):
        return 'Target'
    elif description.startswith('TRADER JOE\'S'):
        return 'Trader Joe\'s'
    elif description.startswith('APL*'):
        return 'Apple'
    elif description.startswith('PAYPAL *NINTENDO'):
        return 'Nintendo'
    elif description.startswith('AMAZON.COM*'):
        return 'Amazon'
    elif description.startswith('AMZN'):
        return 'Amazon'
    elif description.startswith('PP*GOOGLE'):
        return 'Google'
    elif description.startswith('SQ *TASTY WOK EXPRESS LOS ANGELES'):
        return 'TASTY WOK EXPRESS'
    else:
        return description


def parse_discover(row):
    transdate, postdate, description, amount, category = row
    amount = float(amount)
    if amount > 0:
        source = 'Liabilities:US:Discover:Discover-it'
        target = 'Expenses:{}'.format(category)
        date = datetime.strptime(transdate, '%m/%d/%Y')
        merchant = parse_discover_merchant(description)
        return FavaJounralEntry(
            date, merchant, description, source, target, amount
        )
    elif not description.startswith('INTERNET PAYMENT'):
        source = 'Liabilities:US:Discover:Discover-it'
        target = 'Income:US:Refund'
        date = datetime.strptime(transdate, '%m/%d/%Y')
        merchant = parse_discover_merchant(description)
        return FavaJounralEntry(
            date, merchant, description, source, target, amount
        )
    else:
        return None

CHASE_SOURCES = {
    'checking': 'Assets:US:Chase:Checking',
    'savings': 'Assets:US:Chase:Savings',
    'cf': 'Liabilities:US:Chase:Chase-Freedom'
}


def parse_chase_description(description, amount, sourcename):
    source = CHASE_SOURCES[sourcename]
    if description.startswith('USC HOSPITALITY RETAIL'):
        target = 'Expenses:Restaurants'
        merchant = 'USC Hospitality Retail'
    elif description.startswith('DISCOVER'):
        target = 'Liabilities:US:Discover:Discover-it'
        merchant = 'Discover'
    elif description.startswith('UNIVERSITY OF SO PAYROLL'):
        target = 'Income:US:USC:RAship'
        merchant = 'USC'
    else:
        target = 'TOFILL'
        merchant = description
    return source, target, merchant, amount



def parse_chase(row, sourcename):
    if sourcename in ['checking', 'savings']:
        Details,PostingDate,Description,Amount,Type,Balance,CheckorSlip, _ = row
    else:
        _, PostingDate, Description, _, _, Amount = row
    Amount = -float(Amount)
    date = datetime.strptime(PostingDate, '%m/%d/%Y')
    source, target, merchant, amount = parse_chase_description(Description, Amount, sourcename)
    return FavaJounralEntry(date, merchant, Description, source, target, amount)


def main():
    parser = ArgumentParser()
    parser.add_argument('converter', type=str)
    parser.add_argument('filepath', type=str)
    parser.add_argument('outpath', type=str)
    args = parser.parse_args()

    entries = []
    with open(args.filepath, 'r') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        next(reader)
        for row in reader:
            if args.converter == 'discover':
                entry = parse_discover(row)
            elif args.converter.startswith('chase'):
                chase_source = args.converter.split('-')[1]
                entry = parse_chase(row, chase_source)
            else:
                entry = None
            if entry is not None:
                entries.append(entry)
    entries = sorted(entries, key=lambda x: x.date)

    with open(args.outpath, 'w') as outfile:
        for entry in entries:
            entrystr = entry.tostring()
            outfile.write(entrystr + '\n')
            print(entrystr, '\n')


if __name__ == '__main__':
    main()
