import os
import sys


class FavaJounralEntry(object):
    def __init__(self, date, merchant, description, source, target, amount):
        self.date = date
        self.merchant = merchant
        self.description = description
        self.source = source
        self.target = target
        self.amount = amount

    def tostring(self):
        return '''{} * \"{}\" \"{}\"
    {}        {:.2f} USD
    {}
'''.format(self.date.strftime('%Y-%m-%d'), self.merchant, self.description, self.target, self.amount, self.source)