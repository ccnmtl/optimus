#!/usr/bin/python
import urlparse, re


def path_join(base,file):
    # convert backslashes (but remember so we can convert back)
    use_backslashes = 0
    if base.find("\\") != -1 or file.find("\\") != -1:
        use_backslashes = 1
        base = base.replace("\\","/")
        file = file.replace("\\","/")
    # if we strip off any leading 'file:' urljoin
    # can handle it ok
    if base[:5] == 'file:':
        base = base.replace("file:","")
    if file[:5] == 'file:':
        file = file.replace("file:","")
        
    url = 0
    if file[:5] == "http:":
        # result will be a url not a file path
        url = 1
    # if it is a windows path, we strip off the drive letter
    # (saving it for later) 
    drive_pattern = re.compile(r"^[a-zA-Z]:")
    match = drive_pattern.match(file)
    drive = ""
    if match != None:
        drive = match.group()
        # file is an absolute windows path, we can just use it
        combined = file[2:]
    else:
        match = drive_pattern.match(base)
        if match != None:
            drive = match.group()
            base = base[2:]
        # let urljoin do the hard work
        combined = urlparse.urljoin(base,file)
        # tack back on a drive letter
        if drive != "" and not url:
            combined = drive + "//" + combined
    
    if use_backslashes and not url:
        # make sure that we have at most two slashes in a row
        pattern = re.compile(r"//{2,}")
        combined = pattern.sub("//",combined)
        # remove any double slashes except the one after C:
        pattern = re.compile(r"(?<!:)//")
        combined = pattern.sub("/",combined)
        # convert slashes back to backslashes
        combined = combined.replace("/","\\")
    return combined


if __name__ == "__main__":
    test_data = [("/home/anders/","file.py","/home/anders/file.py"), # normal unix path
    ("http://www.foo.com/bar/","file.py","http://www.foo.com/bar/file.py"), # basic url
    ("simulations/foo/","file.py","simulations/foo/file.py"), # relative paths
    ("C:\\\\program files\\foo\\","file.py","C:\\\\program files\\foo\\file.py"), # basic windows filenames
    ("/home/anders/foo/","../file.py","/home/anders/file.py"), # simple '..'
    ("simulations/foo/","../file.py","simulations/file.py"), # relative with '..'
    ("simulations/foo/","http://www.example.com/file.py","http://www.example.com/file.py"), # if the file is absolute, we just use that
    ("simulations/foo/","/foo/file.py","/foo/file.py"),
    ("C:\\\\program files\\foo\\","C:\\\\foo\\file.py","C:\\\\foo\\file.py"),
    ("simulations\\foo\\","file.py","simulations\\foo\\file.py"),
    ("file:simulations/foo/","file.py","simulations/foo/file.py"),
    ("file:/home/anders/","file.py","/home/anders/file.py"),
    ("file:/home/anders/","file:/foo/file.py","/foo/file.py"),
    ("file:/home/anders/","../file.py","/home/file.py"),
    ("file:/home/anders/","../../file.py","/file.py")
    ]

    
    for base,file,expected_result in test_data:
        actual_result = path_join(base,file)
        if actual_result == expected_result:
            print "pass"
        else:
            print "fail (%s,%s) returned %s" % (base,file,actual_result)

