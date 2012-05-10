import os
import sys
sys.path.append(os.getenv('PYTHON_PKGS'))
import nose 
import nose.config


myconfig = os.path.join(os.getcwd(), 'tests.sikuli', 'nose.cfg')
nose.config.config_files = [myconfig]
c = nose.config.Config()
c.configure()
nose.run()

