#This can be used to automatically publish the release summaries to a dokuwiki
#Ideally used on a git post-recieve hook
#Set the {variables} to you purposes.

import os
import sys
os.chdir("{Location to execute from}")
from ditto import issues
from ditto.core import ReleaseSummaryCommand
target_dir = "{Location of dokuwiki pages namespace directory to publish to}"

for release in issues.get_project().releases:
    command = ReleaseSummaryCommand(["-r",release.name(),"-f","dokuwiki"])
    sys.stdout = open(target_dir+release.name()+".txt",'w')
    command.action()

sys.stdout = open(target_dir+"index"+".txt",'w')
print("======Releases======")
for release in issues.get_project("{issues folder name}").releases:
    print("  * [["+release.name()+"]]")
sys.stdout = sys.__stdout__

