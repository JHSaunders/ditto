import sys
import argparse

commands = {}

def register_command(cls):
    """Registers a command as usable."""
    commands[cls.command_name()] = cls
    return cls

class Arg():
    """Defintion for an argument. Used to specify the arguments for a Command"""
    def __init__(self,name,switch,prompt="",type=str,default=""):
        self.name = name
        self.switch = switch
        self.prompt = prompt
        if prompt == "":
            prompt =name
        self.type = type
        self.default = default
        
class Command():
    """
    A Command. This implements a command line command. Its specifies the 
    arguments required as well as the name of the command. New commands should
    inherit from this and implement the action function as well as set up the
    name,description and arguments fields. 
    
    The arguments field is a list if Arg objects.
    """
    
    name="no_name"
    description= ""    
    arguments = []
    
    def __init__(self,argv):
        parser = self.setup_args()
        args = parser.parse_args(argv)
        self.argument_values = args       
                
    def setup_args(self):
        self.argument_map={}
        for arg in self.arguments:
            self.argument_map[arg.name] = arg
        parser = argparse.ArgumentParser(description=self.description,prog="%s %s"%(sys.argv[0], self.command_name()))
        for arg in self.arguments:
            parser.add_argument(*("--"+arg.name,"-"+arg.switch),**{"type":arg.type,"help":arg.prompt})
        return parser
    
    def prompt_arg(self,name):        
        """Prompt for the value of an argument"""
        while True:
            try:
                arg = self.argument_map[name]        
                raw_val = raw_input(arg.prompt+":")
                val = arg.type(raw_val)
                setattr(self.argument_values,arg.name, val)
                return val
            except Exception as e:
                print "Invalid value, please re-enter"
    
    
    def cond_prompt_arg(self,name):
        """Prompt for the value of an argument if it has not already been given"""
        if getattr(self.argument_values,name)==None:
            return self.prompt_arg(name)
        else:
            return getattr(self.argument_values,name)
            
    def prompt_all_args(self):
        """prompt for the values of all outstanding arguments"""
        for arg in self.arguments:
                self.cond_prompt_arg(arg.name)                
            
    def action(self):
        print "no action"
    
    @classmethod
    def command_name(cls):
        return cls.name

@register_command
class HelpCommand(Command):
    
    name = "help"
    description= "Display this help file"
    
    def action(self):
        print "Available Commands:"
        
        for command, cls in commands.items():
            print "  {0:<20}: {1}".format(command,cls.description)

def execute_command():
    """
    Executes a command the command name must be given as the first argument
    with the command arguments following.
    """
    
    command_name = sys.argv[1]
    if command_name in commands:
        command = commands[command_name](sys.argv[2:])
        command.action()
    else:
        print "Unknown command"
