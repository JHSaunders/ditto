import yaml
import uuid
import os
import warnings
from datetime import datetime

warnings.simplefilter('ignore')

def create_project(folder,project_name,username,name,email):
    config_stream = file('.issue-config.yaml', 'w')
    yaml.dump({"folder":folder,"username":username,"name":name,"email":email},config_stream,default_flow_style=False)
    config_stream.close()

    try:
        os.mkdir(folder)
        print("New folder %s created for issues"%folder)
        project_stream = file('%s/project.yaml'%folder, 'w')
        yaml.dump({"project_name":project_name,"started":datetime.now()},project_stream,default_flow_style=False)
        project_stream.close()
        print("New project started")
    except Exception as e:
        pass

__project = None
def get_project():
    global __project
    if __project == None:
        root_dir = os.getcwd()
        while not os.path.exists(os.path.join(root_dir,".issue-config.yaml")):
            root_dir = os.sep.join(root_dir.split(os.sep)[:-1])
        __project = Project(root_dir)
    return __project

class Project:
    def __init__(self,root_folder):
        config = yaml.load(file(os.path.join(root_folder,".issue-config.yaml")))
        self._config = config
        self._root_folder = root_folder
        self._issue_folder = config["folder"]
        self._yaml = yaml.load(file(os.path.join(root_folder,self._issue_folder,"project.yaml")))
        self._issues = []
        self._releases = []
        for fname in os.listdir(os.path.join(root_folder,self._issue_folder)):
            if fname.startswith("issue-") and fname.endswith(".yaml"):
                guid = fname[6:-5]
                self._issues.append(Issue(project=self
                    ,guid=guid
                    ,filename = os.path.join(root_folder,self._issue_folder,fname)
                    ,yaml=yaml.load(file(os.path.join(root_folder,self._issue_folder,fname)))))
            elif fname.startswith("release-") and fname.endswith(".yaml"):
                guid = fname[8:-5]
                release = Release(project=self
                    ,guid=guid
                    ,yaml=yaml.load(file(os.path.join(root_folder,self._issue_folder,fname))))
                self._releases.append(release)

        self._issues.sort(key=lambda issue: issue.get_creation_date())
        self.set_issue_names()

    def save_project(self):
        yaml.dump(self._yaml,
            file(os.path.join(self._root_folder,self._issue_folder,"project.yaml"),'w'),
            default_flow_style=False)

    def save_issue(self,issue):
        yaml.dump(issue._yaml,
            file(os.path.join(self._root_folder,self._issue_folder,"issue-"+issue._guid+".yaml"),'w'),
            default_flow_style=False)

    def save_release(self,release):
        yaml.dump(release._yaml,
            file(os.path.join(self._root_folder,self._issue_folder,"release-"+release._guid+".yaml"),'w'),
            default_flow_style=False)

    def set_issue_names(self):
        component_counts = {}
        for issue in self._issues:
            component = issue.get_value("component")
            if component not in component_counts:
                component_counts[component]=0
            component_counts[component]+=1
            issue.name = "%s%s"%(component[0:2],component_counts[component])

    def add_issue(self):
        guid = str(uuid.uuid1())
        issue = Issue(project=self,guid=guid,yaml=[],filename="")
        self._issues.append(issue)
        return issue

    def add_release(self):
        guid = str(uuid.uuid1())
        release = Release(project=self,guid=guid,yaml={})
        self._releases.append(release)
        return release

    def remove_issue(self,issue):
        try:
            os.remove(os.path.join(self._root_folder,self._issue_folder,"issue-"+issue._guid+".yaml"))
        finally:
            self._issues.remove(issue)

    def user_string(self):
        return "%s (%s) <%s>"%(self._config["username"],self._config["name"],self._config["email"])

    def get_value(self,key):
        return self._yaml.get(key,None)

    def set_value(self,key,value):
        self._yaml[key] = value

    def append_value(self,key,value):
        if key not in self._yaml:
            self._yaml[key] = []
        self._yaml[key].append(value)

    def attribute_contains(self,key,value):
        if key not in self._yaml:
            return False
        else:
            return value in self._yaml[key]

    def get_issue(self,name):
        for issue in self._issues:
            if issue.name==name:
                return issue
        return None

    def get_release(self,name):
        for release in self._releases:
            if release.name()==name:
                return release
        return None

    @property
    def releases(self):
        return self._releases

    def is_issue_name(self,name):
        return self.get_issue(name) != None

    def is_release_name(self,name):
        return self.get_release(name) != None

def issue_name(name):
    if not get_project().is_issue_name(name):
        raise ValueError()
    return name

class Issue:
    def __init__(self, *args, **kwargs):
        self._guid = kwargs["guid"]
        self._yaml = kwargs["yaml"]
        self._project = kwargs["project"]
        self._filename = kwargs["filename"]
        self.properties = {
            "title": str,
            "description": str,
            "release": release_name,
            "component": component_name,
            "state": issue_state_name,
            }
    

    def set_value(self,key,value):
        self._yaml.append({"key":key,"value":str(value),"user":self._project.user_string(),"timestamp":datetime.now()})

    def get_value(self,key,default=None):
        value=default
        for entry in self._yaml:
            if entry["key"] == key:
                value = entry["value"]
        return value

    def get_issue_name(self):
        return self.name

    def get_creation_date(self):
        return self._yaml[0]["timestamp"]

    @property
    def state(self):
        return self.get_value("state",default="open")

    @property
    def estimate(self):
        return float(self.get_value("estimate",default=0))

    @property
    def actual(self):
        return float(self.get_value("actual",default=0))

    @property
    def description(self):
        return self.get_value("description",default="")

    @property
    def title(self):
        return self.get_value("title",default="")

    @property
    def release(self):
        release = self.get_value("release",default="")
        return release if get_project().is_release_name(release) else ""

    @property
    def component(self):
        component = self.get_value("component",default="")
        return component if get_project().attribute_contains("component",component) else ""

    @property
    def owner(self):
        owner = self.get_value("owner",default="")
        return owner

    def summary(self):
        owner = "({0:8})".format(self.owner) if self.owner!="" else "{0:10}".format("")
        if self.state=="open":
            return "\033[0m{0}\t(o):{1:<70} {2} e:{3}h\033[0m".format(self.name,self.title, owner, self.estimate)
        else:
            return "\033[31m{0}\t(c):{1:<70} {2} e:{3}h\ta:{4}h\033[0m".format(self.name,self.title, owner, self.estimate,self.actual)

def issue_state_name(name):
    if name not in ["open","closed"]:
        raise ValueError()
    return name
    
def component_name(name):
    if not get_project().attribute_contains("components",name):
        raise ValueError()
    return name

def not_component_name(name):
    if get_project().attribute_contains("components",name):
        raise ValueError()
    return name

def release_name(name):
    if not get_project().is_release_name(name):
        raise ValueError()
    return name

def release_name_or_blank(name):
    if not(name=="" or get_project().is_release_name(name)):
        raise ValueError()
    return name

def not_release_name(name):
    if get_project().is_release_name(name):
        raise ValueError()
    return name

class Release:
    def __init__(self, *args, **kwargs):
        self._guid = kwargs["guid"]
        self._yaml = kwargs["yaml"]
        self._project = kwargs["project"]        
        self.properties = {
            "name": str,
            "description": str,
            }
        
    def name(self):
        return self._yaml["name"]

    def get_value(self,key,default=None):
        return self._yaml.get(key,default)

    def set_value(self,key,value):
        self._yaml[key] = value

    def issues(self):
        return filter(lambda x: self.name() == x.release,get_project()._issues)

    @property
    def description(self):
        return self.get_value("description","")
    
    def owners(self):
        owners = set()
        for issue in self.issues():
            if issue.owner!="":
                owners.add(issue.owner)
        return owners

    def statistics(self,owner="-"):
        est_done = 0
        est_undone = 0
        actual_done = 0
        for issue in self.issues():
            if owner=="-" or issue.owner == owner:
                if issue.state == "closed":
                    est_done += float(issue.get_value("estimate",0))
                    actual_done += float(issue.actual)
                else:
                    est_undone += float(issue.estimate)

        if est_done>0:
            actual_undone = actual_done / est_done * est_undone
        else:
            actual_undone = est_undone

        return(est_done,est_undone,actual_done,actual_undone)
