# -*- coding: utf-8 -*-
"""
Created on Thu Mar 28 14:16:56 2024

@author: Aparna
"""
ANNOTATION_SETTINGS = dict(
    K=dict(
        html_class='enzyme',
        type='KEGG Gene',        
        rest_file='ko',
        descr_prefix='ko:'),
    EC=dict(
        html_class='enzyme',
        type='Enzyme Commission',        
        rest_file='enzyme',
        descr_prefix='ec:'),
    R=dict(
        html_class='enzyme',
        type='KEGG Reaction',
        
        rest_file='rn',
        descr_prefix='rn:'),
    RC=dict(
        html_class='enzyme',
        type='KEGG Reaction Class',
        
        rest_file='rc',
        descr_prefix='rc:'),
    C=dict(
        html_class='compound',
        type='KEGG Compound',
        rest_file='compound',
        descr_prefix='cpd:'),
    G=dict(
        html_class='compound',
        type='KEGG Glycan',        
        rest_file='glycan',
        descr_prefix='gl:'),
    D=dict(
        html_class='compound',
        type='KEGG Drug',       
        rest_file='drug',
        descr_prefix='dr:'),
    DG=dict(
        html_class='compound',
        type='KEGG Drug Group',       
        rest_file='dgroup',
        descr_prefix='dg:'),
    BR=dict(
        html_class='brite',
        type='KEGG Brite Entry',        
        rest_file='br',
        descr_prefix=''),
    MAP=dict(
        html_class='kegg-map',
        type='KEGG Map',       
        rest_file='pathway',
        descr_prefix='map'),
    GR=dict(
        html_class='undefined',
        type='KEGG group',       
        rest_file='',
        descr_prefix=''),
    O=dict(
        html_class='undefined',
        type='KEGG other',       
        rest_file='',
        descr_prefix=''),
    Gene=dict(
        html_class='gene',
        type='Org gene',       
        rest_file='org',
        descr_prefix='')
    
)