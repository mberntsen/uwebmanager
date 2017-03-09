
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
    with open('/home/martijn/.uweb/sites.json', 'r') as f:
      sites = simplejson.load(f)
    if self.post.getfirst('action'):
      action = self.post.getfirst('action')
      if action in ('start', 'stop', 'restart'):
        sitename = self.post.getfirst('site')
        if sitename != 'uwebmanager':
          router = sites[sitename]['router']
          workdir = sites[sitename]['workdir']
          subprocess.Popen(['python', '-m', router, action], cwd=workdir).wait()
        else:
          message = 'Cannot stop manager itself :)'
      else:
        message = 'Invalid action (%s)' % action

    sites2 = []
    for key, value in sites.items():
      value['key'] = key
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
            value['class'] = 'success'
          else:
            value['status'] = 'Stopped'
            value['class'] = 'error'
          break
        except IOError:
          pass
        except:
          value['status'] = 'Dunno'
          value['class'] = ''
      sites2 = sites2 + [value]
    return self.parser.Parse('index.utp', sites=sites2, message=message)

  def FourOhFour(self, path):
    """The request could not be fulfilled, this returns a 404."""
    return uweb.Response(self.parser.Parse('404.utp', path=path),
                         httpcode=404)
