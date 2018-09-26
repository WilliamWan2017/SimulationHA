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
    p=standardre.compile("(dot\*)([a-zA-Z0-9][a-zA-Z0-9]*)([^a-zA-Z0-9]|$)")
    if standardre.search(p, strEquation ):
        return p.sub(r"diff(\2)\3",strEquation)
    p=standardre.compile("([a-dA-Z][a-zA-Z0-9]*)(\*dot)")
    return p.sub(r"diff(\1)",strEquation)


def formatVariableName(strEquation):
     p=standardre.compile(r'([a-zA-Z0-9])(_\{)([a-zA-Z0-9])(\})')
     return p.sub(r'\1\3',strEquation)

def formatContinuourVariable(strEquation,Variables):
    #p=standardre.compile(r'(\()(x|y|t|pt)(\))')
    #strParttern=
    p=standardre.compile(r'(^|[^a-zA-Z0-9])('+'|'.join(Variables)+r')($|[^a-zA-Z0-9])')
    #return p.sub(r'\1\2(t)\3',strEquation)
    if "diff" in strEquation:        
        return p.sub(r"\1\2(t)\3",strEquation)
    else:            
        return p.sub(r"\1S.sympify('\2(t)')\3",strEquation)
def formatContinuourVariable_old(strEquation,Variables):
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
    
def formatSympifySubEquation(strEquation):
    p1=standardre.compile(r'([a-zA-Z]+)(\()([^()]*)(\))') 
    p2=standardre.compile(r'(^|[^a-zA-Z])(\()([^()]*)(\))')
     
    
    strTmp=strEquation#p.sub(r'#\2$',strEquation) 
    while '(' in strTmp: 
        strTmp=p1.sub(r"S.\1#\3$",strTmp)   
        strTmp=p2.sub(r"\1#\3$",strTmp)       
    strTmp=strTmp.replace('#','(')
    strTmp=strTmp.replace('$',')')    
    return strTmp
   
   
def formatSympifySubEquation_old(strEquation):
    sympyEquation=['exp','sum','prod','log','ln','sin','cos','tan','csc','sec',
                   'cot','arcsin','arccos','arctan','arccsc','arcsec','arccot',
                   'sinh','cosh','tanh','arcsinh','arccosh','arctanh','sqrt',
                   'times','cdot','div','frac','mathit'
                   ]
      

    p=standardre.compile(r'(^|[^a-zA-Z0-9])('+'|'.join(sympyEquation)+r')($|[^a-zA-Z0-9])')   
    return p.sub(r'\1S.\2\3',strEquation)
def formatSympify(strEquation):
    
    
    p=standardre.compile(r'^([0-9.]+)$')
    if (p.match(strEquation)):   
        return 'S.sympify(\''+strEquation+'\')'    
    p=standardre.compile(r'^([a-zA-Z0-9]+)$')
    if (p.match(strEquation)):   
        return 'S.sympify('+strEquation+')'
    p=standardre.compile(r'^([\(\)a-zA-Z0-9]+)$')
    if (p.match(strEquation)):   
        return 'S.sympify(\''+strEquation+'\')'   
    else: 
        return 'S.sympify('+formatSympifySubEquation(strEquation)+')'

def formatSympify_old(strEquation):
    isMustAddSym=False
    p=standardre.compile(r'(\()([^()]*)(\))')
    p2=standardre.compile(r'([\w]*)(\()([^()]*)(\))')
    p3=standardre.compile(r'([\w]*)(\()([^()]*)(\))')
    strTmp=strEquation#p.sub(r'#\2$',strEquation)
    if (not p3.match(strTmp)):
        isMustAddSym=True
    else:
        isMustAddSym=False
    strTmp=p2.sub(r"S.sympify#'\1#\3$'$",strTmp)
    while '(' in strTmp:            
        if (not p3.match(strTmp)):
            isMustAddSym=True
        else:
            isMustAddSym=False 
        strTmp=p2.sub(r"S.sympify#\1#\3$$",strTmp)       
    strTmp=strTmp.replace('#','(')
    strTmp=strTmp.replace('$',')')    
    if isMustAddSym:
        if "S.sympify" in strTmp:
            strTmp='S.sympify('+strTmp+')' 
        else:
            if not "(" in strTmp:
                strTmp='S.sympify('+strTmp+')'
            else:
                strTmp='S.sympify(\''+strTmp+'\')'
    return strTmp
 
def formatBlockName(strLine):
    p=standardre.compile(r'Block Begin (.*)\$')
    return p.search(strLine).group(1)
    
