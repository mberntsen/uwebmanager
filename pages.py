
#!/usr/bin/python
"""Html generators for the base uweb server"""

import uweb
import simplejson
import subprocess
import re
import os
import sys

class PageMaker(uweb.DebuggingPageMaker):
  """Holds all the html generators for the webapp

  Each page as a separate method.
  """

  def Index(self):
    """Returns the index.html template"""
    message = ''
    sites_file = os.path.expanduser('~/.uweb/sites.json')
    with open(sites_file, 'r') as f:
      sites = simplejson.load(f)
    postaction = self.post.getfirst('action', None)
    if postaction not in ('start', 'stop', 'restart', None):
      message = 'Invalid action (%s)' % postaction
    postsite = self.post.getfirst('site', None)
    if postsite == 'uwebmanager':
      postside = None
      message = 'Cannot manage the manager this way:)'

    sites2 = []
    for key in sorted(sites.keys()):
      value = sites[key]
      value['name'] = key
      if key == postsite:
        router = value['router']
        workdir = value['workdir']
        w = subprocess.Popen(['python', '-m', router, postaction], cwd=workdir).wait()
        if postaction in ('start', 'restart') and w == 0:
          value['status'] = 'Running'
        else:
          value['status'] = 'Stopped'
      else:
        paths = [value['workdir']] + sys.path
        for path in paths:
          filename = path + '/' + value['router'].replace('.', '/') + '.py'
          try:
            with open(filename, 'r') as f:
              code = f.read()
            m = re.search('PACKAGE = \'([a-z_]*)\'', code)
            packagename = m.group(1)
            routername = value['router'].split('.')[-1]
            pidfile = '/var/lock/underdark/' + packagename + '/' + routername + '.pid'
            if os.path.exists(pidfile):
              value['status'] = 'Running'
            else:
              value['status'] = 'Stopped'
            break
          except IOError:
            pass
          except:
            value['status'] = 'Dunno'
      sites2 = sites2 + [value]
    return self.parser.Parse('index.utp', sites=sites2, message=message, sites_file=sites_file)

  def FourOhFour(self, path):
    """The request could not be fulfilled, this returns a 404."""
    return uweb.Response(self.parser.Parse('404.utp', path=path),
                         httpcode=404)
