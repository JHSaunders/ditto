Ditto
=====

Yet another distributed issue tracker

Author: James Saunders \<james.h.saunders@gmail.com\>

This is a python based issue tracker that operates in a similar manner to ditz or pitz. It is recoded completely to be very easy to extend and to be very light weight. The issue files are not compatible with either ditz or pitz. Currently this is very much a work in progress, it is tailored towards dokuwiki integration for the output.

Installation
------------

Installation uses distutils (I think), to run use:
    python setup.py install
it requires PyYaml and argparse

To do a development install use:
    python setup.py develop
This is a great option if you are making changes or often pull down the new version since it will only create symlinks to files in your development working tree so changes you make immediately affect the command line.

Overview
--------

Ditto manages issues. Issues have a title, description and estimated time to completion. Issues are automatically given names which are of the form [component][#] where # is an increasing number.These names are variable but should be used in the ditto commands. Issues are associated with components which are specific sections of a project. Issues are also associated with a release. A release is a collection of issues that must be completed for some feature to be implemented, the equivalent of a sprint in the agile world. As previously stated, issues have time estimates, and when closed are given an actual time to completion.

ditto is purely command line based, which makes it fast to use for programmers. To use ditto you first have to 'ditto init', this will ask for your details and the location you wish to store ditto issues (usually .issues). If an issues folder and a project already exists the project will not be overwritten but simply linked to. Run this command in the root folder of your repository. Once that is done you can run 'ditto help' for a list of available commands.

The important ones you will need are:

* ditto add-component : Adds a component to the project
* ditto add-release: Adds a release to the project
* ditto add: Add and issue
* ditto remove: Remove an issue
* ditto close: Closes an issue
* ditto open: Reopens a closed issue
* ditto list: Lists issues
* ditto release-summary: Creates a summary of a release either for the console or in dokuwiki syntax, this can be used to automatically publish to dokuwiki site on a git post-recieve hook.

