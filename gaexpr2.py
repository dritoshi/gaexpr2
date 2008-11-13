import math
import wsgiref.handlers
import os

from google.appengine.ext import webapp
from google.appengine.ext import search
from google.appengine.ext import db
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template

class Expression(db.Model):
  affy_id       = db.StringProperty()
  gene_symbol   = db.StringProperty()
  entrezid      = db.StringProperty()
  gene_name     = db.StringProperty()
  evector_day0  = db.FloatProperty()
  evector_day2  = db.FloatProperty()
  evector_day4  = db.FloatProperty()
  evector_day10 = db.FloatProperty()
  ppargox_day0  = db.FloatProperty()
  ppargox_day2  = db.FloatProperty()
  ppargox_day4  = db.FloatProperty()
  ppargox_day10 = db.FloatProperty()


class MainPage(webapp.RequestHandler):
  def get(self):
      
    url = "http://chart.apis.google.com/chart?cht=lxy&chco=1E5692,3E9A3B&chs=300x225&chxt=x,y&chxl=0:|0|2|4|6|8|10|1:|2|4|6|8|10&chds=0,10,2,10,0,10,2,10&chd=t:"

    # I use the webapp framework to retrieve the keyword
    keyword = self.request.get('keyword')

    if not keyword:
      self.response.out.write("No keyword has been set.")
    else:
      # Search the 'Expression' Entity based on our keyword
      query = search.SearchableQuery('Expression')
      query.Search(keyword)
      template_values = {}
      for result in query.Run():
        # Graph (Using Google Chart API)
        evector = ",".join([str(result['evector_day' + suffix]) for suffix in ["0", "2", "4", "10"]])
        ppargox = ",".join([str(result['ppargox_day' + suffix]) for suffix in ["0", "2", "4", "10"]])
        graph = url + "0,2,4,10|" + evector + "|0,2,4,10|" + ppargox

        template_values['affy_id']     = result['affy_id']
        template_values['gene_symbol'] = result['gene_symbol']
        template_values['gene_name']   = result['gene_name']
        template_values['entrezid']    = result['entrezid']
        template_values['graph']       = graph

      path = os.path.join(os.path.dirname(__file__), 'index.html')
      self.response.out.write(template.render(path, template_values))

    
class IdSearchForm(webapp.RequestHandler):
  def get(self):
    template_values = {}
    path = os.path.join(os.path.dirname(__file__), 'search.html')
    self.response.out.write(template.render(path, template_values))
    
class Coexpression(webapp.RequestHandler):
  def mean(self, exprs):
    mean = 0.0
    for expr in exprs:
      mean += expr
    return mean / len(exprs)

  def sd(self, deviations):
    sd = 0.0
    for deviation in deviations:
      sd += deviation**2
    return math.sqrt(sd)

  def deviations(self, exprs, mean):
    return [expr - mean for expr in exprs]

  def covariance(self, target_deviations, subject_deviations):
    covar = 0.0
    for target, subject in zip(target_deviations, subject_deviations):
      covar += target * subject
    return covar

  def get(self):
    # Start of calcation coexpression gene
    # I use the webapp framework to retrieve the keyword
    keyword = self.request.get('keyword')

    if not keyword:
      result = "No keyword has been set"
    else:
      # Search the 'Expression' Entity based on our keyword
      # get log2 ratio expressions of target gene
      query = search.SearchableQuery('Expression')
      query.Search(keyword)
      for result in query.Run():
         target_gene_exprs = [result['ppargox_day' + suffix]-result['evector_day' + suffix] for suffix in ["0", "2", "4", "10"]]

      target_mean       = self.mean(target_gene_exprs)
      target_deviations = self.deviations(target_gene_exprs, target_mean)
      target_sd         = self.sd(target_deviations)

      # get log2 ratio expressions of subject genes
      coexpression_genes = []
      subject_genes = db.GqlQuery("SELECT * FROM Expression")
      for subject_gene in subject_genes:
        # bad code ;-)
        subject_gene_exprs = [subject_gene.ppargox_day0  - subject_gene.evector_day0,
                              subject_gene.ppargox_day2  - subject_gene.evector_day2,
                              subject_gene.ppargox_day4  - subject_gene.evector_day4,
                              subject_gene.ppargox_day10 - subject_gene.evector_day10]

        # calc corr.
        subject_mean       = self.mean(subject_gene_exprs)
        subject_deviations = self.deviations(subject_gene_exprs, subject_mean)
        subject_sd         = self.sd(subject_deviations)

        covar = self.covariance(target_deviations, subject_deviations)
        cor = covar / (subject_sd * target_sd)

        # filtering
        if math.fabs(cor) >= 0.9:
          coexpression_genes.append({'affy_id': subject_gene.affy_id,
                                     'gene_symbol': subject_gene.gene_symbol,
                                     'cor': cor})

      template_values = {'coexpression_genes': coexpression_genes,
                         'keyword': keyword}
      path = os.path.join(os.path.dirname(__file__), 'coexpression.html')
      self.response.out.write(template.render(path, template_values))


application = webapp.WSGIApplication(
                                     [('/', MainPage),
                                      ('/search', IdSearchForm),
                                      ('/coexpression', Coexpression)],
                                     debug=True)

def main():                                       
  run_wsgi_app(application)

if __name__ == "__main__":
  main()
