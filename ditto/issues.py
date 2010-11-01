import yaml
import uuid
import os
import warnings
from datetime import datetime

warnings.simplefilter('ignore')

def create_project(folder,project_name,name,email):
    config_stream = file('.issue-config.yaml', 'w')
    yaml.dump({"folder":folder,"name":name,"email":email},config_stream,default_flow_style=False)
    config_stream.close()
    
    try:
        os.mkdir(folder)
        print("New folder %s created for issues"%folder)  
        project_stream = file('%s/project.yaml'%folder, 'w')
        yaml.dump({"project_name":project_name,"started":datetime.now()},project_stream,default_flow_style=False)        
        project_stream.close()
        print("new project started")
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
            issue.name = "%s-%s"%(component,component_counts[component])    
    
    def add_issue(self):
        guid = str(uuid.uuid1())
        issue = Issue(project=self,guid=guid,yaml=[])
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
        return "%s <%s>"%(self._config["name"],self._config["email"])
    
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
    
    def summary(self):
        if self.get_value("state","open")=="open":
            return "{0}\t(o):{1:<70} e:{2}h".format(self.name,self.get_value("title"), self.get_value("estimate"))
        else:
            return "{0}\t(c):{1:<70} e:{2}h\ta:{3}h".format(self.name,self.get_value("title"), self.get_value("estimate"),self.get_value("actual"))

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
       
    def name(self):
        return self._yaml["name"]
    
    def get_value(self,key):
        return self._yaml.get(key,None)
        
    def set_value(self,key,value):
        self._yaml[key] = value
