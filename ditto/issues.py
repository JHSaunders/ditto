import json
import uuid
import os
import warnings
from datetime import datetime

warnings.simplefilter('ignore')

_issues_config_dir = None
def set_issues_config_dir(issues_config_dir):
    global _issues_config_dir
    _issues_config_dir = issues_config_dir

class DateEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return str(obj)
        return json.JSONEncoder.default(self, obj)

def create_project(folder,project_name,username,name,email):
    config_stream = file('.issue-config.json', 'w')
    json.dump({"folder":folder,"username":username,"name":name,"email":email},config_stream,cls = DateEncoder)
    config_stream.close()

    try:
        os.mkdir(folder)
        print("New folder %s created for issues"%folder)
        project_stream = file('%s/project.json'%folder, 'w')
        json.dump({"project_name":project_name,"started":datetime.now()},project_stream,cls = DateEncoder)
        project_stream.close()
        print("New project started")
    except Exception as e:
        pass

__project = None
def get_project():
    """issues_config_dir only necessary if get_project has not
    been called at least once and the config file is in a non-standard
    location"""
    global __project
    global _issues_config_dir
    if __project == None:
        if _issues_config_dir is None:
            root_dir = os.getcwd()
            while not os.path.exists(os.path.join(root_dir,".issue-config.json")):
                if len(root_dir) == 0:
                    raise Exception("Couldn't find .issue-config.json in %s or its parents" % root_dir)
                root_dir = os.sep.join(root_dir.split(os.sep)[:-1])
        else:
            if not os.path.exists(_issues_config_dir):
                raise Exception("custom _issues_config_dir not found at %s" % _issues_config_dir)
            if not os.path.exists(os.path.join(_issues_config_dir, ".issue-config.json")):
                raise Exception("custom issues_config file not found in %s" % _issues_config_dir)
            root_dir = _issues_config_dir
        __project = Project(root_dir)
    return __project

class Project:
    def __init__(self,root_folder):
        config = json.load(file(os.path.join(root_folder,".issue-config.json")))
        self._config = config
        self._root_folder = root_folder
        self._issue_folder = config["folder"]
        self._json = json.load(file(os.path.join(root_folder,self._issue_folder,"project.json")))
        self._issues = []
        self._releases = []
        for fname in os.listdir(os.path.join(root_folder,self._issue_folder)):
            if fname.startswith("issue-") and fname.endswith(".json"):
                guid = fname[6:-5]
                self._issues.append(Issue(project=self
                    ,guid=guid
                    ,filename = os.path.join(root_folder,self._issue_folder,fname)
                    ,json=json.load(file(os.path.join(root_folder,self._issue_folder,fname)))))
            elif fname.startswith("release-") and fname.endswith(".json"):
                guid = fname[8:-5]
                release = Release(project=self
                    ,guid=guid
                    ,json=json.load(file(os.path.join(root_folder,self._issue_folder,fname))))
                self._releases.append(release)

        self._issues.sort(key=lambda issue: issue.get_creation_date())
        self.set_issue_names()

    def save_project(self):
        json.dump(self._json,
            file(os.path.join(self._root_folder,self._issue_folder,"project.json"),'w'),cls = DateEncoder)

    def save_issue(self,issue):
        json.dump(issue._json,
            file(os.path.join(self._root_folder,self._issue_folder,"issue-"+issue._guid+".json"),'w'),cls = DateEncoder)

    def save_release(self,release):
        json.dump(release._json,
            file(os.path.join(self._root_folder,self._issue_folder,"release-"+release._guid+".json"),'w'),cls = DateEncoder)

    def set_issue_names(self):
        component_counts = {}
        for issue in self._issues:
            component = issue.get_value("component")
            if component not in component_counts:
                component_counts[component]=0
            component_counts[component]+=1

            issue.name = issue.get_value("master_name")
            if issue.name is None:
                issue.name = "t_%s%s"%(component[0:2],component_counts[component])
            
    def set_issue_master_names(self):
        component_counts = {}

        if "is_master_name_server" not in self._config or self._config["is_master_name_server"] != "yes":
            raise Exception("You are not a master name server, don't call this function!")

        if "master_name_server" not in self._config or self._config["master_name_server"] is None:
            raise Exception("Badly configured master name server, missing config option [master_name_server]")

        def generate_master_name(x):
            return "ditto%d" % x

        for issue in self._issues:
            if issue.get_value("master_name") is None:
                master_name_candidate_id = len(self._issues)
                while self.is_issue_name(generate_master_name(master_name_candidate_id)):
                    master_name_candidate_id += 1
                issue.set_value("master_name", generate_master_name(master_name_candidate_id))
                issue.set_value("master_name_server", self._config["master_name_server"])
                self.save_issue(issue)

    def add_issue(self):
        guid = str(uuid.uuid1())
        issue = Issue(project=self,guid=guid,json=[],filename="")
        self._issues.append(issue)
        return issue

    def add_release(self):
        guid = str(uuid.uuid1())
        release = Release(project=self,guid=guid,json={})
        self._releases.append(release)
        return release

    def remove_issue(self,issue):
        try:
            os.remove(os.path.join(self._root_folder,self._issue_folder,"issue-"+issue._guid+".json"))
        finally:
            self._issues.remove(issue)

    def user_string(self):
        return "%s (%s) <%s>"%(self._config["username"],self._config["name"],self._config["email"])

    def get_value(self,key):
        return self._json.get(key,None)

    def set_value(self,key,value):
        self._json[key] = value

    def append_value(self,key,value):
        if key not in self._json:
            self._json[key] = []
        self._json[key].append(value)

    def attribute_contains(self,key,value):
        if key not in self._json:
            return False
        else:
            return value in self._json[key]

    def get_issue(self,name):
        for issue in self._issues:
            if issue.name==name:
                return issue
        return None

    def get_release(self,name):
        for release in self._releases:
            if release.name().find(name)!=-1:
                return release
        return None

    def get_root_folder(self):
        return self._root_folder
    
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
        self._json = kwargs["json"]
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
        self._json.append({"key":key,"value":str(value),"user":self._project.user_string(),"timestamp":datetime.now()})

    def get_value(self,key,default=None):
        value=default
        for entry in self._json:
            if entry["key"] == key:
                value = entry["value"]
        return value

    def get_issue_name(self):
        return self.name

    def get_creation_date(self):
        return self._json[0]["timestamp"]

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

    def detailed_summary(self):
        summary = self.summary()
        summary += "\n%s " % self.description
        return summary


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
        self._json = kwargs["json"]
        self._project = kwargs["project"]        
        self.properties = {
            "name": str,
            "description": str,
            }
        
    def name(self):
        return self._json["name"]

    def get_value(self,key,default=None):
        return self._json.get(key,default)

    def set_value(self,key,value):
        self._json[key] = value

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
