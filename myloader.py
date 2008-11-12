from google.appengine.api import users
from google.appengine.ext import bulkload
from google.appengine.api import datastore_types
from google.appengine.ext import search

class ExpressionLoader(bulkload.Loader):
  def __init__(self):
    # Our 'Expression' entity contains a affyid string and an expression float data
    bulkload.Loader.__init__(self, 'Expression',
                         [('affy_id',       str),
                          ('gene_symbol',   str),
                          ('entrezid',      str),
                          ('gene_name',     str),			  
                          ('evector_day0',  float),
                          ('evector_day2',  float),
                          ('evector_day4',  float),
                          ('evector_day10', float),			  
                          ('ppargox_day0',  float),
                          ('ppargox_day2',  float),
                          ('ppargox_day4',  float),
                          ('ppargox_day10', float),
                          ])

  def HandleEntity(self, entity):
    ent = search.SearchableEntity(entity)
    return ent

if __name__ == '__main__':
  bulkload.main(ExpressionLoader())
