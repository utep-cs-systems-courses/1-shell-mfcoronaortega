#Remember
# - pipe() The output of a process is the input to another. -> "|" symbol
# - fork()
# - dup() or dup2()
# - execve() (you cannot use execvp)
# - wait()
# - open() and close()
# - chdir()

# $PATH environment variable. <-- look this up

import os, sys, re


#global variables
availableCmmds = {
    "cd": "cd",
    "ls": "ls",
    "|": "|", #pipe
    "&": "&", #run in the background (wait4child = false# )
    "pwd": "pwd",
    ">": ">", #redirec
    "<": "<", #redirect
    "pwd": "pwd"
}

wait4Child = True
notFound = "Command not found.\n"
passing = "Passed Test  \n"
myInput = ""

#EXECUTE$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
def execute(someCmmd): #DONE
    pid = os.getpid()
    rc = os.fork()
    if rc < 0:
        os.write(2, ("fork failed, returning %d\n" % rc).encode())
        sys.exit(1)
    elif rc == 0:
        if "/" in someCmmd:
            program = someCmmd[0]
            try:
                os.execve(program,someCmmd, os.environ)
            except FileNotFoundError:
                pass
            os.write(2, "Unable to execute.".encode())
        for dir in re.split(':', os.environ['PATH']):
            program = '%s/%s' % (dir, someCmmd[0])
            try:
                os.execve(program, someCmmd, os.environ)
            except FileNotFoundError:
                pass
            os.write(2, "Unable to execute.".encode())
            sys.exit(1)
    elif rc > 0:
        if wait4Child:  # by default always wait for child
            os.wait()
        os.write(2, ("child finished\n").encode())

#REDIRECT$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
def redirect(someCmmd): #DONE
        if "<" in someCmmd: #checks input
            os.close(0)
            os.open(someCmmd[someCmmd.index('<')+ 1], os.O_RDONLY)
            os.set_inheritable(0, True)
            someCmmd.remove(someCmmd[someCmmd.index('<')+1])
            someCmmd.remove('<')
        if ">" in someCmmd: #checks output
            os.close(1)
            os.open(someCmmd[someCmmd.index('>') + 1], os.O_CREAT | os.O_WRONLY) #create or write only
            os.set_inheritable(1, True)
            someCmmd.remove(someCmmd[someCmmd.index('<') + 1])
            someCmmd.remove('>')

#PIPE$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
def pipe(someCmmd):
    read, write = os.pipe()
    rc = os.fork()
    left = someCmmd[:someCmmd.index('|')]
    right = someCmmd[someCmmd.index('|'+1):]

    if rc < 0:
        print("fork failed, returning %d\n" % rc, file=sys.stderr)
        sys.exit(1)
    elif rc == 0: #whatever is on the left executes
        os.close(1)
        os.dup(write)
        os.set_inheritable(1, True)
        for fd in (read, write):
            os.close(fd)
        execute(left)
        sys.exit(0)
    else:
        os.wait()
        os.close(0)
        os.dup(read)
        os.set_inheritable(0, True)

        for fd in (read, write):
            os.close(fd)
        if '|' in right:
            pipe(right)
        execute(right)
        sys.exit(1)






#INPUT_HANDLER$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
def input_handler(someCmmd):
    global wait4Child #Using global boolean
    global notFound

    # LIST OF COMMANDS
    if someCmmd[0] == "cd": #CHANGE DIRECTORY
        try:
            os.chdir(someCmmd[1])
        except FileNotFoundError:
            os.write(1, "No such directory.\n".encode())
    elif someCmmd[0] == "pwd":
        os.write(2, (os.getcwd() + "\n").encode())
    elif "|" in someCmmd:
        pipe(someCmmd)
    elif "&" in someCmmd:
        wait4Child = False
    elif "<" in someCmmd or ">" in someCmmd:
        redirect(someCmmd)
    else:
        execute(someCmmd)

#PROMPT$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
def prompt():
    global notFound
    global passing
    global myInput

    if 'PS1' in os.environ: #IF variable PS1 in bash exists, set prompt
        myPrompt = os.environ['PS1']
    else: #ELSE set prompt to default '$'
        myPrompt = '$'

    while myInput != "exit":
        myInput = input(os.getcwd() + myPrompt)
        cmmd = myInput.split() #parses user imput

        if len(cmmd) != 0:
            if cmmd[0] in availableCmmds:
                input_handler(cmmd)
                os.write(2, passing.encode())
            # IF not try executing (call execute)
            else:
                execute(cmmd)
                return
        else:
            os.write(2, notFound.encode())

    os.write(2, ("Terminating Shell\n").encode())
    sys.exit(1)

#RUN$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
def main():
    prompt()

if __name__ == '__main__':
        main()