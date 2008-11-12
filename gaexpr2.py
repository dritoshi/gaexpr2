import wsgiref.handlers

from google.appengine.ext import webapp
from google.appengine.ext import search
from google.appengine.ext.webapp.util import run_wsgi_app

class MainPage(webapp.RequestHandler):
  def get(self):
      
    url = "http://chart.apis.google.com/chart?cht=lxy&chco=1E5692,3E9A3B&chs=200x125&chxt=x,y&chxl=0:|0|2|4|6|8|10|1:|2|4|6|8|10&chds=0,10,2,10,0,10,2,10&chd=t:"

    self.response.headers['Content-Type'] = 'text/html'
    self.response.out.write('<html><body>')
    
    # I use the webapp framework to retrieve the keyword
    keyword = self.request.get('keyword')

    if not keyword:
      self.response.out.write("No keyword has been set")
    else:
      # Search the 'Expression' Entity based on our keyword
      query = search.SearchableQuery('Expression')
      query.Search(keyword)
      for result in query.Run():
         # Annotation
         self.response.out.write('<div><pre>')
         self.response.out.write('Affy ID: %s\n'     % result['affy_id'])
         self.response.out.write('Gene Symbol: %s\n' % result['gene_symbol'])
         self.response.out.write('Gene Name: %s\n'   % result['gene_name'])
         self.response.out.write('Entrez Gene: <a href="http://www.ncbi.nlm.nih.gov/sites/entrez?db=gene&cmd=Retrieve&dopt=full_report&list_uids=%s">' % result['entrezid'] + "%s</a>\n" % result['entrezid'])
         self.response.out.write('</pre></div>')
         
         # Graph (Using Google Chart API)
         evector = ",".join([`result['evector_day' + suffix]` for suffix in ["0", "2", "4", "10"]])
         ppargox = ",".join([`result['ppargox_day' + suffix]` for suffix in ["0", "2", "4", "10"]])
         graph = url + "0,2,4,10|" + evector + "|0,2,4,10|" + ppargox
         self.response.out.write('<img src="%s">' % graph)

    self.response.out.write('<div><a href="search">Back</a></div>')
    self.response.out.write('</body></html>')
    
class IdSearchForm(webapp.RequestHandler):
  def get(self):
    self.response.headers['Content-Type'] = 'text/html'
    self.response.out.write("""
      <html>
        <body>
          <h1>Gene Expression Database</h1>
          <form action="/" method="get">
            <div>
              Keyword: <input type="text" name="keyword" rows="1" cols="12">
              <input type="submit" value="Search"> (ex. 100005_at, Traf4)
            </div>
          </form>
          <hr/>
          <a href="http://itoshi.tv/">Itoshi NIKAIDO, Ph. D.</a>, dritoshi at gmail dot com
          <div>
            <img src="http://code.google.com/appengine/images/appengine-silver-120x30.gif" alt="Powered by Google App Engine" />
          </div>
        </body>
      </html>""")


application = webapp.WSGIApplication(
                                     [('/', MainPage),
                                      ('/search', IdSearchForm)],
                                     debug=True)

def main():                                       
  run_wsgi_app(application)

if __name__ == "__main__":
  main()
