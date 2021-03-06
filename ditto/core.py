#!/usr/bin/python
from command import Command,Arg,execute_command,register_command,ValueList
import issues
import tempfile
import subprocess
import os
import sys

@register_command
class Init(Command):
    name = "init"
    description= "Initializes a new project."
    arguments = [
        Arg("folder","f","Folder to store issues in"),
        Arg("username","u","user name (unique and short)"),
        Arg("name","n","Full name"),
        Arg("email","e","Email Address"),
        Arg("project","p","Project Name"),
        ]

    def action(self):
        self.cond_prompt_arg("folder")
        self.cond_prompt_arg("username")
        self.cond_prompt_arg("name")
        self.cond_prompt_arg("email")

        if not os.path.exists(self.argument_values.folder):
            self.cond_prompt_arg("project")

        issues.create_project(self.argument_values.folder,
        self.argument_values.project,
        self.argument_values.username,
        self.argument_values.name,
        self.argument_values.email)

@register_command
class AddIssueCommand(Command):
    name = "add"
    description= "Add a new issue."
    arguments = [
        Arg("title","t","Issue title"),
        Arg("description","d","Issue description",large=True),
        Arg("estimate","e","Estimated time(h)",float),        
        Arg("release","r","Release",issues.release_name_or_blank),
        Arg("owner","o","Owner",str),
        ]

    def action(self):
        project = issues.get_project()
        self.prompt_all_args()

        issue = project.add_issue()
        issue.set_value("title",self.argument_values.title)
        issue.set_value("description",self.argument_values.description)        
        issue.set_value("estimate",self.argument_values.estimate)
        issue.set_value("release",self.argument_values.release)
        issue.set_value("owner",self.argument_values.owner)
        issue.set_value("state","open")
        project.save_issue(issue)

@register_command
class RemoveIssueCommand(Command):

    name = "remove"
    description= "Remove an issue."
    arguments = [
        Arg("name","n","Issue name",issues.issue_name),
        ]

    def action(self):
        project = issues.get_project()
        self.prompt_all_args()
        issue = project.get_issue(self.argument_values.name)
        project.remove_issue(issue)

@register_command
class CloseIssueCommand(Command):

    name = "close"
    description= "Close an issue."
    arguments = [
        Arg("name","n","Issue to close",issues.issue_name),
        Arg("time","t","Actual time to complete issue(decimal or time format)",str),
        ]

    def action(self):
        project = issues.get_project()
        self.prompt_all_args()
        issue = project.get_issue(self.argument_values.name)
        issue.set_value("state","closed")
        issue.set_value("actual",self.normalize_time(self.argument_values.time))
        project.save_issue(issue)

    def normalize_time(self, time):
        """accepts times in decimal format (eg 1.5) or time format (eg
        1:30) and returns it in decimal format"""
        try:
            time.index(":")
            parts = time.split(":")
            return "%.3f" % (float(parts[0]) + (float(parts[1]))/60)
        except ValueError:
            return time

@register_command
class EstimateIssueCommand(Command):
    name = "estimate"
    description= "Change an issues time estimate."
    arguments = [
        Arg("name","n","Issue whose time to estimate:",issues.issue_name),
        Arg("time","t","Estimated time to complete issue(h)",float),
        ]

    def action(self):
        project = issues.get_project()
        self.prompt_all_args()

        issue = project.get_issue(self.argument_values.name)
        issue.set_value("estimate",self.argument_values.time)
        project.save_issue(issue)

@register_command
class OpenIssueCommand(Command):

    name = "open"
    description= "Open an issue."
    arguments = [
        Arg("name","n","Issue to open",issues.issue_name),
        ]

    def action(self):
        project = issues.get_project()
        self.prompt_all_args()
        issue = project.get_issue(self.argument_values.name)
        issue.set_value("state","open")
        project.save_issue(issue)

@register_command
class ShowIssueCommand(Command):
    name = "show-issue"
    description = "Show issue "
    arguments = [
        Arg("name", "n", "Issue to show: ", issues.issue_name),
        ]

    def action(self):
        project = issues.get_project()
        self.cond_prompt_arg("name")
        issue = project.get_issue(self.argument_values.name)
        print(issue.detailed_summary())

@register_command
class EditIssueCommand(Command):

    name = "edit-issue"
    description= "Edit a Issue "
    arguments = [
        Arg("name","n","Issue to edit:",issues.issue_name),
        ]

    def action(self):
        project = issues.get_project()
        self.cond_prompt_arg("name")
        issue = project.get_issue(self.argument_values.name)
        file_name = issue._filename
        try:
            editor = os.environ['EDITOR']
        except KeyError:
            editor = 'nano'

        subprocess.call([editor, file_name])


@register_command
class AddReleaseCommand(Command):

    name = "add-release"
    description= "Add a new release."
    arguments = [
        Arg("name","n","Release name",issues.not_release_name),
        Arg("description","d","Release description",large=True),
        ]

    def action(self):
        project = issues.get_project()
        self.prompt_all_args()
        release = project.add_release()
        release.set_value("name",self.argument_values.name)
        release.set_value("description",self.argument_values.description)
        project.save_release(release)

@register_command
class AssignReleaseCommand(Command):

    name = "assign-release"
    description= "Assign an issue to a release."
    arguments = [
        Arg("issue","i","Issue to assign",issues.issue_name),
        Arg("release","r","Release to assign to",issues.release_name_or_blank),
        ]

    def action(self):
        project = issues.get_project()
        self.prompt_all_args()
        issue = project.get_issue(self.argument_values.issue)
        issue.set_value("release",self.argument_values.release)
        project.save_issue(issue)

@register_command
class AssignOwnerCommand(Command):

    name = "owner"
    description= "Assign an issue an owner."
    arguments = [
        Arg("issue","i","Issue to assign",issues.issue_name),
        Arg("owner","o","Owner to assign to",str),
        ]

    def action(self):
        project = issues.get_project()
        self.prompt_all_args()
        issue = project.get_issue(self.argument_values.issue)
        issue.set_value("owner",self.argument_values.owner)
        project.save_issue(issue)

@register_command
class DescribeReleaseCommand(Command):

    name = "release-description"
    description= "Edit a releases description."
    arguments = [
        Arg("release","r","Release to describe",issues.release_name_or_blank),
        ]

    def action(self):
        project = issues.get_project()
        self.cond_prompt_arg("release")
        release = project.get_release(self.argument_values.release)
        t = tempfile.NamedTemporaryFile(delete=False)
        t.write(release.get_value('description'))
        t.close()
        try:
            editor = os.environ['EDITOR']
        except KeyError:
            editor = 'nano'
        subprocess.call([editor, t.name])
        t = open(t.name)
        raw_val = t.read()
        release.set_value('description',raw_val)
        project.save_release(release)

@register_command
class ListIssuesCommand(Command):
    name = "list"
    description= "List all issues."
    alternate_names = ["ls"]
    
    arguments = [
        Arg("display","d","issues to display (a) all,(o) open,(c) closed"),
        Arg("release","r","show only issues for a release",issues.release_name_or_blank),
        Arg("owner","o","show only issues for an owner",str),
        ]

    def action(self):
        display = self.argument_values.display
        if display == None:
            display = 'o'
        owner = self.argument_values.owner
        
        project = issues.get_project()
        for issue in project._issues:
            if self.argument_values.release == None or self.argument_values.release == issue.release:
                if display =="a" or (issue.state.lower()[0] == display.lower()[0]):
                    if owner == None or owner.lower() == issue.owner.lower():
                        print issue.summary()

@register_command
class ReleaseSummaryCommand(Command):
    name = "release-summary"
    alternate_names = ["rs"]
    description= "Create a summary of a release."

    arguments = [
        Arg("release","r","show only issues for a release(or part of the name)",issues.release_name_or_blank),
        Arg("format","f","output format",ValueList("dokuwiki","console"),default = "console"),
        ]

    def action(self):
        self.cond_prompt_arg("release")
        if self.argument_values.format == "dokuwiki":
            self.dokuwiki_output()
        else:
            self.console_output()

    def dokuwiki_output(self):
        project = issues.get_project()
        if self.argument_values.release!="":
            release = project.get_release(self.argument_values.release)
            release_name = release.name()
            print("====== {0} ======".format(release.name()))

            stats = release.statistics()
            print("\n**Totals:**")
            print("  * Total Estimated Work: {0}h".format(stats[0]+stats[1]))
            print("  * Estimated Work Completed: {0}h".format(stats[0]))
            print("  * Actual Work Time: {0}h".format(stats[2]))
            print("  * Estimated Remaining Work: {0}h".format(stats[1]))
            print("  * Probable Remaining Time: {0}h".format(stats[3]))

            for owner in release.owners():
                stats = release.statistics(owner)
                print("\n**{0}:**".format(owner))
                print("  * Total Estimated Work: {0}h".format(stats[0]+stats[1]))
                print("  * Estimated Work Completed: {0}h".format(stats[0]))
                print("  * Actual Work Time: {0}h".format(stats[2]))
                print("  * Estimated Remaining Work: {0}h".format(stats[1]))
                print("  * Probable Remaining Time: {0}h".format(stats[3]))
                
            print("===== Description =====")
            print(release.description)
        else:
            release_name = ""
            print("====== {0} ======".format("Unassigned Issues"))

        print("===== Issues =====")
        print("==== Summary ====")
        print "^ID ^Title ^ Owner ^ Status ^ Estimated Time(h) ^Actual Time(h) ^ "
        for issue in project._issues:
            if release_name == issue.release:
                print("|[[#{id}|{id}]] |{title} |{owner} |{status} | {estimate} | {actual} |".format(id=issue.name,
                    title=issue.title,
                    status = issue.state,
                    estimate = issue.estimate,
                    owner = issue.owner,
                    actual = issue.actual if issue.state == "closed" else " "))
        
        print("==== Descriptions ====")
        for issue in project._issues:
            if release_name == issue.release:
                print("==={id}===".format(id=issue.name))
                print("**{title}**".format(title = issue.title))
                if issue.description!="":
                    print("")
                    print(issue.description)
                print("")
                if issue.owner !="":
                    print("  * Owner:{0}".format(issue.owner))
                print("  * Status:{0}".format(issue.state))
                print("  * Estimate:{0}".format(issue.estimate))
                if issue.state == "closed":
                    print("  * Actual(h):{0}".format(issue.actual))

    def console_output(self):
        project = issues.get_project()
        if self.argument_values.release!="":
            release = project.get_release(self.argument_values.release)
            release_name = release.name()
            
            print("Release: {0}".format(release.name()))
        else:
            release_name = ""
            print("{0}".format("Unassigned Issues:"))

        for issue in project._issues:
            if release_name == issue.release:
                print(issue.summary())

        if self.argument_values.release!="":
            release = project.get_release(self.argument_values.release)
            stats = release.statistics()
            print("\nOverall:")
            print("  * Total Estimated Work: {0}h".format(stats[0]+stats[1]))
            print("  * Estimated Work Completed: {0}h".format(stats[0]))
            print("  * Actual Work Time: {0}h".format(stats[2]))
            print("  * Estimated Remaining Work: {0}h".format(stats[1]))
            print("  * Probable Remaining Time: {0}h".format(stats[3]))
        
            for owner in release.owners():
                stats = release.statistics(owner)
                print("\n{0}:".format(owner))
                print("  * Total Estimated Work: {0}h".format(stats[0]+stats[1]))
                print("  * Estimated Work Completed: {0}h".format(stats[0]))
                print("  * Actual Work Time: {0}h".format(stats[2]))
                print("  * Estimated Remaining Work: {0}h".format(stats[1]))
                print("  * Probable Remaining Time: {0}h".format(stats[3]))

def try_int(s):
    "Convert to integer if possible."
    try: return int(s)
    except: return s

def natsort_key(s):
    "Used internally to get a tuple by which s is sorted."
    import re
    return map(try_int, re.findall(r'(\d+|\D+)', s))

@register_command
class ListReleasesCommand(Command):
    name = "list-releases"
    description= "Lists the releases."
    alternate_names = ["lsr"]
    arguments = [ ]
    
    def action(self):
        project = issues.get_project()
        releases = [r for r in project.releases]
        def get_name(r):
            return natsort_key(r.name())
        releases.sort(key=get_name)
        for release in releases:
            print release.name()

@register_command
class GetGuidForId(Command):
    name = "get-guid"
    description= "Gets the guid for a specific issue id."
    arguments = [ Arg("name","n","Issue to get guid for",issues.issue_name), ]
    
    def action(self):
        project = issues.get_project()
        self.prompt_all_args()
        issue = project.get_issue(self.argument_values.name)
        sys.stdout.write(issue._guid)

@register_command
class NumberIssues(Command):
    name = "number-issues"
    description= "System function: Sets unique numbers for all issues ONLY runnable by the master numbering server"
    arguments = []

    def action(self):
        project = issues.get_project()
        project.set_issue_master_names()

def main():
    execute_command()

#def main():
#    import cProfile
#    cProfile.run('submain()', '/home/james/dittoprof')
    

if __name__ == "__main__":
    main()  
