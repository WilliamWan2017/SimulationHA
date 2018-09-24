# -*- coding: utf-8 -*-
"""
Created on Wed Aug 29 09:21:02 2018

@author: william
"""
import re as standardre
from sympy import *
from sympy.parsing.sympy_parser import parse_expr 
#sympy.parsing.latex.parse_latex(s)[、、]
from sympy.abc import x,y,z,a,b,c,f,t,k,n
import json 
from latex2sympy.process_latex import process_sympy
import sys

def formatParseLatex4Design(strLatex):
    strLatex=strLatex.replace('$', '')
    str1=strLatex.split('=')
    leftEquation=format4Design(str1[0])
    rightEquation=format4Design(str1[1] )
    return leftEquation,rightEquation
 
def formatParseLatex4Code(strLatex,Variables):
    str1=strLatex.split('=')
    leftEquation,variableName=format4SoruceCode(str1[0],Variables)
    rightEquation,variableName2=format4SoruceCode(str1[1],Variables )
    return leftEquation,rightEquation,variableName
    
def format4Design(strLatex):
    strResult=formatSinglePart(strLatex)
    strResult=formatVariableName(strResult)
    strResult=formatDot(strResult)
    return strResult

def format4SoruceCode(strLatex,Variables):
    strResult=format4Design(strLatex)
    VariableName=getContinuousVariable(strResult,Variables)
    strResult=formatSympify(strResult)
    strResult=formatContinuourVariable(strResult,Variables)
    return strResult,VariableName


def formatSinglePart(strLatex):
    strEquation=str(process_sympy(strLatex))
    if "dot*" in strEquation:
        strEquation=formatDot(strEquation)
    if "_{" in strEquation:
        strEquation=formatVariableName(strEquation)
    return strEquation

def formatDot(strEquation):
    p=standardre.compile("(dot\*)([e-zE-Z0-9][a-zA-Z0-9]*)([^a-zA-Z0-9]|$)")
    if standardre.search(p, strEquation ):
        return p.sub(r"diff(\2)\3",strEquation)
    p=standardre.compile("([a-dA-D][a-zA-Z0-9]*)(\*dot)")
    return p.sub(r"diff(\1)",strEquation)

def formatVariableName(strEquation):
     p=standardre.compile(r'([a-zA-Z0-9])(_\{)([a-zA-Z0-9])(\})')
     return p.sub(r'\1\3',strEquation)

def formatSympify(strEquation):
    p=standardre.compile(r'([^\+\=\*/]*)([\+\=\*/])([^\+\=\*/]*)')
    strResult=''
    needMoreSympify=False
    AddOneSympify=False
    for tmp in p.split(strEquation):
        if "(" in tmp:
            tmp='S.sympify(\''+tmp+'\')'
            AddOneSympify=True 
        elif not tmp:
            needMoreSympify=True
        strResult+=tmp
    if needMoreSympify:
        strResult='S.sympify(\''+strResult+'\')' 
    elif not AddOneSympify:        
        strResult='S.sympify(\''+strResult+'\')' 
        
    #if "(" in strEquation:
    #    strResult='S.sympify(\''+strResult+'\')' 
    return strResult
def formatContinuourVariable(strEquation,Variables):
    #p=standardre.compile(r'(\()(x|y|t|pt)(\))')
    #strParttern=
    p=standardre.compile(r'(\()('+'|'.join(Variables)+r')(\))')
    return p.sub(r'\1\2(t)\3',strEquation)

def getContinuousVariable(strEquation,Variables):
    p=standardre.compile(r'(\()('+'|'.join(Variables)+r')(\))')
    searchG=standardre.search(p, strEquation )
    if searchG:
        return searchG.group(2)
    else:
        
        return '';
