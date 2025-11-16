import os
import sys
import subprocess
import glob as glob
import argparse 



'''This program cleans up the openfoam cases, deletes the processors directories
   - Can archive the cases
   - Can go into the archive location and look for the oldest cases, deleting or zipping them to save space
'''

parser = argparse.ArgumentParser(prog='archive-v0.1',description='Cleans up OF cases, deletes old cases in archive')
                    
parser.add_argument("-t","--trial", required = True, type=int, nargs = 2,
                    help='Identifies range of files to perform archival actions on.')
parser.add_argument("-a","--archive", action="store_true",
                    help='Will move the cases to the archive drive.')
# parser.add_argument('-d',"--controlDict", action="store_true", 
#                     help='Writes only controlDict for solver.')
# parser.add_argument("--new", action="store_true", 
#                     help='Writes a new caseSetup, will overwrite what is currently there if it exists!')
# parser.add_argument("--modules", action="store_true", 
#                     help='Shows all possible modules.')

args = parser.parse_args()

### Getting paths ###
path = os.getcwd() #path of the case
jobPath = os.path.abspath(os.path.join(path,os.pardir)) #path of the job i.e. 100001
jobNumber = os.path.split(jobPath)[1] #job number i.e. 100001
### End getting paths ###



def main():
    #finding the right trial folders
    trialPaths = findCases()
    
    if args.archive:
        print('Selected cases will be archived to the archive drive after clean up process.')

    print('\tFound {} trial folders to archive.'.format(len(trialPaths)))
    for trialNumber in sorted(trialPaths.keys()):
        trialInitSize = get_directory_size_os_walk(trialPaths[trialNumber])
        print('\t\t{}: {} : {}Gb'.format(trialNumber,trialPaths[trialNumber],round(trialInitSize/1e9,2)))

    #confirm with user
    confirm = input('PROCEED WITH CLEAN UP OF THESE CASES? (y/n):')
    print(confirm.lower())
    if confirm.lower() == 'y':
        print('\nPROCEEDING WITH CLEAN UP!')
        print('-----------------------------------')
        print('\nNOTE: This process is not reversible! Make sure this is what you want to do!')
    elif confirm.lower() == 'n':
        sys.exit('EXITING!')
    else:
        print('Please enter either y or n!')
       
    
    confirm = input('\n\nCONFIRM AGAIN, PROCEED WITH CLEAN UP OF THESE CASES? (y/n):')
    if confirm.lower() == 'y':
        print('\nPROCEEDING WITH CLEAN UP!')
    elif confirm.lower() == 'n':
        sys.exit('EXITING!')
    else:
        print('Please enter either y or n!')
        sys.exit('EXITING!')
    
    #cleaning up the cases
    caseCleanUp(trialPaths)





    

def caseCleanUp(trialPaths):
    print('Cleaning up:')
    #list of files and dirs to keep
    keepList = ['caseSetup','system','constant','EnSight',
                'postProcessing','log.*','*.csv','*.dat',
                '*.png', '*.out']
    for trialNumber in sorted(trialPaths.keys()):
        
        trialPath = trialPaths[trialNumber]

        #make temporary directory to hold files to keep
        if not os.path.exists(os.path.join(trialPath,'tempKeep')):
            subprocess.call(['mkdir',os.path.join(trialPath,'tempKeep')])
        print('\t{}: {}'.format(trialNumber,trialPath))
        keepPaths = []
        for item in keepList:
            paths = glob.glob(os.path.join(trialPath,item))
            #print('\t\tKeeping: {}'.format(paths))
            keepPaths.extend(paths)
        
        for item in keepPaths:
            print('\t\tMoving {} to tempKeep directory'.format(item))
            subprocess.call(['mv',item,os.path.join(trialPath,'tempKeep/.')])

        #delete everything else in the trial folder
        print('\t\tDeleting remaining files and directories in trial folder...')
        remainingItems = glob.glob(os.path.join(trialPath,'*'))
        for item in remainingItems:
            if item == os.path.join(trialPath,'tempKeep'):
                continue
            print('\t\t\tDeleting: {}'.format(item))
           
            

def get_directory_size_os_walk(start_path='.'):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(start_path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            # Skip if it's a symbolic link to avoid double-counting or errors with broken links
            if not os.path.islink(fp):
                total_size += os.path.getsize(fp)
    return total_size     
            

    


def findCases():
    #check that script is run in the right place
    if not os.path.split(path)[-1].lower() == 'cases':
        print('ERROR! This script must be run from within the cases folder of a job directory.')
        sys.exit()

    trialRange = range(args.trial[0],args.trial[1]+1)
    trialsList = glob.glob(os.path.join(path,'*'))
    print('Checking for trial folders to archive...')
    trialPaths = {}
    for trial in trialsList:
        #filter out the directories
        if not os.path.isdir(trial):
            continue
        
        #extract the trial number, could have formats like trial001, or trial001_half, 
        #but we want only the number with no leading zeros, it should filter out trials
        #that are named incorrectly
        trialBase = os.path.split(trial)[-1]
        trialNumberStr = ''.join(filter(str.isdigit,trialBase))
        if trialNumberStr == '':
            continue
        trialNumber = int(trialNumberStr)

        if trialNumber in trialRange:
            trialPaths[trialNumber] = trial

    return trialPaths        
        

        




main()

