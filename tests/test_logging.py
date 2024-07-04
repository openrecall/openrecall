import pytest
import logging
import openrecall.log_config
import glob, os
from openrecall.log_config import setup_logging, set_logging_level

setup_logging()

def read_last_lines(file="openrecall.log",N=10):
    last_lines=[]
    with open(file,"r") as f:
        for line in f.readlines()[-N:]: 
            last_lines.append(line)
    return last_lines

def test_logfile_existence():
    file=glob.glob("openrecall.log",recursive=True)
    assert len(file)==1
    assert file[0]=="openrecall.log"

def test_logging():
    logging.error("this is a testmessage")
    file=glob.glob("openrecall.log",recursive=True)
    assert len(file)==1
    assert file[0]=="openrecall.log"
    last_line=read_last_lines(N=1)[0]
    assert(last_line.find("this is a testmessage")>0)

def test_set_logging_level():
    set_logging_level("WARNING")
    logging.warning("this is a message that should be displayed")
    last_line=read_last_lines(N=1)[0]
    assert(last_line.find("this is a message that should be displayed")>0)
    logging.info("this is a message that should NOT be displayed")
    last_line=read_last_lines(N=1)[0]
    assert(last_line.find("this is a message that should NOT be displayed")==-1)


