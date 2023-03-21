import pandas as pd

from utils import findOccurrences
import db_functions as db

def addExperiment(**args):
    expId = db.addExperiment(args)
    return expId

def addCultivation(expId):
    number_cult = db.countRecords('CultivationConditions', 'experimentId', str(expId))
    cultId = expId*100 + number_cult + 1
    db.addCultivation(str(cultId), CULT_DESCRIPTION, str(expId))

    return cultId

def addReplicates(expId, cultId, headers, files):
    number_rep = db.countRecords('TechnicalReplicates', 'cultivationId', str(cultId))

    for i, f in enumerate(files):
        repId = str(cultId) + '_' + str(number_rep + i + 1)
        db.addReplicate(str(repId), REP_DESCRIPTION, str(cultId))
        
        #Get directory of the provided paths
        path_end = max(findOccurrences(f, "/"))
        path = f[:path_end+1]

        #Read file with all the data
        df = pd.read_table(f, sep=" ")
        
        growth_data = df[df.columns.intersection(headers['abundance'])]
        growth_data = growth_data.round({'OD': 3})
        
        ph_data = df[df.columns.intersection(headers['ph'])]
        ph_data = ph_data.round({'pH': 3})

        metabolites_data = df[df.columns.intersection(headers['metabolites'])]
        
        # If len(df.columns) <= 1 (only time column), we do not save it
        if len(growth_data.columns) > 1:
            g_path = path+'abundance_file.txt'
            growth_data.to_csv(g_path, sep=" ", index=False)
            db.addReplicateFile(repId,bacterialAbundanceFile=g_path)
        
        if len(ph_data.columns) > 1:    
            p_path = path+'pH_file.txt'
            ph_data.to_csv(p_path, sep=" ", index=False)
            db.addReplicateFile(repId,phFile=p_path)
        
        if len(metabolites_data.columns) > 1:
            m_path = path+'metabolites_file.txt'
            metabolites_data.to_csv(m_path, sep=" ", index=False)
            db.addReplicateFile(repId,metabolitesFile=m_path)