
#!/usr/bin/python
"""Html generators for the base uweb server"""

import uweb
import simplejson
import subprocess
import re
import os
import imp

class PageMaker(uweb.DebuggingPageMaker):
  """Holds all the html generators for the webapp

  Each page as a separate method.
  """

  def Index(self):
    """Returns the index.html template"""
    message = ''
    with open('/home/martijn/.uweb/sites.json', 'r') as f:
      sites = simplejson.load(f)
    if self.post.getfirst('action'):
      action = str(self.post.getfirst('action'))
      sitename = self.post.getfirst('site')
      if sitename != 'uwebmanager':
        router = sites[sitename]['router']
        workdir = sites[sitename]['workdir']
        subprocess.Popen(['python', '-m', router, action], cwd=workdir).wait()

    sites2 = []
    for key, value in sites.items():
      value['key'] = key
      #parts = value['router'].split('.')
      #a, b, c = imp.find_module(parts[0], [value['workdir']])
      #for part in parts[1:]:
      #  a, b, c = imp.find_module(part, b)
      #asdf
      filename = value['workdir'] + '/' + value['router'].replace('.', '/') + '.py'
      try:
        with open(filename, 'r') as f:
          code = f.read()
        m = re.search('PACKAGE = \'([a-z_]*)\'', code)
        packagename = m.group(1)
        routername = value['router'].split('.')[-1]
        pidfile = '/var/lock/underdark/' + packagename + '/' + routername + '.pid'
        if os.path.exists(pidfile):
          value['status'] = 'Running'
          value['class'] = 'success'
        else:
          value['status'] = 'Stopped'
          value['class'] = 'error'
      except:
        value['status'] = 'Dunno'
        value['class'] = ''
      sites2 = sites2 + [value]
    return self.parser.Parse('index.utp', sites=sites2, message=message)

  def FourOhFour(self, path):
    """The request could not be fulfilled, this returns a 404."""
    return uweb.Response(self.parser.Parse('404.utp', path=path),
                         httpcode=404)
