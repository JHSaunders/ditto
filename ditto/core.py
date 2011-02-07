#!/usr/bin/python
from command import Command,Arg,execute_command,register_command,ValueList
import issues
import tempfile
import subprocess
import os

@register_command
class Init(Command):
    name = "init"
    description= "Initializes a new project."
    arguments = [
        Arg("folder","f","Folder to store issues in"),
        Arg("name","n","Full name"),
        Arg("email","e","Email Address"),
        Arg("project","p","Project Name"),
        ]

    def action(self):
        self.cond_prompt_arg("folder")
        self.cond_prompt_arg("name")
        self.cond_prompt_arg("email")

        if not os.path.exists(self.argument_values.folder):
            self.cond_prompt_arg("project")

        issues.create_project(self.argument_values.folder,
        self.argument_values.project,
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
        Arg("component","c","Component",issues.component_name),
        Arg("release","r","Release",issues.release_name_or_blank),
        ]

    def action(self):
        project = issues.get_project()
        self.prompt_all_args()

        issue = project.add_issue()
        issue.set_value("title",self.argument_values.title)
        issue.set_value("description",self.argument_values.description)
        issue.set_value("component",self.argument_values.component)
        issue.set_value("estimate",self.argument_values.estimate)
        issue.set_value("release",self.argument_values.release)
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
        Arg("time","t","Actual time to complete issue(h)",float),
        ]

    def action(self):
        project = issues.get_project()
        self.prompt_all_args()
        issue = project.get_issue(self.argument_values.name)
        issue.set_value("state","closed")
        issue.set_value("actual",self.argument_values.time)
        project.save_issue(issue)

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
class AddComponentCommand(Command):

    name = "add-component"
    description= "Add a new component."
    arguments = [
        Arg("name","n","Component name",issues.not_component_name),
        ]

    def action(self):
        project = issues.get_project()
        self.prompt_all_args()
        project.append_value("components",self.argument_values.name)
        project.save_project()

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

    arguments = [
        Arg("display","d","issues to display (a) all,(o) open,(c) closed"),
        Arg("release","r","show only issues for a release",issues.release_name_or_blank),
        ]

    def action(self):
        display = self.argument_values.display
        if display == None:
            display = 'o'
        project = issues.get_project()
        for issue in project._issues:
            if self.argument_values.release == None or self.argument_values.release == issue.release:
                if display =="a" or (issue.state.lower()[0] == display.lower()[0]):
                    print issue.summary()

@register_command
class ReleaseSummaryCommand(Command):
    name = "release-summary"
    alternate_names = ["rs"]
    description= "Create a summary of a release."

    arguments = [
        Arg("release","r","show only issues for a release",issues.release_name_or_blank),
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
            print("====== {0} ======".format(release.name()))

            stats = release.statistics()

            print("  * Total Estimated Work: {0}h".format(stats[0]+stats[1]))
            print("  * Estimated Work Completed: {0}h".format(stats[0]))
            print("  * Actual Work Time: {0}h".format(stats[2]))
            print("  * Estimated Remaining Work: {0}h".format(stats[1]))
            print("  * Probable Remaining Time: {0}h".format(stats[3]))

            print("===== Description =====")
            print(release.description)
        else:
            print("====== {0} ======".format("Unassigned Issues"))

        print("===== Issues =====")
        print("==== Summary ====")
        print "^ID ^Title ^ Status ^ Estimated Time(h) ^Actual Time(h) ^ "
        for issue in project._issues:
            if self.argument_values.release == issue.release:
                print("|[[#{id}|{id}]] |{title} |{status} | {estimate} | {actual} |".format(id=issue.name,
                    title=issue.title,
                    status = issue.state,
                    estimate = issue.estimate,
                    actual = issue.actual if issue.state == "closed" else " "))

        print("==== Descriptions ====")
        for issue in project._issues:
            if self.argument_values.release == issue.release:
                print("==={id}===".format(id=issue.name))
                print("**{title}**".format(title = issue.title))
                if issue.description!="":
                    print("")
                    print(issue.description)
                print("")
                print("  * Status:{0}".format(issue.state))
                print("  * Estimate:{0}".format(issue.estimate))
                if issue.state == "closed":
                    print("  * Actual(h):{0}".format(issue.actual))

    def console_output(self):
        project = issues.get_project()
        if self.argument_values.release!="":
            release = project.get_release(self.argument_values.release)
            print("Release: {0}".format(release.name()))
        else:
            print("{0}".format("Unassigned Issues:"))

        for issue in project._issues:
            if self.argument_values.release == issue.release:
                print(issue.summary())

        if self.argument_values.release!="":
            release = project.get_release(self.argument_values.release)
            stats = release.statistics()
            print("\nStatistics:")
            print("  * Total Estimated Work: {0}h".format(stats[0]+stats[1]))
            print("  * Estimated Work Completed: {0}h".format(stats[0]))
            print("  * Actual Work Time: {0}h".format(stats[2]))
            print("  * Estimated Remaining Work: {0}h".format(stats[1]))
            print("  * Probable Remaining Time: {0}h".format(stats[3]))



@register_command
class ListReleasesCommand(Command):
    name = "list-releases"
    description= "Lists the releases."
    arguments = [ ]

    def action(self):
        project = issues.get_project()
        for release in project.releases:
            print release.name()

def main():
    execute_command()

if __name__ == "__main__":
    main()
