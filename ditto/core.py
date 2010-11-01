#!/usr/bin/python
from command import Command,Arg,execute_command,register_command
import issues
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
        Arg("description","d","Issue description"),
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
        Arg("name","n","Issue to close:",issues.issue_name),
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
class CloseIssueCommand(Command):
    
    name = "open"
    description= "Open an issue."
    arguments = [
        Arg("name","n","Issue to close:",issues.issue_name),      
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
    description= "Add a new component"
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
    description= "Add a new release"
    arguments = [
        Arg("name","n","Release name",issues.not_release_name),
        Arg("description","d","Release description"),        
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
    description= "Add a new release"
    arguments = [
        Arg("name","n","Issue to assign",issues.issue_name),
        Arg("release","r","Release to assign to",issues.release_name_or_blank),        
        ]
        
    def action(self):
        project = issues.get_project()
        self.prompt_all_args()
        issue = project.get_issue(self.argument_values.name)
        issue.set_value("release",self.argument_values.release)
        project.save_issue(issue)

@register_command
class ListIssuesCommand(Command):
    name = "list"
    description= "List all issues"

    arguments = [
        Arg("display","d","issues to display (a) all,(o) open,(c) closed"),
        Arg("release","r","show only issues for a release",issues.release_name_or_blank),
        ]
    
    def action(self):
        display = self.argument_values.display
        if display == None:
            display = 'a'
        project = issues.get_project()
        for issue in project._issues:
            if self.argument_values.release == None or self.argument_values.release == issue.get_value("release",""):
                if display =="a" or (issue.get_value("state","open").lower()[0] == display.lower()[0]):           
                    print issue.summary()

@register_command
class ReleaseSummaryCommand(Command):
    name = "release-summary"
    description= "Create a summary of a release"

    arguments = [
        Arg("release","r","show only issues for a release",issues.release_name_or_blank),
        ]
    
    def action(self):
        self.prompt_all_args()
        project = issues.get_project()
        if self.argument_values.release!="":
            release = project.get_release(self.argument_values.release)            
            print("====== {0} ======".format(release.name()))                    
            print("===== Description =====")
            print(release.get_value("description"))
        else:
            print("====== {0} ======".format("Unassigned Issues"))                    
        
        print("===== Issues =====")
        print("==== Summary ====")
        print "^ID ^Title ^ Status ^ Estimated Time(h) ^Actual Time(h) ^ "
        for issue in project._issues:
            if self.argument_values.release == issue.get_value("release",""):
                print("|[[#{id}|{id}]] |{title} |{status} | {estimate} | {actual} |".format(id=issue.name,
                    title=issue.get_value("title"),
                    status = issue.get_value("state",""),
                    estimate = issue.get_value("estimate"),
                    actual = issue.get_value("actual","")))
        print("==== Descriptions ====")
        for issue in project._issues:
            if self.argument_values.release == issue.get_value("release",""):
                print("===={id}==== \n**Title:{title}**\n\nDescription: {description} \n\n  * Status:{status} \n  * Estimate: {estimate} \n  * Actual:{actual}".format(id=issue.name,
                    title=issue.get_value("title"),
                    description=issue.get_value("description"),
                    status = issue.get_value("state",""),
                    estimate = issue.get_value("estimate"),
                    actual = issue.get_value("actual","Not closed")))

def main():
    execute_command()      

if __name__ == "__main__":
    main()
