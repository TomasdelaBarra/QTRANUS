import numpy as np
from TranusConfig import *
from LcalInterface import *
import logging
import sys
import os.path
from Tools import line_remove_strings


class LCALparam:
    '''LCALparam class:
    This class is meant to read all the Tranus LCAL input files, and store
    the lines in local variables.
    '''

    def __init__(self,t):
        '''LCALparam(tranusConfig)
        Constructor of the class, this object has a local variable for each of the
        Tranus lines relevants to LCAL.

        Parameters
        ----------
        tranusConfig : TranusConfig object
            The corresponding TranusConfig object of your project.

        Class Attributes
        ----------------
        list_zones: list
            List of zones.
        list_zones_ext: list
            List of external zones.
        nZones: integer  (len(list_zones))
            Number of zones in list_zones.
        list_sectors: list
            List of Economical Sectors.
        nSectors: integer (len(list_sectors))
            Number of Economical Sectors.
        housingSectors: 1-dimensional ndarray
            Subset of list_sectors including the land-use housing sectors.
        substitutionSectors: 1-dimensional ndarray
            Subset of list_sectors that have substitution.

        Variables from L0E section 1.1, and their corresponding initialized value:
        ExogProd = np.zeros((nSectors,nZones))
            Exogenous base-year Production X* for each sector and zone.
        InduProd = np.zeros((nSectors,nZones))
            Induced base-year Production X_0 for each sector and zone. 
        ExogDemand = np.zeros((nSectors,nZones))  
            Exogenous Demand for each sector and zone.
        Price = np.zeros((nSectors,nZones))
            Base-year prices for each sector and zone.
        ValueAdded = np.zeros((nSectors,nZones))
            Value Added for each sector and zone.
        Attractor = np.zeros((nSectors,nZones))
            Attractors W^n_i for each sector and zone.
        Rmin = np.zeros((nSectors,nZones))
            Lower limit to production, is not used in LCAL. 
        Rmax = np.zeros((nSectors,nZones))
            Upeer limit to production, is not used in LCAL.
        
        Variables from L1E section 2.1:
        alfa = np.zeros(nSectors) 
            Exponent in the Attractor formula. 
        beta = np.zeros(nSectors)
            Dispersion parameter in Pr^n_{ij}
        lamda  = np.zeros(nSectors)
            Marginal Localization Utility of price. 
        thetaLoc = np.zeros(nSectors)
            Exponent in normalization in Localization Utility, not used.

        Variables from L1E section 2.2:
        demax = np.zeros((nSectors,nSectors))
            Elastic demand function max value, for housing consuming->land-use 
            sectors.
        demin = np.zeros((nSectors,nSectors))
            Elastic demand function min value, for housing consuming->land-use 
            sectors.
        delta = np.zeros((nSectors,nSectors))
            Disperion parameter in the demand function a^{mn}_i

        Variables from L1E section 2.3:
        sigma = np.zeros(nSectors)
            Dispersion parameter in Substitution logit, no longer used.
        thetaSub = np.zeros(nSectors)
            Exponent in normalization in substitution logit, not used. 
        omega = np.zeros((nSectors,nSectors))
            Relative weight in substitution logit.
        Kn = np.zeros((nSectors,nSectors),dtype=int)
            Set of possible substitution sectors.

        Variables from L1E section 3.2:
        bkn = np.zeros((nSectors,nSectors))
            Coefficients of the attractor weight.

        Disutil transport, monetary cost transport from C1S:
        t_nij = np.zeros((nSectors,nZones,nZones))
            Disutility of transportation between to zones for a given sector.
        tm_nij = np.zeros((nSectors,nZones,nZones))
            Monetary cost of transportation between to zones for a given sector.
        '''

        #Global Parameters
        self.nbIterations = 0
        self.convergenceFactor = 0
        self.smoothingFactor = 0
        
        self.list_zones,self.list_zones_ext=t.numberingZones()  # list of zones [1,2,4,5,8,....
        self.nZones = len(self.list_zones) #number of zones: 225   

        self.list_sectors   = t.numberingSectors() # list of sectors [1,2,3,4,5,6,7,8,9,10,11,12,13,14,16,17,18,19,20,21,22]
        self.nSectors       = len(self.list_sectors)   #number of sectors: 20
        self.housingSectors = np.array([-1])    #array not initialized
        self.substitutionSectors = np.array([-1])    #array not initialized
        #Variables from L0E section 1.1
        self.ExogProd       = np.zeros((self.nSectors,self.nZones))
        self.InduProd       = np.zeros((self.nSectors,self.nZones))
        self.ExogDemand     = np.zeros((self.nSectors,self.nZones))  
        self.Price          = np.zeros((self.nSectors,self.nZones))
        self.ValueAdded     = np.zeros((self.nSectors,self.nZones))
        self.Attractor      = np.zeros((self.nSectors,self.nZones))
        self.Rmin           = np.zeros((self.nSectors,self.nZones))
        self.Rmax           = np.zeros((self.nSectors,self.nZones))
        #Variables from L1E s ection 2.1
        self.alfa           = np.zeros(self.nSectors)  
        self.beta           = np.zeros(self.nSectors)
        self.lamda          = np.zeros(self.nSectors)
        self.thetaLoc       = np.zeros(self.nSectors)
        #Variables from L1E section 2.2
        self.demax          = np.zeros((self.nSectors,self.nSectors))
        self.demin          = np.zeros((self.nSectors,self.nSectors))
        self.delta          = np.zeros((self.nSectors,self.nSectors))
        #Variables from L1E section 2.3
        self.sigma          = np.zeros(self.nSectors)
        self.thetaSub       = np.zeros(self.nSectors)
        self.omega          = np.zeros((self.nSectors,self.nSectors))
        self.Kn             = np.zeros((self.nSectors,self.nSectors),dtype=int)
        #Variables from L1E section 3.2
        self.bkn            = np.zeros((self.nSectors,self.nSectors))
        #Disutil transport, monetary cost transport from C1S
        self.t_nij          = np.zeros((self.nSectors,self.nZones,self.nZones))
        self.tm_nij         = np.zeros((self.nSectors,self.nZones,self.nZones))
        
        
        #More variables, unused but required for rewriting the files
        self.list_names_sectors = []
        self.list_utility_lvl2 = np.zeros(self.nSectors)  
        self.list_price_lvl2 = np.zeros(self.nSectors)  
        self.list_price_cost_ratio = np.zeros(self.nSectors)  
        self.list_sector_type =np.zeros(self.nSectors)  
        self.read_files(t)
        self.normalize()
    
    def read_files(self, t):
        '''read_files(t)
        Reads the files L0E, L1E and C1S to load the LCAL lines into the
        LCALparam object.
        Parameters
        ----------
        t : TranusConfig object
            The TranusConfig file of your project.

        Example
        -------
        You could use this method for realoading the lines from the files
        after doing modifications.
        >>>filename = '/ExampleC_n/'
        >>>t = TranusConfig(nworkingDirectory = filename)
        >>>param = LCALparam(t)
        >>>param.beta
        array([ 0.,  1.,  1.,  3.,  0.])
        #modify some parameter, for example:
        >>>param.beta[2]=5
        >>>param.beta
        array([ 0.,  1.,  5.,  3.,  0.])
        >>>param.read_files(t)
        >>>param.beta
        array([ 0.,  1.,  1.,  3.,  0.])
        '''
        print "  Loading LCAL object from: %s"%t.workingDirectory
        self.read_C1S(t)
        self.read_L0E(t)
        self.read_L1E(t)
        return

    def read_L0E(self,t):
        '''read_LOE(t)
        Reads the corresponding LOE file located in the workingDirectory.
        Stores what is readed in local variables of the LCALparam object.
        This method is hardcoded, meaning that if the file structure of the
        LOE file changes, probably this method needs to be updated as well.

        It's not meant to be used externally, it's used when you call the 
        constructor of the class.
        '''

        filename=os.path.join(t.workingDirectory,t.obs_file)
        logging.debug("Reading Localization Data File (L0E), [%s]", filename)
        
        filer = open(filename, 'r')
        lines = filer.readlines()
        filer.close()
        
        length_lines = len(lines)
        for i in range(length_lines):
            lines[i]=str.split(lines[i])
        
        """ Section that we are interested in. """
        string = "1.1"
        """ Getting the section line number within the file. """
        for line in range(len(lines)):
            if (lines[line][0] == string):
                break
        """ End of section. This is horribly harcoded as we depend
            on the format of the Tranus lines files and we don't have any control
            over it. Also, this format will probably change in the future, hopefully
            to a standarized one.
        """
        end_of_section = "*-"

        
        line+=2 #puts you in the first line for reading
        
        while lines[line][0][0:2] != end_of_section:
            n,i=self.list_sectors.index(float(lines[line][0])),self.list_zones.index(float(lines[line][1])) #n,i=sector,zone
            self.ExogProd[n,i]      =lines[line][2]
            self.InduProd[n,i]      =lines[line][3]
            self.ExogDemand[n,i]    =lines[line][4]
            self.Price[n,i]         =lines[line][5]
            self.ValueAdded[n,i]    =lines[line][6]
            self.Attractor[n,i]     =lines[line][7]
            
            line+=1
        
        """ Filter sectors """
        
        string = "2.1"
        """ Getting the section line number within the file. """
        for line in range(len(lines)):
            if (lines[line][0] == string):
                break
            
        line+=2 #puts you in the first line for reading            
        while lines[line][0][0:2] != end_of_section:
            n,i=self.list_sectors.index(float(lines[line][0])),self.list_zones.index(float(lines[line][1]))
            self.ExogDemand[n,i]    =lines[line][2]
            line+=1
        
        string = "2.2"              
        """ Getting the section line number within the file. """
        for line in range(len(lines)):
            if (lines[line][0] == string):
                break
            
        line+=2 #puts you in the first line for reading              
        while lines[line][0][0:2] != end_of_section:
            n,i=self.list_sectors.index(float(lines[line][0])),self.list_zones.index(float(lines[line][1]))
            self.Rmin[n,i]      =lines[line][2]
            self.Rmax[n,i]      =lines[line][3]
            line+=1
            
        string = "3."               
        """ Getting the section line number within the file. """
        for line in range(len(lines)):
            if (lines[line][0] == string):
                break
            
        line+=2 #puts you in the first line for reading 
        list_housing=[]             
        while lines[line][0][0:2] != end_of_section:
            n,i=self.list_sectors.index(float(lines[line][0])),self.list_zones.index(float(lines[line][1]))
            if n not in list_housing:
                list_housing.append(n)
            self.Rmin[n,i]      =lines[line][2]
            self.Rmax[n,i]      =lines[line][3]
            line+=1
        self.housingSectors=np.array(list_housing)
        return
    
    def read_C1S(self,t):
        '''read_C1S(t)
        Reads COST_T.MTX and DISU_T.MTX files generated using ./mats from the 
        C1S file. Normally, this files are created when you first create your
        TranusConfig file.

        Stores what is readed in local variables of the LCALparam object.
        This method is hardcoded, meaning that if the file structure of the
        COST_T.MTX and DISU_T.MTX file changes, probably this method needs 
        to be updated as well.

        It's not meant to be used externally, it's used when you call the 
        constructor of the class.
        '''
        interface = LcalInterface(t, t.workingDirectory)
        if not os.path.isfile(os.path.join(t.workingDirectory,"COST_T.MTX")):
            logging.debug(os.path.join(t.workingDirectory,"COST_T.MTX")+': not found!')
            logging.debug("Creating Cost Files with ./mats")
            if interface.runMats() != 1:
                logging.error('Generating Disutily files has failed')

        #Reads the C1S file using mats
        #this is hardcoded because we are using intermediate files DISU_T.MTX and COST_T.MTX
        path = t.workingDirectory
        logging.debug("Reading Activity Location Parameters File (C1S) with Mats")
        
        filer = open(os.path.join(path,"COST_T.MTX"), 'r')
        lines = filer.readlines()
        filer.close()
        
        sector_line=4   #line where the 1st Sector is written
        line=9          #line where the matrix begins
        # print 'Zones: %s'%self.nZones
        while line<len(lines):
            n=int(lines[sector_line][0:4])
            z = 0
            while True:
                param_line = (lines[line][0:4]+lines[line][25:]).split()
                if len(param_line)==0:
                    break
                try:
                    i=int(param_line[0])
                    aux_z = self.list_zones.index(i)
                    # print aux_z
                except ValueError:
                    aux_z = z 
                    # print '>> %s'%aux_z
                if z < self.nZones:
                    self.tm_nij[self.list_sectors.index(n),aux_z,:] = param_line[1:self.nZones+1]
                z+=1
                line+=1
                if line==len(lines):
                    break
            sector_line=line+4
            line+=9     #space in lines between matrices
            
        filer = open(os.path.join(path,"DISU_T.MTX"), 'r')
        lines = filer.readlines()
        filer.close()

        sector_line=4
        line=9
        
        while line<len(lines):
            n=int(lines[sector_line][0:4])
            z = 0
            while True:
                param_line = (lines[line][0:4]+lines[line][25:]).split()
                if len(param_line)==0:
                    break
                try:
                    i=int(param_line[0])
                    aux_z = self.list_zones.index(i)
                    # print aux_z
                except ValueError:
                    aux_z = z 
                    # print '>> %s'%aux_z
                if z < self.nZones:
                    self.t_nij[self.list_sectors.index(n),aux_z,:] = param_line[1:self.nZones+1]
                z+=1
                line+=1
                if line==len(lines):
                    break
            sector_line=line+4
            line+=9     #space in lines between matrices

        return
        
    def read_L1E(self,t):
        '''read_L1E(t)
        Reads the corresponding L1E file located in the workingDirectory.
        Stores what is readed in local variables of the LCALparam object.
        This method is hardcoded, meaning that if the file structure of the
        L1E file changes, probably this method needs to be updated as well.

        It's not meant to be used externally, it's used when you call the 
        constructor of the class.
        '''

        filename=os.path.join(t.workingDirectory,t.scenarioId,t.param_file)
        logging.debug("Reading Activity Location Parameters File (L1E), [%s]", filename)
        
        filer = open(filename, 'r')
        lines = filer.readlines()
        copyLines = list(lines)
        filer.close()
        length_lines = len(lines)
        for i in range(length_lines):
            lines[i]=str.split(lines[i])
        
        string = "1.0"
        for line in range(len(lines)):
            if (lines[line][0] == string):
                break
        line+=2
        self.nbIterations = lines[line][0]
        self.convergenceFactor = lines[line][1]
        self.smoothingFactor = lines[line][2]
        """ Section that we are interested in. """

        string = "2.1"
        """ Getting the section line number within the file. """
        for line in range(len(lines)):
            if (lines[line][0] == string):
                break
        """ End of section. This is horribly harcoded as we depend
            on the format of the Tranus lines files and we don't have any control
            over it. Also, this format will probably change in the future, hopefully
            to a standarized one.
        """
        end_of_section = "*-"
        line+=3
        while lines[line][0][0:2] != end_of_section:
            param_line=line_remove_strings(lines[line])  #we remove the strings from each line!
            self.list_names_sectors.append(copyLines[line].split("'")[1])  #extraction of the sector's name from the unsplit copy, in case there is a space in the name
            n=self.list_sectors.index(float(param_line[0]))
            self.alfa[n]        =param_line[6]
            #print param_line
            self.beta[n]        =param_line[1]
            self.lamda[n]   =param_line[3]
            self.thetaLoc[n]    =param_line[5]
            
            self.list_utility_lvl2[n] =param_line[2]
            self.list_price_lvl2[n] =param_line[4]
            self.list_price_cost_ratio[n] =param_line[7]
            self.list_sector_type[n] =param_line[8]
            line+=1
        

        
        string = "2.2"
        """ Getting the section line number within the file. """
        for line in range(len(lines)):
            if (lines[line][0] == string):
                break
        line+=2
        while lines[line][0][0:2] != end_of_section:
            m,n=self.list_sectors.index(float(lines[line][0])),self.list_sectors.index(float(lines[line][1]))
            self.demin[m,n]=lines[line][2]
            self.demax[m,n]=lines[line][3]
            if self.demax[m,n]==0:
                self.demax[m,n]=self.demin[m,n]
            self.delta[m,n]=lines[line][4]
            line+=1    


        
        string = "2.3"
        """ Getting the section line number within the file. """
        for line in range(len(lines)):
            if (lines[line][0] == string):
                break
        line+=2
        n=0
        list_sub_sectors=[]
        while lines[line][0][0:2] != end_of_section:
            if len(lines[line])==5:
                n=self.list_sectors.index(float(lines[line][0]))
                self.sigma[n]   =lines[line][1]
                self.thetaSub[n]    =lines[line][2]
                self.Kn[n,self.list_sectors.index(float(lines[line][3]))]=1
                self.omega[n,self.list_sectors.index(float(lines[line][3]))]=lines[line][4]
                list_sub_sectors.append(n)
            if len(lines[line])==2:
                self.Kn[n,self.list_sectors.index(int(lines[line][0]))]=1
                self.omega[n,self.list_sectors.index(float(lines[line][0]))]=lines[line][1]
            
            line+=1
            
        self.substitutionSectors = np.array(list_sub_sectors)
        

        
        string = "3.2"
        """ Getting the section line number within the file. """
        for line in range(len(lines)):
            if (lines[line][0] == string):
                break
        line+=2
        while lines[line][0][0:2] != end_of_section:
            m,n=self.list_sectors.index(float(lines[line][0])),self.list_sectors.index(float(lines[line][1]))
            self.bkn[m,n]=lines[line][2]
            line+=1    
        
        return
        
    def write_L1E(self,t):
        '''write_L1E(self, t)
        Overwrite the contents of the L1E file with the data contained in the LCALparam object
        Parameters
        ----------
        t : TranusConfig object
            The TranusConfig file of your project.
        '''
        filename=os.path.join(t.workingDirectory,t.scenarioId,t.param_file)
        logging.debug("Writing Activity Location Parameters File (L1E), [%s]", filename)
        filer = open(filename, 'r')
        lines = filer.readlines()
        length_lines = len(lines)
        filer.close()
        filer = open(filename, 'w')
        linesSplit = [[] for x in xrange(len(lines))]
        for i in range(length_lines):
            linesSplit[i]=str.split(lines[i])
        #Section 2.1
        #Header
        for n in range(0,5):
            filer.write(lines[n])
        
        #Global Parameters
        line_aux =  "{0}{1}{2}  / \n".format(str(self.nbIterations).rjust(14), str(self.convergenceFactor).rjust(15), str(self.smoothingFactor).rjust(11))
        filer.write(line_aux)
        
        for n in range(6,11):
            filer.write(lines[n])
        #Data
        for n in range(len(self.list_sectors)):
            line_aux = "{0} {1} {2}{3}{4}{5}{6}{7}{8}{9}  {10}\n" .format(str(self.list_sectors[n]).rjust(12), ("'"+self.list_names_sectors[n]+"'").ljust(22), str(round(self.beta[n],1)).ljust(11), str(round(self.list_utility_lvl2[n])).ljust(11), str(self.lamda[n]).ljust(11), str(round(self.list_price_lvl2[n])).ljust(11), str(self.thetaLoc[n]).ljust(11), str(self.alfa[n]).ljust(11),str(self.list_price_cost_ratio[n]).ljust(11),str(int(self.list_sector_type[n])).ljust(3), "/")
            filer.write(line_aux)
        #Section 2.2
        #Header
        string = "2.2"
        for line in range(len(lines)):
            if (linesSplit[line][0] == string):
                break
        filer.write(lines[line-1])
        filer.write(lines[line])
        filer.write(lines[line+1])
        #Data
        for m in range(len(self.list_sectors)):
            for n in range(len(self.list_sectors)):
                if(self.demax[m][n] != 0 or self.demin[m][n] != 0):
                    if(self.demax[m][n] == self.demin[m][n]):
                        line_aux = "{0}{1}{2}{3}{4} /\n" .format(str(self.list_sectors[m]).rjust(12), str(self.list_sectors[n]).rjust(9), str(self.demin[m][n]).rjust(15), str(0).rjust(15), str(self.delta[m][n]).rjust(15))
                    else:
                        line_aux = "{0}{1}{2}{3}{4} /\n" .format(str(self.list_sectors[m]).rjust(12), str(self.list_sectors[n]).rjust(9), str(self.demin[m][n]).rjust(15), str(self.demax[m][n]).rjust(15), str(self.delta[m][n]).rjust(15))
                    
                    filer.write(line_aux)
        #Section 2.3
        #Header
        string = "2.3"
        for line in range(len(lines)):
            if (linesSplit[line][0] == string):
                break
        filer.write(lines[line-1])
        filer.write(lines[line])
        filer.write(lines[line+1])
        #Data
        for n in range(len(self.list_sectors)):
            if(n in self.substitutionSectors):
                m = self.list_sectors[n]
                #Get the first value of substitution for this sector
                checkSubstitution = 0
                i = -1
                while checkSubstitution != 1 :
                    i = i+1
                    checkSubstitution = self.Kn[n,i]
                
                line_aux = "{0}{1}{2}{3}{4}\n" .format(str(m).rjust(12), str(self.sigma[n]).rjust(16), str(self.thetaSub[n]).rjust(9), str(self.list_sectors[i]).rjust(10), str(self.omega[n,i]).rjust(13)) 
                filer.write(line_aux)
                #Add all the other values of substitution for this sector then line of separation
                while i < len(self.list_sectors)-1:
                    i=i+1
                    if(self.Kn[n,i] == 1):
                        line_aux ="{0}{1}\n" .format(str(self.list_sectors[i]).rjust(47), str(self.omega[n,i]).rjust(13))
                        filer.write(line_aux)
                filer.write("                                       /\n")
        #Recopy of the 3.1 part, since it isn't affected here
        string = "3.0"
        for line in range(len(lines)):
            if (linesSplit[line][0] == string):
                break
        line = line -1;
        while(linesSplit[line][0]!="3.2"):
            filer.write(lines[line])
            line = line +1
        filer.write(lines[line])
        filer.write(lines[line+1])
        #Section 3.2
        for m in range(len(self.list_sectors)):
            for n in range(len(self.list_sectors)):
                if(self.bkn[m,n] != 0):
                    line_aux = "{0}{1}{2}{3}\n" .format(str(self.list_sectors[m]).rjust(12), str(self.list_sectors[n]).rjust(9), str(self.bkn[m][n]).rjust(11), str(0).rjust(11))
                    filer.write(line_aux)
        
        filer.write("*------------------------------------------------------------------------- /\n")
        return
    
    def normalize(self, t = -1, tm = -1, P = -1, D = -1):
        '''normalize input variables of utilities'''
        if t == -1:
            t = 10**np.floor(np.log10(self.t_nij.max()))
        if tm == -1:
            tm = 10**np.floor(np.log10(self.tm_nij.max()))
        if P == -1:
            P = 10**np.floor(np.log10(self.Price[self.housingSectors,:].max()))
        if D == -1:
            D = 10**np.floor(np.log10(self.demax[:,self.housingSectors].max()))
        print '>Normalising Model<'
        print ' t_nij scale: %f'%t
        print ' tm_nij scale: %f'%tm
        print ' Price scale: %f'%P
        print ' Deman scale: %f'%D
        self.t_nij  /= t
        self.tm_nij /= tm
        self.Price  /= P
        # self.demin[:,self.housingSectors] /= D
        # self.demax[:,self.housingSectors] /= D
        return 

    def __str__(self):
        ex =    """See class docstring"""
        
        return ex
        


if __name__=="__main__":
    from sys import stdout
    log_level = logging.ERROR
    logging.basicConfig(format = '%(asctime)s - %(levelname)s - %(message)s',
                        level  = log_level,
                        stream = stdout)
    t=TranusConfig()
    print "Creating object t: TranusConfig()"
    param=LCALparam(t)
    print "Creating object from class param=LCALparam(t)"
