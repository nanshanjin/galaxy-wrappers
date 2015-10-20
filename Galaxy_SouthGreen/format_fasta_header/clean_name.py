#!/usr/bin/env python
# -*- coding: utf8 -*-

from multiprocessing import Process, Manager
import os, sys, random, datetime,re
import json

# Pour chaque organisme : regex générale du type de nomenclature, puis à chaque ligne du fichier, test si on trouve  une des correspondances, et selon les cas, ajout du code espèce, remplacement P/T/G et/ou transcrit 1 avec ".1" ou juste sans extension

remove_tr= sys.argv[1] # yes or no
fasta_path = sys.argv[2] # fasta a trier
output_path=sys.argv[3] #  fasta resultat

fasta_file=open(fasta_path,'r')
output_file=open(output_path,'w')
rap_msu_file=open("/bank/genfam/RAP-MSU.txt",'r') #fichier d'équivalence RAP/MSU pour le riz
dic_rap_to_msu={}
dic_msu_to_rap={}

# lotja_file=open("/bank/genfam/genome_data/LOTJA/LOTJA-Kazusa2.5-locus_tag.json",'r')
# lotja_dic=json.loads(lotja_file.read())
# lotja_file.close()

# poptr_file=open("/bank/genfam/genome_data/POPTR/POPTR-JGI2-locus_tag.json",'r')
# poptr_dic=json.loads(poptr_file.read())
# poptr_file.close()

# création des dictionnaires de traduction RAP vers MSU et MSU vers RAP
for line in rap_msu_file :
    rap_msu = line.split('\t')
    rap=rap_msu[0].strip()
    msu=rap_msu[1].split(',')
    dic_rap_to_msu[rap]=msu[0]
    for i in msu :
        dic_msu_to_rap[i.strip()]=rap

		
fasta=fasta_file.readlines()
pat_ARATH_transc=r'(AT[0-9]+G[0-9]{5}\.[0-9]+[^_])'
pat_ARATH=r'(AT[0-9]+G[0-9]{5}[^_\.])'
pat_bradi_transc=r'(Bradi[0-9]+g[0-9]{5}\.[0-9]+[^_])'
pat_bradi=r'(Bradi[0-9]+g[0-9]{5}[^_\.])'
pat_glyma=r'(Glyma[0-9]+g[0-9]{5}[^_\.])'
pat_glyma_transc=r'(Glyma[0-9]+g[0-9]{5}\.[0-9]+[^_])'
pat_gosra=r'(Gorai\.[0-9]+G[0-9]{6}\.[0-9]+[^_])'
pat_lotja=r'(LjSGA_[0-9]{6}\.[0-9]+[^_])' #pb id avec coge
pat_maize=r'(GRMZM[0-9]+[G][0-9]{6}\_[TGP][0-9]+[^_])'
pat_MALDO=r'(MD[CP][0-9]{10}(\.)*[0-9]*[^_])'
pat_manes=r'(cassava4\.1_[0-9]{6}m[^_])'
pat_medtr=r'(Medtr[0-9]+g[0-9]{6}[^_\.])'
pat_medtr_transcr=r'(Medtr[0-9]+g[0-9]{6}[^_][0-9]+)'
pat_musa=r'(GSMUA_Achr([0-9]+|(Un_random))[TGP][0-9]{5}\_[0-9]{3}[^_])'
pat_orysj_MSU=r'((LOC_)?Os[0-9]{2}g[0-9]{5}(\.[0-9]+)?[^0-9])'
pat_orysj_RAP=r'(Os[0-9]{2}g[0-9]{7}[a|b]?)'
pat_ricco=r'([0-9]{5}.m[0-9]{6}(\.[0-9]+)*[^_])'
pat_sollc=r'(Solyc[0-9]{2}g[0-9]{6}\.[0-9]+\.[0-9]+[^_])'
pat_soltu=r'(PGSC[0-9]{4}DM[GTP][0-9]{9}(\.[0-9]+)*[^_])'
pat_sorbi=r'(Sb[0-9]{2}g[0-9]{6}\.[0-9]+[^_])'
pat_cucsa=r'(Cucsa\.[0-9]{6}(\.[0-9]+)?)'
pat_citsi=r'(orange[0-9]+\.[0-9]+g[0-9]{6}m[^_])'
pat_horvu=r'((CDS:)*MLOC_[0-9]{5}\.[0-9]+[^_])'
pat_CAJCA=r'(C.cajan_[0-9]{5}(\[.[0-9]+)[^_])'
pat_MUSBA=r'(ITC[0-9]{4}_Bchr[0-9]+_[TPG][0-9]+[^_])'
pat_POPTR=r'(Potri\.[0-9]{3}G[0-9]{6}\.[1-9]+[^_])' #pb id avec coge
pat_PHODC=r'(PDK_[0-9]{2}s[0-9]+[Lg][0-9]{3}[^_])'
pat_thecc=r'(Tc[0-9]{2}_[tg][0-9]{6}[^_])' #pb id avec coge
pat_theccbis=r'(TCM\_[0-9]{6}[^_])' #pb id avec coge
pat_vitvi=r'(GSVIVT[0-9]{11}[^_])'
pat_vitvibis=r'(LOC[0-9]{9}[^_])'


seqfasta=""
for line in fasta:
	if line[0]==">":
		name = line[1:]
		# Si l'option de retrait des transcrits alternatifs est "yes" : on teste si la séquence fasta précédente est un transcrit alternatif, et dans ce cas on ne l'écrit pas dans le fichier de sortie
		#test
		if remove_tr=="yes" \
		and re.search(r'(\.[2-9]_[A-Z]{5})', seqfasta, flags=0)==None \
		and re.search(r'(\.[1-9]{2}_)', seqfasta, flags=0)==None \
		and re.search(r'(_T0[2-9]_)', seqfasta, flags=0)==None \
		and re.search(r'(_T[1-9]{2}_)', seqfasta, flags=0)==None \
		and re.search(r'(_00[2-9]_MUSAC)', seqfasta, flags=0)==None \
		and re.search(r'(_0[1-9]{2}_MUSAC)', seqfasta, flags=0)==None \
		and re.search(r'(_P0[2-9]_MAIZE)', seqfasta, flags=0)==None \
		and re.search(r'(_P[1-9]{2}_MAIZE)', seqfasta, flags=0)==None \
		and re.search(r'(g0[1-9]{2}_PHODC)', seqfasta, flags=0)==None \
		and re.search(r'(g00[2-9]_PHODC)', seqfasta, flags=0)==None : 
			output_file.write(seqfasta)
		elif remove_tr=="no":
			output_file.write(seqfasta)
		line = line.replace("_ZEAMA","_MAIZE")
		line=line.replace('_ORYSA','_ORYSJ')
		line = line.replace("_SOLLY","_SOLLC")
		line = line.replace("_PHODA","_PHODC")
		line = line.replace('\"',"")
		if re.search(pat_vitvibis, line, flags=0):
			arathres=re.search(pat_vitvibis, line, flags=0)
			name = arathres.group(0).strip()
			newname=name+"_VITVI"
			line = line.replace(name,newname)
		if re.search(pat_vitvi, line, flags=0):
			arathres=re.search(pat_vitvi, line, flags=0)
			name = arathres.group(0).strip()
			newname=name+"_VITVI"
			line = line.replace(name,newname)
		elif re.search(pat_thecc, line, flags=0):
			arathres=re.search(pat_thecc, line, flags=0)
			name = arathres.group(0).strip()
			line = line.replace("t","g")
			newname=name+"_THECC"
			line = line.replace(name,newname)
		elif re.search(pat_theccbis, line, flags=0):
			arathres=re.search(pat_theccbis, line, flags=0)
			name = arathres.group(0).strip()
			newname=name+"_THECC"
			line = line.replace(name,newname)
		elif re.search(pat_orysj_MSU, line, flags=0): #si locus tag au format msu
			arathres=re.search(pat_orysj_MSU, line, flags=0)
			name = arathres.group(0).strip()
			if re.search("LOC_", name, flags=0):
				gene_name =name
			else:
				gene_name = "LOC_"+name
			if re.search("\.[0-9]+", name, flags=0):
				gene_name = gene_name
			else:
				gene_name = gene_name+".1"
			newname= dic_msu_to_rap[gene_name[:-1]+"1"]
			if newname!="None":
				newname=newname+gene_name[-2:]
			else:
				newname = gene_name
			if re.search("_ORYSJ", line, flags=0):
				newname=newname
			else :
				newname=newname+"_ORYSJ"
			line = line.replace(name,newname)
		elif re.search(pat_orysj_RAP, line, flags=0): #si locus tag au format RAP
			arathres=re.search(pat_orysj_RAP, line, flags=0)
			name = arathres.group(0).strip()
			if re.search("_ORYSJ", line, flags=0):
				newname=name
			else:
				if name[-1:]=="a":
					newname = name[0:-1]+".1"
				elif name[-1:]=="b":
					newname = name[0:-1]+".2"
				else:
					newname= name
				newname=newname+"_ORYSJ"
			line = line.replace(name,newname)
		elif re.search(pat_PHODC, line, flags=0):
			arathres=re.search(pat_PHODC, line, flags=0)
			name = arathres.group(0).strip()
			newname = name.replace("L","g")
			newname=newname+"_PHODC"
			line = line.replace(name,newname)
		elif re.search(pat_MALDO, line, flags=0):
			arathres=re.search(pat_MALDO, line, flags=0)
			name = arathres.group(0).strip()
			name = name.replace("C","P")
			newname=name+"_MALDO"
			line = line.replace(name,newname)
		elif re.search(pat_cucsa, line, flags=0):
			arathres=re.search(pat_cucsa, line, flags=0)
			name = arathres.group(0).strip()
			if re.search("_CUCSA", line, flags=0):
				newname=name
			else:
				newname=name+"_CUCSA"
			newname = newname.replace('CDS:','')
			line = line.replace(name,newname)
			line = line.replace(".1_","_")
			# print line
		elif re.search(pat_POPTR, line, flags=0):
			arathres=re.search(pat_POPTR, line, flags=0)
			name = arathres.group(0)
			newname=name[:-1]+"_POPTR"
			line = line.replace(name,newname)
		elif re.search(pat_MUSBA, line, flags=0):
			arathres=re.search(pat_MUSBA, line, flags=0)
			name = arathres.group(0)
			newname=name[:-1]+"_MUSBA"
			newname = newname.replace('G','T')
			newname = newname.replace('P','T')
			line = line.replace(name,newname)
		elif re.search(pat_CAJCA, line, flags=0):
			arathres=re.search(pat_CAJCA, line, flags=0)
			name = arathres.group(0)
			newname=name[:-1]+"_CAJCA"
			line = line.replace(name,newname)
		elif re.search(pat_horvu, line, flags=0):
			arathres=re.search(pat_horvu, line, flags=0)
			name = arathres.group(0)
			newname=name[:-1]+"_HORVU"
			line = line.replace(name,newname)
		elif re.search(pat_citsi, line, flags=0):
			arathres=re.search(pat_citsi, line, flags=0)
			name = arathres.group(0)
			newname=name[:-1]+"_CITSI"
			line = line.replace(name,newname)
		elif re.search(pat_sorbi, line, flags=0):
			arathres=re.search(pat_sorbi, line, flags=0)
			name = arathres.group(0)
			newname=name[:-1]+"_SORBI"
			line = line.replace(name,newname)
		elif re.search(pat_soltu, line, flags=0):
			arathres=re.search(pat_soltu, line, flags=0)
			name = arathres.group(0)
			newname=name[:-1]+"_SOLTU"
			newname = newname.replace('T','G')
			newname = newname.replace('P','G')
			line = line.replace(name,newname)
		elif re.search(pat_sollc, line, flags=0):
			arathres=re.search(pat_sollc, line, flags=0)
			name = arathres.group(0)
			newname=name[:-1]+"_SOLLC"
			line = line.replace(name,newname)
		elif re.search(pat_ricco, line, flags=0):
			arathres=re.search(pat_ricco, line, flags=0)
			name = arathres.group(0)
			newname=name[:-1]+"_RICCO"
			line = line.replace(name,newname)
		elif re.search(pat_ARATH_transc, line, flags=0):
			arathres=re.search(pat_ARATH_transc, line, flags=0)
			name = arathres.group(0)
			newname=name[:-1]+"_ARATH"
			line = line.replace(name,newname)
		elif re.search(pat_ARATH, line, flags=0):
			arathres=re.search(pat_ARATH, line, flags=0)
			name = arathres.group(0)[:-1]
			newname=name+".1_ARATH"
			line = line.replace(name,newname)
		elif re.search(pat_gosra, line, flags=0):
			arathres=re.search(pat_gosra, line, flags=0)
			name = arathres.group(0)
			newname=name[:-1]+"_GOSRA"
			line = line.replace(name,newname)
		elif re.search(pat_lotja, line, flags=0):
			arathres=re.search(pat_gosra, line, flags=0)
			name = arathres.group(0)
			newname=name[:-1]+"_LOTJA"
			line = line.replace(name,newname)
		elif re.search(pat_musa, line, flags=0):
			arathres=re.search(pat_musa, line, flags=0)
			name = arathres.group(0)[:-1]
			newname = name.replace('T','G')
			newname = newname.replace('P','G')
			newname=name+"_MUSAC"
			line = line.replace(name,newname)
		elif re.search(pat_medtr, line, flags=0):
			arathres=re.search(pat_medtr, line, flags=0)
			name = arathres.group(0)
			newname=name[:-1]+".1_MEDTR"
			line = line.replace(name,newname)
		elif re.search(pat_medtr_transcr, line, flags=0):
			arathres=re.search(pat_medtr_transcr, line, flags=0)
			name = arathres.group(0)
			if re.search("_MEDTR", line, flags=0):
				newname=name
			else:
				newname=name+"_MEDTR"
			line = line.replace(name,newname)
		elif re.search(pat_manes, line, flags=0):
			manesres=re.search(pat_manes, line, flags=0)
			name = manesres.group(0)
			newname=name[:-1]+"_MANES"
			line = line.replace(name,newname)
		elif re.search(pat_maize, line, flags=0):
			bradires=re.search(pat_maize, line, flags=0)
			name = bradires.group(0)[:-1]
			newname=name.replace(".v6a","_MAIZE")
			newname=newname.replace("P","G")
			newname=newname.replace("T","G")
			newname=name+"_MAIZE"
			line = line.replace(name,newname)
		elif re.search(pat_glyma, line, flags=0):
			bradires=re.search(pat_glyma, line, flags=0)
			name = bradires.group(0)
			newname=name[:-1]+".1_GLYMA"
			line = line.replace(name,newname)
		elif re.search(pat_glyma_transc, line, flags=0):
			bradires=re.search(pat_glyma_transc, line, flags=0)
			name = bradires.group(0)
			newname=name[:-1]+"_GLYMA"
			line = line.replace(name,newname)
		elif re.search(pat_bradi_transc, line, flags=0):
			bradires=re.search(pat_bradi_transc, line, flags=0)
			name = bradires.group(0)
			newname=name[:-1]+"_BRADI"
			line = line.replace(name,newname)
		elif re.search(pat_bradi, line, flags=0):
			bradires=re.search(pat_bradi, line, flags=0)
			name = bradires.group(0)
			newname=name[:-1]+".1_BRADI"
			line = line.replace(name,newname)
		seqfasta=line
	else:
		seqfasta=seqfasta+line

if remove_tr=="yes" \
and re.search(r'(\.[2-9]_[A-Z]{5})', seqfasta, flags=0)==None \
and re.search(r'(\.[1-9]{2}_)', seqfasta, flags=0)==None \
and re.search(r'(_T0[2-9]_)', seqfasta, flags=0)==None \
and re.search(r'(_T[1-9]{2}_)', seqfasta, flags=0)==None \
and re.search(r'(_00[2-9]_MUSAC)', seqfasta, flags=0)==None \
and re.search(r'(_0[1-9]{2}_MUSAC)', seqfasta, flags=0)==None \
and re.search(r'(_P0[2-9]_MAIZE)', seqfasta, flags=0)==None \
and re.search(r'(_P[1-9]{2}_MAIZE)', seqfasta, flags=0)==None \
and re.search(r'(g0[1-9]{2}_PHODC)', seqfasta, flags=0)==None \
and re.search(r'(g00[2-9]_PHODC)', seqfasta, flags=0)==None :
	output_file.write(seqfasta)
elif remove_tr=="no":
	output_file.write(seqfasta)	

			
fasta_file.close()
output_file.close()

